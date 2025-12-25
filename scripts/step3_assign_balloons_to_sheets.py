import ezdxf
import json
import re
from pathlib import Path
from shapely.geometry import Point, box

# ---------------- CONFIG ----------------
DXF_PATH = "data/DD801582-1-00.dxf"
BALLOONS_JSON = "output/balloons.json"
OUTPUT_JSON = "output/balloons_with_sheet.json"

SECTION_PADDING = 4000   # drawing units – safe margin

# ----------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DXF_PATH = BASE_DIR / DXF_PATH
BALLOONS_JSON = BASE_DIR / BALLOONS_JSON
OUTPUT_JSON = BASE_DIR / OUTPUT_JSON

doc = ezdxf.readfile(DXF_PATH)
msp = doc.modelspace()

# ---------------- STEP 1: Detect SECTION / VIEW labels ----------------
sections = []

SECTION_PATTERNS = [
    (r"SECTION\s*A", 3),
    (r"SECTION\s*B", 4),
    (r"SECTION\s*C", 5),
    (r"FRONT VIEW WITHOUT DOOR", 2),
    (r"REAR", 2),
    (r"TOP VIEW|FRONT VIEW|LHS VIEW|RHS VIEW|BOTTOM VIEW", 1),
]

for e in msp.query("MTEXT"):
    text = e.text.replace("\\P", " ").upper()
    insert = e.dxf.insert

    for pattern, sheet_no in SECTION_PATTERNS:
        if re.search(pattern, text):
            x, y = insert.x, insert.y
            region = box(
                x - SECTION_PADDING,
                y - SECTION_PADDING,
                x + SECTION_PADDING,
                y + SECTION_PADDING,
            )
            sections.append({
                "sheet": sheet_no,
                "region": region,
                "label": text.strip()
            })

# ---------------- STEP 2: Load balloons ----------------
with open(BALLOONS_JSON) as f:
    balloons = json.load(f)

# ---------------- STEP 3: Assign balloons to sections ----------------
unassigned = []

for b in balloons:
    pt = Point(b["center"][0], b["center"][1])
    assigned = False

    for sec in sections:
        if sec["region"].contains(pt):
            b["sheet_index"] = sec["sheet"]
            assigned = True
            break

    if not assigned:
        b["sheet_index"] = 1   # fallback = overview sheet
        unassigned.append(b)

# ---------------- STEP 4: Save result ----------------
OUTPUT_JSON.parent.mkdir(exist_ok=True)

with open(OUTPUT_JSON, "w") as f:
    json.dump(balloons, f, indent=2)

print("✅ Balloon → sheet assignment completed")
print(f"⚠️ Unassigned (fallback to sheet 1): {len(unassigned)}")

