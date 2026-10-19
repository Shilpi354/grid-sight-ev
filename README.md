# GridSight EV — Mapping India's EV Charging Infrastructure

**Platform:** GridSight EV — Decision support and spatial intelligence platform for electric vehicle charging infrastructure.  
**Scope:** Delhi EV Charging Infrastructure Map + Explainable Coverage & Future Capacity Planner + 36 States/UTs National Reference Datasets.

---

## 1. Quick Start & Setup Commands

### Prerequisites
- **Node.js** `>= 18.x` (tested on `v22.17.1`) and **npm** `>= 9.x`
- **Python** `>= 3.10` with `pymupdf`, `openpyxl`, `pillow`, `numpy`, `pyshp`, and `shapely`

### Commands

```bash
# 1. Install frontend dependencies
npm install

# 2. (Optional) Re-run the Stage 1 reproducible data-integration pipeline from data/raw/
npm run process-data

# 3. Run the automated data & schema validation test suite
npm test

# 4. Run TypeScript strict type checking and production bundle build
npm run typecheck
npm run build

# 5. Start the interactive development server (http://localhost:5173)
npm run dev
```

---

## 2. System Architecture

To ensure fast, deterministic performance across CSV, PDF-extracted, Shapefile, GeoJSON, and GeoTIFF raster datasets without requiring an external database server, the project is structured into two decoupled layers:

### Layer 1: Reproducible Python Data-Integration Pipeline (`scripts/process_data.py`)
- Reads original, unmodified datasets from `data/raw/` and writes cleaned, schema-validated JSON and simplified GeoJSON bundles to both `data/processed/` and `public/data/`.
- **Unit & Duplicate Resolution:** Distinguishes **Charging Stations (Sites)**, **Charger Rows (EVSE)**, **Connectors (Nozzles)**, and **Battery Swap Dockets**. In `BEE_EV_PCS_Data_29277_20251026.pdf` (`39,641` rows), `8,428` exact duplicate rows represent multi-unit chargers at the same location; clustering by `(CPO, Location, round(Lat,4), round(Lon,4))` recovers **29,371 unique sites** (`29,117` unique coordinate pairs) and **44,066 total connectors**.
- **Spatial Point-in-Polygon Standardization:** Assigns geocoded chargers to canonical State (`Admin2.shp`, 36 polygons) and District (`2011_Dist.shp`, 9 Delhi district polygons) boundaries using `shapely` spatial containment, bypassing the `46` raw state string variants and `1,288` district spelling variants in BEE.
- **WorldPop 1km GeoTIFF Raster Integration:** Integrates pixel values from `WorldPop_ind_ppp_2020_1km_Aggregated.tif` inside each of Delhi's 9 district polygons and across **375 spatial grid cells (`2.0 km × 2.0 km`)**, scaled to the National Commission on Population (NCP) 2025 Delhi projection (`22.30 million`).

### Layer 2: Interactive Geospatial Frontend (`src/`)
- Built with **React 18 + Vite + TypeScript** and **Leaflet 1.9 + React-Leaflet 4.2**.
- **`src/types/data.ts`**: Strict TypeScript interfaces and runtime schema validators (`validateNationalBundle`, `validateDelhiBundle`).
- **`src/utils/planningEngine.ts`**: Pure, decoupled coverage & future charger requirement calculation engine (`evaluateDelhiGridCoverage`, `computeDelhiDistrictFutureRequirements`, `computeNationalStateFutureRequirements`).
- **`src/components/NationalOverviewView.tsx` (Stage 2)**: 36-State interactive choropleth & 400+ district hub cluster map, vehicle category filters (`2W`, `3W`, `4W/LMV`, `Bus`, `Goods`), strictly separated infrastructure source selector (`BEE`, `PIB OMC`, `PIB FAME-II`, `OSM`), state deep-dive inspector, and comparative ranking charts.
- **`src/components/DelhiPilotView.tsx` (Stage 3)**: High-resolution NCT of Delhi map visibly distinguishing EV Charging vs. Battery Swapping stations, operator/power/connector filters, toggleable overlays (`Major Roads`, `3,534 Demand Attractors`, `576 Power Substations/Transformers`), RTO-to-District demand crosswalk toggle, and a **Verified Facts vs. Analytical Estimates vs. Unavailable Information** station inspector.
- **`src/components/CoveragePlanningView.tsx` (Stage 4)**: Interactive `2.0 km × 2.0 km` grid coverage evaluator with configurable distance rules (`0.5 km` to `5.0 km`, including Delhi EV Policy's `3.0 km` target), underserved priority cell identification, and **Low / Baseline / High 2030 EV growth scenarios**.
- **`src/components/DataAuditView.tsx`**: Complete source reconciliation matrix, validation summary, and documented data gaps.

---

## 3. Dataset Inventory & Strict Source Separation

All raw files are preserved unchanged in `data/raw/` and catalogued in [`data/source_manifest.csv`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/source_manifest.csv):

| Source ID | Dataset & Local Path | Reference Date | Verified Record Count & Scope |
| :--- | :--- | :--- | :--- |
| **SRC-01** | `data/raw/charging/BEE_EV_PCS_Data_29277_20251026.pdf` & `_extracted.csv` | 26 Oct 2025 | **39,641 charger rows** (`29,277` filename stations / `29,371` unique sites / `44,066` connectors) across all 36 States/UTs |
| **SRC-02** | `data/raw/charging/PIB_PRID_2246042_OMC_Statewise_EVPCS_20260301.csv` | 01 Mar 2026 | **27,737 installed**, **21 decommissioned**, **22,753 operational (82.03%)** OMC stations across 36 States/UTs |
| **SRC-03** | `data/raw/charging/PIB_PRID_2246045_FAMEII_Statewise_EVPCS_20260301.csv` | 01 Mar 2026 | **8,932 FAME-II OMC installed** + **227 PSE installed** (`6,645` operational of `9,332` sanctioned nationally) |
| **SRC-04** | `data/raw/charging/Delhi_SwitchDelhi_charging_stations_20261019.csv` | 19 Oct 2026 | **891 raw records** (`876` unique: `573` EV Charging + `303` Battery Swapping; `6,841` charging points) in NCT of Delhi |
| **SRC-05** | `data/raw/charging/OSM_India_charging_stations_20261019.csv` | 19 Oct 2026 | **725 mapped features** across India (`179` inside NCT of Delhi) |
| **SRC-06** | `data/raw/vahan/VAHAN_state_ev_summary_20261019.csv` & companions | 19 Oct 2026 | **10,689,490 active EVs** across 36 States/UTs + **23 Delhi RTOs** (`549,153` active EVs in Delhi) |
| **SRC-07** | `data/raw/boundaries/Admin2.shp` & `2011_Dist.shp` | 2011 / 2020 | **36 State/UT polygons** & **641 District polygons** (`9` in NCT of Delhi) — DataMeet (CC BY 4.0) |
| **SRC-08** | `data/raw/roads/OSM_Delhi_major_roads_20261019.json` & `.csv` | 19 Oct 2026 | **8,087 major highway ways** (`motorway`, `trunk`, `primary`, `secondary`) in Delhi NCR |
| **SRC-09** | `data/raw/demographics/WorldPop_ind_ppp_2020_1km_Aggregated.tif` & `NITI_IEMI_2025_State_Population_GSDP.csv` | 2020 / 2025 | National 1km population raster (CC BY 4.0) + NCP 2025 state population, area & MoSPI GSDP |
| **SRC-10** | `data/raw/electricity/BEE_State_EV_Tariff_Annexure_A.pdf` & `OSM_Delhi_power_infrastructure_20261019.csv` | 2025 / 2026 | 36-State LT/HT EV tariffs + **576 mapped power grid features** in Delhi (`341` substations, `194` transformers, `41` plants) |
| **SRC-11** | `data/raw/context/NITI_Aayog_IEMI_2025.pdf`, `BEE_State_Nodal_Agencies_Annexure_B.xlsx`, `OSM_Delhi_demand_attractors_20261019.csv` | 2025 / 2026 | NITI IEMI 2025 report, 27 State Nodal Agencies, and **3,534 geocoded POIs** across 12 categories in Delhi |

---

## 4. Key Limitations & Engineering Guardrails

1. **No Conflation of Incompatible Charger Counts:** BEE (`29,277` stations), MoPNG OMC (`22,753` operational / `27,737` installed), MHI FAME-II (`6,645` operational / `9,332` sanctioned), Switch Delhi (`876` stations), and OSM (`725` features) overlap partially and have different reporting dates; they are never added together.
2. **Substation Proximity ≠ Electrical Hosting Capacity:** Mapped OSM substations (`341`) and transformers (`194`) provide physical routing distance only. Available MVA hosting capacity and feeder spare load are non-public DISCOM data and are explicitly flagged as unavailable.
3. **Real-Time Occupancy Telemetry Unavailable:** `https://ev.delhi.gov.in/openev/` returned `HTTP 502 Bad Gateway` during audit, and `available == no_of_chargers` on 100% of rows in Switch Delhi's static JSON.
4. **Centralized Commercial RTO Registrations in Delhi:** In VAHAN Delhi (`549,153` EVs), `64,723` commercial EVs (`DL51`, `DL52`, `DL53`) are registered at centralized Burari transport units. The Delhi Pilot provides a transparent toggle between direct Zonal RTO counts (`DL1–DL13` = `484,430` EVs, Verified Fact) and POI/population-weighted commercial redistribution (`549,153` EVs, Analytical Estimate).

---

## 5. Attribution & Licences
- **Government Disclosures:** Ministry of Road Transport & Highways (MoRTH VAHAN4), Bureau of Energy Efficiency (BEE), Ministry of Heavy Industries (MHI), Ministry of Petroleum & Natural Gas (MoPNG), Press Information Bureau (PIB), NITI Aayog, Central Electricity Authority (CEA), and Transport Department, Govt. of NCT of Delhi (Switch Delhi).
- **Open Geospatial & Demographic Layers:** DataMeet Community Maps (`CC BY 4.0`), WorldPop University of Southampton (`CC BY 4.0`), OpenStreetMap Contributors (`ODbL 1.0`), and CARTO Dark Matter Basemaps.
