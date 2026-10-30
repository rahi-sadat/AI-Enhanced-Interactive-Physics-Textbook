"""Generate offline Schemdraw circuits with measured, native-pixel ground truth.

Run from the repository root; see docs/SYNTHETIC_CIRCUIT_DATASET.md.
No production perception, schema, compiler, solver, or VLM is imported.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from dataclasses import dataclass, field
import hashlib
import io
import json
import math
from pathlib import Path
import platform
import random
import shutil
import sys

import matplotlib

matplotlib.use("Agg")
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.transforms import Affine2D, Bbox
import numpy as np
import PIL
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import schemdraw
import schemdraw.elements as elm
from schemdraw.segments import Segment, SegmentText


CLASSES = ("resistor", "voltage_source", "capacitor", "switch")
PREFIXES = ("R", "V", "C", "S")
TOPOLOGIES = (
    "series", "parallel_resistors", "series_parallel", "rc_series",
    "rc_parallel", "mixed_rc", "open_switch", "closed_switch",
    "multi_branch", "many_rc",
)
PALETTE = ("#d43d37", "#2078c4", "#298449", "#9451b1")
SCHEMA_VERSION = "synthetic-circuits-1.0"
MARKER = ".circuit_dataset_generator.json"
DEFAULT_OUTPUT = Path("datasets/circuits_v1/synthetic_v1")


def point_key(p):
    return tuple(round(float(v), 8) for v in p)


def rounded(p):
    return [round(float(v), 5) for v in p]


def overlap(a, b, clearance=0):
    return (a[0] < b[2] + clearance and b[0] < a[2] + clearance
            and a[1] < b[3] + clearance and b[1] < a[3] + clearance)


def line_hits_box(a, b, box):
    """Liang-Barsky clipping, including diagonal scan-rotated wire segments."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    lo, hi = 0.0, 1.0
    for p, q in ((-dx, a[0]-box[0]), (dx, box[2]-a[0]),
                 (-dy, a[1]-box[1]), (dy, box[3]-a[1])):
        if abs(p) < 1e-12:
            if q < 0:
                return False
        elif p < 0:
            lo = max(lo, q/p)
        else:
            hi = min(hi, q/p)
    return lo <= hi


@dataclass
class Layout:
    topology: str
    components: list = field(default_factory=list)
    wires: list = field(default_factory=list)

    def component(self, kind, a, b, state=None):
        self.components.append(dict(kind=kind, a=point_key(a), b=point_key(b), state=state))

    def wire(self, a, b):
        if point_key(a) != point_key(b):
            self.wires.append((point_key(a), point_key(b)))


def chain(layout, kinds, a, b, state=None):
    for i, kind in enumerate(kinds):
        p = tuple(a[j] + (b[j]-a[j])*i/len(kinds) for j in (0, 1))
        q = tuple(a[j] + (b[j]-a[j])*(i+1)/len(kinds) for j in (0, 1))
        layout.component(kind, p, q, state if kind == "switch" else None)


def make_layout(index: int, rng: random.Random) -> Layout:
    """Balanced topology schedule; random structure is separate from appearance."""
    topology = TOPOLOGIES[index % len(TOPOLOGIES)]
    layout = Layout(topology)
    # At 600 samples this guarantees >=420 switches, before random additions.
    switched = topology not in {"series", "parallel_resistors", "rc_series"} or rng.random() < .55
    state = "open" if topology == "open_switch" else "closed" if topology == "closed_switch" else rng.choice(("open", "closed"))
    if topology in {"series", "rc_series", "open_switch", "closed_switch"}:
        kinds = ["resistor"] * rng.randint(1, 3)
        if topology != "series":
            kinds += ["capacitor"] * rng.randint(1, 2)
        if switched:
            kinds.append("switch")
        rng.shuffle(kinds)
        n_top = rng.randint(1, min(3, len(kinds)))
        n_right = min(len(kinds)-n_top, rng.randint(0, 2))
        n_bottom = len(kinds)-n_top-n_right
        width = max(n_top, n_bottom, 1) * rng.uniform(2.65, 3.55)
        height = max(1, n_right) * rng.uniform(2.8, 3.7)
        source_count = 2 if len(kinds) < 6 and rng.random() < .15 else 1
        chain(layout, ["voltage_source"]*source_count, (0, 0), (0, height))
        for group, a, b in (
            (kinds[:n_top], (0, height), (width, height)),
            (kinds[n_top:n_top+n_right], (width, height), (width, 0)),
            (kinds[n_top+n_right:], (width, 0), (0, 0)),
        ):
            chain(layout, group, a, b, state) if group else layout.wire(a, b)
    else:
        if topology == "parallel_resistors":
            branches = [["resistor"] for _ in range(rng.randint(2, 4))]
            feed = []
        elif topology == "series_parallel":
            branches = [["resistor"]*rng.randint(1, 2) for _ in range(rng.randint(2, 3))]
            feed = ["resistor"]
        elif topology == "rc_parallel":
            branches = [["resistor"], ["capacitor"]]
            branches += [[rng.choice(("resistor", "capacitor"))] for _ in range(rng.randint(0, 2))]
            feed = []
        elif topology == "mixed_rc":
            branches = [["resistor", "capacitor"], [rng.choice(("resistor", "capacitor"))]]
            feed = ["resistor", "capacitor"]
        elif topology == "multi_branch":
            branches = [["resistor"], ["capacitor"]]
            branches += [[rng.choice(("resistor", "capacitor"))] for _ in range(rng.randint(1, 3))]
            feed = []
        else:
            branches = [["resistor", "capacitor"] for _ in range(rng.randint(2, 3))]
            feed = []
        if switched:
            feed.append("switch")
        # Bound object count, preserving both R and C where required.
        while 1 + len(feed) + sum(map(len, branches)) > 8:
            branch = max(branches, key=len)
            if len(branch) == 1:
                branches.pop()
            else:
                branch.pop()
        rng.shuffle(branches)
        for branch in branches:
            rng.shuffle(branch)
        height = max(map(len, branches)) * rng.uniform(2.7, 3.6)
        feed_width = max(1, len(feed)) * rng.uniform(2.65, 3.5)
        spacing = rng.uniform(2.7, 3.8)
        layout.component("voltage_source", (0, 0), (0, height))
        if feed:
            chain(layout, feed, (0, height), (feed_width, height), state)
        else:
            layout.wire((0, height), (feed_width, height))
        layout.wire((0, 0), (feed_width, 0))
        for i, branch in enumerate(branches):
            x = feed_width + i*spacing
            if i:
                layout.wire((x-spacing, height), (x, height))
                layout.wire((x-spacing, 0), (x, 0))
            chain(layout, branch, (x, height), (x, 0))
    # Quarter turns change layout and orientations; printed labels remain upright.
    turn = rng.randrange(4)
    def rotate(p):
        x, y = p
        return point_key(((x, y), (-y, x), (-x, -y), (y, -x))[turn])
    for c in layout.components:
        c["a"], c["b"] = rotate(c["a"]), rotate(c["b"])
    layout.wires = [(rotate(a), rotate(b)) for a, b in layout.wires]
    return layout


class TrackedSymbol(elm.Element):
    """Native Schemdraw body, without Element2Term's automatic long leads.

    SegmentText polarity marks are drawn and measured separately. The original
    first segment's endpoint anchors define the two electrical attachment sites.
    This uses the documented custom Element/Segment interface, not guessed boxes.
    """
    def __init__(self, native, **kwargs):
        super().__init__(**kwargs)
        self.segments = deepcopy([s for s in native.segments if not isinstance(s, SegmentText)])
        self.marks = deepcopy([s for s in native.segments if isinstance(s, SegmentText)])
        path = np.asarray(native.segments[0].path)
        finite = path[np.isfinite(path).all(axis=1)]
        self.anchors.update(a=tuple(finite[0]), b=tuple(finite[-1]))


def make_symbol(kind, rng, state=None):
    if kind == "resistor":
        style = rng.choice(("ansi_zigzag", "iec_rectangle"))
        native = elm.ResistorIEEE() if style == "ansi_zigzag" else elm.ResistorIEC()
        value = rng.choice((1, 5, 10, 22, 47, 100, 220, 1000, 2200))
        display = f"{value/1000:g} kΩ" if value >= 1000 else f"{value} Ω"
        unit = "ohm"
    elif kind == "voltage_source":
        style = rng.choice(("cell_1", "battery_2", "dc_circle"))
        native = {"cell_1": elm.BatteryCell, "battery_2": elm.Battery, "dc_circle": elm.SourceV}[style]()
        value = rng.choice((3, 5, 9, 12, 18, 24))
        unit, display = "V", f"{value} V"
    elif kind == "capacitor":
        style = rng.choice(("parallel_plates", "polarized_parallel", "polarized_curved"))
        native = elm.Capacitor2(polar=True) if style == "polarized_curved" else elm.Capacitor(polar=style == "polarized_parallel")
        micro = rng.choice((1, 10, 22, 47, 100, 220))
        value, unit, display = micro*1e-6, "F", f"{micro} µF"
    else:
        state = state or rng.choice(("open", "closed"))
        style = f"{state}_contacts"
        native = elm.Switch(nc=state == "closed")
        if state == "closed":
            # Explicit contact-to-contact blade, using native contact geometry.
            # The ordinary nc symbol's angled blade is less clear at small sizes.
            left, right = native.segments[1].center, native.segments[2].center
            native.segments[0] = Segment([(0, 0), (float('nan'), float('nan')), left, right,
                                         (float('nan'), float('nan')), (1, 0)])
        value, unit, display = None, None, ""
    return TrackedSymbol(native), dict(symbol_style=style, value=value, unit=unit,
                                       display_value=display, state=state if kind == "switch" else None)


def electrical_nodes(layout):
    """Union only explicit wires, never component terminals or switch contacts."""
    parent = {}
    def find(p):
        p = point_key(p)
        parent.setdefault(p, p)
        if parent[p] != p:
            parent[p] = find(parent[p])
        return parent[p]
    for a, b in layout.wires:
        parent[find(b)] = find(a)
    for c in layout.components:
        find(c["a"]); find(c["b"])
    roots = sorted({find(p) for p in parent})
    ids = {root: f"N{i}" for i, root in enumerate(roots)}
    return {p: ids[find(p)] for p in parent}


def artist_box(artists, renderer, height, dpi):
    """Tight artist geometry plus its real half-stroke; display -> PNG pixels."""
    boxes = []
    for artist in artists:
        box = artist.get_window_extent(renderer)
        if not np.isfinite(box.extents).all():
            continue
        # Matplotlib path extents omit the stroke. Point sizes are physical,
        # hence dpi/72 is the exact conversion, not an arbitrary pixel offset.
        pad = artist.get_linewidth()*dpi/144 if hasattr(artist, "get_linewidth") else 0
        boxes.append(box.padded(pad))
    if not boxes:
        raise ValueError("A generated symbol has no measurable body artists")
    b = Bbox.union(boxes)
    return [float(b.x0), float(height-b.y1), float(b.x1), float(height-b.y0)]


def render_sample(index, seed, *, return_debug=False):
    rng = random.Random(seed)
    layout = make_layout(index, rng)
    node_map = electrical_nodes(layout)
    dims = ((768, 640), (960, 720), (1024, 768), (1152, 864), (1280, 960), (960, 960))
    width, height = rng.choice(dims)
    points = np.asarray([p for c in layout.components for p in (c["a"], c["b"])])
    span = np.ptp(points, axis=0)
    if span[1] > span[0]*1.4:
        width, height = height, width
    center = (points.min(axis=0)+points.max(axis=0))/2
    margin = rng.uniform(68, 102)
    scale = min((width-2*margin)/(span[0]+1.6), (height-2*margin)/(span[1]+1.6))
    angle = 0.0 if rng.random() < .25 else rng.uniform(-1.6, 1.6)
    linewidth = rng.uniform(1.1, 2.0)
    fontsize = rng.choice((9, 10, 11, 12, 13))
    font = rng.choice(("DejaVu Sans", "DejaVu Serif", "DejaVu Sans Mono"))
    paper = rng.choice(((255, 255, 255), (253, 252, 248), (249, 248, 244)))
    dpi = 100
    fig = Figure(figsize=(width/dpi, height/dpi), dpi=dpi, facecolor=np.array(paper)/255)
    canvas = FigureCanvasAgg(fig)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    ax.set_xlim(center[0]-width/(2*scale), center[0]+width/(2*scale))
    ax.set_ylim(center[1]-height/(2*scale), center[1]+height/(2*scale))
    ax.set_autoscale_on(False)
    scan = Affine2D().rotate_deg_around(*center, angle)
    transform = scan + ax.transData
    pixel_transform = transform + Affine2D().scale(1, -1).translate(0, height)
    def pixel(p):
        return rounded(pixel_transform.transform(p))
    def draw(elements):
        old = set(ax.get_children())
        d = schemdraw.Drawing(show=False)
        d.config(lw=linewidth, color="#171717", bgcolor=tuple(v/255 for v in paper), fontsize=fontsize, font=font)
        for element in elements:
            d.add(element)
        d.draw(show=False, canvas=ax)
        new = [a for a in ax.get_children() if a not in old]
        for artist in new:
            artist.set_transform(transform)
        return new

    components, body_artists, wire_records = [], [], []
    counts = Counter()
    label_mode = rng.choices(("values_and_designators", "designators_only", "unlabelled"), (55, 30, 15))[0]
    for spec in layout.components:
        kind = spec["kind"]
        class_id = CLASSES.index(kind)
        counts[kind] += 1
        desig = f"{PREFIXES[class_id]}{counts[kind]}"
        symbol, info = make_symbol(kind, rng, spec["state"])
        a, b = np.asarray(spec["a"]), np.asarray(spec["b"])
        # Cell long plate is terminal a; the circular source's + is terminal b.
        if kind == "voltage_source" and info["symbol_style"] != "dc_circle":
            a, b = b, a
        elif kind in {"resistor", "switch"} and rng.random() < .5:
            a, b = b, a
        direction = (b-a)/np.linalg.norm(b-a)
        theta = math.degrees(math.atan2(direction[1], direction[0]))
        symbol_scale = rng.uniform(.85, 1.2)
        anchor_a, anchor_b = map(np.asarray, (symbol.anchors["a"], symbol.anchors["b"]))
        mid = (anchor_a+anchor_b)/2
        rot = np.array([[direction[0], -direction[1]], [direction[1], direction[0]]])
        origin = (a+b)/2 - symbol_scale*(rot@mid)
        symbol.at(tuple(origin)).theta(theta).scale(symbol_scale)
        artists = draw([symbol])
        ta, tb = symbol.absanchors["a"], symbol.absanchors["b"]
        nid_a, nid_b = node_map[point_key(a)], node_map[point_key(b)]
        for u, v, nid in ((a, ta, nid_a), (tb, b, nid_b)):
            wire_records.append(dict(node_id=nid, points_px=[pixel(u), pixel(v)]))
        component = dict(id=desig, **{"class": kind}, class_id=class_id, designator=desig,
                         **info, parameter_provenance="synthetic_ground_truth",
                         terminals={"a": pixel(ta), "b": pixel(tb)},
                         nodes={"a": nid_a, "b": nid_b}, text=[],
                         orientation_deg=round((theta+angle) % 360, 5))
        if kind == "voltage_source":
            component["positive_terminal"] = "b" if info["symbol_style"] == "dc_circle" else "a"
            component["battery_cells"] = {"cell_1": 1, "battery_2": 2, "dc_circle": 0}[info["symbol_style"]]
        if kind == "capacitor" and symbol.marks:
            component["positive_terminal"] = "a"
        components.append(component)
        body_artists.append(artists)
        # Preserve the native + polarity mark position, measured as separate text.
        component["_marks"] = [(pixel(symbol.transform.transform(mark.xy)), mark.text) for mark in symbol.marks]

    for a, b in layout.wires:
        wire_records.append(dict(node_id=node_map[a], points_px=[pixel(a), pixel(b)]))
    # Wires use pixel positions inverted through the exact transform to avoid
    # a second geometry convention; every connection is an explicit lead.
    wire_elements = []
    inverse = pixel_transform.inverted()
    for w in wire_records:
        u, v = [tuple(inverse.transform(p)) for p in w["points_px"]]
        wire_elements.append(elm.Line().at(u).to(v))
    draw(wire_elements)
    # Junction dots are drawn only at explicit degree >=3 graph vertices.
    degree = Counter(p for c in layout.components for p in (c["a"], c["b"]))
    degree.update(p for w in layout.wires for p in w)
    junctions = [p for p, n in degree.items() if n >= 3]
    draw([elm.Dot(radius=.045).at(p) for p in junctions]) if junctions else None
    canvas.draw()
    renderer = canvas.get_renderer()
    for c, artists in zip(components, body_artists):
        c["bbox_xyxy_px"] = rounded(artist_box(artists, renderer, height, dpi))

    text_artists, used_text = [], []
    body_boxes = [c["bbox_xyxy_px"] for c in components]
    stroke_px = linewidth*dpi/72
    def add_text(content, pos, role, c):
        # Pixel -> data mapping includes the same scan affine as the symbols.
        xy = pixel_transform.inverted().transform(pos)
        t = ax.text(*xy, content, fontfamily=font, fontsize=fontsize,
                    color="#171717", ha="center", va="center", rotation=angle,
                    rotation_mode="anchor", transform=transform)
        box = artist_box([t], renderer, height, dpi)
        if not (2 <= box[0] < box[2] <= width-2 and 2 <= box[1] < box[3] <= height-2):
            t.remove()
            return None
        if any(overlap(box, b, stroke_px) for b in body_boxes+used_text):
            t.remove()
            return None
        if any(line_hits_box(*w["points_px"], box) for w in wire_records):
            t.remove()
            return None
        used_text.append(box)
        text_artists.append(t)
        item = dict(content=content, role=role, position_px=rounded(pos),
                    bbox_xyxy_px=rounded(box), rotation_deg=round(angle, 5))
        c["text"].append(item)
        return item

    for c in components:
        for pos, mark in c.pop("_marks"):
            if not add_text(mark, pos, "polarity", c):
                raise ValueError("Native polarity mark overlaps another symbol, wire or label")
        if label_mode == "unlabelled":
            continue
        content = c["designator"]
        if label_mode == "values_and_designators" and c["display_value"]:
            content += " = " + c["display_value"]
        # Measure actual glyph dimensions before selecting an uncluttered site.
        probe = ax.text(0, 0, content, fontsize=fontsize, fontfamily=font)
        probe_box = probe.get_window_extent(renderer)
        probe.remove()
        tw, th = probe_box.width, probe_box.height
        x0, y0, x1, y1 = c["bbox_xyxy_px"]
        cx, cy = (x0+x1)/2, (y0+y1)/2
        gap = th*.65 + stroke_px
        horizontal = abs(c["terminals"]["a"][0]-c["terminals"]["b"][0]) > abs(c["terminals"]["a"][1]-c["terminals"]["b"][1])
        above_below = [(cx, y0-gap-th/2), (cx, y1+gap+th/2)]
        left_right = [(x1+gap+tw/2, cy), (x0-gap-tw/2, cy)]
        candidates = above_below+left_right if horizontal else left_right+above_below
        placed = any(add_text(content, pos, "designator_and_value" if " = " in content else "designator", c) for pos in candidates)
        if not placed:
            raise ValueError(f"No readable text placement for {c['id']}")

    canvas.draw()
    image = Image.fromarray(np.asarray(canvas.buffer_rgba())[:, :, :3].copy())
    blur = rng.choice((0.0, 0.0, .18, .28, .38))
    noise = rng.choice((0.0, 0.0, .45, .8, 1.1))
    quality = rng.choice((None, None, 85, 90, 95))
    if blur:
        image = image.filter(ImageFilter.GaussianBlur(blur))
    if noise:
        pixels = np.asarray(image, dtype=np.float32)
        pixels += np.random.default_rng(seed).normal(0, noise, (height, width, 1))
        image = Image.fromarray(np.clip(np.rint(pixels), 0, 255).astype(np.uint8))
    if quality:
        stream = io.BytesIO()
        image.save(stream, format="JPEG", quality=quality, subsampling=0)
        stream.seek(0)
        image = Image.open(stream).convert("RGB")
        image.load()
    # Photometric operations above do not move geometry. No crop, resize, or
    # image-space rotation follows annotation; scan rotation is already in M.
    nodes = []
    for nid in sorted(set(node_map.values())):
        nodes.append(dict(id=nid, positions_px=[pixel(p) for p in sorted(node_map) if node_map[p] == nid]))
    metadata = dict(schema_version=SCHEMA_VERSION, generation_seed=seed,
                    coordinate_space="source_px", width=width, height=height,
                    topology=layout.topology, label_mode=label_mode,
                    drawing_to_final_px=pixel_transform.get_matrix().tolist(),
                    appearance=dict(font_family=font, font_size_pt=fontsize,
                                    line_width_pt=linewidth, line_width_px=stroke_px,
                                    paper_rgb=paper, scan_rotation_deg=angle,
                                    blur_radius_px=blur, scan_noise_std=noise, jpeg_quality=quality),
                    components=components, nodes=nodes, wires=wire_records,
                    junctions_px=[pixel(p) for p in junctions],
                    connections=[dict(component_id=c["id"], terminal=t, node_id=nid)
                                 for c in components for t, nid in c["nodes"].items()])
    debug = dict(figure=fig, canvas=canvas, body_artists=body_artists,
                 text_artists=text_artists, renderer=renderer)
    if return_debug:
        return image, metadata, debug
    fig.clear()
    return image, metadata


def yolo_rows(record):
    w, h = record["width"], record["height"]
    for c in record["components"]:
        x0, y0, x1, y1 = c["bbox_xyxy_px"]
        yield f"{c['class_id']} {(x0+x1)/(2*w):.9f} {(y0+y1)/(2*h):.9f} {(x1-x0)/w:.9f} {(y1-y0)/h:.9f}"


def annotate(image, record):
    image = image.copy()
    pen = ImageDraw.Draw(image)
    font = ImageFont.truetype(str(Path(matplotlib.get_data_path())/"fonts/ttf/DejaVuSans.ttf"), 13)
    for c in record["components"]:
        color = PALETTE[c["class_id"]]
        pen.rectangle(c["bbox_xyxy_px"], outline=color, width=2)
        x, y = c["bbox_xyxy_px"][:2]
        pen.text((x, max(0, y-17)), c["id"]+":"+c["class"], fill=color, font=font, stroke_width=1, stroke_fill="white")
        for name, p in c["terminals"].items():
            px, py = p
            pen.ellipse((px-3, py-3, px+3, py+3), fill="#ff9900", outline="black")
            pen.text((px+4, py+3), name, fill="black", font=font)
        for t in c["text"]:
            pen.rectangle(t["bbox_xyxy_px"], outline="#999999", width=1)
    return image


def contact_sheet(root, records, target, columns=5, thumb=(300, 240)):
    rows = math.ceil(len(records)/columns)
    sheet = Image.new("RGB", (columns*thumb[0], rows*(thumb[1]+28)), "#e9e9e9")
    pen = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(str(Path(matplotlib.get_data_path())/"fonts/ttf/DejaVuSans.ttf"), 12)
    for i, r in enumerate(records):
        with Image.open(root/r["image_filename"]) as source:
            small = source.convert("RGB")
            small.thumbnail(thumb)
        x, y = i % columns*thumb[0], i//columns*(thumb[1]+28)
        sheet.paste(small, (x+(thumb[0]-small.width)//2, y+(thumb[1]-small.height)//2))
        pen.text((x+5, y+thumb[1]+3), f"{Path(r['image_filename']).stem} · {r['topology']}", fill="black", font=font)
    target.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(target)


def overview_records(records):
    """Six samples per topology, interleaved to avoid periodic sampling alias."""
    groups = [[r for r in records if r["topology"] == topology] for topology in TOPOLOGIES]
    groups = [[group[i] for i in np.linspace(0, len(group)-1, min(len(group), 6), dtype=int)]
              if group else [] for group in groups]
    return [group[row] for row in range(6) for group in groups if row < len(group)]


def valid_point(p, w, h):
    return (isinstance(p, (list, tuple)) and len(p) == 2
            and all(isinstance(v, (int, float)) and math.isfinite(v) for v in p)
            and 0 <= p[0] < w and 0 <= p[1] < h)


def valid_box(b, w, h):
    return (isinstance(b, (list, tuple)) and len(b) == 4
            and all(isinstance(v, (int, float)) and math.isfinite(v) for v in b)
            and 0 <= b[0] < b[2] <= w and 0 <= b[1] < b[3] <= h)


def validate_dataset(root: Path, expected_count=None):
    """Independent read-back of PNG, YOLO, JSONL, graph and raster evidence.

    Returns a JSON-serializable report; CLI exits nonzero on any detected error.
    Invalid records are reported rather than silently clipped or repaired.
    """
    root = Path(root)
    errors, records = [], []
    def error(kind, image, detail):
        errors.append(dict(kind=kind, image=image, detail=str(detail)))
    marker = json.loads((root/MARKER).read_text(encoding="utf-8"))
    expected_count = expected_count if expected_count is not None else marker["count"]
    for split in ("train", "val"):
        path = root/"metadata"/f"{split}.jsonl"
        if not path.exists():
            error("missing_metadata", split, path)
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            try:
                record = json.loads(line)
                if not isinstance(record, dict):
                    raise ValueError("A metadata row must be a JSON object")
                if not isinstance(record.get("image_filename"), str) or not isinstance(record.get("label_filename"), str):
                    raise ValueError("Missing image or label filename")
                if record.get("split") != split:
                    error("split", str(path), lineno)
                records.append(record)
            except (ValueError, TypeError) as exc:
                error("metadata_json", str(path), f"line {lineno}: {exc}")
    images = {p.relative_to(root).as_posix(): p for split in ("train", "val") for p in (root/"images"/split).glob("*") if p.is_file()}
    labels = {p.relative_to(root).as_posix(): p for split in ("train", "val") for p in (root/"labels"/split).glob("*") if p.is_file()}
    expected_images = {r.get("image_filename") for r in records}
    expected_labels = {r.get("label_filename") for r in records}
    if len(images) != expected_count or len(records) != expected_count:
        error("count", "dataset", f"images={len(images)}, metadata={len(records)}, expected={expected_count}")
    if set(images) != expected_images:
        error("missing_metadata", "dataset", sorted(set(images)^expected_images, key=str))
    if set(labels) != expected_labels:
        error("image_label_pairs", "dataset", sorted(set(labels)^expected_labels, key=str))
    if len(expected_images) != len(records) or len(expected_labels) != len(records):
        error("duplicate_metadata", "dataset", "Repeated image or label record")
    split_counts = Counter(r.get("split") for r in records)
    train_count = round(expected_count*.8)
    if split_counts != Counter(train=train_count, val=expected_count-train_count):
        error("split_count", "dataset", split_counts)
    classes, styles, topologies, resolutions, object_counts, label_modes = (Counter() for _ in range(6))
    split_classes = defaultdict(Counter)
    file_hashes, pixel_hashes = defaultdict(list), defaultdict(list)
    for r in records:
        name = r.get("image_filename", "<missing>")
        try:
            if type(r["generation_seed"]) is not int or r["topology"] not in TOPOLOGIES:
                error("metadata_schema", name, "Invalid generation seed or topology")
            matrix = np.asarray(r["drawing_to_final_px"], dtype=float)
            if matrix.shape != (3, 3) or not np.isfinite(matrix).all() or abs(np.linalg.det(matrix)) < 1e-12:
                error("metadata_schema", name, "Invalid render affine")
            if Path(name).name != Path(r["label_filename"]).with_suffix(".png").name:
                error("image_label_pairs", name, "Different image and label stems")
            w, h = r["width"], r["height"]
            image_path, label_path = root/name, root/r["label_filename"]
            try:
                with Image.open(image_path) as decoded:
                    decoded.load()
                    if decoded.size != (w, h) or decoded.format != "PNG":
                        error("dimensions", name, decoded.size)
                    rgb = decoded.convert("RGB")
                    gray = np.asarray(rgb.convert("L"))
                    pixel_hashes[hashlib.sha256(rgb.tobytes()).hexdigest()].append(name)
                digest = hashlib.sha256(image_path.read_bytes()).hexdigest()
                file_hashes[digest].append(name)
                if r.get("image_sha256") != digest:
                    error("image_hash", name, "PNG no longer matches its metadata")
            except (OSError, ValueError) as exc:
                error("image_decode", name, exc)
                continue
            lines = label_path.read_text(encoding="utf-8").splitlines() if label_path.exists() else []
            comps = r["components"]
            if not lines:
                error("empty_annotations", name, "No YOLO labels")
            if len(lines) != len(comps):
                error("object_count", name, f"YOLO={len(lines)}, metadata={len(comps)}")
            if not 2 <= len(comps) <= 8:
                error("object_count", name, len(comps))
            if not {"resistor", "voltage_source"} <= {c["class"] for c in comps}:
                error("required_components", name, "Missing resistor or voltage source")
            if len({c["id"] for c in comps}) != len(comps):
                error("component_ids", name, "Repeated component ID")
            nodes = {n["id"]: n for n in r["nodes"]}
            for n in nodes.values():
                if not n["positions_px"] or not all(valid_point(p, w, h) for p in n["positions_px"]):
                    error("node_coordinates", name, n["id"])
            for wire in r["wires"]:
                if wire["node_id"] not in nodes or len(wire["points_px"]) != 2 or not all(valid_point(p, w, h) for p in wire["points_px"]):
                    error("wire_coordinates", name, wire)
            # Independently reconstruct each conductor from its raster-space
            # endpoints. A shared node ID alone cannot join disconnected leads.
            for nid, node in nodes.items():
                adjacency = defaultdict(set)
                for wire in r["wires"]:
                    if wire["node_id"] == nid:
                        a, b = map(point_key, wire["points_px"])
                        adjacency[a].add(b)
                        adjacency[b].add(a)
                required = {point_key(p) for p in node["positions_px"]}
                required.update(point_key(p) for c in comps for t, p in c["terminals"].items() if c["nodes"][t] == nid)
                if required:
                    visited, pending = set(), [next(iter(required))]
                    while pending:
                        current = pending.pop()
                        if current not in visited:
                            visited.add(current)
                            pending.extend(adjacency[current]-visited)
                    if not required <= visited or set(adjacency)-visited:
                        error("conductor_connectivity", name, nid)
            if r["coordinate_space"] != "source_px" or r["schema_version"] != SCHEMA_VERSION:
                error("metadata_schema", name, "Unsupported coordinate space/version")
            expected_connections = {(c["id"], t, nid) for c in comps for t, nid in c["nodes"].items()}
            actual_connections = {(c["component_id"], c["terminal"], c["node_id"]) for c in r["connections"]}
            if expected_connections != actual_connections or len(r["connections"]) != 2*len(comps):
                error("connections", name, "Missing, extra or duplicated terminal-node connection")
            for i, c in enumerate(comps):
                cid, box = c["class_id"], c["bbox_xyxy_px"]
                if type(cid) is not int or cid not in range(4) or CLASSES[cid] != c["class"]:
                    error("component_class", name, c["id"])
                if not c["designator"] or c["parameter_provenance"] != "synthetic_ground_truth":
                    error("metadata_schema", name, c["id"])
                unit = {"resistor": "ohm", "voltage_source": "V", "capacitor": "F", "switch": None}.get(c["class"])
                if c["unit"] != unit or (c["class"] != "switch" and
                        (not isinstance(c["value"], (int, float)) or not math.isfinite(c["value"]) or c["value"] <= 0)):
                    error("physical_value", name, c["id"])
                if c["class"] == "switch" and (c["value"] is not None or c["state"] not in {"open", "closed"}):
                    error("physical_value", name, c["id"])
                classes[c["class"]] += 1
                split_classes[r["split"]][c["class"]] += 1
                styles[c["symbol_style"]] += 1
                if not valid_box(box, w, h):
                    error("pixel_bbox", name, c["id"])
                    continue
                x0, y0, x1, y1 = box
                crop = gray[math.floor(y0):math.ceil(y1), math.floor(x0):math.ceil(x1)]
                if not crop.size or np.count_nonzero(crop < 150) < 3:
                    error("component_visibility", name, c["id"])
                if set(c["terminals"]) != {"a", "b"} or set(c["nodes"]) != {"a", "b"}:
                    error("terminals", name, c["id"])
                for t, p in c["terminals"].items():
                    if not valid_point(p, w, h) or c["nodes"][t] not in nodes:
                        error("terminal_coordinates", name, c["id"]+t)
                        continue
                    attached = any(wire["node_id"] == c["nodes"][t] and any(np.linalg.norm(np.subtract(p, q)) < 1e-3 for q in wire["points_px"]) for wire in r["wires"])
                    if not attached:
                        error("terminal_attachment", name, c["id"]+t)
                    radius = math.ceil(r["appearance"]["line_width_px"]+1)
                    x, y = map(round, p)
                    patch = gray[max(0, y-radius):min(h, y+radius+1), max(0, x-radius):min(w, x+radius+1)]
                    if not patch.size or patch.min() > 150:
                        error("terminal_visibility", name, c["id"]+t)
                for t in c["text"]:
                    if not valid_point(t["position_px"], w, h) or not valid_box(t["bbox_xyxy_px"], w, h) or not t["content"]:
                        error("text_coordinates", name, c["id"])
                    if any(overlap(t["bbox_xyxy_px"], other["bbox_xyxy_px"]) for other in comps):
                        error("text_symbol_overlap", name, c["id"])
                if i < len(lines):
                    try:
                        values = lines[i].split()
                        if len(values) != 5 or int(values[0]) != cid:
                            raise ValueError("Class or field count mismatch")
                        cx, cy, bw, bh = map(float, values[1:])
                        if not all(math.isfinite(v) and 0 <= v <= 1 for v in (cx, cy, bw, bh)) or bw <= 0 or bh <= 0:
                            raise ValueError("Nonfinite, out-of-range or nonpositive YOLO values")
                        restored = [(cx-bw/2)*w, (cy-bh/2)*h, (cx+bw/2)*w, (cy+bh/2)*h]
                        if not valid_box(restored, w+1e-5, h+1e-5) or not np.allclose(restored, box, atol=2e-5, rtol=0):
                            raise ValueError("YOLO box differs from final pixel box")
                    except (ValueError, OverflowError) as exc:
                        error("yolo_annotation", name, f"line {i+1}: {exc}")
            object_counts[str(len(comps))] += 1
            topologies[r["topology"]] += 1
            resolutions[f"{w}x{h}"] += 1
            label_modes[r["label_mode"]] += 1
        except (KeyError, TypeError, ValueError, IndexError, OSError) as exc:
            error("metadata_record", name, exc)
    duplicates = [names for names in pixel_hashes.values() if len(names) > 1]
    if duplicates:
        error("duplicate_images", "dataset", duplicates)
    if expected_count >= 600:
        for kind in CLASSES:
            if classes[kind] < 300:
                error("class_balance", "dataset", f"{kind}: {classes[kind]} < 300")
    return dict(schema_version=SCHEMA_VERSION, total_images=len(images),
                train_images=split_counts["train"], val_images=split_counts["val"],
                total_objects=sum(classes.values()), class_counts=dict(classes),
                split_class_counts={s: dict(c) for s, c in split_classes.items()},
                topology_distribution=dict(topologies), symbol_style_distribution=dict(styles),
                resolution_distribution=dict(resolutions), components_per_image=dict(object_counts),
                label_mode_distribution=dict(label_modes),
                duplicate_count=sum(len(d)-1 for d in duplicates), duplicate_groups=duplicates,
                duplicate_file_count=sum(len(d)-1 for d in file_hashes.values() if len(d) > 1),
                invalid_annotation_count=len(errors), validation_passed=not errors,
                bounding_box_validation_passed=not any(e["kind"] in {"pixel_bbox", "yolo_annotation", "component_visibility", "text_symbol_overlap", "object_count", "empty_annotations", "metadata_record"} for e in errors),
                terminal_validation_passed=not any(e["kind"].startswith("terminal") or e["kind"] in {"connections", "wire_coordinates", "node_coordinates", "conductor_connectivity", "metadata_record"} for e in errors),
                seed=marker["seed"], generator_version=SCHEMA_VERSION,
                environment=marker["environment"], errors=errors,
                limitations=["All images and validation examples are synthetic; no claim of accuracy on real textbooks.",
                             "Four target classes only; no handwritten, page-layout, or real-photo coverage.",
                             "No detector was trained or production recognition pipeline modified."])


def dataset_readme(count, seed):
    return f"""# Synthetic printed circuit dataset v1

{count} synthetic PNG diagrams generated with Schemdraw; seed **{seed}**.
80% train / 20% validation. Classes: 0 resistor, 1 voltage_source,
2 capacitor, 3 switch. Every diagram has 2–8 target components,
at least one resistor and at least one voltage source.

Regenerate from the repository root:

```powershell
python -m pip install -r scripts/requirements-circuit-dataset.txt
python scripts/generate_circuit_dataset.py --count {count} --seed {seed} --output datasets/circuits_v1/synthetic_v1 --preview
python scripts/generate_circuit_dataset.py --output datasets/circuits_v1/synthetic_v1 --validate
```

Existing outputs are refused. `--overwrite` only replaces directories bearing
this generator's marker, and is restricted to descendants of the current directory.

## Annotation contract

YOLO labels contain symbol bodies only: ANSI/IEC resistor, cell/battery/DC
source, capacitor plates (flat/curved), switch blade and contact rings.
Wires and external printed text, including capacitor polarity marks, have
separate metadata and are excluded from target boxes. Intrinsic DC-source
signs inside its circle are part of that symbol.

Coordinates are continuous native `source_px`: origin top left, x right,
y down. Boxes use `[x_min,y_min,x_max,y_max]` with exclusive geometric
upper bounds; terminals/text positions are `[x,y]`. Values are canonical
ohm, V, F; switches have null numeric value/unit and an explicit state.
Values remain known in metadata even when omitted from the printed image;
`label_mode` and each component's `text` record what is actually visible.
Values have `synthetic_ground_truth` provenance and are never runtime evidence.

Each JSONL row records its image/label paths, dimensions, seed, PNG SHA-256,
topology, render affine, appearance, components, separate text boxes,
electrical nodes, explicit wire paths, junctions and terminal-node connections.
Terminal a/b are the native symbol-body attachment anchors; extended wire
leads are separate paths. Node membership is derived only from explicit wires.
Open switches have distinct nodes and an open blade; no wire spans the gap.
Polarized capacitors record their positive terminal; voltage sources record
positive terminal and battery cell count.

The body artist extents come from Schemdraw's native segments, excluding
automatic lead extensions, plus their measured physical stroke width.
The exact Matplotlib display-to-PNG affine maps body geometry, wires,
terminals, nodes and text. Minor scan rotation is rendered through this same
affine. Blur, scan noise and a JPEG encode/decode round trip are photometric
only. The final output is always PNG; no resizing or cropping follows labels.

`previews/annotated_samples/` shows colored boxes, orange terminal points
(a/b) and gray external text boxes. `contact_sheet.png` samples the dataset;
`previews/contact_sheets/` covers every image in pages of 60.
See `dataset_report.json` for actual counts, hashes and read-back validation.

All validation examples are synthetic and share the generator's style family.
Synthetic validation is not evidence of real-textbook recognition accuracy.
Collect a separate, held-out real printed textbook evaluation set before
assessing a trained detector. No YOLO model is trained here.
"""


def prepare_output(output: Path, overwrite=False):
    if output.is_symlink():
        raise ValueError("Refusing a symlink as the output directory")
    output = output.resolve()
    if output.exists():
        if not overwrite:
            raise ValueError(f"Output already exists: {output}. Choose a new output or explicitly use --overwrite.")
        # Never delete a computed path without checking its resolved boundary.
        workspace = Path.cwd().resolve()
        if not output.is_relative_to(workspace) or output == workspace or output.is_symlink():
            raise ValueError("Overwrite is restricted to real subdirectories of the current working directory")
        marker = output/MARKER
        if not marker.is_file() or json.loads(marker.read_text(encoding="utf-8")).get("generator_version") != SCHEMA_VERSION:
            raise ValueError("Refusing to overwrite a directory not created by this generator")
        shutil.rmtree(output)
    for group in ("images", "labels"):
        for split in ("train", "val"):
            (output/group/split).mkdir(parents=True, exist_ok=True)
    (output/"metadata").mkdir()
    (output/"previews"/"annotated_samples").mkdir(parents=True)
    return output


def generate_dataset(count, seed, output, *, preview=False, overwrite=False):
    if count < 1:
        raise ValueError("--count must be positive")
    if schemdraw.__version__ != "0.23":
        raise ValueError("This geometry adapter is verified for Schemdraw 0.23; install scripts/requirements-circuit-dataset.txt")
    output = prepare_output(Path(output), overwrite)
    env = dict(python=platform.python_version(), schemdraw=schemdraw.__version__,
               matplotlib=matplotlib.__version__, pillow=PIL.__version__, numpy=np.__version__)
    marker = dict(generator_version=SCHEMA_VERSION, seed=seed, count=count, environment=env)
    (output/MARKER).write_text(json.dumps(marker, indent=2)+"\n", encoding="utf-8")
    # Stratified by topology; samples have independent seeds and are generated
    # once (no shared source image is augmented across the split).
    by_topology = defaultdict(list)
    for index in range(count):
        by_topology[index % len(TOPOLOGIES)].append(index)
    val_indices = set()
    splitter = random.Random(seed ^ 0x51A17)
    for group in by_topology.values():
        splitter.shuffle(group)
        val_indices.update(group[:len(group)//5])
    desired_val = count-round(count*.8)
    remaining = sorted(set(range(count))-val_indices)
    splitter.shuffle(remaining)
    val_indices.update(remaining[:desired_val-len(val_indices)])
    records, rejected_layouts = [], []
    handles = {s: (output/"metadata"/f"{s}.jsonl").open("w", encoding="utf-8", newline="\n") for s in ("train", "val")}
    try:
        for index in range(count):
            split = "val" if index in val_indices else "train"
            sample_seed = seed+index*1_000_003
            # Reject unreadable placements deterministically, retaining topology
            # and recording the actual accepted seed and rejected attempt count.
            for attempt in range(80):
                try:
                    image, record = render_sample(index, sample_seed+attempt*97_409)
                    break
                except ValueError as exc:
                    rejected_layouts.append(dict(index=index, attempt=attempt, reason=str(exc)))
            else:
                raise ValueError(f"Unable to render image {index}: {rejected_layouts[-1]}")
            stem = f"circuit_{index+1:06d}"
            record.update(image_filename=f"images/{split}/{stem}.png", label_filename=f"labels/{split}/{stem}.txt",
                          split=split, sample_index=index, rejected_attempts=attempt)
            image_path = output/record["image_filename"]
            image.save(image_path, format="PNG")
            record["image_sha256"] = hashlib.sha256(image_path.read_bytes()).hexdigest()
            (output/record["label_filename"]).write_text("\n".join(yolo_rows(record))+"\n", encoding="utf-8")
            handles[split].write(json.dumps(record, ensure_ascii=False, allow_nan=False)+"\n")
            records.append(record)
            if index < (24 if preview else 12):
                annotate(image, record).save(output/"previews"/"annotated_samples"/f"{stem}.png")
            if (index+1) % 25 == 0 or index+1 == count:
                print(f"Generated {index+1}/{count}", flush=True)
    finally:
        for handle in handles.values():
            handle.close()
    selected = overview_records(records)
    contact_sheet(output, selected, output/"previews"/"contact_sheet.png")
    for offset in range(0, count, 60):
        contact_sheet(output, records[offset:offset+60], output/"previews"/"contact_sheets"/f"all_{offset//60+1:02d}.png")
    annotated_records = [dict(r, image_filename=f"previews/annotated_samples/{Path(r['image_filename']).name}")
                         for r in records[:24 if preview else 12]]
    contact_sheet(output, annotated_records, output/"previews"/"annotated_contact_sheet.png", columns=3, thumb=(480, 360))
    (output/"data.yaml").write_text(
        f"path: {json.dumps(output.as_posix())}\ntrain: images/train\nval: images/val\nnames:\n"+
        "".join(f"  {i}: {kind}\n" for i, kind in enumerate(CLASSES)), encoding="utf-8")
    (output/"README.md").write_text(dataset_readme(count, seed), encoding="utf-8")
    report = validate_dataset(output, count)
    report["rejected_layout_attempts"] = len(rejected_layouts)
    report["rejection_reasons"] = dict(Counter(r["reason"] for r in rejected_layouts))
    (output/"dataset_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=600)
    parser.add_argument("--seed", type=int, default=20261030)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--preview", action="store_true", help="Save 24 annotated previews (default 12)")
    parser.add_argument("--validate", action="store_true", help="Read-only validation of an existing dataset; do not generate")
    parser.add_argument("--overwrite", action="store_true", help="Explicitly replace a marked generated dataset inside the current directory")
    args = parser.parse_args(argv)
    try:
        report = validate_dataset(args.output) if args.validate else generate_dataset(args.count, args.seed, args.output, preview=args.preview, overwrite=args.overwrite)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"Dataset error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["validation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
