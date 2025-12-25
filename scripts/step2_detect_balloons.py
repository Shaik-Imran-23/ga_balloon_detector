import ezdxf
import json
import re
from pathlib import Path
from math import hypot

BASE_DIR = Path(__file__).resolve().parent.parent
DXF_PATH = BASE_DIR / "data" / "DD801582-1-00.dxf"
OUTPUT_JSON = BASE_DIR / "output" / "balloons.json"

doc = ezdxf.readfile(DXF_PATH)
msp = doc.modelspace()

def clean_text(t):
    if ";" in t:
        t = t.split(";")[-1]
    t = re.sub(r"\\[A-Za-z0-9\.]+", "", t)
    t = t.replace("{", "").replace("}", "")
    return t.strip()

def is_numeric(txt):
    return txt.isdigit()

balloons = []
used_centers = []

# -------------------------------------------------
# 1️⃣ BLOCK-BASED BALLOON DETECTION (PRIMARY)
# -------------------------------------------------
for ins in msp.query("INSERT"):
    block_name = ins.dxf.name
    if block_name not in doc.blocks:
        continue

    block = doc.blocks.get(block_name)

    has_circle = False
    number = None

    for e in block:
        if e.dxftype() == "CIRCLE":
            has_circle = True
        elif e.dxftype() in ("TEXT", "MTEXT"):
            txt = clean_text(e.text if e.dxftype() == "MTEXT" else e.dxf.text)
            if is_numeric(txt):
                number = txt

    if has_circle and number:
        cx, cy = ins.dxf.insert.x, ins.dxf.insert.y
        balloons.append({
            "balloon_no": number,
            "center": [round(cx, 2), round(cy, 2)],
            "source": "BLOCK"
        })
        used_centers.append((cx, cy))

# -------------------------------------------------
# 2️⃣ EXPLODED GEOMETRY BALLOONS (FALLBACK)
# -------------------------------------------------
numeric_texts = []

for t in msp.query("TEXT"):
    txt = clean_text(t.dxf.text)
    if is_numeric(txt):
        ip = t.dxf.insert
        numeric_texts.append((txt, ip.x, ip.y))

for t in msp.query("MTEXT"):
    txt = clean_text(t.text)
    if is_numeric(txt):
        ip = t.dxf.insert
        numeric_texts.append((txt, ip.x, ip.y))

for c in msp.query("CIRCLE"):
    cx, cy = c.dxf.center.x, c.dxf.center.y
    r = c.dxf.radius

    # Skip circles near already-detected block balloons
    if any(hypot(cx - ux, cy - uy) < 40 for ux, uy in used_centers):
        continue

    for txt, tx, ty in numeric_texts:
        if hypot(cx - tx, cy - ty) <= r:
            balloons.append({
                "balloon_no": txt,
                "center": [round(cx, 2), round(cy, 2)],
                "radius": round(r, 2),
                "source": "GEOMETRY"
            })
            break

with open(OUTPUT_JSON, "w") as f:
    json.dump(balloons, f, indent=2)

print(f"Detected {len(balloons)} balloons (block + geometry)")

