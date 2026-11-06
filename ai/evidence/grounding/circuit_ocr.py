"""Pure normalization/parsing of immutable circuit OCR evidence.

Recognition remains the OCR provider's operation. These functions never alter
its raw tokens, infer a unit for a bare number, or establish physical ownership.
"""
import math
import re

from shared.schemas.evidence import SourceBBox
from ai.resolution.units import UnitEngine


def normalize_circuit_text(raw):
    text=raw.strip().translate(str.maketrans('₀₁₂₃₄₅₆₇₈₉০১২৩৪৫৬৭৮৯','01234567890123456789'))
    text=re.sub(r'([RrVvCc])\s*_\s*(\d+)',r'\1\2',text)
    # Normalize notation only for parsing; raw OCR evidence stays intact.
    # Parentheses enclose values, not products.
    return re.sub(r'\(\s*([^()]*)\s*\)',r' \1',text).strip()


def parse_circuit_label(text):
    """Parse normalized notation with case-sensitive SI prefixes, no geometry."""
    if any(word in text.lower() for word in ('parallel circuit','combination circuit','series-parallel',
        'series circuit','fig.','figure','dc circuit','circuit diagram')):
        return None
    designator=re.fullmatch(r'([RrVvCc])(\d*)',text)
    if designator:
        letter,index=designator.groups()
        return dict(type={'R':'resistor','V':'voltage_source','C':'capacitor'}[letter.upper()],
                    desig=letter.upper()+(index or '1'),val=None,unit=None)
    if text in ('+','-','十'):
        return dict(type='polarity',desig='+' if text in ('+','十') else '-',val=None,unit=None)
    # Tokens with both designator and value (e.g. "R1 = 10 Ω", "V=6 V").
    match=re.fullmatch(r'(?:([RrVvCc])(\d*)\s*(?:=\s*|\s+))?(?:=\s*)?'
                       r'((?:\d+(?:\.\d*)?|\.\d+))\s*([kKmMmunpµμ]?(?:Ω|ω|(?i:ohms?|volts?)|V|v|F))',text)
    if match:
        letter,index,number,unit=match.groups()
        if unit.endswith(('Ω','ω')):
            unit=unit[:-1]+'Ω'
            if unit.startswith('K'):unit='k'+unit[1:]
        dimension='resistance' if unit.endswith('Ω') or unit.lower().endswith(('ohm','ohms')) else 'capacitance' if unit.endswith('F') else 'voltage'
        kind={'resistance':'resistor','capacitance':'capacitor','voltage':'voltage_source'}[dimension]
        if letter and {'R':'resistor','V':'voltage_source','C':'capacitor'}[letter.upper()]!=kind:
            return None
        quantity=UnitEngine.parse_quantity(float(number),unit,dimension)
        if not quantity.success or not math.isfinite(quantity.canonical_value):
            return None
        return dict(type=kind,desig=letter.upper()+(index or '1') if letter else None,
                    val=quantity.canonical_value,unit=quantity.canonical_unit)
    if re.fullmatch(r'\d+(?:\.\d+)?',text):
        return dict(type='raw_number',desig=None,val=float(text),unit=None)
    return None


def parse_circuit_ocr_tokens(tokens):
    """Parse recognition results and uniquely join adjacent number/unit tokens."""
    parsed=[]
    for token in tokens:
        spec=parse_circuit_label(normalize_circuit_text(token.raw_text))
        if spec and token.bbox_source_px:
            b=token.bbox_source_px
            parsed.append(dict(spec,tok=token,tokens=[token],raw=token.raw_text,bbox=b,
                               cx=b.x+b.width/2,cy=b.y+b.height/2))
    # OCR can emit a bare number and a separate unit. Each must be the other's
    # unique adjacent partner on the same text row or column; ties stay raw.
    numbers=[p for p in parsed if p['type']=='raw_number']
    units=[t for t in tokens if t.bbox_source_px and re.fullmatch(
        r'[kKmMmunpµμ]?(?:Ω|ω|(?i:ohms?|volts?)|V|v|F)',normalize_circuit_text(t.raw_text))]
    pairs=[]
    for p in numbers:
        a=p['bbox']
        for t in units:
            b=t.bbox_source_px
            horizontal=min(a.y_max,b.y_max)-max(a.y,b.y)>.5*min(a.height,b.height)
            vertical=min(a.x_max,b.x_max)-max(a.x,b.x)>.5*min(a.width,b.width)
            gap=max(a.x-b.x_max,b.x-a.x_max,0) if horizontal else max(a.y-b.y_max,b.y-a.y_max,0)
            if (horizontal or vertical) and gap<=2*max(a.height,b.height):
                pairs.append((gap/max(a.height,b.height,1),p,t))
    for distance,p,t in pairs:
        if any((q is p or u is t) and (q is not p or u is not t) and d<=distance+.25 for d,q,u in pairs):
            continue
        spec=parse_circuit_label(normalize_circuit_text(p['tok'].raw_text+' '+t.raw_text))
        if not spec:continue
        a,b=p['bbox'],t.bbox_source_px
        box=SourceBBox(min(a.x,b.x),min(a.y,b.y),max(a.x_max,b.x_max)-min(a.x,b.x),max(a.y_max,b.y_max)-min(a.y,b.y))
        p.update(spec,tokens=[p['tok'],t],bbox=box,cx=box.x+box.width/2,cy=box.y+box.height/2)
    return parsed
