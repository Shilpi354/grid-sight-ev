# DATA QUALITY REPORT — EV Infra Map India

**Audit Date:** 19 October 2026  
**Project Scope:** National Overview (36 States/UTs) + Detailed Pilot Geography (NCT of Delhi)  
**Companion Documents:** [`DATA_AVAILABILITY_AUDIT.md`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/DATA_AVAILABILITY_AUDIT.md) | [`DATA_GAPS.md`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/DATA_GAPS.md) | [`data/source_manifest.csv`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/source_manifest.csv)

---

## 1. Executive Summary of Audited Datasets

Every dataset downloaded into [`data/raw/`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw) was programmatically inspected for record counts, unit definitions (station vs. EVSE/charger row vs. connector vs. vehicle), exact and near duplicates, column-by-column missingness, coordinate validity inside India (`6.0°N–37.5°N, 68.0°E–97.5°E`) and NCT of Delhi (`28.35°N–28.95°N, 76.80°E–77.45°E`), string standardization errors, and structural biases.

### High-Level Quality Scorecard

| Dataset File | Primary Scope | Total Records | Exact Duplicate Rows | Valid Coordinates (%) | Geographic Coverage | Primary Quality Finding / Bias |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| [`BEE_EV_PCS_Data_29277_20251026_extracted.csv`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/charging/BEE_EV_PCS_Data_29277_20251026_extracted.csv) | National Public Chargers (BEE) | **39,641** charger rows (`44,066` connectors) | **8,428** (`21.26%`) | **39,522 / 39,641** (`99.70%` in India bbox) | All 36 States/UTs (`46` raw state strings) | Multi-charger stations listed as separate identical rows; `104` IOCL rows have `Lat == Lon`; no operational status flag |
| [`PIB_PRID_2246042_OMC_Statewise_EVPCS_20260301.csv`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/charging/PIB_PRID_2246042_OMC_Statewise_EVPCS_20260301.csv) | National OMC Chargers (MoPNG) | **38** state/UT rows (`27,737` installed; `22,753` operational) | **0** (`0.00%`) | N/A (State table) | 36 States/UTs (`38` rows; MP & Bihar split across 2 rows) | Reveals `17.97%` of installed OMC stations (`4,984`) are not yet operational (awaiting grid connection/commissioning) |
| [`PIB_PRID_2246045_FAMEII_Statewise_EVPCS_20260301.csv`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/charging/PIB_PRID_2246045_FAMEII_Statewise_EVPCS_20260301.csv) | National FAME-II Chargers (MHI) | **36** state rows (`8,932` OMC FAME-II installed) | **0** (`0.00%`) | N/A (State table) | 34 States/UTs + Total | Scheme-specific subset (`6,645` operational of `9,332` total FAME-II sanctioned); must not be added to BEE/OMC totals |
| [`Delhi_SwitchDelhi_charging_stations_20261019.csv`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/charging/Delhi_SwitchDelhi_charging_stations_20261019.csv) | Pilot Public Chargers & Swap (GNCTD) | **891** stations (`573` charging, `318` swapping; `6,841` points) | **15** (`1.68%`) | **764 / 891** (`85.75%` in Delhi bbox; **100%** of charging, **61.95%** of swap) | NCT of Delhi (`116` PIN codes) | `121` swap stations lack lat/lon; `available == no_of_chargers` on 100% of rows (static capacity, not live occupancy) |
| [`OSM_India_charging_stations_20261019.csv`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/charging/OSM_India_charging_stations_20261019.csv) | Crowdsourced Chargers (OSM) | **725** features (`182` in Delhi) | **0** (`0.00%`) | **725 / 725** (`100.00%`) | 31 States/UTs (heavy bias in Delhi & Kerala) | Severe undercoverage (`2.48%` of BEE station count) and `75.7%` missing capacity tags |
| [`VAHAN_state_ev_summary_20261019.csv`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/vahan/VAHAN_state_ev_summary_20261019.csv) | National Active EV Fleet (MoRTH) | **36** States/UTs (`10,689,490` active EVs) | **0** (`0.00%`) | N/A (State table) | All 36 States/UTs (`100%`) | Telangana shows `27,821` active EVs on VAHAN due to recent migration from state RTA portal; `26.39%` national fleet is `ACTIVE_NON_COMPLIANT` |
| [`VAHAN_Delhi_RTO_ev_summary_20261019.csv`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/vahan/VAHAN_Delhi_RTO_ev_summary_20261019.csv) | Pilot Active EV Fleet by RTO (MoRTH) | **23** RTO entries (`16` active registering units; `549,153` EVs) | **0** (`0.00%`) | N/A (RTO table) | NCT of Delhi (`100%`) | `64,723` commercial EVs (`11.79%`) registered at centralized Burari units (`DL51`, `DL52`, `DL53`) rather than residential zones |
| [`Admin2.shp`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/boundaries/Admin2.shp) & [`2011_Dist.shp`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/boundaries/2011_Dist.shp) | Administrative Boundaries (DataMeet) | **36** States/UTs & **641** Districts | **0** (`0.00%`) | **100.00%** valid polygons | All 36 States/UTs; 641 Census 2011 Districts (`9` in Delhi) | District boundaries reflect 2011 Census (`641` districts vs. `~780` in 2026); `Admin2.shp` includes modern `36` States/UTs (Ladakh & J&K separated) |
| [`OSM_Delhi_major_roads_20261019.csv`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/roads/OSM_Delhi_major_roads_20261019.csv) | Pilot Road Network (OSM) | **8,087** highway ways | **0** (`0.00%`) | **8,087 / 8,087** (`100.00%`) | NCT of Delhi & NCR fringe | `0%` missing geometry/class, but `54.10%` missing `lanes` and `71.16%` missing `maxspeed` |
| [`OSM_Delhi_power_infrastructure_20261019.csv`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/electricity/OSM_Delhi_power_infrastructure_20261019.csv) | Pilot Power Grid Nodes (OSM) | **576** features (`341` substations, `194` transformers, `41` plants) | **0** (`0.00%`) | **576 / 576** (`100.00%`) | NCT of Delhi bbox | `100%` valid coordinates, but `78.65%` missing `voltage` and `99.31%` missing `rating` (MVA) |
| [`OSM_Delhi_demand_attractors_20261019.csv`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/context/OSM_Delhi_demand_attractors_20261019.csv) | Pilot Demand Attractors (OSM) | **3,534** POIs across 12 classes | **0** (`0.00%`) | **3,534 / 3,534** (`100.00%`) | NCT of Delhi bbox | `100%` valid coordinates and `category`; `36.16%` unnamed (`parking` lots & minor `fuel` stations) |

---

## 2. Deep-Dive Audit: BEE National Public Charging Station Dataset

- **Source File:** [`data/raw/charging/BEE_EV_PCS_Data_29277_20251026.pdf`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/charging/BEE_EV_PCS_Data_29277_20251026.pdf) (`1,159` pages, `7.94 MB`)
- **Extracted Dataset:** [`data/raw/charging/BEE_EV_PCS_Data_29277_20251026_extracted.csv`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/charging/BEE_EV_PCS_Data_29277_20251026_extracted.csv) (`39,641` rows × `13` columns)

### 2.1 Unit of Observation & Duplicate Analysis (Why 39,641 Rows ≠ 39,641 Stations)
A critical finding of this audit is that **each row in the BEE PDF represents a charger unit or connector group at a site, NOT a distinct physical charging station**:
- **PDF Filename:** `EV_PCS_Data_29277_20251026.pdf` (indicating **29,277** unique stations in BEE's internal database as of 26 October 2025).
- **Total Extracted Rows:** **39,641** rows.
- **Sum of `No_of_Connectors`:** **44,066** individual charging connectors/nozzles.
- **Exact Duplicate Rows (across all 12 data columns):** **8,428 rows (`21.26%`)** are exact duplicates of another row on the same page. For example, when an operator like UJOY or IOCL installs 3 identical `3.3 kW LEV AC` chargers (`1 connector` each) at the same address, the BEE database exports 3 identical rows with `No_of_Connectors = 1`.
- **Unique Spatial / Site Groupings:**
  - Unique `(Latitude, Longitude)` pairs: **29,117**
  - Unique `(CPO_Name, Location, Latitude, Longitude)` tuples: **29,371** (matching the `29,277` station count in the filename within `0.32%`).
- **Implementation Rule:** Never report `39,641` as the "number of charging stations." Always report **29,277 stations** (or **29,117 unique geocoded locations**), **39,641 charger records**, and **44,066 connectors** (`696,652.27 kW` total rated charger power).

### 2.2 Column-by-Column Missingness & Data Types (BEE Dataset, $N = 39,641$)

| Column Name | Data Type | Non-Null Count | Missing / Invalid Count | Missing % | Quality & Format Notes |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `Page` | Integer | 39,641 | 0 | `0.000%` | PDF page index (`1` to `1159`) |
| `CPO_Name` | String | 39,641 | 0 | `0.000%` | `59` unique CPO names (`IOCL` = 8,364; `UJOY` = 7,644; `BPCL` = 6,617; `Reliance BP` = 3,635; `Tata Power` = 3,240; `HPCL` = 2,316) |
| `Govt_Private` | Categorical | 39,641 | 0 | `0.000%` | Exactly 2 values: `Govt.` (`20,945` / `52.84%`) and `Private` (`18,696` / `47.16%`) |
| `State` | String | 39,641 | 0 | `0.000%` | **46 distinct strings** for 36 States/UTs due to casing/typos (see Section 2.4) |
| `District` | String | 39,641 | 0 | `0.000%` | **1,288 distinct strings** due to spelling variants, city names entered in district column, and post-2011 splits |
| `City_Village` | String | 39,641 | 0 | `0.000%` | Free-text locality/city name (`9,840+` unique strings) |
| `Location` | String | 39,641 | 0 | `0.000%` | Street address / retail outlet name |
| `Latitude` | Float | 39,639 | **2** | `0.005%` | Blank on 2 rows: Row 25827 (`UJOY`, Raigad, Maharashtra, p. 770) and Row 35953 (`HPCL`, Kannauj, UP, p. 1064) |
| `Longitude` | Float | 39,638 | **3** (`2` blank, `1` corrupted) | `0.008%` | Blank on the 2 rows above; corrupted as `###########` on Row 36796 (`IOCL`, Mathura, UP, p. 1082) due to narrow Excel column width prior to PDF export |
| `Connector_Type` | String | 39,641 | 0 | `0.000%` | `26` distinct strings (`LEV AC Charge point` = 16,351; `Bharat AC-001` = 4,907; `CCS` = 4,215; `Type-II AC` = 4,174; `CCS-II` = 3,604; `Bharat AC` = 1,894; `Bharat DC-001` = 1,781) |
| `Charger_Rating_kW` | Float | 39,641 | 0 | `0.000%` | Range: `3.0` to `500.0` kW (most common: `3.3 kW`, `7.4 kW`, `10 kW`, `15 kW`, `30 kW`, `60 kW`) |
| `Connector_Rating_kW` | Float | 39,641 | 0 | `0.000%` | Rating per nozzle (`3.3 kW` on `56.8%` of rows) |
| `No_of_Connectors` | Integer | 39,641 | 0 | `0.000%` | Sum = **44,066** connectors (`1` connector on `36,278` rows; `2` connectors on `2,672` rows; `3+` on `691` rows) |

### 2.3 Coordinate Validity & Spatial Outlier Audit (BEE Dataset)
Out of **39,641** rows:
- **39,638 rows (`99.992%`)** parse as valid floating-point `(Latitude, Longitude)` numbers.
- **39,522 rows (`99.700%`)** fall strictly inside India's bounding box (`6.0°N <= Lat <= 37.5°N` and `68.0°E <= Lon <= 97.5°E`).
- **116 rows (`0.293%`)** have numeric coordinates outside India's bounding box:
  1. **`Latitude == Longitude` Copy-Paste Bug (`104` rows, all `IOCL`):** Exactly **104 IOCL records** have their `Latitude` value duplicated into the `Longitude` column (e.g., `Lat = 27.684776, Lon = 27.684776` in Bharatpur, Rajasthan; `Lat = 28.187573, Lon = 28.187573` in Alwar, Rajasthan; `Lat = 13.063046, Lon = 13.063046` in Chennai, Tamil Nadu). Because longitudes in `9°E–31°E` fall in Africa/Europe, a simple `abs(Latitude - Longitude) < 0.001` filter catches all 104 rows with 100% precision.
  2. **Leading Digit / Decimal Typos (`12` rows):** The remaining 12 out-of-bbox rows have minor digit typos in Longitude or Latitude (e.g., `Lon = 7.728` instead of `77.28`, or `Lat = 82.87` instead of `28.87`).
  3. **Zero `(0, 0)` or Swapped `(Lon, Lat)` Rows:** **0 rows** have `(0, 0)` coordinates and **0 rows** have swapped `(Lon, Lat)` where `68 <= Lat <= 97`.

### 2.4 State Name Fragmentation in BEE (`46` Raw Strings → `36` Canonical States/UTs)
Because CPOs entered state names without a strict lookup constraint in BEE's portal, `State` contains **46 unique strings** instead of 36:
- **Case & Spelling Splits Detected:**
  - Kerala: `Kerala` (`1,975`) + `KERALA` (`65`) = **2,040**
  - Tamil Nadu: `Tamil Nadu` (`2,568`) + `Tamil nadu` (`55`) = **2,623**
  - Bihar: `Bihar` (`536`) + `BIHAR` (`12`) = **548**
  - Uttarakhand: `Uttarakhand` (`310`) + `Uttrakhand` (`294`) = **604**
  - Chhattisgarh: `Chhattisgarh` (`519`) + `Chattisgarh` (`234`) = **753**
  - West Bengal: `West Bengal` (`754`) + `WestBengal` (`69`) = **823**
  - Jammu & Kashmir: `Jammu and Kashmir` (`254`) + `Jammu & Kashmir` (`101`) = **355**
  - Odisha: `Odisha` (`658`) + `ODISHA` (`3`) + `Orissa` (`2`) = **663**
  - Rajasthan: `Rajasthan` (`1,671`) + `RAJASTHAN` (`2`) = **1,673**
  - Andaman & Nicobar: `Andaman and Nicobar Islands` (`4`) + `Andaman & Nicobar` (`2`) = **6**
  - DNH & DD: `Dadra and Nagar Haveli and Daman and Diu` (`10`) + `Daman and Diu` (`4`) = **14**

---

## 3. Deep-Dive Audit: Official Parliamentary (PIB) OMC & FAME-II Datasets

To prevent combining incompatible totals, we audited the two official Lok Sabha replies dated **27 March 2026** (reporting status as of **01 March 2026**):

### 3.1 MoPNG OMC Dataset ([`PIB_PRID_2246042_OMC_Statewise_EVPCS_20260301.csv`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/charging/PIB_PRID_2246042_OMC_Statewise_EVPCS_20260301.csv))
- **Record Count:** **38 rows** (covering all 36 States/UTs; `Madhya Pradesh` and `Bihar` appear twice in the official parliamentary table because supplementary rows were appended at the bottom—rows `20` & `37` for MP [`1,771 + 42 = 1,813` installed] and rows `5` & `38` for Bihar [`661 + 2 = 663` installed]).
- **Completeness:** **0% missing values** across all 9 columns (`FY 20-21` through `FY 25-26`, `Total Installed`, `Decommissioned`, `Operational`).
- **Key Bias Uncovered (Installed vs. Operational Gap):**
  - **Total Installed OMC Stations:** **27,737** (`IOCL + BPCL + HPCL` cumulative FY20-21 to 01.03.2026)
  - **Decommissioned:** **21**
  - **Operational:** **22,753 (`82.03%`)**
  - **Uncommissioned Backlog:** **4,963 installed stations (`17.89%`)** are awaiting DISCOM grid energization or final commissioning.
  - **Worst State Commissioning Ratios:** Ladakh (`1` operational of `10` installed = `10.0%`), Maharashtra (`1,599 / 3,389 = 47.2%`), Gujarat (`844 / 1,422 = 59.4%`), Jharkhand (`316 / 478 = 66.1%`).
  - **Delhi Pilot OMC Status:** `219` installed, `0` decommissioned, **`201` operational (`91.8%`)**.

### 3.2 MHI FAME-II Dataset ([`PIB_PRID_2246045_FAMEII_Statewise_EVPCS_20260301.csv`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/charging/PIB_PRID_2246045_FAMEII_Statewise_EVPCS_20260301.csv))
- **Record Count:** **36 rows** (35 state/region entries + Total row = **8,932** FAME-II chargers installed by OMCs) + **5 rows** in [`PIB_PRID_2246045_FAMEII_PSE_Entities_20260301.csv`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/charging/PIB_PRID_2246045_FAMEII_PSE_Entities_20260301.csv) (**227** chargers installed by other PSEs/entities, including `72` by EESL in Delhi).
- **Overall FAME-II Sanctioned vs. Operational:** Out of **9,332** EV PCS sanctioned under FAME-II across India, **6,645 (`71.21%`)** are operational as of 01.03.2026.
- **Non-Additivity Rule:** The `8,932` OMC FAME-II stations are a **subsidized subset** of the `27,737` total OMC stations in `PIB_PRID_2246042`, which in turn overlap with the `17,297` OMC charger rows (`IOCL` 8,364 + `BPCL` 6,617 + `HPCL` 2,316) in the BEE dataset. They must never be summed together.

---

## 4. Deep-Dive Audit: Pilot Geography — Delhi Switch Delhi Charging Database

- **Source File:** [`data/raw/charging/Delhi_SwitchDelhi_charging_stations_20261019.csv`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/charging/Delhi_SwitchDelhi_charging_stations_20261019.csv) (`891` rows × `18` columns)

### 4.1 Record Structure & Station Type Split ($N = 891$)
- **`station_type = "Charging"`:** **573 stations (`64.31%`)** accounting for **6,523 charging points**.
- **`station_type = "Battery swapping"`:** **318 stations (`35.69%`)** accounting for **318 station entries** (`2,707` swapping dockets recorded across the `401` rows with non-nil docket counts).
- **Total `no_of_chargers`:** **6,841** charging/swapping points.
- **Exact Duplicate Rows:** **15 rows (`1.68%`)** are exact duplicates across all 18 columns (leaving **876 unique station records**).

### 4.2 Column-by-Column Missingness (Switch Delhi Dataset, $N = 891$)

| Column Name | Missing / Empty / `"nil"` Count | Missing % | Audit Interpretation |
| :--- | :---: | :---: | :--- |
| `station_type` | 0 | `0.00%` | `Charging` (`573`) or `Battery swapping` (`318`) |
| `company_name` | 0 | `0.00%` | Operator/brand (`BOLT`, `TATA Power`, `Sun Mobility`, `Battery Smart`, `ElectriVa`, `EESL`, `Statiq`, etc.) |
| `no_of_chargers` | 0 | `0.00%` | Integer (`1` to `646`; sum = `6,841`) |
| `available` | 0 | `0.00%` | **Static Bias:** Equals `no_of_chargers` (`6,841`) on `100%` of rows; does NOT reflect real-time occupancy |
| `pincode` | 0 | `0.00%` | Valid 6-digit Delhi PIN codes (`110001` to `110097`) on 100% of rows |
| `address` | 5 | `0.56%` | `5` rows have `"nil"` street address (all 5 have valid PIN code and coordinates) |
| `open` (Operating Hours) | 8 | `0.90%` | `8` rows have `"nil"` (remaining `883` have hours, e.g., `12:00 AM - 11:59 PM`) |
| `payment_modes` | 8 | `0.90%` | `8` rows have `"nil"` (`E-Wallet`, `UPI`, `Cash`, `App`) |
| `region` | 103 | `11.56%` | Blank on `103` rows due to incomplete PIN lookup dictionary in portal JS |
| `latitude` | **121** | `13.58%` | **0% missing on `Charging` (`573/573` valid)**; **38.05% missing on `Battery swapping` (`121/318` blank)** |
| `longitude` | **121** | `13.58%` | Same `121` battery swapping stations as `latitude` |
| `capacity` (kW Rating) | 121 | `13.58%` | Blank/nil on the same `121` battery swapping stations (`3.3KW` on `466` rows, `15 kW` on `76` rows, `10KW` on `70` rows) |
| `id` | 299 | `33.56%` | Portal internal ID is `"nil"` on `299` newer rows (`589` unique IDs among `592` populated rows) |
| `charger_type` | 318 | `35.69%` | `"nil"` on all `318` battery swapping stations; **0% missing on the `573` EV charging stations** (`BOLT 16A LITE` = 380, `LEV AC` = 71, `DC-001` = 42, `CCS2/Type-2` = 37) |
| `cost_per_unit` | 405 | `45.45%` | Blank/nil on `318` swap stations + `87` charging stations (`INR 0–22/kWh` where populated) |
| `if_battery_swap_station,_no._of_dockets` | 490 | `54.99%` | `"nil"` on `490` charging stations; populated (`4` to `16` dockets) on swap stations |
| `contact_number` | 694 | `77.89%` | `"nil"` on `694` stations |
| `name` (Contact Person) | 694 | `77.89%` | `"nil"` on `694` stations |

### 4.3 Spatial Coordinate Check (Switch Delhi Dataset)
- Out of **770 stations** with numeric coordinates (`573` charging + `197` swapping):
  - **764 stations (`99.22%`)** fall strictly inside the Delhi NCR bounding box (`28.35°N–28.95°N, 76.80°E–77.45°E`).
  - **6 stations (`0.78%`)** have coordinate typos placing them outside Delhi NCR (e.g., `Lat = 19.28` or `Lon = 72.85`), which can be corrected or filtered using their verified 6-digit Delhi `pincode` (`1100xx`).

---

## 5. Deep-Dive Audit: VAHAN Active EV Registration Datasets

- **Source Files:**
  - [`data/raw/vahan/VAHAN_state_ev_summary_20261019.csv`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/vahan/VAHAN_state_ev_summary_20261019.csv) (`36` States/UTs)
  - [`data/raw/vahan/VAHAN_state_ev_by_subcategory_20261019.csv`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/vahan/VAHAN_state_ev_by_subcategory_20261019.csv) (`378` state × subcategory rows)
  - [`data/raw/vahan/VAHAN_state_ev_yearwise_20261019.csv`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/vahan/VAHAN_state_ev_yearwise_20261019.csv) (`555` state × year rows, `2011–2026`)
  - [`data/raw/vahan/VAHAN_Delhi_RTO_ev_summary_20261019.csv`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/vahan/VAHAN_Delhi_RTO_ev_summary_20261019.csv) (`23` Delhi RTO rows)

### 5.1 Completeness & Internal Consistency Checks
- **Missing Values:** **0.00% missing** across all columns in all four VAHAN CSV files.
- **Exact Cross-Table Additivity Verified:**
  - Sum of `Total_Active_EV` across all 36 States/UTs = **10,689,490**
  - Sum of Vehicle Categories: `2W (6,084,692) + 3W (3,782,480) + 4W_LMV (740,301) + Goods (52,521) + Bus (21,530) + Others (7,966)` = **10,689,490** (`0` discrepancy)
  - Sum of Fuel Labels: `ELECTRIC(BOV) (6,350,724) + PURE EV (4,338,219) + SOLAR (378) + PLUG-IN HYBRID EV (142) + FUEL CELL HYDROGEN (27)` = **10,689,490** (`0` discrepancy)
  - Sum of Compliance Status: `ACTIVE_COMPLIANT (7,869,058 / 73.61%) + ACTIVE_NON_COMPLIANT (2,820,432 / 26.39%)` = **10,689,490** (`0` discrepancy)
  - Sum of Delhi's 23 RTOs in `VAHAN_Delhi_RTO_ev_summary_20261019.csv` = **549,153**, matching the `Delhi` row in `VAHAN_state_ev_summary_20261019.csv` (`549,153`) to the exact vehicle (`0` discrepancy).

### 5.2 Known Structural Biases in VAHAN Data
1. **Active Compliant vs. Active Non-Compliant (`26.39%` Non-Compliant):**
   - Over one-quarter (**2,820,432**) of India's registered active EVs are flagged as `ACTIVE_NON_COMPLIANT` (vehicles with expired fitness certificates, road tax arrears, or pending insurance—predominantly older e-rickshaws/3Ws). In Uttar Pradesh (`1,984,743` total EVs, where `71.4%` are 3Ws), non-compliant active vehicles represent a substantial share of the fleet.
2. **Telangana Historical Under-Count on VAHAN4:**
   - Telangana (`TG`) shows **27,821** active EVs on VAHAN because Telangana operated an independent state RTA portal until its recent migration to VAHAN4. In contrast, NITI Aayog's IEMI 2025 report notes Telangana's full state RTA fleet. Any national per-EV charger ratio (`EVs per public charger`) must flag Telangana's VAHAN migration artifact so Telangana is not artificially ranked as having excess chargers per EV.
3. **Centralized Commercial RTO Registration in Delhi (`DL51`, `DL52`, `DL53`):**
   - Out of **23 RTO entries** in Delhi, **7 entries** are specialized Fitness Centers (`VIU BURARI - DL21`, `JHULJHULI FITNESS CENTER - DL22/DL23`, `RANHOLA FITNESS CENTER - DL24`, `DWARKA FITNESS CENTER - DL25`, `MAJRA DABAS - DL26`, `NANGLOI - DL27`) with `0` primary vehicle registrations.
   - Among the **16 active registering RTOs**, **3 centralized commercial units** in North/Central Delhi (`RAJPUR ROAD/VIU BURARI - DL51` with `46,660` EVs; `BURARI TAXI UNIT - DL52` with `15,227` EVs; `BURARI AUTO UNIT - DL53` with `2,836` EVs) hold **64,723 commercial EVs (`11.79%` of Delhi's entire EV fleet)**—including **93.64% of all electric buses (`5,151 / 5,501`)** and **81.94% of all electric goods vehicles (`3,421 / 4,177`)** in Delhi. Naive mapping of `DL51–DL53` to North/Central Delhi would distort spatial demand unless redistributed across commercial/transit corridors.

---

## 6. Deep-Dive Audit: OpenStreetMap (OSM), Boundaries, and Contextual Layers

### 6.1 OpenStreetMap India Charging Stations ([`OSM_India_charging_stations_20261019.csv`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/charging/OSM_India_charging_stations_20261019.csv), $N = 725$)
- **Duplicates:** `0` duplicate `osm_id` values.
- **Coordinate Validity:** **725 / 725 (`100.00%`)** fall inside India's bounding box; **182 (`25.10%`)** fall inside NCT of Delhi.
- **Tag Missingness:**
  - `latitude` / `longitude`: `0.00%` missing
  - `access`: `60.28%` missing (`437 / 725`)
  - `operator`: `68.14%` missing (`494 / 725`)
  - `name`: `72.41%` missing (`525 / 725`)
  - `capacity`: `75.72%` missing (`549 / 725`)
  - `fee`: `77.52%` missing (`562 / 725`)
  - `opening_hours`: `83.86%` missing (`608 / 725`)
  - `sockets_json` (connector type breakdown): `92.00%` missing (`667 / 725`)
  - `output` (kW rating): `99.31%` missing (`720 / 725`)
- **Bias Assessment:** OSM captures only **2.48%** of India's official station count (`725` vs `29,277` in BEE) and is heavily skewed toward volunteer mapping campaigns in **Delhi (`182`)** and **Kerala (KSEB pole chargers)**. OSM must be used strictly as a supplemental verification layer, never as the primary national baseline.

### 6.2 Pilot Contextual Layers in NCT of Delhi (Roads, Power Grid, Demand Attractors)
1. **OSM Delhi Major Roads ([`OSM_Delhi_major_roads_20261019.csv`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/roads/OSM_Delhi_major_roads_20261019.csv), $N = 8,087$ ways):**
   - `highway_class`: `0.00%` missing (`793` `motorway`, `1,393` `trunk`, `1,442` `primary`, `4,459` `secondary`).
   - Geometry (`center_lat`, `center_lon`, full polyline in `.json`): `0.00%` missing.
   - Attribute missingness: `oneway` (`8.20%`), `name` (`24.67%`), `surface` (`45.10%`), `lanes` (`54.10%`), `maxspeed` (`71.16%`), `ref` (`78.66%`).
2. **OSM Delhi Power Infrastructure ([`OSM_Delhi_power_infrastructure_20261019.csv`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/electricity/OSM_Delhi_power_infrastructure_20261019.csv), $N = 576$ features):**
   - `power_type`: `0.00%` missing (`341` `substation`, `194` `transformer`, `41` `plant`).
   - `latitude` / `longitude`: `0.00%` missing (`100%` inside Delhi bbox).
   - Attribute missingness: `name` (`67.19%`), `substation_type` (`69.44%`), `voltage` (`78.65%`), `operator` (`80.56%`), `rating` (`99.31%`).
3. **OSM Delhi Demand Attractors ([`OSM_Delhi_demand_attractors_20261019.csv`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/context/OSM_Delhi_demand_attractors_20261019.csv), $N = 3,534$ POIs):**
   - `category` & `latitude` / `longitude`: `0.00%` missing (`1,069` parking, `651` hospitals, `637` fuel stations, `267` Metro/rail stations, `212` colleges/universities, `205` malls/supermarkets, `195` industrial zones, `167` commercial zones, `76` retail zones, `55` bus stations/terminals).
   - `name`: `36.16%` missing (mostly surface parking polygons and residential landuse zones).

### 6.3 Administrative Boundaries, Population & Tariff Layers
1. **DataMeet Boundaries ([`Admin2.shp`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/boundaries/Admin2.shp) & [`2011_Dist.shp`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/boundaries/2011_Dist.shp)):**
   - `Admin2.shp` (`36` records): `0%` missing `ST_NM`, valid closed polygons for all 36 States/UTs (including separate `Ladakh` and `Jammu & Kashmir`, plus merged `Dadra and Nagar Haveli and Daman and Diu`).
   - `2011_Dist.shp` (`641` records): `0%` missing `DISTRICT`, `ST_NM`, `ST_CEN_CD`, `DT_CEN_CD`, `censuscode`. Contains `9` Census 2011 districts for `NCT of Delhi` (`North West`, `North`, `North East`, `East`, `New Delhi`, `Central`, `West`, `South West`, `South`).
2. **NITI Aayog State Population & GSDP ([`NITI_IEMI_2025_State_Population_GSDP.csv`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/demographics/NITI_IEMI_2025_State_Population_GSDP.csv), $N = 35$):**
   - `0%` missing across `Population_Million_2025`, `Area_sq_km`, and `GSDP_INR_Crores` for the 35 profiled States/UTs (Ladakh's `0.30M` population and `59,146 sq km` area are documented in the audit notes for 36-state completeness).
3. **WorldPop 1km Population Raster ([`WorldPop_ind_ppp_2020_1km_Aggregated.tif`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/demographics/WorldPop_ind_ppp_2020_1km_Aggregated.tif)):**
   - Complete national coverage (`19.09 MB` GeoTIFF, WGS84, `30 arc-second` / `~1 km` resolution) with `NoData` strictly confined to water bodies and areas outside national borders.
4. **BEE State EV Tariffs ([`BEE_State_EV_Tariff_Annexure_A.pdf`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/electricity/BEE_State_EV_Tariff_Annexure_A.pdf), $N = 36$):**
   - Covers all 36 States/UTs (`28` States + `8` UTs) with LT and HT EV energy charges (`Rs/kWh` or `Rs/kVAh`) and fixed demand charges (`Rs/kW/month` or `Rs/kVA/month`).

---

## 7. Mandatory Data Hygiene Rules Before Platform Coding

Based on the quality findings above, the data processing pipeline in Phase 2 (only after user approval) must enforce these five deterministic rules:
1. **Never Mix Incompatible Charger Totals:** Maintain separate schema tables and UI layer toggles for:
   - **BEE National Registry:** `29,277` stations / `29,117` unique coordinate pairs / `39,641` charger rows / `44,066` connectors (as of 26 Oct 2025).
   - **MoPNG OMC Registry:** `27,737` installed / `22,753` operational (as of 01 Mar 2026).
   - **MHI FAME-II Registry:** `9,332` sanctioned / `6,645` operational (as of 01 Mar 2026).
   - **Delhi Switch Delhi Registry:** `891` stations (`573` charging + `318` swapping) / `6,841` points (as of 19 Oct 2026).
   - **OpenStreetMap Extract:** `725` crowdsourced stations (`182` in Delhi) (as of 19 Oct 2026).
2. **Filter the 119 Invalid/Out-of-Bbox BEE Coordinates:** Exclude or flag the `3` non-numeric rows and `116` out-of-bbox rows (`104` IOCL `Lat == Lon` copy-paste rows + `12` digit-typo rows) from map rendering while retaining them in state-level tabular totals via their normalized `State` field.
3. **Deduplicate Multi-Row BEE Stations for Site-Level Spatial Analysis:** Aggregate the `39,641` BEE rows by `(CPO_Name, Location, round(Latitude, 4), round(Longitude, 4))` so co-located chargers at a single site are represented as **one station marker** with summed `total_connectors` (`44,066` nationally) and `total_capacity_kw` (`696.65 MW` nationally), rather than overlapping markers that bias spatial nearest-neighbor calculations.
4. **Spatial Join (`ST_Within`) Over String Matching:** Assign every geocoded charger to its canonical State (`Admin2.shp`) and District (`2011_Dist.shp`) via spatial point-in-polygon containment, eliminating the `46` state string variants and `1,288` district string variants in BEE.
5. **Flag Telangana's VAHAN Migration & Delhi's Burari Commercial RTOs:** Display a data-note badge on Telangana (`27,821` VAHAN4 active EVs) and apply a transparent POI/population-weighted redistribution option for Delhi's centralized Burari commercial RTOs (`DL51`, `DL52`, `DL53` = `64,723` commercial EVs).
