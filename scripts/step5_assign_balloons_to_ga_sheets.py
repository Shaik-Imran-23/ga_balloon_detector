import json
import math

BALLOONS_JSON = "output/balloons.json"
SHEETS_JSON = "output/sheet_anchors.json"
OUTPUT_JSON = "output/balloons_with_final_sheet.json"

# -----------------------------
# Load data
# -----------------------------
with open(BALLOONS_JSON) as f:
    balloons = json.load(f)

with open(SHEETS_JSON) as f:
    sheets = json.load(f)

# -----------------------------
# Assign nearest GA sheet
# -----------------------------
for b in balloons:
    bx, by = b["center"]

    nearest_sheet = None
    min_dist = float("inf")

    for s in sheets:
        sx, sy = s["ga_anchor"]
        d = math.hypot(bx - sx, by - sy)

        if d < min_dist:
            min_dist = d
            nearest_sheet = s["sheet_index"]

    b["sheet_index"] = nearest_sheet

# -----------------------------
# Save output
# -----------------------------
with open(OUTPUT_JSON, "w") as f:
    json.dump(balloons, f, indent=2)

print(f"Assigned {len(balloons)} balloons to {len(sheets)} GA sheets")

