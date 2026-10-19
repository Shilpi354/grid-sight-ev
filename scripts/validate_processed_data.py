#!/usr/bin/env python3
"""
Automated Schema & Data Invariant Test Suite for EV Infra Map India.
Verifies that Stage 1 processed outputs in `data/processed/` and `public/data/`
match exact official baselines, preserve source separation, and contain zero NaN/null crashes.
"""

import json
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
PUBLIC_DATA_DIR = ROOT_DIR / "public" / "data"


def assert_true(cond: bool, msg: str) -> None:
    if not cond:
        print(f"[FAIL] {msg}", file=sys.stderr)
        sys.exit(1)
    print(f"[PASS] {msg}")


def main() -> None:
    required_files = [
        "national_overview.json",
        "india_states.geojson",
        "delhi_pilot.json",
        "delhi_districts.geojson",
        "delhi_major_roads.geojson",
    ]
    for fname in required_files:
        p1 = PROCESSED_DIR / fname
        p2 = PUBLIC_DATA_DIR / fname
        assert_true(p1.exists() and p1.stat().st_size > 1000, f"data/processed/{fname} exists and is non-empty")
        assert_true(p2.exists() and p2.stat().st_size > 1000, f"public/data/{fname} exists and is non-empty")

    with open(PROCESSED_DIR / "national_overview.json", "r", encoding="utf-8") as f:
        nat = json.load(f)

    states = nat["states"]
    assert_true(len(states) == 36, f"National states count == 36 (got {len(states)})")

    total_vahan_ev = sum(s["total_ev_active"] for s in states)
    assert_true(total_vahan_ev == 10689490, f"VAHAN total active EV across 36 states == 10,689,490 (got {total_vahan_ev})")

    total_bee_rows = sum(s["bee_raw_charger_rows"] for s in states)
    assert_true(total_bee_rows == 39641, f"BEE raw charger rows across 36 states == 39,641 (got {total_bee_rows})")

    total_bee_connectors = sum(s["bee_total_connectors"] for s in states)
    assert_true(total_bee_connectors == 44066, f"BEE total connectors across 36 states == 44,066 (got {total_bee_connectors})")

    total_omc_installed = sum(s["omc_installed_total"] for s in states)
    total_omc_operational = sum(s["omc_operational_total"] for s in states)
    assert_true(total_omc_installed == 27737, f"PIB OMC installed total == 27,737 (got {total_omc_installed})")
    assert_true(total_omc_operational == 22753, f"PIB OMC operational total == 22,753 (got {total_omc_operational})")

    total_fame2_omc = sum(s["fame2_omc_installed"] for s in states)
    assert_true(total_fame2_omc == 8932, f"PIB FAME-II OMC installed total == 8,932 (got {total_fame2_omc})")

    with open(PROCESSED_DIR / "delhi_pilot.json", "r", encoding="utf-8") as f:
        dl = json.load(f)

    assert_true(len(dl["districts_summary"]) == 9, f"Delhi districts count == 9 (got {len(dl['districts_summary'])})")
    assert_true(len(dl["rto_summary"]) == 23, f"Delhi VAHAN RTO count == 23 (got {len(dl['rto_summary'])})")
    dl_rto_ev = sum(r["total_ev_active"] for r in dl["rto_summary"])
    assert_true(dl_rto_ev == 549153, f"Delhi VAHAN RTO sum == 549,153 (got {dl_rto_ev})")

    sd_stations = dl["stations"]["switch_delhi"]
    bee_dl_stations = dl["stations"]["bee"]
    osm_dl_stations = dl["stations"]["osm"]
    assert_true(len(sd_stations) == 876, f"Deduplicated Switch Delhi stations == 876 from 891 raw (got {len(sd_stations)})")
    assert_true(len(bee_dl_stations) > 1800, f"Deduplicated BEE Delhi stations > 1,800 (got {len(bee_dl_stations)})")
    assert_true(len(osm_dl_stations) > 150, f"OSM Delhi stations > 150 (got {len(osm_dl_stations)})")
    assert_true(len(dl["grid_cells_2km"]) > 250, f"Delhi 2km planning grid cells > 250 (got {len(dl['grid_cells_2km'])})")

    print("\nAll Stage 1 data integration & schema validation assertions PASSED!")


if __name__ == "__main__":
    main()
