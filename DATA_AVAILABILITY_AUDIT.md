# EV Infra Map India — Data Availability Audit

**Project:** Techfest 2026–27 (IIT Bombay) — Ministry of Heavy Industries (MHI) & ICAT Challenge 1: *EV Infra Map India*  
**Audit Date:** 19 October 2026  
**Stage:** Pre-Coding Data Collection & Validation Only  
**Project Workspace:** `C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/`

---

## 1. Executive Summary of Source Verification

Every hyperlink and data source listed in `EV_Infra_Map_India_Data_Gap_Audit.docx` was opened, probed via HTTP/API inspection, and tested for machine-readable downloadability on **19 October 2026**.

| Layer | Primary / Secondary Sources Inspected | Download Status | Key Audit Finding |
| :--- | :--- | :--- | :--- |
| **1. EV Population & Registrations** | VAHAN Public Dashboard (`analytics.parivahan.gov.in`) | **Downloaded** (All 36 States/UTs + 23 Delhi RTOs + 2011–2026 trends) | VAHAN exposes undocumented JSON REST endpoints (`/vahandashboard/*`) when called with a valid `JSESSIONID` cookie and `fitnessCheck=0`. **Critical taxonomy finding:** Battery EVs are split across two fuel labels (`ELECTRIC(BOV)` = 6,350,724 and `PURE EV` = 4,338,219) totaling **10,689,490 active EVs**. |
| **2. Existing EV Charging Infrastructure** | BEE EV PCS PDF (26 Oct 2025), PIB PRID 2246042 & 2246045 (27 Mar 2026), Delhi Switch Delhi (`ev.delhi.gov.in`), OSM Overpass API | **Downloaded & Extracted** (39,641 BEE rows; 891 Delhi stations; 725 OSM stations; 3 PIB tables) | The 1,159-page BEE PDF (`EV_PCS_Data_29277.pdf`) is a vector PDF exported from Excel and is **100% machine-extractable** with **99.99% coordinate completeness** (39,638/39,641 rows have numeric Lat/Lon representing ~29,117 unique locations and 44,066 connectors). Delhi's `/charging-station` page embeds a live 891-station JSON array (`all_locations`, 6,841 charging points). |
| **3. Geographic & Administrative Boundaries** | DataMeet Maps GitHub (`github.com/datameet/maps` & `projects.datameet.org/maps/`) | **Downloaded** (36 States/UTs `Admin2.shp`, 641 Districts `2011_Dist.shp`, Composite GeoJSON) | State polygons (`Admin2.shp`, 36 features) reflect post-2019 Ladakh and DNH&DD boundaries. District polygons (`2011_Dist.shp`, 641 features) reflect Census 2011 vintage and lack post-2011 district splits, requiring point-in-polygon joins for coordinates and a name crosswalk for tabular data. |
| **4. Road & Mobility Network** | Geofabrik India (`download.geofabrik.de/asia/india.html`) & OSM Overpass API | **Downloaded** (India `.poly`/`.kml` + 8,087 Delhi Pilot major road segments) | Geofabrik updates `india-latest.osm.pbf` daily (1.6 GB as of 18 Oct 2026) and provides 6 zonal `.gpkg.zip` extracts (e.g., Northern Zone 213 MB). For the Delhi pilot, all 8,087 `motorway`, `trunk`, `primary`, and `secondary` road ways were extracted via Overpass. Traffic volume and travel-time data are not publicly available in OSM. |
| **5. Demographic & Economic Activity** | WorldPop (`id=50771`), Census of India (`censusindia.gov.in`), NITI IEMI 2025, OGD (`data.gov.in`) | **Partially Downloaded** (WorldPop 1km GeoTIFF + 2024 100m metadata; NITI 2025 NCP State Pop & GSDP) | WorldPop's 2024 100m raster (`ind_pop_2024_UC_100m_R2024A_v1.tif`, 1.65 GB) is verified open (CC BY 4.0); the lightweight 1km national GeoTIFF (19.1 MB) and NITI 2025 state population/GSDP baselines were downloaded. `censusindia.gov.in` timed out (`103.151.152.70:80`), and `data.gov.in` requires JanParichay OAuth login for bulk downloads. |
| **6. Electricity Infrastructure** | CEA (`cea.nic.in/ev-charging-standards/`), BEE Tariff Annexure A, Ministry of Power (`powermin.gov.in`), OSM Overpass | **Partially Downloaded** (BEE 36-State EV Tariff PDF; CEA 2019 Annexure-VI PDF; 576 Delhi OSM power features) | `cea.nic.in/ev-charging-standards/` is now behind a login/captcha wall, and legacy `powermin.gov.in` PDF links return HTTP 404. However, BEE's 36-state EV Tariff schedule (`annexure-A.pdf`) and 576 mapped Delhi substations/transformers/plants from OSM were downloaded. Feeder/transformer spare hosting capacity is not publicly disclosed. |
| **7. Supporting Contextual Information** | NITI Aayog IEMI 2025 (`niti.gov.in/node/2424`), BEE State Nodal Agencies XLSX & Policy PDFs, OSM Overpass | **Downloaded** (NITI IEMI 2025 170-p PDF; BEE SNA XLSX; Delhi EV Policy PDF; 3,534 Delhi POIs) | NITI's IEMI 2025 report (published 15 Sep 2026) and BEE's State Nodal Agency directory (`State Nodal Agency for EV.xlsx`) were downloaded, along with 3,534 geocoded demand attractors in Delhi (parking, bus depots/stations, metro/rail stations, fuel pumps, commercial/industrial zones, hospitals, hotels). |

> [!CAUTION]
> **Strict Separation of Incompatible Counts:** In accordance with Requirement 8 and Section 12 of the brief, **BEE EVPCS records (39,641 rows / ~29,277 stations as of 26 Oct 2025)**, **PIB OMC-installed stations (27,737 installed / 22,753 operational as of 01 Mar 2026)**, **PIB FAME-II sanctioned/operational stations (9,332 sanctioned / 6,645 operational; 8,932 OMC + 227 PSE installed as of 01 Mar 2026)**, **Delhi Switch Delhi records (891 stations / 6,841 charging points as of 19 Oct 2026)**, and **OSM mapped stations (725 features as of 19 Oct 2026)** are stored in separate files and **must never be summed together**.

---

## 2. Source-by-Source Audit Findings

### 2.1 Layer 1: EV Population & Vehicle Registration

#### Source 1.1: VAHAN Public Analytics Dashboard
- **Verified URL:** `https://www.analytics.parivahan.gov.in/analytics/publicdashboard/vahan?lang=en` (Canonical valid-SSL URL: `https://analytics.parivahan.gov.in/analytics/publicdashboard/vahan?lang=en`; legacy JSF dashboard at `https://vahan.parivahan.gov.in/vahan4dashboard/`)
- **Source Organisation:** Ministry of Road Transport and Highways (MoRTH), Government of India / National Informatics Centre (NIC)
- **Download Status:** **Downloaded (Reproducible API Extraction)**
  - `data/raw/vahan/VAHAN_national_overview_20261019.json`
  - `data/raw/vahan/VAHAN_state_ev_summary_20261019.csv` (36 States/UTs)
  - `data/raw/vahan/VAHAN_state_ev_by_subcategory_20261019.csv` (378 State × Subcategory rows)
  - `data/raw/vahan/VAHAN_state_ev_yearwise_20261019.csv` (555 State × Year rows, 2011–2026)
  - `data/raw/vahan/VAHAN_Delhi_RTO_ev_summary_20261019.csv` (23 Delhi RTOs)
- **Actual Fields Exposed:**
  - **Filter / Query Parameters:** `fromYear`, `toYear`, `stateCode` (36 two-letter codes), `rtoCode` (`0` for all, or integer RTO ID from `/analytics/json_rtos`), `vehicleClasses` (76 classes), `vehicleMakers`, `vehicleSubCategories` (17 subcategories), `vehicleEmissions` (26 norms), `vehicleFuels` (34 fuel types), `timePeriod` (`0` = Calendar Year, `1` = Financial Year, `2` = As On Date), `vehicleCategoryGroup` (11 groups), `evType` (`PURE EV`, `ELECTRIC BOV`, `PLUG IN HYBRID EV`, `STRONG HYBRID EV`), `vehicleStatus` (11 statuses), `vehicleOwnerType` (27 types), `fitnessCheck` (`0` = No, `1` = Yes), `vehicleType` (`Transport`, `Non-Transport`), `archiveTypeAC` (`ACTIVE_COMPLIANT`), `archiveTypeANC` (`ACTIVE_NON_COMPLIANT`), `archiveTypeTA` (`TEMPORARY_ARCHIVE`), `archiveTypePA` (`PERMANENT_ARCHIVE`).
  - **JSON API Endpoints Verified:**
    1. `/analytics/publicdashboard/vahan/registration/dashboardcount`
    2. `/analytics/publicdashboard/vahandashboard/categoriesdonutchart` (returns all 17 subcategories)
    3. `/analytics/publicdashboard/vahandashboard/classdistribution` (returns all 70+ vehicle classes)
    4. `/analytics/publicdashboard/vahandashboard/vahanyearwiseregistrationtrend` (returns annual counts 2011–2026)
    5. `/analytics/publicdashboard/vahandashboard/fueltypedonutchart` (returns fuel breakdown)
    6. `/analytics/publicdashboard/vahandashboard/statusdistribution` (returns Active Compliant vs Active Non-Compliant split)
    7. `/analytics/publicdashboard/vahandashboard/top5chart` (returns top 5 states only)
    8. `/analytics/json_rtos?stateCode=<XX>` (returns list of `{id, rtoCode, rtoName, stateCode}`)
- **Reporting Period & Freshness:** Live database ("As on Date" = **19 October 2026**; annual series covers **2011 to 2026 YTD**).
- **Geographic Granularity:** National, State/UT (all 36 States/UTs), and RTO level (e.g., 23 RTOs in Delhi). District-level polygons are *not* native to VAHAN; RTOs must be mapped to districts via a crosswalk.
- **Units:** Number of registered vehicles.
- **Licence / Access Constraints:** Public government analytics portal; no login required for the JSON endpoints above, but public viewing does not grant unrestricted commercial redistribution.
- **Technical & Methodological Limitations Identified:**
  1. **TLS Certificate Hostname Mismatch:** `https://www.analytics.parivahan.gov.in` presents a certificate valid only for `*.parivahan.gov.in` and `parivahan.gov.in` (failing strict TLS checks on the `www.analytics` subdomain). Using `https://analytics.parivahan.gov.in` or `verify=False` resolves this.
  2. **Hidden `fitnessCheck=0` Requirement:** Calling the `/vahandashboard/*` endpoints with `fitnessCheck=""` returns `HTTP 400 Bad Request`. In the browser DOM, a hidden `<select id="fitnessCheck">` defaults to `"0"`. Including `fitnessCheck=0` and a valid `JSESSIONID` cookie returns HTTP 200 JSON.
  3. **Rate-Limiting / Silent Empty Arrays:** Sending more than ~15–20 unthrottled requests in a burst causes the server to return empty JSON arrays (`{"labels":[],"data":[]}`). A 0.35s delay between requests with session refresh completely prevents data loss.
  4. **Critical Split Fuel Taxonomy (`ELECTRIC(BOV)` vs `PURE EV`):** Until early 2024, battery electric vehicles in VAHAN were recorded almost exclusively under `vehicleFuels = ELECTRIC(BOV)` (6,350,724 active vehicles). From 2024 onward, VAHAN began recording most new battery EVs under `vehicleFuels = PURE EV` (4,338,219 active vehicles: 493,175 in 2024; 1,565,579 in 2025; 2,279,060 in 2026 YTD). Querying only `ELECTRIC(BOV)` or only `evType = PURE EV` severely undercounts India's EV fleet! Combining all 5 non-ICE/plug-in electric fuel labels (`ELECTRIC(BOV)`, `PURE EV`, `PLUG-IN HYBRID EV` [142], `SOLAR` [378], `FUEL CELL HYDROGEN` [27]) yields the true active EV total of **10,689,490 vehicles** (excluding `STRONG HYBRID EV` [258,083], `PETROL/HYBRID` [1,363,291], `PETROL(E20)/HYBRID` [244,145], and `DIESEL/HYBRID` [180,151], which do not plug into the charging grid).
  5. **Active Compliant vs. Non-Compliant Fleet:** Of the 10,689,490 active EVs, **7,869,058 (73.6%)** are `ACTIVE_COMPLIANT` and **2,820,432 (26.4%)** are `ACTIVE_NON_COMPLIANT` (expired fitness/tax/PUCC/insurance records, especially older e-rickshaws).

---

### 2.2 Layer 2: Existing EV Charging Infrastructure

#### Source 2.1: BEE E-Mobility Page & Public Charging Stations PDF (26 Oct 2025)
- **Verified URLs:**
  - E-Mobility Portal Page: `https://beeindia.gov.in/show_content.php?lang=1&level=2&lid=67&ls_id=345`
  - Detailed Station List PDF: `https://beeindia.gov.in/WriteReadData/RTF1984/EV_PCS_Data_29277.pdf`
- **Source Organisation:** Bureau of Energy Efficiency (BEE), Ministry of Power, Government of India
- **Download Status:** **Downloaded & Extracted**
  - Original PDF: `data/raw/charging/BEE_EV_PCS_Data_29277_20251026.pdf` (7,942,286 bytes; 1,159 pages)
  - Extracted CSV: `data/raw/charging/BEE_EV_PCS_Data_29277_20251026_extracted.csv` (39,641 rows × 13 columns; 6,674,017 bytes)
- **Actual Fields Exposed (12 Columns in PDF):**
  1. `CPO Name` (Charge Point Operator brand/organisation, e.g., `IOCL`, `UJOY`, `BPCL`, `Reliance BP`, `Tata Power`, `HPCL`, `Ather`)
  2. `Govt/Private` (`Govt.` = 20,945 rows; `Private` = 18,696 rows)
  3. `State` (State/UT name)
  4. `District` (District name)
  5. `City/Village` (City/Town/Village name)
  6. `Location` (Street address / landmark description)
  7. `Latitude` (Decimal degrees, 6 decimal places)
  8. `Longitude` (Decimal degrees, 6 decimal places)
  9. `Types of Chargers Installed/ Connector` (e.g., `LEV AC Charge point`, `Bharat AC-001`, `CCS`, `Type-II AC`, `CCS-II`, `Bharat DC-001`, `LEV DC Charge Point (IS-17017-2-7)`)
  10. `Charger Rating` (Rated power of charger in kW)
  11. `Connector Rating` (Rated power of connector in kW)
  12. `No. of Connector` (Integer count of connectors for that row)
- **Reporting Period & Freshness:** Explicitly titled *"EV Public Charging Stations Data till 26th October 2025"*. Internal PDF metadata shows creation/modification on **17 February 2026** (`D:20260217123234`) by `Microsoft Excel`.
- **Geographic Granularity:** Exact station coordinates (`Latitude`, `Longitude`), `City/Village`, `District`, and `State`.
- **Units & Station-vs-Connector Reconciliation:**
  - The PDF filename `EV_PCS_Data_29277.pdf` indicates **29,277 Public Charging Stations (EVPCS)**.
  - The PDF table contains **39,641 rows** and **44,066 total connectors** (`sum(No. of Connector)`), with **29,117 unique `(Latitude, Longitude)` coordinate pairs** and **29,371 unique `(CPO Name, Location, Latitude, Longitude)` combinations**.
  - Why are there 39,641 rows for ~29,277 stations? Because stations with multiple charger types (e.g., one CCS charger + one Bharat AC-001 charger) or multiple identical charger units at the same site are listed as separate rows sharing the same coordinates and address (8,428 rows are exact duplicates across all 12 columns representing multiple identical single-connector chargers at the same station).
- **Licence / Access Constraints:** Publicly disclosed on the official BEE portal for consumer/stakeholder information; standard Government of India attribution applies.
- **Limitations:**
  - Missing fields compared to ideal schema: No explicit `Station_ID`, no `Operational_Status` (operational vs. non-working), no `Access_Type` (public vs. restricted fleet/workplace), and no `Last_Verified_Date` per row.
  - Coordinate anomalies: **3 rows** have non-numeric coordinates (Row 25827 UJOY Raigad and Row 35953 HPCL Kannauj have blank `Latitude`; Row 36796 IOCL Mathura has `###########` Excel column-width overflow in `Longitude`), and **104 IOCL rows** have `Latitude == Longitude` (where Latitude was accidentally pasted into both columns).
  - Unstandardised text casing: 46 distinct `State` strings exist for 36 States/UTs (e.g., `Kerala` vs `KERALA`, `Tamil Nadu` vs `Tamil nadu`, `Uttrakhand`), and 1,288 distinct `District` strings.

#### Source 2.2: PIB / MHI OMC Charging Update (27 March 2026)
- **Verified URL:** `https://www.pib.gov.in/PressReleasePage.aspx?PRID=2246042&lang=1&reg=1`
- **Source Organisation:** Ministry of Heavy Industries (MHI) via Press Information Bureau (PIB), Rajya Sabha written reply by Minister of State Shri Bhupathiraju Srinivasa Varma
- **Download Status:** **Downloaded & Extracted**
  - Raw HTML: `data/raw/charging/PIB_PRID_2246042_OMC_EVPCS_20260327.html`
  - Extracted Table: `data/raw/charging/PIB_PRID_2246042_OMC_Statewise_EVPCS_20260301.csv` (38 rows × 10 columns)
- **Actual Fields Exposed:**
  - Table 1 (FAME-II Financial Status as on 18.03.2026): `Scheme` (`FAME-II`), `Amount Sanctioned` (`912.50` Cr), `Amount Released` (`895.48` Cr), `Amount Utilised` (`655.43` Cr). Also notes Rs. 2,000 Cr allocated under PM E-DRIVE with Rs. 0 released for EVPCS as on 24.03.2026.
  - Annexure Table (State-wise OMC EVPCS as on 01.03.2026): `State`, `FY20-21`, `FY21-22`, `FY22-23`, `FY23-24`, `FY24-25`, `FY25-26 (upto 01.03.26)` [split into `Installed` and `Decommissioned`], `Total EVPCS installed in last five years` (**27,737**), `Total EVPCS operational` (**22,753**).
- **Reporting Period & Freshness:** Published **27 March 2026**; OMC counts as on **01 March 2026**.
- **Geographic Granularity:** State/UT aggregate level (37 rows: 36 States/UTs plus a separate row for `Leh` showing 5 installed in FY24-25 and 5 decommissioned).
- **Limitations:** Covers **Oil Marketing Companies (OMCs) only**; does not provide coordinates or district breakdowns. Crucially states: *"Data regarding EV Public Charging Stations (EVPCS) in Tier-2 and Tier-3 cities, as well as along national highways, is not centrally maintained by MHI."* Also reveals an **18.0% commissioning gap** among OMC stations (22,753 operational out of 27,737 installed).

#### Source 2.3: PIB / MHI FAME-II Operational Chargers Update (27 March 2026)
- **Verified URL:** `https://www.pib.gov.in/PressReleasePage.aspx?PRID=2246045&lang=1&reg=1`
- **Source Organisation:** Ministry of Heavy Industries (MHI) via PIB
- **Download Status:** **Downloaded & Extracted**
  - Raw HTML: `data/raw/charging/PIB_PRID_2246045_FAMEII_EVPCS_20260327.html`
  - State Table: `data/raw/charging/PIB_PRID_2246045_FAMEII_Statewise_EVPCS_20260301.csv` (36 rows)
  - PSE Table: `data/raw/charging/PIB_PRID_2246045_FAMEII_PSE_Entities_20260301.csv` (5 rows)
- **Actual Fields Exposed:**
  - Body text & summary table: As on 01.03.2026, **6,645 EVPCS are operational against 9,332 sanctioned** under FAME-II pan-India, with explicit approved vs. operational counts for Maharashtra (`670` approved, `615` operational) and Uttar Pradesh (`937` approved, `456` operational).
  - Annexure Table A: `S. No.`, `State`, `No. of chargers installed as on 01.03.2026` under FAME-II by OMCs (Total = **8,932** across 36 States/UTs).
  - Annexure Table B: `S. No`, `OMCs/Entities`, `No. of EVPCS installed as on 01.03.2026` by other PSEs (`CESL`: 97, `REIL`: 49, `KSEB`: 30, `SMC`: 50, `POWERGRID`: 1; Total = **227**).
- **Reporting Period & Freshness:** Published **27 March 2026**; data as on **01 March 2026**.
- **Limitations:** Scheme-specific subset (FAME-II only); state-wise operational vs. installed split is only provided for 2 states in the body table while the 36-state Annexure reports *installed* FAME-II OMC chargers.

#### Source 2.4: Delhi Switch Delhi Portal (`ev.delhi.gov.in`)
- **Verified URL:** `https://ev.delhi.gov.in/` and `https://ev.delhi.gov.in/charging-station`
- **Source Organisation:** Transport Department / Dialogue and Development Commission (DDC), Government of NCT of Delhi
- **Download Status:** **Downloaded & Extracted**
  - Raw HTML: `data/raw/charging/Delhi_SwitchDelhi_charging_station_20261019.html` (2,678,126 bytes)
  - Extracted JSON: `data/raw/charging/Delhi_SwitchDelhi_charging_stations_20261019.json` (891 records; 708,874 bytes)
  - Extracted CSV: `data/raw/charging/Delhi_SwitchDelhi_charging_stations_20261019.csv` (891 rows × 25 columns; 232,574 bytes)
- **Actual Fields Exposed (22 Raw JSON Keys + 3 Flattened Keys):**
  - `id` (Station ID, e.g., `S01`, `CDEL00118`)
  - `name` (Station name; populated on 197 records)
  - `vendor` (Operator/CPO name, e.g., `REVOS`, `ElectriVa`, `BSES Yamuna Power Limited (BYPL)`, `Echargeup`, `Massive Mobility`, ` Greenfuel Energy Solutions`, `EESL`, `TPDDL`)
  - `charging_type` (`Charging` = 573 stations; `Battery swapping` = 318 stations)
  - `charger_type` (Connector/EVSE standard, e.g., `BOLT 16A LITE 240V 5A/15A Socket` [380], `LEV AC` [71], `DC-001` [67], `BEVC DC 001` [19], `TYPE - 2` [19], `BEVC-AC001` [6], `BEVC AC 001` [5], `AC Type 2` [2], `CCS Type 2 DC Charger` [1], `CCS2/CHADEMO/TYPE 2 AC` [1], `CCS/ CHAdeMO` [1])
  - `capacity` (Power rating string, e.g., `3.3kw`, `15kw`, `22kw`, `50kw`, `142kW`)
  - `no_of_chargers` (Integer count of charging points/dockets at the station; sum = **6,841**)
  - `available` (Integer count; identical to `no_of_chargers` = **6,841**)
  - `if_battery_swap_station,_no._of_dockets` (Docket count for swap stations)
  - `cost_per_unit` (Tariff in INR/kWh, e.g., `0`, `10`, `12`, `15`)
  - `address`, `postal_code` (6-digit Delhi PIN code), `city`, `country`
  - `latitude`, `longitude`, and nested `coordinates: {latitude, longitude}`
  - `open`, `close`, `timing` (Operating hours), `payment_modes`, `staff` (`Staffed` / `Unstaffed`), `contact_number`
  - `region` (Derived from the page's `region_based` PIN-to-district dictionary: `East Delhi`, `South Delhi`, `West Delhi`, `South West Delhi`, `North West Delhi`, `Central Delhi`, `North Delhi`, `North East Delhi`)
- **Reporting Period & Freshness:** Live snapshot extracted on **19 October 2026**.
- **Limitations:**
  1. **Expired SSL Certificate:** `https://ev.delhi.gov.in/` has an expired X.509 certificate, causing standard browsers and strict HTTP clients to block access unless TLS verification is bypassed (`verify=False`).
  2. **Broken Sub-portals:** `https://ev.delhi.gov.in/openev/` returns `HTTP 502 Bad Gateway` (Nginx), and `https://ev.delhi.gov.in/ev-dashboard` times out after 20 seconds.
  3. **Missing Coordinates on Battery Swap Stations:** All **573 EV Charging stations (100.0%)** have valid coordinates, whereas **121 of the 318 Battery Swapping stations (38.1%)** have empty `latitude`/`longitude` strings (they still have full street addresses and 6-digit PIN codes).
  4. **Outdated `region_based` PIN Dictionary:** 103 stations have valid Delhi PIN codes (e.g., `110001`, `110085`, `110059`) that were omitted from the portal's hardcoded `region_based` JavaScript dictionary, leaving `New Delhi` with 0 assigned stations in the portal's regional tab. Point-in-polygon spatial join against district polygons fixes this completely.

#### Source 2.5: OpenStreetMap Charging Stations (`amenity=charging_station`)
- **Verified URL:** Wiki specification: `https://wiki.openstreetmap.org/wiki/Tag:amenity%3Dcharging_station` | Data extracted via Overpass API (`https://overpass-api.de/api/interpreter`)
- **Source Organisation:** OpenStreetMap Contributors
- **Download Status:** **Downloaded & Extracted**
  - `data/raw/charging/OSM_India_charging_stations_20261019.json` (725 elements)
  - `data/raw/charging/OSM_India_charging_stations_20261019.csv` (725 rows × 27 columns)
- **Actual Fields Exposed:** `osm_id`, `osm_type` (`node`/`way`/`relation`), `timestamp`, `latitude`, `longitude`, `name`, `operator`, `brand`, `network`, `capacity`, `output`, `access`, `fee`, `opening_hours`, `operational_status`, vehicle access tags (`motorcar`, `motorcycle`, `scooter`, `bicycle`, `bus`, `hgv`), address tags (`addr:state`, `addr:district`, `addr:city`, `addr:postcode`), and connector socket tags (`sockets_json`, e.g., `socket:type2`, `socket:ccs2`, `socket:chademo`).
- **Reporting Period & Freshness:** Live OSM snapshot as on **19 October 2026**.
- **Licence / Access Constraints:** **Open Database License (ODbL 1.0)** — requires attribution (`© OpenStreetMap contributors`) and share-alike if an adapted database is publicly distributed.
- **Limitations:** Severe crowd-sourced under-coverage nationally (**725 features** across the India bounding box vs. **29,277 stations** in BEE) and sparse tag completion (`operator` missing in 68.1%, `capacity` in 75.7%, `sockets` in 92.0%, `output` power in 99.3%, `operational_status` in 100.0%). Notably, **182 of the 725 OSM charging stations (25.1%)** are located inside NCT of Delhi.

---

### 2.3 Layer 3: Geographic & Administrative Boundaries

#### Source 3.1: DataMeet Maps Repository
- **Verified URLs:** `https://github.com/datameet/maps` and `https://projects.datameet.org/maps/`
- **Source Organisation:** DataMeet Community Maps Project
- **Download Status:** **Downloaded**
  - State Boundaries (Shapefile): `data/raw/boundaries/Admin2.shp` (`.shx`, `.dbf`, `.prj`, `.cpg`) — 36 State/UT polygons
  - District Boundaries (Shapefile): `data/raw/boundaries/2011_Dist.shp` (`.shx`, `.dbf`, `.prj`) — 641 District polygons
  - Country Composite Boundary (GeoJSON): `data/raw/boundaries/india-composite.geojson`
  - Documentation & Licence: `data/raw/boundaries/DataMeet_LICENSE.txt`, `data/raw/boundaries/DataMeet_README.md`
- **Actual Fields Exposed:**
  - `Admin2.dbf` (36 rows): `ST_NM` (State/UT name, e.g., `Delhi`, `Maharashtra`, `Ladakh`, `Dadra and Nagar Haveli and Daman and Diu`).
  - `2011_Dist.dbf` (641 rows): `DISTRICT` (District name), `ST_NM` (State/UT name, e.g., `NCT of Delhi`), `ST_CEN_CD` (2011 Census State code, e.g., `7` for Delhi), `DT_CEN_CD` (2011 Census District code, `1`–`9` for Delhi), `censuscode` (3-digit national district code, `90`–`98` for Delhi).
- **Reporting Period & Freshness:** `Admin2.shp` reflects post-2019/2020 State/UT reorganization (36 States/UTs). `2011_Dist.shp` is Census 2011 vintage (641 districts).
- **Licence / Access Constraints:** **Creative Commons Attribution 4.0 International (CC BY 4.0)** verified in `LICENSE` and `README.md`.
- **Limitations:**
  - `Admin2.dbf` has no numeric code column (`ST_NM` only), and spells Delhi as `Delhi` whereas `2011_Dist.dbf` spells it as `NCT of Delhi`.
  - `2011_Dist.shp` predates post-2011 district creations (e.g., Telangana's 33 districts, Andhra Pradesh's 26 districts, and Delhi's 2012 creation of *South East* and *Shahdara* districts bringing Delhi from 9 to 11 revenue districts). Point-in-polygon spatial joins work seamlessly for all geocoded chargers, while district-name tabular joins require a crosswalk.

---

### 2.4 Layer 4: Road & Mobility Network

#### Source 4.1: Geofabrik India OSM Extract & Overpass Pilot Road Extract
- **Verified URL:** `https://download.geofabrik.de/asia/india.html`
- **Source Organisation:** Geofabrik GmbH / OpenStreetMap Contributors
- **Download Status:** **Downloaded (Metadata/Polygon + Complete Delhi Pilot Road Network)**
  - `data/raw/roads/geofabrik_india.poly` & `data/raw/roads/geofabrik_india.kml`
  - `data/raw/roads/OSM_Delhi_major_roads_20261019.json` & `data/raw/roads/OSM_Delhi_major_roads_20261019.csv` (8,087 major road ways in Delhi NCR bbox)
- **Actual Fields Exposed:**
  - On Geofabrik server: `india-latest.osm.pbf` (1.6 GB, updated **2026-10-18T20:25:06Z**) and 6 regional sub-extracts (`northern-zone`, `southern-zone`, `western-zone`, `eastern-zone`, `central-zone`, `north-eastern-zone`) in both `.osm.pbf` and `.gpkg.zip` formats. Note that national `india-latest-free.shp.zip` is explicitly discontinued by Geofabrik due to size limit.
  - In `OSM_Delhi_major_roads_20261019.csv` (8,087 rows): `osm_way_id`, `highway_class` (`motorway` [793], `trunk` [1,393], `primary` [1,442], `secondary` [4,459]), `ref` (NH/SH route number), `name`, `oneway`, `lanes`, `surface`, `maxspeed`, `access`, `center_lat`, `center_lon`.
- **Licence / Access Constraints:** **ODbL 1.0**.
- **Limitations:** Static physical network attributes only; does not contain traffic volume (AADT/PCU), congestion, or travel-time matrices.

---

### 2.5 Layer 5: Demographic & Economic Activity

#### Source 5.1: WorldPop India Population Counts (`id=50771` & 1km GeoTIFF)
- **Verified URL:** `https://hub.worldpop.org/geodata/summary?id=50771`
  - Direct 2024 100m GeoTIFF URL (1.65 GB): `https://data.worldpop.org/GIS/Population/Global_2015_2030/R2024A/2024/IND/v1/100m/unconstrained/ind_pop_2024_UC_100m_R2024A_v1.tif`
  - Direct 2020 1km Aggregated GeoTIFF URL (19.1 MB): `https://data.worldpop.org/GIS/Population/Global_2000_2020_1km/2020/IND/ind_ppp_2020_1km_Aggregated.tif`
- **Source Organisation:** WorldPop, University of Southampton (DOI: `10.5258/SOTON/WP00800`)
- **Download Status:** **Downloaded**
  - `data/raw/demographics/WorldPop_ind_ppp_2020_1km_Aggregated.tif` (19,086,801 bytes)
  - `data/raw/demographics/WorldPop_ID50771_India_2024_100m_metadata.html`
  - `data/raw/demographics/WorldPop_ID50771_ind_pop_2024_UC_100m_preview.png`
  - `data/raw/demographics/WorldPop_IND_catalog_metadata.json`
- **Actual Fields / Format:** Single-band floating-point GeoTIFF raster in WGS84 (`EPSG:4326`), where each pixel value represents the estimated number of people per grid square (~100m for R2024A; ~1km for the aggregated product).
- **Reporting Period & Freshness:** R2024A 100m product published **01 December 2024** for reference year **2024**; 1km aggregated raster published **22 June 2020** for reference year **2020**.
- **Licence / Access Constraints:** **Creative Commons Attribution 4.0 International (CC BY 4.0)**.
- **Limitations:** Population is a residential proxy, not a direct measure of commercial/transit EV charging demand. The 2024 100m file is 1.65 GB (`ind_pop_2024_UC_100m_R2024A_v1.tif`); the 19.1 MB 1km raster + NITI 2025 state population projections (`NITI_IEMI_2025_State_Population_GSDP.csv`) provide immediate coverage without requiring a 1.65 GB download during pre-coding.

#### Source 5.2: Census of India (`censusindia.gov.in`)
- **Verified URL:** `https://censusindia.gov.in/`
- **Download Status:** **Not Downloadable (Server Connection Timeout)**
- **Audit Evidence:** Requests to `https://censusindia.gov.in/` redirect to `http://censusindia.gov.in/census.website/` (`103.151.152.70:80`), which fails with `dial tcp 103.151.152.70:80: connectex: A connection attempt failed because the connected party did not properly respond after a period of time`.
- **Realistic Alternative Collected:** State/UT 2025 projected populations from the National Commission on Population (NCP) and 2024–25 GSDP from MoSPI were extracted directly from Section 7 of the NITI Aayog IEMI 2025 report into `data/raw/demographics/NITI_IEMI_2025_State_Population_GSDP.csv`, complemented by the WorldPop national population raster.

#### Source 5.3: Open Government Data (OGD) Platform India (`data.gov.in`)
- **Verified URL:** `https://www.data.gov.in/`
- **Download Status:** **Not Downloaded (Generic Portal Root; Bulk Export Requires JanParichay Login / API Key)**
- **Audit Evidence:** The link in the brief points to the OGD homepage (`https://www.data.gov.in/`). Downloading catalog resources on OGD redirects to `/backend/authmid/v1/login?r=&provider=Janparichay` (National Single Sign-On) or requires a registered OGD API key.

---

### 2.6 Layer 6: Electricity Infrastructure

#### Source 6.1: Central Electricity Authority (CEA) EV Charging Resources (`cea.nic.in`)
- **Verified URLs:**
  - Portal link in brief: `https://cea.nic.in/ev-charging-standards/?lang=en`
  - Direct Regulations PDF linked from BEE page: `https://cea.nic.in/wp-content/uploads/regulations_cpt/2020/09/Legal_Annexure-VI.pdf`
- **Download Status:** **Partially Downloaded** (`data/raw/electricity/CEA_Technical_Standards_Connectivity_2019_Annexure_VI.pdf` downloaded; main `/ev-charging-standards/` page blocked by login wall)
- **Audit Evidence:** Navigating to `https://cea.nic.in/ev-charging-standards/?lang=en` returns an internal CEA Dashboard Login form (`Username is required`, `Password is required`, `Enter captcha here`). Furthermore, CEA publishes national technical standards and state-level power supply aggregates, *not* distribution-level substation/transformer GIS coordinates or feeder hosting capacity.

#### Source 6.2: Ministry of Power (`powermin.gov.in`) & BEE State EV Tariff Schedule (Annexure A)
- **Verified URLs:**
  - Ministry of Power root: `https://powermin.gov.in/`
  - BEE State EV Tariff Schedule (Annexure A): `https://beeindia.gov.in/WriteReadData/RTF1984/annexure-A.pdf`
- **Download Status:** **Downloaded** (`data/raw/electricity/BEE_State_EV_Tariff_Annexure_A.pdf`, 223,655 bytes)
- **Actual Fields Exposed in BEE Annexure A:** `S. No.`, `State Name` (all 36 States/UTs), `Fixed charge (Rs / kW / month)`, `EV Tariff (Rs./unit)` split by LT and HT (e.g., Delhi: Fixed charge = `0`, EV Tariff = `LT: 4.50, HT: 4.00 Rs./unit`; Maharashtra: Fixed = `LT 75/KW, HT 75/KVA`, Tariff = `LT: 6.08, HT: 6.9 Rs./unit`).
- **Limitations:** Legacy guideline PDF URLs under `https://powermin.gov.in/sites/default/files/...` return HTTP 404 Not Found, and `https://evyatra.beeindia.gov.in/` timed out on port 443. Three northeastern states (`Arunachal Pradesh`, `Manipur`, `Nagaland`) have `"Not defined"` EV tariffs in BEE Annexure A.

#### Source 6.3: OpenStreetMap Pilot Electricity Infrastructure (`OSM_Delhi_power_infrastructure_20261019.csv`)
- **Verified URL:** Overpass API (`https://overpass-api.de/api/interpreter`)
- **Download Status:** **Downloaded & Extracted**
  - `data/raw/electricity/OSM_Delhi_power_infrastructure_20261019.json` & `.csv` (576 features in Delhi bbox)
- **Actual Fields Exposed:** `osm_id`, `osm_type`, `power_type` (`substation` = 341, `transformer` = 194, `plant` = 41), `substation_type`, `name`, `operator`, `voltage`, `rating`, `frequency`, `latitude`, `longitude`.
- **Limitations:** While 100% of the 576 power assets have exact coordinates, `voltage` is missing in 78.6%, `operator` in 80.6%, and `rating` (MVA capacity) in 99.3%. Above all, **proximity to a mapped substation does not prove spare feeder or transformer hosting capacity**.

---

### 2.7 Layer 7: Supporting Contextual Information

#### Source 7.1: NITI Aayog India Electric Mobility Index (IEMI) 2025
- **Verified URL:** `https://www.niti.gov.in/node/2424`
  - Direct PDF URL: `https://www.niti.gov.in/sites/default/files/2026-09/India-Electric-Mobility-Index-IEMI-2025.pdf`
- **Source Organisation:** NITI Aayog (prepared in partnership with WRI India)
- **Download Status:** **Downloaded & Extracted**
  - Original Report PDF: `data/raw/context/NITI_Aayog_IEMI_2025.pdf` (170 pages; 9,936,747 bytes)
  - Extracted State Table: `data/raw/demographics/NITI_IEMI_2025_State_Population_GSDP.csv` (35 state profiles extracted with NCP 2025 population, area in $\text{km}^2$, and MoSPI GSDP)
- **Reporting Period & Freshness:** Published **15 September 2026** (`09/15/2026 - 14:07`); assessment data cutoff is **December 2025** (with FY 2024–25 GSDP and 2025 NCP population projections).
- **Actual Contents & Indicators:** Evaluates all 36 States/UTs across 3 themes and 16 indicators (0–100 score scale):
  1. *Transport Electrification Progress* (EV adoption, fleet electrification)
  2. *Charging Infrastructure Readiness* (public charger density per EV, highway/fast charger share, tariff/policy enablers)
  3. *EV Research and Innovation Status* (EV startups per GSDP, R&D initiatives, patents per GSDP)
  - Top ranked states in IEMI 2025: **Delhi (Rank 1, Score 84)**, **Maharashtra (Rank 2, Score 78)**, **Karnataka (Rank 3, Score 73)**, **Chandigarh (Rank 4, Score 71)**, **Goa (Rank 5, Score 65)**, **Tamil Nadu (Rank 6, Score 61)**, **Madhya Pradesh (Rank 7, Score 59)**.
- **Limitations:** Provides composite scores (0–100) and state profile summaries rather than raw point-level datasets.

#### Source 7.2: BEE State Nodal Agencies (Annexure B) & State EV Policies
- **Verified URLs:**
  - State Nodal Agencies Excel file: `https://beeindia.gov.in/WriteReadData/RTF1984/State%20Nodal%20Agency%20for%20EV.xlsx`
  - Delhi EV Policy PDF hosted on BEE server: `https://beeindia.gov.in/WriteReadData/RTF1984/Delhi.pdf`
- **Download Status:** **Downloaded**
  - `data/raw/context/BEE_State_Nodal_Agencies_Annexure_B.xlsx` (10,913 bytes; 27 States/UTs)
  - `data/raw/context/BEE_Delhi_EV_Policy_2020.pdf` (946,530 bytes)
- **Limitations:** Note that the BEE E-Mobility page contains two sets of links for State EV Policies: links pointing to `evyatra.beeindia.gov.in/wp-content/...` (which time out because `evyatra.beeindia.gov.in` is unreachable) and links pointing to `/WriteReadData/RTF1984/<State>.pdf` on `beeindia.gov.in` (which work and download cleanly).

#### Source 7.3: OpenStreetMap Pilot Demand Attractors & Land-Use POIs
- **Verified URL:** Overpass API (`https://overpass-api.de/api/interpreter`)
- **Download Status:** **Downloaded & Extracted**
  - `data/raw/context/OSM_Delhi_demand_attractors_20261019.json` & `.csv` (3,534 geocoded POIs across NCT of Delhi)
- **Actual Fields Exposed:** `osm_id`, `osm_type`, `category` (`parking` [705], `hospital` [656], `hotel` [415], `commercial` [389], `fuel` [386], `station` [253], `industrial` [205], `retail` [171], `marketplace` [109], `attraction` [102], `bus_station` [65], `museum` [47]), `name`, `operator`, `latitude`, `longitude`.
- **Limitations:** 100% geocoded and categorized, but `name` is missing in 36.2% (primarily unnamed surface parking polygons) and `operator` is missing in 87.8%. Does not include daily footfall or parking capacity counts.
