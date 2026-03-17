import json
from pathlib import Path



# ==============================
# 1. rutas
# ==============================

base_path = Path(__file__).resolve().parent.parent

input_file = base_path / "data" / "raw_data" / "colombia.geo.json"

with open(input_file) as f:
    geo = json.load(f)

print(len(geo["features"]))