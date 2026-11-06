"""Generate fresh synthetic holdouts with analytic/source geometry ground truth.

This renderer is independent of perception and training generators. It records
the drawing specification before inference. Synthetic results are never labelled
as real textbook performance. Existing output directories are never overwritten.
"""
import argparse
from copy import deepcopy
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image,ImageDraw,ImageFont


def schematic(complexity=False,fault=False,junction_variant=False):
    image=Image.new('RGB',(740,440),'white');draw=ImageDraw.Draw(image)
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
    components=[]
    wires=[[[80,200],[80,80],[200,80]],[[80,220],[80,340],[200,340]],
        [[280,80],[400,80]],[[280,340],[400,340]],[[400,80],[400,160]],[[400,240],[400,340]],
        [[400,80],[600,80],[600,160]],[[400,340],[600,340],[600,240]]]
    junctions=[[400,80],[400,340]]
    for points in wires:draw.line([tuple(p) for p in points],fill='black',width=3)
    draw.line([(58,200),(102,200)],fill='black',width=3)
    draw.line([(68,220),(92,220)],fill='black',width=3)
    voltage=9 if junction_variant else 12
    draw.text((15,190),f'{voltage}V',fill='black',font=font)
    components.append(dict(id='V',type='voltage_source',value=voltage,bbox=[56,198,104,222],
        terminals=[[80,200],[80,220]],nodes=['A','D']))
    def resistor(cid,value,a,b,nodes,label):
        aa,bb=np.array(a,float),np.array(b,float);axis=(bb-aa)/np.linalg.norm(bb-aa);normal=np.array([-axis[1],axis[0]])
        points=np.array([aa,*[aa+(bb-aa)*i/8+normal*8*(-1)**i for i in range(1,8)],bb])
        draw.line([tuple(p) for p in points],fill='black',width=3)
        draw.text(label,f'{cid} ({value}Ω)',fill='black',font=font)
        lo=points.min(axis=0)-2;hi=points.max(axis=0)+2
        components.append(dict(id=cid,type='resistor',value=value,bbox=[*lo.tolist(),*hi.tolist()],
                               terminals=[a,b],nodes=nodes))
    resistor('R1',7 if junction_variant else 5,[200,80],[280,80],['A','B'],(195,30))
    if junction_variant:
        draw.line([(200,340),(280,340)],fill='black',width=3);wires.append([[200,340],[280,340]])
    else:resistor('R4',1,[200,340],[280,340],['D','C'],(195,365))
    resistor('R2',4 if junction_variant else 3,[400,160],[400,240],['B','C'],(414,192))
    resistor('R3',12 if junction_variant else 6,[600,160],[600,240],['B','C'],(614,192))
    if complexity:
        extra=[[[500,80],[500,160]],[[500,240],[500,340]]]
        for path in extra:draw.line([tuple(p) for p in path],fill='black',width=3)
        wires+=extra;junctions += [[500,80],[500,340]]
        resistor('R5',12,[500,160],[500,240],['B','C'],(510,245))
    for point in junctions:draw.ellipse((point[0]-5,point[1]-5,point[0]+5,point[1]+5),fill='black')
    parallel=3 if junction_variant else 1/(1/3+1/6+(1/12 if complexity else 0))
    equivalent=(7 if junction_variant else 6)+parallel;current=voltage/equivalent
    for c in components:c['current_a']=current if c['id'] in {'V','R1','R4'} else current*parallel/c['value']
    if junction_variant:
        for c in components:c['nodes']=['C' if n=='D' else n for n in c['nodes']]
    if fault:
        bypass=[[80,120],[5,120],[5,300],[80,300]]
        draw.line([tuple(p) for p in bypass],fill='black',width=3);wires.append(bypass)
        junctions += [[80,120],[80,300]]
        for c in components:
            c['nodes']=['A' if n=='D' else n for n in c['nodes']]
    return np.array(image),dict(components=components,wires=wires,junctions=junctions,crossings=[],
        valid=not fault,expected_resistance_ohm=equivalent,source_current_a=current)


def transform_case(image,case,scale=1,angle=0,noise=False):
    h,w=image.shape[:2]
    matrix=cv2.getRotationMatrix2D((w/2,h/2),angle,scale)
    # Preserve every transformed source pixel in a padded native frame.
    corners=cv2.transform(np.array([[[0,0],[w,0],[w,h],[0,h]]],np.float32),matrix)[0]
    lo=np.floor(corners.min(axis=0));hi=np.ceil(corners.max(axis=0));matrix[:,2]-=lo
    output=cv2.warpAffine(image,matrix,tuple((hi-lo).astype(int)),flags=cv2.INTER_LINEAR,borderValue=(255,255,255))
    if noise:
        rng=np.random.default_rng(20261106)
        output=np.clip(output.astype(float)+rng.normal(0,8,output.shape),0,255).astype(np.uint8)
    def points(value):return cv2.transform(np.array([value],np.float32),matrix)[0].astype(float).tolist()
    result=deepcopy(case)
    result['wires']=[points(p) for p in case['wires']]
    result['junctions']=points(case['junctions'])
    for c in result['components']:
        c['terminals']=points(c['terminals'])
        x1,y1,x2,y2=c['bbox'];quad=np.array(points([[x1,y1],[x2,y1],[x2,y2],[x1,y2]]))
        c['bbox']=[*quad.min(axis=0).tolist(),*quad.max(axis=0).tolist()]
    return output,result


def generate(output,junction_only=False):
    output.mkdir(parents=True,exist_ok=False)
    cases=[]
    variants=[('junction_three_resistors',{})] if junction_only else [('clean',{}),('high_resolution',{'scale':2}),('low_resolution',{'scale':.6}),
        ('noisy',{'noise':True}),('rotated',{'angle':12}),('complex',{}),('short_fault',{})]
    for name,options in variants:
        image,truth=schematic(complexity=name=='complex',fault=name=='short_fault',junction_variant=junction_only)
        image,truth=transform_case(image,truth,**options)
        path=output/(name+'.png');Image.fromarray(image).save(path)
        truth.update(id='synthetic_'+name,source=str(path.resolve()),strata=[name,'synthetic'])
        cases.append(truth)
    manifest=dict(schema_version=1,annotation_provenance='Independent procedural source specification recorded before inference. Fresh synthetic holdout, not real textbook imagery or human annotations.',
                  terminal_annotation_uncertainty_px=1,cases=cases)
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2,allow_nan=False),encoding='utf8')
    return manifest


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--junction-only',action='store_true');args=parser.parse_args()
    generate(args.output,args.junction_only)
