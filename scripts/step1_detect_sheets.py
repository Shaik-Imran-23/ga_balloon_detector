import ezdxf
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DXF_PATH = BASE_DIR / "data" / "DD801582-1-00.dxf"
OUTPUT_JSON = BASE_DIR / "output" / "sheets.json"

doc = ezdxf.readfile(DXF_PATH)
msp = doc.modelspace()

def clean_text(t):
    if ";" in t:
        t = t.split(";")[-1]
    t = re.sub(r"\\[A-Za-z0-9\.]+", "", t)
    t = t.replace("{", "").replace("}", "")
    return t.strip().upper()

anchors = []

# Detect GA DRAWING title blocks
for t in msp.query("MTEXT"):
    txt = clean_text(t.text)
    if "GA DRAWING" in txt:
        ip = t.dxf.insert
        anchors.append((ip.x, ip.y))

if not anchors:
    raise RuntimeError("No GA DRAWING anchors found")

# Sort top-to-bottom (AutoCAD Y increases upward)
anchors.sort(key=lambda p: -p[1])

SHEET_WIDTH = 5000    # tuned for your drawing
SHEET_HEIGHT = 3500

sheets = []
for idx, (x, y) in enumerate(anchors, start=1):
    bbox = [
        x - SHEET_WIDTH / 2,
        y - SHEET_HEIGHT,
        x + SHEET_WIDTH / 2,
        y + 500
    ]
    sheets.append({
        "sheet_index": idx,
        "anchor": [x, y],
        "bbox": bbox
    })

with open(OUTPUT_JSON, "w") as f:
    json.dump(sheets, f, indent=2)

print(f"Detected {len(sheets)} GA sheets (text-based)")

