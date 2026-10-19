#!/usr/bin/env python3
"""
Stage 1: Reproducible Data Integration & Validation Pipeline for EV Infra Map India.
Reads original collected datasets from `data/raw/` (preserving them unchanged) and outputs
cleaned, schema-validated, application-ready JSON/GeoJSON/CSV datasets to `data/processed/`
and `public/data/`.

Strict Data Integrity Rules Enforced:
1. BEE (26 Oct 2025), MoPNG OMC (01 Mar 2026), MHI FAME-II (01 Mar 2026),
   Switch Delhi (19 Oct 2026), and OpenStreetMap (19 Oct 2026) counts are kept strictly separate.
2. Station vs. charger row vs. connector units are explicitly resolved and documented.
3. Invalid/out-of-bbox coordinates (e.g., 104 IOCL Lat==Lon rows in BEE) are flagged and
   excluded from spatial rendering while retained in state tabular totals.
4. Spatial Point-in-Polygon containment (`shapely`) is used to assign geocoded stations
   to canonical State (`Admin2.shp`) and District (`2011_Dist.shp`) polygons.
"""

from __future__ import annotations

import csv
import html
import json
import math
import os
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import openpyxl
from PIL import Image
import shapefile
from shapely.geometry import MultiPolygon, Point, Polygon, box, mapping, shape
from shapely.prepared import prep

ROOT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT_DIR / "data" / "raw"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
PUBLIC_DATA_DIR = ROOT_DIR / "public" / "data"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
PUBLIC_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Canonical 36 States & UTs mapping (VAHAN state_code -> canonical name & Admin2 ST_NM)
CANONICAL_STATES: Dict[str, Dict[str, str]] = {
    "AN": {"name": "Andaman & Nicobar Islands", "admin2": "Andaman & Nicobar"},
    "AP": {"name": "Andhra Pradesh", "admin2": "Andhra Pradesh"},
    "AR": {"name": "Arunachal Pradesh", "admin2": "Arunachal Pradesh"},
    "AS": {"name": "Assam", "admin2": "Assam"},
    "BR": {"name": "Bihar", "admin2": "Bihar"},
    "CH": {"name": "Chandigarh", "admin2": "Chandigarh"},
    "CG": {"name": "Chhattisgarh", "admin2": "Chhattisgarh"},
    "DD": {
        "name": "Dadra & Nagar Haveli and Daman & Diu",
        "admin2": "Dadra and Nagar Haveli and Daman and Diu",
    },
    "DL": {"name": "NCT of Delhi", "admin2": "Delhi"},
    "GA": {"name": "Goa", "admin2": "Goa"},
    "GJ": {"name": "Gujarat", "admin2": "Gujarat"},
    "HR": {"name": "Haryana", "admin2": "Haryana"},
    "HP": {"name": "Himachal Pradesh", "admin2": "Himachal Pradesh"},
    "JK": {"name": "Jammu & Kashmir", "admin2": "Jammu & Kashmir"},
    "JH": {"name": "Jharkhand", "admin2": "Jharkhand"},
    "KA": {"name": "Karnataka", "admin2": "Karnataka"},
    "KL": {"name": "Kerala", "admin2": "Kerala"},
    "LA": {"name": "Ladakh", "admin2": "Ladakh"},
    "LD": {"name": "Lakshadweep", "admin2": "Lakshadweep"},
    "MP": {"name": "Madhya Pradesh", "admin2": "Madhya Pradesh"},
    "MH": {"name": "Maharashtra", "admin2": "Maharashtra"},
    "MN": {"name": "Manipur", "admin2": "Manipur"},
    "ML": {"name": "Meghalaya", "admin2": "Meghalaya"},
    "MZ": {"name": "Mizoram", "admin2": "Mizoram"},
    "NL": {"name": "Nagaland", "admin2": "Nagaland"},
    "OR": {"name": "Odisha", "admin2": "Odisha"},
    "PY": {"name": "Puducherry", "admin2": "Puducherry"},
    "PB": {"name": "Punjab", "admin2": "Punjab"},
    "RJ": {"name": "Rajasthan", "admin2": "Rajasthan"},
    "SK": {"name": "Sikkim", "admin2": "Sikkim"},
    "TN": {"name": "Tamil Nadu", "admin2": "Tamil Nadu"},
    "TG": {"name": "Telangana", "admin2": "Telangana"},
    "TR": {"name": "Tripura", "admin2": "Tripura"},
    "UP": {"name": "Uttar Pradesh", "admin2": "Uttar Pradesh"},
    "UK": {"name": "Uttarakhand", "admin2": "Uttarakhand"},
    "WB": {"name": "West Bengal", "admin2": "West Bengal"},
}

ADMIN2_TO_CODE = {v["admin2"]: k for k, v in CANONICAL_STATES.items()}


def normalize_state_to_code(raw_state: str) -> Optional[str]:
    """Deterministically resolves all 46 BEE state strings, PIB strings, and NITI strings to 36 canonical codes."""
    if not raw_state:
        return None
    s = html.unescape(raw_state).strip().lower()
    s = re.sub(r"\s+", " ", s)
    mapping_dict = {
        "andaman & nicobar": "AN",
        "andaman and nicobar islands": "AN",
        "andaman & nicobar island": "AN",
        "andaman & nicobar islands": "AN",
        "andhra pradesh": "AP",
        "arunachal pradesh": "AR",
        "assam": "AS",
        "bihar": "BR",
        "chandigarh": "CH",
        "chhattisgarh": "CG",
        "chattisgarh": "CG",
        "dadra and nagar haveli and daman and diu": "DD",
        "dadra & nagar haveli & daman & diu": "DD",
        "daman and diu": "DD",
        "ut of dnh and dd": "DD",
        "ut of d&nh and d&d": "DD",
        "delhi": "DL",
        "nct of delhi": "DL",
        "new delhi": "DL",
        "goa": "GA",
        "gujarat": "GJ",
        "haryana": "HR",
        "himachal pradesh": "HP",
        "jammu and kashmir": "JK",
        "jammu & kashmir": "JK",
        "jharkhand": "JH",
        "jharkand": "JH",
        "karnataka": "KA",
        "kerala": "KL",
        "keralam": "KL",
        "ladakh": "LA",
        "leh": "LA",
        "lakshadweep": "LD",
        "lakhswadeep": "LD",
        "lakshwadeep": "LD",
        "madhya pradesh": "MP",
        "maharashtra": "MH",
        "manipur": "MN",
        "meghalaya": "ML",
        "mizoram": "MZ",
        "nagaland": "NL",
        "odisha": "OR",
        "orissa": "OR",
        "puducherry": "PY",
        "pondicherry": "PY",
        "punjab": "PB",
        "rajasthan": "RJ",
        "sikkim": "SK",
        "tamil nadu": "TN",
        "telangana": "TG",
        "tripura": "TR",
        "uttar pradesh": "UP",
        "uttarakhand": "UK",
        "uttrakhand": "UK",
        "west bengal": "WB",
        "westbengal": "WB",
    }
    return mapping_dict.get(s)


def classify_connector(conn_str: str, rating_kw: float) -> Tuple[str, str]:
    """Returns (standardized_connector_category, current_type 'AC' | 'DC')."""
    c = (conn_str or "").strip().upper()
    if "CCS" in c:
        return ("CCS / CCS-II (DC)", "DC")
    if "CHADEMO" in c:
        return ("CHAdeMO (DC)", "DC")
    if "DC-001" in c or "BHARAT DC" in c or "GB/T" in c:
        return ("Bharat DC-001", "DC")
    if "LEV DC" in c or "17017-2-7" in c or "IS-17017" in c:
        return ("LEV DC (IS-17017)", "DC")
    if "TYPE-II" in c or "TYPE 2" in c or "TYPE-2" in c or "AC TYPE" in c:
        return ("Type-II AC", "AC")
    if "AC-001" in c or "BHARAT AC" in c:
        return ("Bharat AC-001", "AC")
    if "LEV AC" in c or "16A" in c or "3.3" in c or "INDUSTRIAL" in c or "SOCKET" in c:
        return ("LEV AC / 3.3kW Socket", "AC")
    if "DC" in c or rating_kw >= 25.0:
        return ("Other DC Fast", "DC")
    return ("Other AC", "AC")


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Returns Haversine distance in meters between two WGS84 points."""
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def min_dist_m_to_points(lat: float, lon: float, pts_lat: np.ndarray, pts_lon: np.ndarray) -> float:
    """Vectorized fast approximate spherical distance in meters to nearest point in arrays."""
    if len(pts_lat) == 0:
        return 999999.0
    cos_lat = math.cos(math.radians(lat))
    dy = (pts_lat - lat) * 111320.0
    dx = (pts_lon - lon) * 111320.0 * cos_lat
    dists_sq = dx * dx + dy * dy
    return float(math.sqrt(float(np.min(dists_sq))))


# State EV Tariffs parsed from `data/raw/electricity/BEE_State_EV_Tariff_Annexure_A.pdf`
STATE_EV_TARIFFS: Dict[str, Dict[str, Any]] = {
    "AN": {"fixed": "0", "energy": "10.00 Rs/unit", "lt_rs_kwh": 10.0, "ht_rs_kwh": 10.0},
    "AP": {"fixed": "0", "energy": "6.70 Rs/unit", "lt_rs_kwh": 6.7, "ht_rs_kwh": 6.7},
    "AR": {"fixed": "Not defined", "energy": "Not defined", "lt_rs_kwh": None, "ht_rs_kwh": None},
    "AS": {"fixed": "LT: 150, HT: 180 Rs/kW/mo", "energy": "LT: 5.90, HT: 7.40 Rs/unit", "lt_rs_kwh": 5.9, "ht_rs_kwh": 7.4},
    "BR": {"fixed": "0", "energy": "LT: 8.87, HT: 8.00 Rs/unit", "lt_rs_kwh": 8.87, "ht_rs_kwh": 8.0},
    "CH": {"fixed": "0", "energy": "LT: 3.80, HT: 3.60 Rs/unit", "lt_rs_kwh": 3.8, "ht_rs_kwh": 3.6},
    "CG": {"fixed": "0", "energy": "5.00 Rs/unit", "lt_rs_kwh": 5.0, "ht_rs_kwh": 5.0},
    "DD": {"fixed": "0", "energy": "LT: 5.10, HT: 4.90 Rs/unit", "lt_rs_kwh": 5.1, "ht_rs_kwh": 4.9},
    "DL": {"fixed": "0", "energy": "LT: 4.50, HT: 4.00 Rs/unit", "lt_rs_kwh": 4.5, "ht_rs_kwh": 4.0},
    "GA": {"fixed": "0", "energy": "LT: 4.70, HT: 4.50 Rs/unit", "lt_rs_kwh": 4.7, "ht_rs_kwh": 4.5},
    "GJ": {"fixed": "LT: 25/inst/mo, HT: 25/kVA/mo", "energy": "LT: 4.10, HT: 4.00 Rs/unit", "lt_rs_kwh": 4.1, "ht_rs_kwh": 4.0},
    "HR": {"fixed": "0", "energy": "LT: 6.62, HT: 6.22 Rs/unit", "lt_rs_kwh": 6.62, "ht_rs_kwh": 6.22},
    "HP": {"fixed": "0", "energy": "5.82 Rs/unit", "lt_rs_kwh": 5.82, "ht_rs_kwh": 5.82},
    "JK": {"fixed": "LT: 100/kW, HT: 150-175/kW", "energy": "LT: 5.10, HT: 4.90-5.00 Rs/unit", "lt_rs_kwh": 5.1, "ht_rs_kwh": 4.95},
    "JH": {"fixed": "Rural: 50/kW, Urban: 100/kW", "energy": "Rural: 5.80, Urban: 6.15 Rs/unit", "lt_rs_kwh": 6.15, "ht_rs_kwh": 6.15},
    "KA": {"fixed": "LT: 70-170/kW, HT: 200/kVA", "energy": "5.00 Rs/unit", "lt_rs_kwh": 5.0, "ht_rs_kwh": 5.0},
    "KL": {"fixed": "LT: 90/kW, HT: 270/kVA", "energy": "LT: 5.50, HT: 6.00 Rs/unit", "lt_rs_kwh": 5.5, "ht_rs_kwh": 6.0},
    "LA": {"fixed": "LT: 100/kW, HT: 150-175/kW", "energy": "LT: 5.10, HT: 4.90-5.00 Rs/unit", "lt_rs_kwh": 5.1, "ht_rs_kwh": 4.95},
    "LD": {"fixed": "0", "energy": "7.80 Rs/unit", "lt_rs_kwh": 7.8, "ht_rs_kwh": 7.8},
    "MP": {"fixed": "0", "energy": "LT: 6.79, HT: 6.96 Rs/unit", "lt_rs_kwh": 6.79, "ht_rs_kwh": 6.96},
    "MH": {"fixed": "LT: 75/kW, HT: 75/kVA", "energy": "LT: 6.08, HT: 6.90 Rs/unit", "lt_rs_kwh": 6.08, "ht_rs_kwh": 6.9},
    "MN": {"fixed": "Not defined", "energy": "Not defined", "lt_rs_kwh": None, "ht_rs_kwh": None},
    "ML": {"fixed": "LT: 120/kVA, HT: 230/kVA", "energy": "LT: 9.70, HT: 9.90 Rs/unit", "lt_rs_kwh": 9.7, "ht_rs_kwh": 9.9},
    "MZ": {"fixed": "LT: 75/kW/mo, HT: 75/kVA/mo", "energy": "LT: 8.20/kWh, HT: 8.65/kVAh", "lt_rs_kwh": 8.2, "ht_rs_kwh": 8.65},
    "NL": {"fixed": "Not defined", "energy": "Not defined", "lt_rs_kwh": None, "ht_rs_kwh": None},
    "OR": {"fixed": "0", "energy": "5.50 Rs/unit", "lt_rs_kwh": 5.5, "ht_rs_kwh": 5.5},
    "PY": {"fixed": "0", "energy": "LT: 5.53, HT: 5.33 Rs/unit", "lt_rs_kwh": 5.53, "ht_rs_kwh": 5.33},
    "PB": {"fixed": "0", "energy": "6.28 Rs/kVAh", "lt_rs_kwh": 6.28, "ht_rs_kwh": 6.28},
    "RJ": {"fixed": "LT: 40/kVA, HT: 135/kVA", "energy": "6.00 Rs/unit", "lt_rs_kwh": 6.0, "ht_rs_kwh": 6.0},
    "SK": {"fixed": "500/mo (<45kW), 150/kVA (>45kW)", "energy": "5.50 Rs/unit", "lt_rs_kwh": 5.5, "ht_rs_kwh": 5.5},
    "TN": {"fixed": "LT: 25-138/kVA, HT: 138/kVA", "energy": "6.00 to 9.00 Rs/unit (ToD)", "lt_rs_kwh": 7.5, "ht_rs_kwh": 7.5},
    "TG": {"fixed": "LT: 50/kW, HT: 100/kVA", "energy": "LT: 6.00, HT: 5.00-7.00 Rs/unit", "lt_rs_kwh": 6.0, "ht_rs_kwh": 6.0},
    "TR": {"fixed": "50 Rs/kW", "energy": "6.90 Rs/unit", "lt_rs_kwh": 6.9, "ht_rs_kwh": 6.9},
    "UP": {"fixed": "0", "energy": "LT: 7.70, HT: 7.30 Rs/unit", "lt_rs_kwh": 7.7, "ht_rs_kwh": 7.3},
    "UK": {"fixed": "0", "energy": "6.25 Rs/unit", "lt_rs_kwh": 6.25, "ht_rs_kwh": 6.25},
    "WB": {"fixed": "0", "energy": "6.00 Rs/unit", "lt_rs_kwh": 6.0, "ht_rs_kwh": 6.0},
}


def load_sna_directory() -> Dict[str, str]:
    """Reads State Nodal Agencies from `BEE_State_Nodal_Agencies_Annexure_B.xlsx`."""
    wb = openpyxl.load_workbook(RAW_DIR / "context" / "BEE_State_Nodal_Agencies_Annexure_B.xlsx")
    ws = wb.active
    sna_by_code: Dict[str, str] = {}
    for row in ws.iter_rows(values_only=True):
        if not row or len(row) < 3:
            continue
        st_raw = str(row[1] or "").strip()
        sna_name = str(row[2] or "").strip()
        code = normalize_state_to_code(st_raw)
        if code and sna_name:
            sna_by_code[code] = sna_name
    return sna_by_code


def load_admin_polygons() -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    """
    Loads `Admin2.shp` (36 States/UTs) and `2011_Dist.shp` (9 Delhi districts).
    Returns:
      - state_geoms: {state_code: shapely_geom}
      - state_geojson: simplified GeoJSON FeatureCollection for national map
      - delhi_dist_geoms: {district_name: shapely_geom}
      - delhi_dist_records: {district_name: record_dict}
    """
    print("1. Loading administrative boundaries (Admin2.shp & 2011_Dist.shp)...")
    sf_state = shapefile.Reader(str(RAW_DIR / "boundaries" / "Admin2.shp"))
    state_geoms: Dict[str, Any] = {}
    state_features: List[Dict[str, Any]] = []

    for sr in sf_state.shapeRecords():
        st_nm = sr.record["ST_NM"]
        code = ADMIN2_TO_CODE.get(st_nm) or normalize_state_to_code(st_nm)
        if not code:
            raise ValueError(f"Unmapped Admin2 state name: {st_nm}")
        geom = shape(sr.shape.__geo_interface__)
        if not geom.is_valid:
            geom = geom.buffer(0)
        state_geoms[code] = geom
        # Simplify geometry for fast web map rendering (0.012 deg ~ 1.2 km national view)
        simp_geom = geom.simplify(0.012, preserve_topology=True)
        centroid = geom.centroid
        state_features.append(
            {
                "type": "Feature",
                "properties": {
                    "state_code": code,
                    "state_name": CANONICAL_STATES[code]["name"],
                    "admin2_name": st_nm,
                    "centroid_lat": round(centroid.y, 4),
                    "centroid_lon": round(centroid.x, 4),
                },
                "geometry": mapping(simp_geom),
            }
        )

    state_geojson = {"type": "FeatureCollection", "features": state_features}

    sf_dist = shapefile.Reader(str(RAW_DIR / "boundaries" / "2011_Dist.shp"))
    delhi_dist_geoms: Dict[str, Any] = {}
    delhi_dist_records: Dict[str, Dict[str, Any]] = {}
    for sr in sf_dist.shapeRecords():
        rec = sr.record.as_dict()
        if "delhi" in str(rec.get("ST_NM", "")).lower():
            d_name = str(rec["DISTRICT"]).strip()
            geom = shape(sr.shape.__geo_interface__)
            if not geom.is_valid:
                geom = geom.buffer(0)
            delhi_dist_geoms[d_name] = geom
            delhi_dist_records[d_name] = rec

    print(f"   Loaded {len(state_geoms)} state polygons and {len(delhi_dist_geoms)} Delhi district polygons.")
    return state_geoms, state_geojson, delhi_dist_geoms, delhi_dist_records


def assign_delhi_district(lat: float, lon: float, delhi_dist_geoms: Dict[str, Any]) -> Optional[str]:
    """Point-in-polygon lookup for NCT of Delhi districts, with nearest-polygon fallback if on boundary."""
    pt = Point(lon, lat)
    for d_name, geom in delhi_dist_geoms.items():
        if geom.contains(pt) or geom.touches(pt):
            return d_name
    # Check if within ~2km of Delhi border (for border points)
    best_dist = 999.0
    best_name = None
    for d_name, geom in delhi_dist_geoms.items():
        d = geom.distance(pt)
        if d < best_dist:
            best_dist = d
            best_name = d_name
    if best_dist <= 0.03:  # ~3 km buffer for NCR border stations tagged as Delhi
        return best_name
    return None


# PIN Code prefix / range mapping to Delhi's 9 Census 2011 Districts (used ONLY for the 121 un-geocoded Switch Delhi swap stations)
DELHI_PIN_TO_DISTRICT: Dict[str, str] = {
    "110001": "New Delhi", "110002": "Central", "110003": "South", "110004": "Central",
    "110005": "Central", "110006": "Central", "110007": "North", "110008": "Central",
    "110009": "North", "110010": "South West", "110011": "New Delhi", "110012": "Central",
    "110013": "South", "110014": "South", "110015": "West", "110016": "South West",
    "110017": "South", "110018": "West", "110019": "South", "110020": "South",
    "110021": "New Delhi", "110022": "South West", "110023": "New Delhi", "110024": "South",
    "110025": "South", "110026": "West", "110027": "West", "110028": "South West",
    "110029": "South", "110030": "South", "110031": "East", "110032": "North East",
    "110033": "North West", "110034": "North West", "110035": "North West", "110036": "North",
    "110037": "South West", "110038": "South West", "110039": "North West", "110040": "North West",
    "110041": "West", "110042": "North West", "110043": "South West", "110044": "South",
    "110045": "South West", "110046": "South West", "110047": "South", "110048": "South",
    "110049": "South", "110051": "East", "110052": "North West", "110053": "North East",
    "110054": "North", "110055": "Central", "110056": "North West", "110057": "South West",
    "110058": "West", "110059": "West", "110060": "Central", "110061": "South West",
    "110062": "South", "110063": "West", "110064": "West", "110065": "South",
    "110066": "South West", "110067": "South", "110068": "South", "110070": "South West",
    "110071": "South West", "110072": "South West", "110073": "South West", "110074": "South",
    "110075": "South West", "110076": "South", "110077": "South West", "110078": "South West",
    "110080": "South", "110081": "North West", "110082": "North West", "110083": "North West",
    "110084": "North", "110085": "North West", "110086": "North West", "110087": "West",
    "110088": "North West", "110089": "North West", "110090": "North East", "110091": "East",
    "110092": "East", "110093": "North East", "110094": "North East", "110095": "East",
    "110096": "East", "110097": "South",
}


def compute_worldpop_for_polygons(polygons: Dict[str, Any]) -> Dict[str, float]:
    """
    Integrates WorldPop 1km population raster (`WorldPop_ind_ppp_2020_1km_Aggregated.tif`)
    inside each provided polygon in `polygons`.
    """
    tif_path = RAW_DIR / "demographics" / "WorldPop_ind_ppp_2020_1km_Aggregated.tif"
    img = Image.open(tif_path)
    arr = np.array(img, dtype=np.float64)
    scale = img.tag_v2.get(33550)  # (dx, dy, 0)
    tie = img.tag_v2.get(33922)    # (0, 0, 0, min_lon, max_lat, 0)
    dx, dy = float(scale[0]), float(scale[1])
    lon0, lat0 = float(tie[3]), float(tie[4])

    results: Dict[str, float] = {}
    nrows, ncols = arr.shape

    for key, geom in polygons.items():
        minx, miny, maxx, maxy = geom.bounds
        c_start = max(0, int((minx - lon0) / dx) - 1)
        c_end = min(ncols - 1, int((maxx - lon0) / dx) + 1)
        r_start = max(0, int((lat0 - maxy) / dy) - 1)
        r_end = min(nrows - 1, int((lat0 - miny) / dy) + 1)

        prep_geom = prep(geom)
        total_pop = 0.0
        for r in range(r_start, r_end + 1):
            lat = lat0 - (r + 0.5) * dy
            for c in range(c_start, c_end + 1):
                val = arr[r, c]
                if val <= 0 or math.isnan(val):
                    continue
                lon = lon0 + (c + 0.5) * dx
                if prep_geom.contains(Point(lon, lat)):
                    total_pop += float(val)
        results[key] = round(total_pop, 1)
    return results


def main() -> None:
    state_geoms, state_geojson, delhi_dist_geoms, delhi_dist_records = load_admin_polygons()
    sna_by_code = load_sna_directory()

    # -------------------------------------------------------------------------
    # 2. Load VAHAN Datasets (National, State Summary, Subcategories, Yearwise, Delhi RTOs)
    # -------------------------------------------------------------------------
    print("2. Processing VAHAN active EV registration datasets...")
    with open(RAW_DIR / "vahan" / "VAHAN_national_overview_20261019.json", "r", encoding="utf-8") as f:
        vahan_national_overview = json.load(f)

    vahan_states: Dict[str, Dict[str, Any]] = {}
    with open(RAW_DIR / "vahan" / "VAHAN_state_ev_summary_20261019.csv", "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            code = row["state_code"].strip()
            vahan_states[code] = {
                "state_code": code,
                "state_name": CANONICAL_STATES[code]["name"],
                "total_ev_active": int(row["total_ev_active"]),
                "ev_2w": int(row["ev_2w"]),
                "ev_3w": int(row["ev_3w"]),
                "ev_4w_lmv_pv": int(row["ev_4w_lmv_pv"]),
                "ev_bus": int(row["ev_bus_hpv_mpv"]),
                "ev_goods": int(row["ev_goods_lgv_mgv_hgv"]),
                "ev_other": int(row["ev_other"]),
                "fuel_electric_bov": int(row["fuel_electric_bov"]),
                "fuel_pure_ev": int(row["fuel_pure_ev"]),
                "fuel_plugin_hybrid_ev": int(row["fuel_plugin_hybrid_ev"]),
                "fuel_solar": int(row["fuel_solar"]),
                "fuel_hydrogen": int(row["fuel_hydrogen"]),
                "status_active_compliant": int(row["status_active_compliant"]),
                "status_active_non_compliant": int(row["status_active_non_compliant"]),
                "extraction_date": row["extraction_date"],
                "subcategories": {},
                "yearwise_trend": [],
            }

    with open(RAW_DIR / "vahan" / "VAHAN_state_ev_by_subcategory_20261019.csv", "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            code = row["state_code"].strip()
            if code in vahan_states:
                vahan_states[code]["subcategories"][row["vehicle_subcategory"].strip()] = int(row["active_ev_count"])

    with open(RAW_DIR / "vahan" / "VAHAN_state_ev_yearwise_20261019.csv", "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            code = row["state_code"].strip()
            if code in vahan_states:
                vahan_states[code]["yearwise_trend"].append(
                    {
                        "year": int(row["registration_year"]),
                        "registrations": int(row["ev_registrations"]),
                    }
                )
    for code in vahan_states:
        vahan_states[code]["yearwise_trend"].sort(key=lambda x: x["year"])

    # -------------------------------------------------------------------------
    # 3. Load NITI Aayog IEMI 2025 State Population, Area & GSDP
    # -------------------------------------------------------------------------
    print("3. Processing NITI Aayog IEMI 2025 state population, area & GSDP...")
    demographics_by_code: Dict[str, Dict[str, Any]] = {}
    with open(RAW_DIR / "demographics" / "NITI_IEMI_2025_State_Population_GSDP.csv", "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            code = normalize_state_to_code(row["state_ut"])
            if not code:
                continue
            area = float(row["area_sq_km"]) if row["area_sq_km"] else None
            pop = int(float(row["ncp_2025_population"])) if row["ncp_2025_population"] else None
            gsdp = round(float(row["gsdp_inr_crore"]), 1) if row["gsdp_inr_crore"] else None
            demographics_by_code[code] = {
                "area_sq_km": area,
                "ncp_2025_population": pop,
                "gsdp_inr_crore": gsdp,
            }
    # Fill Lakshadweep baseline (not in NITI 35-row table) from official Census/Survey of India baseline
    if "LD" not in demographics_by_code:
        demographics_by_code["LD"] = {
            "area_sq_km": 32.0,
            "ncp_2025_population": 70000,
            "gsdp_inr_crore": None,
        }

    # -------------------------------------------------------------------------
    # 4. Load PIB OMC & FAME-II State-wise Datasets (Kept Strictly Separate)
    # -------------------------------------------------------------------------
    print("4. Processing PIB MoPNG OMC (PRID 2246042) & MHI FAME-II (PRID 2246045) datasets...")
    omc_by_code: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {
            "fy20_21": 0,
            "fy21_22": 0,
            "fy22_23": 0,
            "fy23_24": 0,
            "fy24_25": 0,
            "fy25_26": 0,
            "decommissioned": 0,
            "installed_total": 0,
            "operational_total": 0,
        }
    )

    def parse_pib_int(val: str) -> int:
        v = html.unescape(val or "").replace(",", "").strip()
        if not v or v == "-" or v == "NA":
            return 0
        return int(float(v))

    with open(RAW_DIR / "charging" / "PIB_PRID_2246042_OMC_Statewise_EVPCS_20260301.csv", "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            st_raw = row["State"].strip()
            if st_raw.lower() == "total":
                continue
            code = normalize_state_to_code(st_raw)
            if not code:
                raise ValueError(f"Unmapped PIB OMC state: {st_raw}")
            rec = omc_by_code[code]
            rec["fy20_21"] += parse_pib_int(row["FY20_21"])
            rec["fy21_22"] += parse_pib_int(row["FY21_22"])
            rec["fy22_23"] += parse_pib_int(row["FY22_23"])
            rec["fy23_24"] += parse_pib_int(row["FY23_24"])
            rec["fy24_25"] += parse_pib_int(row["FY24_25"])
            rec["fy25_26"] += parse_pib_int(row["FY25_26_upto_01032026"])
            rec["decommissioned"] += parse_pib_int(row["Decommissioned"])
            rec["installed_total"] += parse_pib_int(row["Total_EVPCS_Installed_5Yrs"])
            rec["operational_total"] += parse_pib_int(row["Total_EVPCS_Operational_01032026"])

    fame2_by_code: Dict[str, int] = defaultdict(int)
    with open(RAW_DIR / "charging" / "PIB_PRID_2246045_FAMEII_Statewise_EVPCS_20260301.csv", "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            st_raw = row["State"].strip()
            if st_raw.lower() == "total":
                continue
            code = normalize_state_to_code(st_raw)
            if code:
                fame2_by_code[code] += parse_pib_int(row["FAME_II_OMC_Chargers_Installed_01032026"])

    fame2_pse_entities: List[Dict[str, Any]] = []
    with open(RAW_DIR / "charging" / "PIB_PRID_2246045_FAMEII_PSE_Entities_20260301.csv", "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            fame2_pse_entities.append(row)

    # -------------------------------------------------------------------------
    # 5. Load & Clean BEE EVPCS Dataset (39,641 rows -> Stations, Connectors, Clusters, Delhi Subset)
    # -------------------------------------------------------------------------
    print("5. Processing BEE EV_PCS_Data_29277 (39,641 rows)...")
    bee_state_stats: Dict[str, Dict[str, Any]] = {
        code: {
            "raw_charger_rows": 0,
            "exact_duplicate_rows": 0,
            "valid_bbox_rows": 0,
            "invalid_coord_rows": 0,
            "lat_eq_lon_rows": 0,
            "total_connectors": 0,
            "ac_connectors": 0,
            "dc_connectors": 0,
            "total_power_kw": 0.0,
            "govt_rows": 0,
            "private_rows": 0,
            "omc_rows": 0,
            "unique_sites_set": set(),
            "unique_coords_set": set(),
            "cpo_counter": Counter(),
            "connector_counter": Counter(),
            "raw_state_variants": set(),
        }
        for code in CANONICAL_STATES
    }

    seen_exact_rows = set()
    # District/City hub aggregation for fast national map rendering
    hub_clusters: Dict[Tuple[str, str], Dict[str, Any]] = {}
    # Deduplicated physical stations inside NCT of Delhi from BEE
    bee_delhi_sites: Dict[Tuple[str, str, float, float], Dict[str, Any]] = {}

    with open(RAW_DIR / "charging" / "BEE_EV_PCS_Data_29277_20251026_extracted.csv", "r", encoding="utf-8") as f:
        for idx, row in enumerate(csv.DictReader(f), start=1):
            cpo = row["CPO_Name"].strip()
            gov_priv = row["Govt_Private"].strip()
            raw_st = row["State"].strip()
            raw_dist = row["District"].strip()
            city = row["City_Village"].strip()
            loc = row["Location"].strip()
            lat_s = row["Latitude"].strip()
            lon_s = row["Longitude"].strip()
            conn_type = row["Connector_Type"].strip()
            try:
                charger_kw = float(row["Charger_Rating_kW"])
            except ValueError:
                charger_kw = 0.0
            try:
                conn_kw = float(row["Connector_Rating_kW"])
            except ValueError:
                conn_kw = 0.0
            try:
                num_conn = int(float(row["No_of_Connectors"]))
            except ValueError:
                num_conn = 1

            code = normalize_state_to_code(raw_st)
            if not code:
                raise ValueError(f"Unmapped BEE state on row {idx}: {raw_st}")

            st_stat = bee_state_stats[code]
            st_stat["raw_charger_rows"] += 1
            st_stat["raw_state_variants"].add(raw_st)

            # Check exact duplicate across all 12 data columns
            row_sig = (cpo, gov_priv, raw_st, raw_dist, city, loc, lat_s, lon_s, conn_type, charger_kw, conn_kw, num_conn)
            if row_sig in seen_exact_rows:
                st_stat["exact_duplicate_rows"] += 1
            else:
                seen_exact_rows.add(row_sig)

            # Parse and validate coordinates
            coord_valid = False
            lat_eq_lon = False
            lat_val, lon_val = 0.0, 0.0
            try:
                lat_val = float(lat_s)
                lon_val = float(lon_s)
                if abs(lat_val - lon_val) < 0.0005:
                    lat_eq_lon = True
                elif 6.0 <= lat_val <= 37.5 and 68.0 <= lon_val <= 97.5:
                    coord_valid = True
            except ValueError:
                coord_valid = False

            if coord_valid:
                st_stat["valid_bbox_rows"] += 1
                coord_key = (round(lat_val, 4), round(lon_val, 4))
                site_key = (cpo.upper(), loc[:40].upper(), round(lat_val, 4), round(lon_val, 4))
                st_stat["unique_coords_set"].add(coord_key)
                st_stat["unique_sites_set"].add(site_key)
            else:
                st_stat["invalid_coord_rows"] += 1
                if lat_eq_lon:
                    st_stat["lat_eq_lon_rows"] += 1
                # Fallback site key using location string when coordinates are invalid
                site_key = (cpo.upper(), loc[:60].upper(), 0.0, 0.0)
                st_stat["unique_sites_set"].add(site_key)

            st_stat["total_connectors"] += num_conn
            st_stat["total_power_kw"] += charger_kw
            if "govt" in gov_priv.lower():
                st_stat["govt_rows"] += 1
            else:
                st_stat["private_rows"] += 1
            if cpo.upper() in ("IOCL", "BPCL", "HPCL"):
                st_stat["omc_rows"] += 1

            std_conn, ac_dc = classify_connector(conn_type, charger_kw)
            if ac_dc == "DC":
                st_stat["dc_connectors"] += num_conn
            else:
                st_stat["ac_connectors"] += num_conn

            st_stat["cpo_counter"][cpo] += 1
            st_stat["connector_counter"][std_conn] += num_conn

            # Aggregate valid coordinates into District Hub Clusters for the National Map
            if coord_valid:
                norm_dist = re.sub(r"\s+", " ", raw_dist).strip().title()
                hub_key = (code, norm_dist)
                if hub_key not in hub_clusters:
                    hub_clusters[hub_key] = {
                        "state_code": code,
                        "state_name": CANONICAL_STATES[code]["name"],
                        "district": norm_dist,
                        "lat_sum": 0.0,
                        "lon_sum": 0.0,
                        "charger_rows": 0,
                        "sites": set(),
                        "connectors": 0,
                        "dc_connectors": 0,
                        "ac_connectors": 0,
                        "total_kw": 0.0,
                        "cpos": Counter(),
                    }
                hc = hub_clusters[hub_key]
                hc["lat_sum"] += lat_val
                hc["lon_sum"] += lon_val
                hc["charger_rows"] += 1
                hc["sites"].add(site_key)
                hc["connectors"] += num_conn
                if ac_dc == "DC":
                    hc["dc_connectors"] += num_conn
                else:
                    hc["ac_connectors"] += num_conn
                hc["total_kw"] += charger_kw
                hc["cpos"][cpo] += 1

            # Collect BEE stations inside NCT of Delhi (either State == Delhi or inside Delhi polygon)
            if coord_valid and (code == "DL" or (28.40 <= lat_val <= 28.89 and 76.83 <= lon_val <= 77.35)):
                dl_dist = assign_delhi_district(lat_val, lon_val, delhi_dist_geoms)
                if code == "DL" or dl_dist is not None:
                    dl_site_key = (cpo.upper(), round(lat_val, 4), round(lon_val, 4))
                    if dl_site_key not in bee_delhi_sites:
                        bee_delhi_sites[dl_site_key] = {
                            "id": f"BEE-DL-{len(bee_delhi_sites) + 1:04d}",
                            "source": "BEE",
                            "source_date": "2025-10-26",
                            "station_type": "Charging",
                            "vendor": cpo,
                            "govt_private": gov_priv,
                            "address": loc,
                            "city": city,
                            "raw_district": raw_dist,
                            "district": dl_dist or "South West",
                            "latitude": round(lat_val, 6),
                            "longitude": round(lon_val, 6),
                            "coord_status": "VERIFIED_COORDS",
                            "charger_rows_merged": 0,
                            "no_of_chargers": 0,
                            "total_connectors": 0,
                            "dc_connectors": 0,
                            "ac_connectors": 0,
                            "max_capacity_kw": 0.0,
                            "total_capacity_kw": 0.0,
                            "connector_types": set(),
                        }
                    bds = bee_delhi_sites[dl_site_key]
                    bds["charger_rows_merged"] += 1
                    bds["no_of_chargers"] += 1
                    bds["total_connectors"] += num_conn
                    if ac_dc == "DC":
                        bds["dc_connectors"] += num_conn
                    else:
                        bds["ac_connectors"] += num_conn
                    bds["max_capacity_kw"] = max(bds["max_capacity_kw"], charger_kw)
                    bds["total_capacity_kw"] = round(bds["total_capacity_kw"] + charger_kw, 2)
                    bds["connector_types"].add(conn_type)

    # -------------------------------------------------------------------------
    # 6. Load OpenStreetMap India Charging Stations (725 features)
    # -------------------------------------------------------------------------
    print("6. Processing OpenStreetMap India charging stations (725 features)...")
    osm_by_state: Counter = Counter()
    osm_delhi_stations: List[Dict[str, Any]] = []
    prepared_states = {code: prep(geom) for code, geom in state_geoms.items()}

    with open(RAW_DIR / "charging" / "OSM_India_charging_stations_20261019.csv", "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            lat = float(row["latitude"])
            lon = float(row["longitude"])
            pt = Point(lon, lat)
            matched_code = normalize_state_to_code(row.get("addr_state", ""))
            if not matched_code:
                for code, pgeom in prepared_states.items():
                    if pgeom.contains(pt):
                        matched_code = code
                        break
            if matched_code:
                osm_by_state[matched_code] += 1

            # Check if inside NCT of Delhi
            if matched_code == "DL" or (28.40 <= lat <= 28.89 and 76.83 <= lon <= 77.35):
                dl_dist = assign_delhi_district(lat, lon, delhi_dist_geoms)
                if dl_dist is not None:
                    cap_str = row.get("capacity", "").strip()
                    try:
                        cap_int = int(float(cap_str)) if cap_str else 1
                    except ValueError:
                        cap_int = 1
                    osm_delhi_stations.append(
                        {
                            "id": f"OSM-{row['osm_id']}",
                            "osm_id": row["osm_id"],
                            "source": "OSM",
                            "source_date": "2026-10-19",
                            "station_type": "Charging",
                            "vendor": row.get("operator") or row.get("brand") or "OSM Community Mapped",
                            "name": row.get("name") or f"OSM Charging Station #{row['osm_id']}",
                            "address": row.get("addr_city") or dl_dist,
                            "postal_code": row.get("addr_postcode") or "",
                            "district": dl_dist,
                            "latitude": round(lat, 6),
                            "longitude": round(lon, 6),
                            "coord_status": "VERIFIED_COORDS",
                            "no_of_chargers": cap_int,
                            "total_connectors": cap_int,
                            "dc_connectors": 0,
                            "ac_connectors": cap_int,
                            "max_capacity_kw": None,
                            "total_capacity_kw": None,
                            "charger_type": row.get("output") or "Unspecified in OSM",
                            "power_class": "Unspecified (OSM)",
                            "cost_per_unit": row.get("fee") or "Unspecified",
                            "timing": row.get("opening_hours") or "Unspecified",
                        }
                    )

    # -------------------------------------------------------------------------
    # 7. Load Delhi Contextual Layers (Power Grid, Major Roads, Demand Attractors)
    # -------------------------------------------------------------------------
    print("7. Processing NCT of Delhi power grid nodes (576), major roads (8,087), and demand attractors (3,534)...")
    delhi_power_nodes: List[Dict[str, Any]] = []
    substation_lats: List[float] = []
    substation_lons: List[float] = []

    with open(RAW_DIR / "electricity" / "OSM_Delhi_power_infrastructure_20261019.csv", "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            lat = float(row["latitude"])
            lon = float(row["longitude"])
            dl_dist = assign_delhi_district(lat, lon, delhi_dist_geoms) or "Outer NCR Fringe"
            ptype = row["power_type"].strip()
            delhi_power_nodes.append(
                {
                    "osm_id": row["osm_id"],
                    "power_type": ptype,
                    "substation_type": row["substation_type"].strip() or "Unspecified",
                    "name": row["name"].strip() or f"{ptype.title()} #{row['osm_id']}",
                    "operator": row["operator"].strip() or "Unspecified Utility (DISCOM/DTL)",
                    "voltage": row["voltage"].strip() or "Unspecified",
                    "rating": row["rating"].strip() or "Unspecified",
                    "district": dl_dist,
                    "latitude": round(lat, 6),
                    "longitude": round(lon, 6),
                }
            )
            if ptype in ("substation", "transformer"):
                substation_lats.append(lat)
                substation_lons.append(lon)

    sub_lat_arr = np.array(substation_lats, dtype=np.float64)
    sub_lon_arr = np.array(substation_lons, dtype=np.float64)

    delhi_attractors: List[Dict[str, Any]] = []
    with open(RAW_DIR / "context" / "OSM_Delhi_demand_attractors_20261019.csv", "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            lat = float(row["latitude"])
            lon = float(row["longitude"])
            dl_dist = assign_delhi_district(lat, lon, delhi_dist_geoms)
            if not dl_dist:
                continue
            delhi_attractors.append(
                {
                    "osm_id": row["osm_id"],
                    "category": row["category"].strip(),
                    "name": row["name"].strip() or f"{row['category'].replace('_', ' ').title()}",
                    "operator": row["operator"].strip() or "",
                    "district": dl_dist,
                    "latitude": round(lat, 5),
                    "longitude": round(lon, 5),
                }
            )

    # Extract simplified major road polylines for Delhi map overlay
    with open(RAW_DIR / "roads" / "OSM_Delhi_major_roads_20261019.json", "r", encoding="utf-8") as f:
        raw_roads_json = json.load(f)

    road_features: List[Dict[str, Any]] = []
    road_center_lats: List[float] = []
    road_center_lons: List[float] = []
    district_road_counts: Counter = Counter()
    corridor_groups: Dict[Tuple[str, str, str], List[Tuple[float, float]]] = defaultdict(list)

    for elem in raw_roads_json.get("elements", []):
        tags = elem.get("tags", {})
        hw = tags.get("highway", "secondary")
        center = elem.get("center")
        if center and "lat" in center and "lon" in center:
            clat, clon = float(center["lat"]), float(center["lon"])
            road_center_lats.append(clat)
            road_center_lons.append(clon)
            dl_dist = assign_delhi_district(clat, clon, delhi_dist_geoms)
            if dl_dist:
                district_road_counts[dl_dist] += 1
            r_name = tags.get("name", "").strip()
            r_ref = tags.get("ref", "").strip()
            if r_name or r_ref or hw in ("motorway", "trunk", "primary"):
                corridor_groups[(hw, r_ref, r_name or r_ref or hw.title())].append((clon, clat))

    # Build clean connected corridor LineStrings from grouped way centroids (splitting jumps > 1.8 km)
    for (hw, r_ref, r_name), pts in corridor_groups.items():
        if len(pts) < 2:
            continue
        # Nearest-neighbor chain ordering for corridor segments
        remaining = list(pts)
        remaining.sort(key=lambda p: (p[0], p[1]))
        current_line = [remaining.pop(0)]
        while remaining:
            last_x, last_y = current_line[-1]
            best_i = 0
            best_d2 = 999999.0
            for i, (px, py) in enumerate(remaining):
                d2 = (px - last_x) ** 2 + (py - last_y) ** 2
                if d2 < best_d2:
                    best_d2 = d2
                    best_i = i
            nxt = remaining.pop(best_i)
            if math.sqrt(best_d2) <= 0.018:  # ~1.8 km continuity threshold
                if best_d2 > 1e-9:
                    current_line.append(nxt)
            else:
                if len(current_line) >= 2:
                    road_features.append(
                        {
                            "type": "Feature",
                            "properties": {"highway": hw, "name": r_name, "ref": r_ref},
                            "geometry": {"type": "LineString", "coordinates": [[round(x, 5), round(y, 5)] for x, y in current_line]},
                        }
                    )
                current_line = [nxt]
        if len(current_line) >= 2:
            road_features.append(
                {
                    "type": "Feature",
                    "properties": {"highway": hw, "name": r_name, "ref": r_ref},
                    "geometry": {"type": "LineString", "coordinates": [[round(x, 5), round(y, 5)] for x, y in current_line]},
                }
            )

    road_lat_arr = np.array(road_center_lats, dtype=np.float64)
    road_lon_arr = np.array(road_center_lons, dtype=np.float64)

    # -------------------------------------------------------------------------
    # 8. Process Delhi Switch Delhi Charging & Battery Swapping Stations (891 records)
    # -------------------------------------------------------------------------
    print("8. Processing Switch Delhi charging & battery swapping stations (891 records)...")
    district_centroids = {
        d_name: (geom.centroid.y, geom.centroid.x) for d_name, geom in delhi_dist_geoms.items()
    }

    switch_delhi_stations: List[Dict[str, Any]] = []
    seen_switch_sigs = set()
    switch_exact_duplicates = 0
    switch_raw_total = 0

    with open(RAW_DIR / "charging" / "Delhi_SwitchDelhi_charging_stations_20261019.csv", "r", encoding="utf-8") as f:
        for idx, row in enumerate(csv.DictReader(f), start=1):
            switch_raw_total += 1
            sig = tuple(row[k].strip() for k in sorted(row.keys()))
            if sig in seen_switch_sigs:
                switch_exact_duplicates += 1
                continue
            seen_switch_sigs.add(sig)

            stype_raw = row["charging_type"].strip()
            station_type = "Battery Swapping" if "swap" in stype_raw.lower() else "Charging"
            pin = row["postal_code"].strip()
            lat_s = row["latitude"].strip()
            lon_s = row["longitude"].strip()

            coord_valid = False
            lat_val, lon_val = 0.0, 0.0
            try:
                lat_val = float(lat_s)
                lon_val = float(lon_s)
                if 28.35 <= lat_val <= 28.95 and 76.80 <= lon_val <= 77.45:
                    coord_valid = True
            except ValueError:
                coord_valid = False

            if coord_valid:
                dl_dist = assign_delhi_district(lat_val, lon_val, delhi_dist_geoms) or DELHI_PIN_TO_DISTRICT.get(pin, "South")
                coord_status = "VERIFIED_COORDS"
            else:
                dl_dist = DELHI_PIN_TO_DISTRICT.get(pin, "West")
                # Deterministic small jitter around district centroid based on PIN + index so un-geocoded swap kiosks can be optionally previewed
                base_lat, base_lon = district_centroids[dl_dist]
                angle = (idx * 137.508) * (math.pi / 180.0)
                radius = 0.004 + (idx % 11) * 0.0018
                lat_val = round(base_lat + radius * math.sin(angle), 6)
                lon_val = round(base_lon + radius * math.cos(angle), 6)
                coord_status = "PIN_CENTROID_ESTIMATE"

            cap_raw = row["capacity"].strip()
            cap_kw = None
            m_kw = re.search(r"(\d+(?:\.\d+)?)", cap_raw)
            if m_kw:
                cap_kw = float(m_kw.group(1))

            try:
                n_chargers = int(float(row["no_of_chargers"].strip() or "1"))
            except ValueError:
                n_chargers = 1

            dockets_raw = row.get("if_battery_swap_station,_no._of_dockets", "").strip()
            try:
                n_dockets = int(float(dockets_raw)) if dockets_raw and dockets_raw.lower() != "nil" else None
            except ValueError:
                n_dockets = None

            ch_type = row["charger_type"].strip()
            if ch_type.lower() == "nil" or not ch_type:
                ch_type = "Battery Swap Dock" if station_type == "Battery Swapping" else "Standard AC"

            if station_type == "Battery Swapping":
                power_class = "Battery Swapping"
                dc_conn = 0
                ac_conn = 0
            elif cap_kw and cap_kw >= 25.0 or "CCS" in ch_type.upper() or "DC" in ch_type.upper():
                power_class = "DC Fast (>=15-25 kW)"
                dc_conn = n_chargers
                ac_conn = 0
            elif cap_kw and cap_kw >= 7.0 or "TYPE-2" in ch_type.upper() or "TYPE 2" in ch_type.upper():
                power_class = "AC Fast (7-22 kW)"
                dc_conn = 0
                ac_conn = n_chargers
            else:
                power_class = "AC Slow (<=3.3 kW)"
                dc_conn = 0
                ac_conn = n_chargers

            cost_raw = row["cost_per_unit"].strip()
            cost_num = None
            if cost_raw and cost_raw.lower() != "nil":
                try:
                    cost_num = float(cost_raw)
                except ValueError:
                    cost_num = None

            nearest_sub_m = round(min_dist_m_to_points(lat_val, lon_val, sub_lat_arr, sub_lon_arr), 0) if coord_status == "VERIFIED_COORDS" else None
            nearest_road_m = round(min_dist_m_to_points(lat_val, lon_val, road_lat_arr, road_lon_arr), 0) if coord_status == "VERIFIED_COORDS" else None

            raw_id = row["id"].strip()
            st_id = raw_id if (raw_id and raw_id.lower() != "nil") else f"SWD-{idx:04d}"

            switch_delhi_stations.append(
                {
                    "id": f"SD-{st_id}-{idx}",
                    "portal_id": raw_id if raw_id.lower() != "nil" else None,
                    "source": "SWITCH_DELHI",
                    "source_date": "2026-10-19",
                    "station_type": station_type,
                    "vendor": row["vendor"].strip() or "Unspecified Operator",
                    "name": f"{row['vendor'].strip()} — {row['address'].strip()[:38]}",
                    "address": row["address"].strip() if row["address"].strip().lower() != "nil" else f"PIN {pin}, New Delhi",
                    "postal_code": pin,
                    "district": dl_dist,
                    "portal_region": row["region"].strip() or None,
                    "latitude": round(lat_val, 6),
                    "longitude": round(lon_val, 6),
                    "coord_status": coord_status,
                    "no_of_chargers": n_chargers,
                    "total_connectors": n_chargers,
                    "dc_connectors": dc_conn,
                    "ac_connectors": ac_conn,
                    "swap_dockets": n_dockets,
                    "max_capacity_kw": cap_kw,
                    "total_capacity_kw": round(cap_kw * n_chargers, 2) if cap_kw else None,
                    "charger_type": ch_type,
                    "power_class": power_class,
                    "cost_per_unit": f"₹{cost_raw}/kWh" if cost_num is not None else "Not Disclosed",
                    "cost_per_unit_inr": cost_num,
                    "timing": row["timing"].strip() if row["timing"].strip().lower() != "nil" else "24x7 / Unspecified",
                    "payment_modes": row["payment_modes"].strip() if row["payment_modes"].strip().lower() != "nil" else "UPI / App",
                    "staff": row["staff"].strip() if row["staff"].strip().lower() != "nil" else "Unstaffed",
                    "nearest_substation_m": nearest_sub_m,
                    "nearest_highway_m": nearest_road_m,
                }
            )

    # Finalize BEE Delhi stations list with power_class and substation/highway proximity
    bee_delhi_list: List[Dict[str, Any]] = []
    for site in bee_delhi_sites.values():
        conn_list = sorted(site["connector_types"])
        max_kw = site["max_capacity_kw"]
        if site["dc_connectors"] > 0 or max_kw >= 25.0:
            pclass = "DC Fast (>=15-25 kW)"
        elif max_kw >= 7.0:
            pclass = "AC Fast (7-22 kW)"
        else:
            pclass = "AC Slow (<=3.3 kW)"
        lat_v, lon_v = site["latitude"], site["longitude"]
        bee_delhi_list.append(
            {
                "id": site["id"],
                "portal_id": site["id"],
                "source": "BEE",
                "source_date": "2025-10-26",
                "station_type": "Charging",
                "vendor": site["vendor"],
                "govt_private": site["govt_private"],
                "name": f"{site['vendor']} — {site['address'][:38]}",
                "address": site["address"],
                "postal_code": "",
                "district": site["district"],
                "latitude": lat_v,
                "longitude": lon_v,
                "coord_status": "VERIFIED_COORDS",
                "charger_rows_merged": site["charger_rows_merged"],
                "no_of_chargers": site["no_of_chargers"],
                "total_connectors": site["total_connectors"],
                "dc_connectors": site["dc_connectors"],
                "ac_connectors": site["ac_connectors"],
                "swap_dockets": None,
                "max_capacity_kw": max_kw,
                "total_capacity_kw": site["total_capacity_kw"],
                "charger_type": ", ".join(conn_list),
                "power_class": pclass,
                "cost_per_unit": "Tariff Not in BEE PDF (State LT: ₹4.50/kWh)",
                "cost_per_unit_inr": None,
                "timing": "Not in BEE PDF",
                "payment_modes": "CPO App / Bharat QR",
                "staff": site["govt_private"],
                "nearest_substation_m": round(min_dist_m_to_points(lat_v, lon_v, sub_lat_arr, sub_lon_arr), 0),
                "nearest_highway_m": round(min_dist_m_to_points(lat_v, lon_v, road_lat_arr, road_lon_arr), 0),
            }
        )

    for osm_st in osm_delhi_stations:
        lat_v, lon_v = osm_st["latitude"], osm_st["longitude"]
        osm_st["nearest_substation_m"] = round(min_dist_m_to_points(lat_v, lon_v, sub_lat_arr, sub_lon_arr), 0)
        osm_st["nearest_highway_m"] = round(min_dist_m_to_points(lat_v, lon_v, road_lat_arr, road_lon_arr), 0)

    # -------------------------------------------------------------------------
    # 9. Build National States Summary Table (36 States/UTs)
    # -------------------------------------------------------------------------
    print("9. Building National States Summary (36 States/UTs)...")
    national_states_list: List[Dict[str, Any]] = []

    for code in sorted(CANONICAL_STATES.keys(), key=lambda c: CANONICAL_STATES[c]["name"]):
        vahan = vahan_states[code]
        bee = bee_state_stats[code]
        omc = omc_by_code[code]
        fame2_omc = fame2_by_code[code]
        demo = demographics_by_code[code]
        tariff = STATE_EV_TARIFFS[code]

        unique_bee_stations = len(bee["unique_sites_set"])
        unique_bee_coords = len(bee["unique_coords_set"])
        total_connectors = bee["total_connectors"]
        dc_connectors = bee["dc_connectors"]
        ac_connectors = bee["ac_connectors"]
        total_ev = vahan["total_ev_active"]

        # MoPNG OMC operational ratio for this state
        omc_inst = omc["installed_total"]
        omc_oper = omc["operational_total"]
        omc_ratio = round(omc_oper / omc_inst, 4) if omc_inst > 0 else 1.0

        # Estimate operational BEE stations by applying state OMC commissioning ratio to OMC rows
        omc_share_in_bee = (bee["omc_rows"] / bee["raw_charger_rows"]) if bee["raw_charger_rows"] > 0 else 0.0
        est_operational_bee_stations = int(
            round(unique_bee_stations * ((1.0 - omc_share_in_bee) + omc_share_in_bee * omc_ratio))
        )

        pop_m = (demo["ncp_2025_population"] / 1_000_000.0) if demo["ncp_2025_population"] else None
        area_km2 = demo["area_sq_km"]

        national_states_list.append(
            {
                "state_code": code,
                "state_name": CANONICAL_STATES[code]["name"],
                "admin2_name": CANONICAL_STATES[code]["admin2"],
                # VAHAN Active EV Fleet (19 Oct 2026)
                "vahan_date": "2026-10-19",
                "total_ev_active": total_ev,
                "ev_2w": vahan["ev_2w"],
                "ev_3w": vahan["ev_3w"],
                "ev_4w_lmv_pv": vahan["ev_4w_lmv_pv"],
                "ev_bus": vahan["ev_bus"],
                "ev_goods": vahan["ev_goods"],
                "ev_other": vahan["ev_other"],
                "fuel_electric_bov": vahan["fuel_electric_bov"],
                "fuel_pure_ev": vahan["fuel_pure_ev"],
                "fuel_plugin_hybrid_ev": vahan["fuel_plugin_hybrid_ev"],
                "fuel_solar": vahan["fuel_solar"],
                "fuel_hydrogen": vahan["fuel_hydrogen"],
                "status_active_compliant": vahan["status_active_compliant"],
                "status_active_non_compliant": vahan["status_active_non_compliant"],
                "non_compliant_share_pct": round(100.0 * vahan["status_active_non_compliant"] / max(1, total_ev), 1),
                "vahan_note": (
                    "Telangana recently migrated from its separate state RTA portal to central VAHAN4; historical pre-migration fleet (~2.1L) is on state portal."
                    if code == "TG"
                    else None
                ),
                "subcategories": vahan["subcategories"],
                "yearwise_trend": vahan["yearwise_trend"],
                # BEE EVPCS Registry (26 Oct 2025) - kept strictly separate
                "bee_date": "2025-10-26",
                "bee_unique_stations": unique_bee_stations,
                "bee_unique_coords": unique_bee_coords,
                "bee_raw_charger_rows": bee["raw_charger_rows"],
                "bee_exact_duplicate_rows": bee["exact_duplicate_rows"],
                "bee_valid_bbox_rows": bee["valid_bbox_rows"],
                "bee_invalid_coord_rows": bee["invalid_coord_rows"],
                "bee_lat_eq_lon_rows": bee["lat_eq_lon_rows"],
                "bee_total_connectors": total_connectors,
                "bee_ac_connectors": ac_connectors,
                "bee_dc_connectors": dc_connectors,
                "bee_total_power_kw": round(bee["total_power_kw"], 1),
                "bee_govt_rows": bee["govt_rows"],
                "bee_private_rows": bee["private_rows"],
                "bee_omc_rows": bee["omc_rows"],
                "bee_raw_state_strings": sorted(bee["raw_state_variants"]),
                "bee_top_cpos": [
                    {"cpo": k, "rows": v} for k, v in bee["cpo_counter"].most_common(6)
                ],
                "bee_connector_breakdown": [
                    {"type": k, "connectors": v} for k, v in bee["connector_counter"].most_common(8)
                ],
                # PIB MoPNG OMC Registry (01 Mar 2026) - kept strictly separate
                "omc_date": "2026-03-01",
                "omc_installed_total": omc_inst,
                "omc_decommissioned": omc["decommissioned"],
                "omc_operational_total": omc_oper,
                "omc_operational_pct": round(100.0 * omc_ratio, 1),
                "omc_fy_trend": {
                    "FY20-21": omc["fy20_21"],
                    "FY21-22": omc["fy21_22"],
                    "FY22-23": omc["fy22_23"],
                    "FY23-24": omc["fy23_24"],
                    "FY24-25": omc["fy24_25"],
                    "FY25-26": omc["fy25_26"],
                },
                # PIB MHI FAME-II OMC Installed (01 Mar 2026) - kept strictly separate
                "fame2_date": "2026-03-01",
                "fame2_omc_installed": fame2_omc,
                # OpenStreetMap Crowdsourced (19 Oct 2026) - kept strictly separate
                "osm_date": "2026-10-19",
                "osm_charging_stations": osm_by_state.get(code, 0),
                # Demographics, Tariffs & SNA Context
                "area_sq_km": area_km2,
                "ncp_2025_population": demo["ncp_2025_population"],
                "gsdp_inr_crore": demo["gsdp_inr_crore"],
                "ev_tariff_fixed": tariff["fixed"],
                "ev_tariff_energy": tariff["energy"],
                "ev_tariff_lt_rs_kwh": tariff["lt_rs_kwh"],
                "ev_tariff_ht_rs_kwh": tariff["ht_rs_kwh"],
                "state_nodal_agency": sna_by_code.get(code, "Transport / Power Dept."),
                # Clearly Labelled Analytical Indicators
                "evs_per_bee_station": round(total_ev / unique_bee_stations, 1) if unique_bee_stations > 0 else None,
                "evs_per_bee_connector": round(total_ev / total_connectors, 1) if total_connectors > 0 else None,
                "ev_4w_per_dc_connector": round(vahan["ev_4w_lmv_pv"] / dc_connectors, 1) if dc_connectors > 0 else None,
                "bee_stations_per_100k_pop": round(unique_bee_stations / (pop_m * 10.0), 2) if pop_m else None,
                "bee_stations_per_1000_sq_km": round(unique_bee_stations / (area_km2 / 1000.0), 2) if area_km2 else None,
                "est_operational_bee_stations": est_operational_bee_stations,
            }
        )

    # -------------------------------------------------------------------------
    # 10. Process Delhi District EV Demand Crosswalk & WorldPop Integration
    # -------------------------------------------------------------------------
    print("10. Integrating Delhi RTO EV demand crosswalk & WorldPop 1km raster across 9 Delhi districts...")
    delhi_worldpop_2020 = compute_worldpop_for_polygons(delhi_dist_geoms)
    total_dl_wp = sum(delhi_worldpop_2020.values())
    # Scale 2020 WorldPop district totals proportionally to NCP 2025 Delhi population (22,300,000)
    delhi_pop_2025 = {
        d: int(round(pop * (22_300_000.0 / max(1.0, total_dl_wp))))
        for d, pop in delhi_worldpop_2020.items()
    }

    # Load Delhi 23 RTO rows
    rto_rows: List[Dict[str, Any]] = []
    with open(RAW_DIR / "vahan" / "VAHAN_Delhi_RTO_ev_summary_20261019.csv", "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rto_rows.append(
                {
                    "rto_code": f"DL-{row['rto_code'].strip()}",
                    "rto_num": int(row["rto_code"].strip()),
                    "rto_name": row["rto_name"].strip(),
                    "total_ev_active": int(row["total_ev_active"]),
                    "ev_2w": int(row["ev_2w"]),
                    "ev_3w": int(row["ev_3w"]),
                    "ev_4w_lmv_pv": int(row["ev_4w_lmv_pv"]),
                    "ev_bus": int(row["ev_bus_hpv_mpv"]),
                    "ev_goods": int(row["ev_goods"]),
                    "is_centralized_commercial_unit": int(row["rto_code"].strip()) in (51, 52, 53),
                    "is_fitness_center_only": int(row["total_ev_active"]) == 0,
                }
            )

    # Geographic RTO -> Census 2011 District Crosswalk for the 13 zonal registering RTOs (DL1-DL13)
    # Note: DL51 (Rajpur Road/VIU Burari), DL52 (Burari Taxi Unit), DL53 (Burari Auto Unit) are centralized
    # commercial registration units located in North/Central Delhi.
    RTO_TO_DISTRICT_MAP: Dict[int, str] = {
        1: "North",        # Mall Road - DL1
        2: "Central",      # I P Estate - DL2
        3: "South",        # South Delhi (Sheikh Sarai) - DL3
        4: "West",         # Janakpuri - DL4
        5: "North East",   # Loni Road - DL5
        6: "Central",      # Sarai Kale Khan - DL6 (serves Central/South-East ring)
        7: "East",         # Mayur Vihar - DL7
        8: "North West",   # Wazirpur - DL8
        9: "South West",   # Dwarka - DL9
        10: "West",        # Rajouri Garden - DL10
        11: "North West",  # Rohini - DL11
        12: "New Delhi",   # Vasant Vihar / New Delhi SW - DL12
        13: "East",        # Surajmal Vihar / Shahdara - DL13
    }

    dist_poi_counts: Counter = Counter(a["district"] for a in delhi_attractors)
    total_dl_pois = max(1, sum(dist_poi_counts.values()))

    # Initialize district aggregation dictionary
    delhi_districts_summary: Dict[str, Dict[str, Any]] = {}
    for d_name, geom in delhi_dist_geoms.items():
        # Approximate area in sq km using cosine latitude projection
        cos_lat = math.cos(math.radians(28.6139))
        area_km2 = round(geom.area * (111.32 ** 2) * cos_lat, 2)
        delhi_districts_summary[d_name] = {
            "district": d_name,
            "census_code": delhi_dist_records[d_name]["censuscode"],
            "area_sq_km": area_km2,
            "worldpop_2020": int(round(delhi_worldpop_2020[d_name])),
            "ncp_2025_population_est": delhi_pop_2025[d_name],
            "mapped_rtos": [],
            # Zonal RTO registrations (verified direct geographic RTOs DL1-DL13)
            "zonal_rto_ev_total": 0,
            "zonal_rto_2w": 0,
            "zonal_rto_3w": 0,
            "zonal_rto_4w": 0,
            "zonal_rto_bus": 0,
            "zonal_rto_goods": 0,
            # Redistributed commercial EVs from centralized Burari units (DL51, DL52, DL53 = 64,723 EVs)
            "redistributed_burari_commercial_ev": 0,
            # Total estimated active EV demand in district (Zonal RTO + Redistributed Commercial)
            "estimated_total_ev_demand": 0,
            "estimated_ev_2w": 0,
            "estimated_ev_3w": 0,
            "estimated_ev_4w": 0,
            "estimated_ev_bus": 0,
            "estimated_ev_goods": 0,
            # Charger counts by source (kept strictly separate)
            "switch_delhi_charging_stations": 0,
            "switch_delhi_swap_geocoded": 0,
            "switch_delhi_swap_pin_estimated": 0,
            "switch_delhi_total_stations": 0,
            "switch_delhi_charging_points": 0,
            "switch_delhi_dc_points": 0,
            "switch_delhi_ac_points": 0,
            "switch_delhi_swap_dockets": 0,
            "bee_stations": 0,
            "bee_charger_rows": 0,
            "bee_connectors": 0,
            "bee_dc_connectors": 0,
            "bee_ac_connectors": 0,
            "bee_total_kw": 0.0,
            "osm_stations": 0,
            # Contextual layers
            "substations_count": 0,
            "transformers_count": 0,
            "demand_attractors_count": dist_poi_counts.get(d_name, 0),
            "major_road_ways_count": district_road_counts.get(d_name, 0),
        }

    burari_totals = {"total": 0, "2w": 0, "3w": 0, "4w": 0, "bus": 0, "goods": 0}
    for r in rto_rows:
        rnum = r["rto_num"]
        if rnum in RTO_TO_DISTRICT_MAP:
            d_target = RTO_TO_DISTRICT_MAP[rnum]
            ds = delhi_districts_summary[d_target]
            ds["mapped_rtos"].append(r["rto_name"])
            ds["zonal_rto_ev_total"] += r["total_ev_active"]
            ds["zonal_rto_2w"] += r["ev_2w"]
            ds["zonal_rto_3w"] += r["ev_3w"]
            ds["zonal_rto_4w"] += r["ev_4w_lmv_pv"]
            ds["zonal_rto_bus"] += r["ev_bus"]
            ds["zonal_rto_goods"] += r["ev_goods"]
        elif rnum in (51, 52, 53):
            burari_totals["total"] += r["total_ev_active"]
            burari_totals["2w"] += r["ev_2w"]
            burari_totals["3w"] += r["ev_3w"]
            burari_totals["4w"] += r["ev_4w_lmv_pv"]
            burari_totals["bus"] += r["ev_bus"]
            burari_totals["goods"] += r["ev_goods"]

    # Distribute centralized Burari commercial fleet (64,723 EVs) using 50% POI weight + 50% population weight
    for d_name, ds in delhi_districts_summary.items():
        poi_w = ds["demand_attractors_count"] / total_dl_pois
        pop_w = ds["ncp_2025_population_est"] / 22_300_000.0
        w = 0.5 * poi_w + 0.5 * pop_w
        c_3w = int(round(burari_totals["3w"] * w))
        c_4w = int(round(burari_totals["4w"] * w))
        c_bus = int(round(burari_totals["bus"] * w))
        c_goods = int(round(burari_totals["goods"] * w))
        c_tot = c_3w + c_4w + c_bus + c_goods
        ds["redistributed_burari_commercial_ev"] = c_tot
        ds["estimated_ev_2w"] = ds["zonal_rto_2w"]
        ds["estimated_ev_3w"] = ds["zonal_rto_3w"] + c_3w
        ds["estimated_ev_4w"] = ds["zonal_rto_4w"] + c_4w
        ds["estimated_ev_bus"] = ds["zonal_rto_bus"] + c_bus
        ds["estimated_ev_goods"] = ds["zonal_rto_goods"] + c_goods
        ds["estimated_total_ev_demand"] = ds["zonal_rto_ev_total"] + c_tot

    # Tally Switch Delhi, BEE, OSM, and Power Grid nodes by Delhi district
    for st in switch_delhi_stations:
        d_name = st["district"]
        if d_name in delhi_districts_summary:
            ds = delhi_districts_summary[d_name]
            ds["switch_delhi_total_stations"] += 1
            if st["station_type"] == "Charging":
                ds["switch_delhi_charging_stations"] += 1
                ds["switch_delhi_charging_points"] += st["no_of_chargers"]
                ds["switch_delhi_dc_points"] += st["dc_connectors"]
                ds["switch_delhi_ac_points"] += st["ac_connectors"]
            else:
                if st["coord_status"] == "VERIFIED_COORDS":
                    ds["switch_delhi_swap_geocoded"] += 1
                else:
                    ds["switch_delhi_swap_pin_estimated"] += 1
                ds["switch_delhi_swap_dockets"] += st["swap_dockets"] or st["no_of_chargers"]

    for st in bee_delhi_list:
        d_name = st["district"]
        if d_name in delhi_districts_summary:
            ds = delhi_districts_summary[d_name]
            ds["bee_stations"] += 1
            ds["bee_charger_rows"] += st["charger_rows_merged"]
            ds["bee_connectors"] += st["total_connectors"]
            ds["bee_dc_connectors"] += st["dc_connectors"]
            ds["bee_ac_connectors"] += st["ac_connectors"]
            ds["bee_total_kw"] = round(ds["bee_total_kw"] + (st["total_capacity_kw"] or 0.0), 1)

    for st in osm_delhi_stations:
        d_name = st["district"]
        if d_name in delhi_districts_summary:
            delhi_districts_summary[d_name]["osm_stations"] += 1

    for pn in delhi_power_nodes:
        d_name = pn["district"]
        if d_name in delhi_districts_summary:
            if pn["power_type"] == "substation":
                delhi_districts_summary[d_name]["substations_count"] += 1
            elif pn["power_type"] == "transformer":
                delhi_districts_summary[d_name]["transformers_count"] += 1

    # Build Delhi Districts GeoJSON with full metrics
    delhi_dist_features: List[Dict[str, Any]] = []
    for d_name, geom in delhi_dist_geoms.items():
        ds = delhi_districts_summary[d_name]
        centroid = geom.centroid
        ds["centroid_lat"] = round(centroid.y, 5)
        ds["centroid_lon"] = round(centroid.x, 5)
        ds["evs_per_switch_delhi_point"] = round(
            ds["estimated_total_ev_demand"] / max(1, ds["switch_delhi_charging_points"]), 1
        )
        ds["evs_per_bee_connector"] = round(
            ds["estimated_total_ev_demand"] / max(1, ds["bee_connectors"]), 1
        )
        delhi_dist_features.append(
            {
                "type": "Feature",
                "properties": ds,
                "geometry": mapping(geom.simplify(0.0008, preserve_topology=True)),
            }
        )

    delhi_districts_geojson = {"type": "FeatureCollection", "features": delhi_dist_features}

    # -------------------------------------------------------------------------
    # 11. Build Stage 4 Spatial Planning Grid for NCT of Delhi (2.0 km x 2.0 km cells)
    # -------------------------------------------------------------------------
    print("11. Generating 2.0km x 2.0km spatial planning grid across NCT of Delhi for Stage 4 coverage analysis...")
    # Coordinate arrays for distance queries in Stage 4
    sd_chg_lats = np.array([s["latitude"] for s in switch_delhi_stations if s["station_type"] == "Charging" and s["coord_status"] == "VERIFIED_COORDS"])
    sd_chg_lons = np.array([s["longitude"] for s in switch_delhi_stations if s["station_type"] == "Charging" and s["coord_status"] == "VERIFIED_COORDS"])

    sd_swap_lats = np.array([s["latitude"] for s in switch_delhi_stations if s["station_type"] == "Battery Swapping" and s["coord_status"] == "VERIFIED_COORDS"])
    sd_swap_lons = np.array([s["longitude"] for s in switch_delhi_stations if s["station_type"] == "Battery Swapping" and s["coord_status"] == "VERIFIED_COORDS"])

    bee_dl_lats = np.array([s["latitude"] for s in bee_delhi_list])
    bee_dl_lons = np.array([s["longitude"] for s in bee_delhi_list])

    dc_fast_lats = np.array(
        [s["latitude"] for s in switch_delhi_stations if s["dc_connectors"] > 0 and s["coord_status"] == "VERIFIED_COORDS"]
        + [s["latitude"] for s in bee_delhi_list if s["dc_connectors"] > 0]
    )
    dc_fast_lons = np.array(
        [s["longitude"] for s in switch_delhi_stations if s["dc_connectors"] > 0 and s["coord_status"] == "VERIFIED_COORDS"]
        + [s["longitude"] for s in bee_delhi_list if s["dc_connectors"] > 0]
    )

    any_off_lats = np.concatenate([sd_chg_lats, bee_dl_lats])
    any_off_lons = np.concatenate([sd_chg_lons, bee_dl_lons])

    # 2.0 km grid step: dlat ~ 0.018 deg, dlon ~ 0.0205 deg at 28.6N
    dlat, dlon = 0.018, 0.0205
    lat_edges = np.arange(28.40, 28.89, dlat)
    lon_edges = np.arange(76.83, 77.35, dlon)

    grid_cells: List[Dict[str, Any]] = []
    cell_polygons: Dict[str, Any] = {}

    for r_idx, lat_s in enumerate(lat_edges):
        for c_idx, lon_w in enumerate(lon_edges):
            lat_n = lat_s + dlat
            lon_e = lon_w + dlon
            clat = round((lat_s + lat_n) / 2.0, 5)
            clon = round((lon_w + lon_e) / 2.0, 5)
            d_name = assign_delhi_district(clat, clon, delhi_dist_geoms)
            if not d_name:
                continue
            # Ensure center point is strictly inside one of the 9 Delhi district polygons
            if not any(g.contains(Point(clon, clat)) for g in delhi_dist_geoms.values()):
                continue
            cid = f"DL-GRID-{r_idx:02d}-{c_idx:02d}"
            c_poly = box(lon_w, lat_s, lon_e, lat_n)
            cell_polygons[cid] = c_poly
            grid_cells.append(
                {
                    "cell_id": cid,
                    "district": d_name,
                    "center_lat": clat,
                    "center_lon": clon,
                    "bounds": [[round(float(lat_s), 5), round(float(lon_w), 5)], [round(float(lat_n), 5), round(float(lon_e), 5)]],
                    "worldpop_2025_est": 0,
                    "poi_count": 0,
                    "transit_hub_count": 0,
                    "commercial_poi_count": 0,
                    "road_segments_count": 0,
                    "substations_in_cell": 0,
                    "nearest_substation_m": round(min_dist_m_to_points(clat, clon, sub_lat_arr, sub_lon_arr), 0),
                    "dist_switch_charging_km": round(min_dist_m_to_points(clat, clon, sd_chg_lats, sd_chg_lons) / 1000.0, 2),
                    "dist_switch_swap_km": round(min_dist_m_to_points(clat, clon, sd_swap_lats, sd_swap_lons) / 1000.0, 2),
                    "dist_bee_station_km": round(min_dist_m_to_points(clat, clon, bee_dl_lats, bee_dl_lons) / 1000.0, 2),
                    "dist_dc_fast_km": round(min_dist_m_to_points(clat, clon, dc_fast_lats, dc_fast_lons) / 1000.0, 2),
                    "dist_any_official_km": round(min_dist_m_to_points(clat, clon, any_off_lats, any_off_lons) / 1000.0, 2),
                    "switch_stations_in_cell": 0,
                    "switch_points_in_cell": 0,
                    "bee_stations_in_cell": 0,
                    "bee_connectors_in_cell": 0,
                    "dc_connectors_in_cell": 0,
                }
            )

    cell_wp = compute_worldpop_for_polygons(cell_polygons)
    wp_scale = 22_300_000.0 / max(1.0, sum(cell_wp.values()))

    # Index cells by (r_idx, c_idx) for O(1) point assignment
    cell_by_rc: Dict[Tuple[int, int], Dict[str, Any]] = {}
    for cell in grid_cells:
        parts = cell["cell_id"].split("-")
        rc = (int(parts[2]), int(parts[3]))
        cell_by_rc[rc] = cell
        cell["worldpop_2025_est"] = int(round(cell_wp.get(cell["cell_id"], 0.0) * wp_scale))

    def get_cell(lat: float, lon: float) -> Optional[Dict[str, Any]]:
        ri = int((lat - 28.40) / dlat)
        ci = int((lon - 76.83) / dlon)
        return cell_by_rc.get((ri, ci))

    for a in delhi_attractors:
        c = get_cell(a["latitude"], a["longitude"])
        if c:
            c["poi_count"] += 1
            if a["category"] in ("station", "bus_station", "parking", "fuel"):
                c["transit_hub_count"] += 1
            else:
                c["commercial_poi_count"] += 1

    for rlat, rlon in zip(road_center_lats, road_center_lons):
        c = get_cell(rlat, rlon)
        if c:
            c["road_segments_count"] += 1

    for pn in delhi_power_nodes:
        if pn["power_type"] in ("substation", "transformer"):
            c = get_cell(pn["latitude"], pn["longitude"])
            if c:
                c["substations_in_cell"] += 1

    for st in switch_delhi_stations:
        if st["coord_status"] == "VERIFIED_COORDS":
            c = get_cell(st["latitude"], st["longitude"])
            if c:
                c["switch_stations_in_cell"] += 1
                c["switch_points_in_cell"] += st["no_of_chargers"]
                c["dc_connectors_in_cell"] += st["dc_connectors"]

    for st in bee_delhi_list:
        c = get_cell(st["latitude"], st["longitude"])
        if c:
            c["bee_stations_in_cell"] += 1
            c["bee_connectors_in_cell"] += st["total_connectors"]
            c["dc_connectors_in_cell"] += st["dc_connectors"]

    # Compute transparent Demand Index (0-100) for each 2km x 2km grid cell
    max_cell_pop = max((c["worldpop_2025_est"] for c in grid_cells), default=1)
    max_cell_poi = max((c["poi_count"] for c in grid_cells), default=1)
    max_cell_road = max((c["road_segments_count"] for c in grid_cells), default=1)

    for c in grid_cells:
        pop_norm = min(1.0, c["worldpop_2025_est"] / max(1, max_cell_pop * 0.65))
        poi_norm = min(1.0, c["poi_count"] / max(1, max_cell_poi * 0.50))
        road_norm = min(1.0, c["road_segments_count"] / max(1, max_cell_road * 0.50))
        c["demand_score"] = round(100.0 * (0.45 * pop_norm + 0.35 * poi_norm + 0.20 * road_norm), 1)

    # -------------------------------------------------------------------------
    # 12. Format National District Hub Clusters for Fast Map Rendering
    # -------------------------------------------------------------------------
    national_clusters_list: List[Dict[str, Any]] = []
    for (code, dist_name), hc in hub_clusters.items():
        n_rows = hc["charger_rows"]
        top_cpo, top_cpo_cnt = hc["cpos"].most_common(1)[0]
        national_clusters_list.append(
            {
                "id": f"HUB-{code}-{len(national_clusters_list)+1:04d}",
                "state_code": code,
                "state_name": hc["state_name"],
                "district": dist_name,
                "latitude": round(hc["lat_sum"] / n_rows, 4),
                "longitude": round(hc["lon_sum"] / n_rows, 4),
                "unique_stations": len(hc["sites"]),
                "charger_rows": n_rows,
                "total_connectors": hc["connectors"],
                "dc_connectors": hc["dc_connectors"],
                "ac_connectors": hc["ac_connectors"],
                "total_power_kw": round(hc["total_kw"], 1),
                "top_cpo": top_cpo,
                "top_cpo_rows": top_cpo_cnt,
            }
        )
    national_clusters_list.sort(key=lambda x: x["unique_stations"], reverse=True)

    # -------------------------------------------------------------------------
    # 13. Save All Outputs to `data/processed/` and `public/data/`
    # -------------------------------------------------------------------------
    print("12. Writing processed outputs to data/processed/ and public/data/...")

    national_bundle = {
        "metadata": {
            "generated_at": "2026-10-19",
            "sources": {
                "vahan": {
                    "organisation": "Ministry of Road Transport & Highways (MoRTH) — VAHAN4 Public Dashboard",
                    "reference_date": "2026-10-19",
                    "total_active_ev": 10689490,
                    "active_compliant": 7869058,
                    "active_non_compliant": 2820432,
                    "fuel_labels_included": ["ELECTRIC(BOV)", "PURE EV", "PLUG-IN HYBRID EV", "SOLAR", "FUEL CELL HYDROGEN"],
                    "fuel_labels_excluded": ["STRONG HYBRID EV", "PETROL/HYBRID", "DIESEL/HYBRID"],
                },
                "bee": {
                    "organisation": "Bureau of Energy Efficiency (BEE), Ministry of Power",
                    "dataset": "EV_PCS_Data_29277_20251026.pdf",
                    "reference_date": "2025-10-26",
                    "published_date": "2026-02-17",
                    "filename_station_count": 29277,
                    "deduplicated_site_count": sum(s["bee_unique_stations"] for s in national_states_list),
                    "unique_coord_pairs": sum(s["bee_unique_coords"] for s in national_states_list),
                    "raw_charger_rows": 39641,
                    "exact_duplicate_rows": sum(s["bee_exact_duplicate_rows"] for s in national_states_list),
                    "total_connectors": 44066,
                    "valid_bbox_rows": 39522,
                    "invalid_coord_rows": 119,
                    "lat_eq_lon_iocl_rows": 104,
                },
                "pib_omc": {
                    "organisation": "Ministry of Heavy Industries / MoPNG (Lok Sabha / Rajya Sabha PIB PRID 2246042)",
                    "reference_date": "2026-03-01",
                    "published_date": "2026-03-27",
                    "installed_total": 27737,
                    "decommissioned_total": 21,
                    "operational_total": 22753,
                    "operational_pct": 82.03,
                },
                "pib_fame2": {
                    "organisation": "Ministry of Heavy Industries (Lok Sabha PIB PRID 2246045)",
                    "reference_date": "2026-03-01",
                    "published_date": "2026-03-27",
                    "total_sanctioned": 9332,
                    "total_operational": 6645,
                    "omc_installed": 8932,
                    "pse_installed": 227,
                    "pse_entities": fame2_pse_entities,
                },
                "osm": {
                    "organisation": "OpenStreetMap Contributors (ODbL 1.0)",
                    "reference_date": "2026-10-19",
                    "mapped_features": 725,
                },
            },
            "national_vahan_overview": vahan_national_overview,
        },
        "states": national_states_list,
        "district_hub_clusters": national_clusters_list,
    }

    delhi_pilot_bundle = {
        "metadata": {
            "pilot_geography": "NCT of Delhi",
            "generated_at": "2026-10-19",
            "niti_iemi_2025_rank": 1,
            "niti_iemi_2025_score": 77,
            "area_sq_km": 1484.0,
            "ncp_2025_population": 22300000,
            "vahan_active_ev_total": 549153,
            "vahan_zonal_rto_ev_total": 484430,
            "vahan_burari_commercial_ev_total": 64723,
            "sources": {
                "switch_delhi": {
                    "url": "https://ev.delhi.gov.in/charging-station",
                    "reference_date": "2026-10-19",
                    "raw_records": switch_raw_total,
                    "exact_duplicates_removed": switch_exact_duplicates,
                    "deduplicated_stations": len(switch_delhi_stations),
                    "charging_stations": sum(1 for s in switch_delhi_stations if s["station_type"] == "Charging"),
                    "battery_swapping_stations": sum(1 for s in switch_delhi_stations if s["station_type"] == "Battery Swapping"),
                    "verified_coord_stations": sum(1 for s in switch_delhi_stations if s["coord_status"] == "VERIFIED_COORDS"),
                    "pin_centroid_estimated_swap_stations": sum(1 for s in switch_delhi_stations if s["coord_status"] == "PIN_CENTROID_ESTIMATE"),
                    "total_charging_points": sum(s["no_of_chargers"] for s in switch_delhi_stations),
                },
                "bee_delhi": {
                    "url": "https://beeindia.gov.in/WriteReadData/RTF1984/EV_PCS_Data_29277.pdf",
                    "reference_date": "2025-10-26",
                    "raw_charger_rows_in_delhi": 3475,
                    "deduplicated_stations": len(bee_delhi_list),
                    "total_connectors": sum(s["total_connectors"] for s in bee_delhi_list),
                    "dc_connectors": sum(s["dc_connectors"] for s in bee_delhi_list),
                    "ac_connectors": sum(s["ac_connectors"] for s in bee_delhi_list),
                    "total_power_kw": round(sum(s["total_capacity_kw"] or 0.0 for s in bee_delhi_list), 1),
                },
                "osm_delhi": {
                    "reference_date": "2026-10-19",
                    "mapped_stations": len(osm_delhi_stations),
                },
                "context_layers": {
                    "power_nodes_total": len(delhi_power_nodes),
                    "substations": sum(1 for p in delhi_power_nodes if p["power_type"] == "substation"),
                    "transformers": sum(1 for p in delhi_power_nodes if p["power_type"] == "transformer"),
                    "plants": sum(1 for p in delhi_power_nodes if p["power_type"] == "plant"),
                    "demand_attractors": len(delhi_attractors),
                    "major_road_ways_raw": 8087,
                    "major_road_polylines_rendered": len(road_features),
                },
            },
        },
        "rto_summary": rto_rows,
        "districts_summary": list(delhi_districts_summary.values()),
        "stations": {
            "switch_delhi": switch_delhi_stations,
            "bee": bee_delhi_list,
            "osm": osm_delhi_stations,
        },
        "grid_cells_2km": grid_cells,
        "overlays": {
            "power_nodes": delhi_power_nodes,
            "demand_attractors": delhi_attractors,
        },
    }

    delhi_roads_geojson = {"type": "FeatureCollection", "features": road_features}

    outputs = [
        ("national_overview.json", national_bundle),
        ("india_states.geojson", state_geojson),
        ("delhi_pilot.json", delhi_pilot_bundle),
        ("delhi_districts.geojson", delhi_districts_geojson),
        ("delhi_major_roads.geojson", delhi_roads_geojson),
    ]

    for fname, data_obj in outputs:
        for target_dir in (PROCESSED_DIR, PUBLIC_DATA_DIR):
            out_path = target_dir / fname
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(data_obj, f, ensure_ascii=False, separators=(",", ":"))
        size_kb = (PROCESSED_DIR / fname).stat().st_size / 1024.0
        print(f"   Saved {fname} ({size_kb:.1f} KB)")

    # Also write a clean flat CSV of the 36-state merged summary to `data/processed/national_states_summary.csv`
    csv_cols = [
        "state_code", "state_name", "total_ev_active", "ev_2w", "ev_3w", "ev_4w_lmv_pv", "ev_bus", "ev_goods",
        "status_active_compliant", "status_active_non_compliant",
        "bee_unique_stations", "bee_raw_charger_rows", "bee_total_connectors", "bee_dc_connectors", "bee_ac_connectors", "bee_total_power_kw",
        "omc_installed_total", "omc_operational_total", "omc_operational_pct",
        "fame2_omc_installed", "osm_charging_stations",
        "ncp_2025_population", "area_sq_km", "gsdp_inr_crore", "ev_tariff_lt_rs_kwh",
        "evs_per_bee_station", "evs_per_bee_connector", "bee_stations_per_100k_pop",
    ]
    with open(PROCESSED_DIR / "national_states_summary.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=csv_cols, extrasaction="ignore")
        writer.writeheader()
        for st_row in national_states_list:
            writer.writerow(st_row)

    print("Stage 1 Data Integration completed successfully!")


if __name__ == "__main__":
    main()
