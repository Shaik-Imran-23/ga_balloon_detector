import ezdxf
import json
import math
import re

DXF_PATH = "data/DD801582-1-00.dxf"
OUTPUT_JSON = "output/sheet_anchors.json"

doc = ezdxf.readfile(DXF_PATH)
msp = doc.modelspace()

def extract_mtext_number(text):
    text = re.sub(r"[{}]", "", text)
    text = re.sub(r"\\[A-Za-z0-9]+;", "", text)
    m = re.search(r"\d+", text)
    return int(m.group()) if m else None

# -----------------------------
# Collect MTEXT entities
# -----------------------------
ga_texts = []
sheet_numbers = []

for e in msp.query("MTEXT"):
    txt = e.plain_text().upper().strip()
    pos = (e.dxf.insert.x, e.dxf.insert.y)

    if "GA DRAWING" in txt:
        ga_texts.append({
            "pos": pos
        })

    num = extract_mtext_number(txt)
    if num is not None:
        sheet_numbers.append({
            "sheet_index": num,
            "pos": pos
        })

# -----------------------------
# Pair GA DRAWING with nearest number
# -----------------------------
sheets = []

for ga in ga_texts:
    gx, gy = ga["pos"]

    nearest = None
    min_dist = float("inf")

    for sn in sheet_numbers:
        sx, sy = sn["pos"]
        d = math.hypot(sx - gx, sy - gy)

        if d < min_dist:
            min_dist = d
            nearest = sn

    if nearest:
        sheets.append({
            "sheet_index": nearest["sheet_index"],
            "ga_anchor": list(ga["pos"]),
            "number_anchor": list(nearest["pos"])
        })

sheets.sort(key=lambda x: x["sheet_index"])

with open(OUTPUT_JSON, "w") as f:
    json.dump(sheets, f, indent=2)

print(f"Detected {len(sheets)} GA sheets using GA DRAWING + MTEXT number")

