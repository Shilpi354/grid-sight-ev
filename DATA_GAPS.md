# DATA GAPS & MITIGATION SPECIFICATION — EV Infra Map India

**Audit Date:** 19 October 2026  
**Project Scope:** National Overview (36 States/UTs) + Detailed Pilot Geography (NCT of Delhi)  
**Companion Documents:** [`DATA_AVAILABILITY_AUDIT.md`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/DATA_AVAILABILITY_AUDIT.md) | [`DATA_QUALITY_REPORT.md`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/DATA_QUALITY_REPORT.md) | [`data/source_manifest.csv`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/source_manifest.csv)

---

## Executive Overview of Data Gaps

While our pre-coding collection recovered **39,641 geocoded public charger records** from BEE (`EV_PCS_Data_29277`), **891 official Delhi charging/swapping stations**, **10,689,490 active EV registrations** across all 36 States/UTs from VAHAN, **725 OSM charging stations**, and supporting boundary, road, population, tariff, and grid datasets, several structural gaps remain across Indian public EV infrastructure and mobility portals.

In strict adherence to the project brief, **no missing fields have been fabricated or silently imputed**. Every gap is catalogued below with:
1. **Exact Missing Fields / Granularity**
2. **Official Source URL & Failure / Restriction Mechanism**
3. **Manual Steps or Institutional Permissions Required**
4. **Verified Workaround / Alternative Dataset Used for Implementation**

---

## 1. Public Charging Station Registry Gaps

### Gap 1.1: Station-Level Operational Status, Real-Time Availability, and Unique Station ID in BEE EVPCS
- **Official Source URL:** `https://beeindia.gov.in/en/ev-public-charging-stations` (`https://beeindia.gov.in/sites/default/files/2026-02/EV_PCS_Data_29277_20251026.pdf`)
- **Exact Missing Fields:**
  - `Station_ID` (unique persistent identifier linking multiple connectors/dispensers at the same physical site)
  - `Operational_Status` (`Operational`, `Awaiting Grid Connection`, `Under Maintenance`, `Decommissioned`)
  - `Real_Time_Occupancy` (live connector availability via OCPI/OCPP)
  - `Access_Restriction` (`24x7 Public`, `Restricted / Gated Commercial`, `Fleet / Bus Depot Only`)
  - `Tariff_INR_per_kWh` (station-specific user charging fee)
  - `Commissioning_Date` / `Last_Verified_Timestamp`
  - `Highway_Classification` (`National Highway`, `State Highway`, `Urban`, `Tier-2/Tier-3 City`)
- **Why Unavailable:** BEE publishes a static PDF export of CPO submissions (`39,641` charger/connector rows representing `29,277` stations as of 26 October 2025). Furthermore, the Ministry of Heavy Industries explicitly stated in Lok Sabha Unstarred Question No. 4169 ([`PIB_PRID_2246045_FAMEII_EVPCS_20260327.html`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/charging/PIB_PRID_2246045_FAMEII_EVPCS_20260327.html)):
  > *"The data related to number of EV public charging stations installed in Tier 2 and Tier 3 cities and along National Highways is not maintained centrally in Ministry of Heavy Industries."*
- **Impact of Gap:** As proven by MoPNG's Lok Sabha reply ([`PIB_PRID_2246042_OMC_Statewise_EVPCS_20260301.csv`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/charging/PIB_PRID_2246042_OMC_Statewise_EVPCS_20260301.csv)), out of **27,737** OMC EV charging stations installed nationwide as of 01.03.2026, only **22,753 (82.03%)** are operational—with severe commissioning lags in states such as Maharashtra (`1,599` operational out of `3,389` installed, or `47.18%`). Treating all `39,641` BEE rows as active stations overstates operational capacity by ~18% on OMC networks.
- **Manual Steps / Permissions Required to Obtain Official Field:**
  1. Request OCPI 2.2.1 read-only credentials from BEE's **National Unified EV National Portal / EV Yatra** (`https://evyatra.beeindia.gov.in`) or State Nodal Agencies listed in [`BEE_State_Nodal_Agencies_Annexure_B.xlsx`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/context/BEE_State_Nodal_Agencies_Annexure_B.xlsx).
  2. File RTI / academic data requests with IOCL, BPCL, and HPCL retail automation divisions for station-level commissioning dates and operational flags.
- **Realistic Alternative / Analytical Mitigation:**
  1. **Synthetic `Station_ID` Clustering:** Group the `39,641` BEE rows by `(CPO_Name, Normalized_Location, round(Latitude, 4), round(Longitude, 4))` to reconstruct the **29,117–29,371 unique physical stations** while preserving total connector counts (`44,066` connectors) and summed kW capacity.
  2. **State-Level Operational Discount Factor:** Apply MoPNG's state-wise `Operational / Installed` ratio from [`PIB_PRID_2246042_OMC_Statewise_EVPCS_20260301.csv`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/charging/PIB_PRID_2246042_OMC_Statewise_EVPCS_20260301.csv) to OMC rows (`IOCL`, `BPCL`, `HPCL`) when computing effective operational charger supply.
  3. **Spatial Highway Tagging:** Spatially buffer National and State Highways (`motorway`, `trunk`, `primary`) from OpenStreetMap by `250m–500m` to classify BEE stations into Highway Corridor vs. Urban/Rural stations.

---

### Gap 1.2: Delhi OpenEV Portal (`502 Bad Gateway`) & Un-Geocoded Battery Swapping Stations
- **Official Source URLs:**
  - `https://ev.delhi.gov.in/openev/` (and `https://ev.delhi.gov.in/openev/data-explorer`)
  - `https://ev.delhi.gov.in/charging-station`
- **Exact Missing Fields:**
  1. **OpenEV Live OCPI Feed (`/openev/`):** Dynamic session utilization, real-time connector status (`AVAILABLE` / `CHARGING` / `OUTOFORDER`), and historical hourly occupancy curves.
  2. **Switch Delhi Battery Swapping Coordinates:** Out of **891** stations scraped from `ev.delhi.gov.in/charging-station` ([`Delhi_SwitchDelhi_charging_stations_20261019.csv`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/charging/Delhi_SwitchDelhi_charging_stations_20261019.csv)), all **573 EV Charging stations (100%)** have valid latitude/longitude, but **121 out of 318 Battery Swapping stations (38.05%)** have empty `latitude` and `longitude` strings (`""`), alongside `nil` values in `capacity` and `charger_type`.
  3. **Incomplete PIN-to-Region Mapping in Switch Delhi:** `103` rows (`11.56%`) have `"region": ""` because the portal's frontend JavaScript PIN lookup dictionary omits several valid Delhi PIN codes (e.g., `110056`, `110090`, `110097`).
- **Why Unavailable:**
  - `https://ev.delhi.gov.in/openev/` returns `HTTP 502 Bad Gateway (nginx/1.18.0 (Ubuntu))` because the upstream Node.js/Python OpenEV microservice hosted by the Transport Department, GNCTD is offline.
  - On `https://ev.delhi.gov.in/charging-station`, battery swapping operators (primarily Sun Mobility / Battery Smart batches) submitted street addresses and PIN codes without decimal coordinates for 121 kiosks.
- **Manual Steps / Permissions Required:**
  - Contact the **EV Cell, Transport Department, GNCTD** (`5/9 Under Hill Road, Delhi - 110054`) or **Dialogue and Development Commission of Delhi (DDCD)** to report the `502 Bad Gateway` on `/openev/` and request the backend CSV dump of OpenEV static & dynamic tables.
- **Realistic Alternative / Analytical Mitigation:**
  1. **Use Verified Switch Delhi + BEE Delhi Extracts:** Combine Switch Delhi's **770 geocoded stations** (`573` charging + `197` swapping) with BEE's **3,475 Delhi charger records** (`1,960` unique coordinate pairs)—keeping both layers distinct in the UI toggle and deduplicating spatially within `50m` for composite coverage analysis.
  2. **PIN-Code & Address Geocoding for the 121 Swap Stations:** Every one of the 121 un-geocoded battery swapping stations has a populated `address` and `6-digit PIN code` (e.g., `110041`, `110043`, `110059`). They can be assigned to their exact Delhi District/Ward via PIN-to-District lookup or geocoded via Nominatim/OpenStreetMap street matching (flagged as `geocoded_from_address = true`).
  3. **Spatial Point-in-Polygon Region Assignment:** Replace Switch Delhi's incomplete PIN dictionary with a direct spatial join (`ST_Within`) against [`2011_Dist.shp`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/boundaries/2011_Dist.shp) so 100% of geocoded Delhi stations receive an official district name.

---

## 2. EV Registration & Fleet Demand Gaps (VAHAN)

### Gap 2.1: District-Level National VAHAN Table & Monthly Time-Series Export
- **Official Source URL:** `https://vahan.parivahan.gov.in/vahan4dashboard/` (`vahan/view/reportview.xhtml`)
- **Exact Missing Fields:**
  - Direct single-click CSV download of **District-level** (`780+` districts) or **All-India RTO-level** (`1,400+` RTOs) EV registrations across all 36 States/UTs simultaneously.
  - Pre-packaged **Monthly EV Registration Time-Series** (`YYYY-MM` by state and vehicle class) in a single bulk file.
  - **Home / Overnight Parking Location** vs. **Registering RTO Jurisdiction** (especially for centralized commercial RTOs).
- **Why Unavailable:**
  - VAHAN's JSF/PrimeFaces application enforces stateful `jakarta.faces.ViewState` tokens and only exposes RTO dropdown options *after* a single state is selected in the session state.
  - Even in the pilot geography (**NCT of Delhi**, where we extracted all **23 RTO entries** in [`VAHAN_Delhi_RTO_ev_summary_20261019.csv`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/vahan/VAHAN_Delhi_RTO_ev_summary_20261019.csv)), commercial fleets are registered at centralized non-geographic transport units rather than residential districts:
    - `RAJPUR ROAD/VIU BURARI - DL51`: **46,660 EVs** (`41,374` 3W, `5,151` Bus)
    - `BURARI TAXI UNIT - DL52`: **15,227 EVs** (`11,039` 4W taxis, `3,421` goods)
    - `BURARI AUTO UNIT - DL53`: **2,836 EVs** (`2,704` 3W)
  - Furthermore, **Telangana** only joined the central VAHAN4 portal recently (showing `27,821` active EVs on VAHAN vs. ~`2.1 lakh` cumulative historical EVs on the Telangana RTA portal).
- **Manual Steps / Permissions Required:**
  - Automated iteration across all 36 states × 1,400+ RTOs via VAHAN's AJAX endpoint requires ~1,500 sequential POST requests (risking WAF IP throttling).
  - For Telangana historical registrations prior to VAHAN onboarding, download the Telangana Open Data RTA quarterly dumps (`https://data.telangana.gov.in/`).
- **Realistic Alternative / Analytical Mitigation:**
  1. **National Overview at State Granularity + Pilot at RTO/District Granularity:** Use our verified 36-State VAHAN datasets ([`VAHAN_state_ev_summary_20261019.csv`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/vahan/VAHAN_state_ev_summary_20261019.csv), [`VAHAN_state_ev_by_subcategory_20261019.csv`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/vahan/VAHAN_state_ev_by_subcategory_20261019.csv), [`VAHAN_state_ev_yearwise_20261019.csv`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/vahan/VAHAN_state_ev_yearwise_20261019.csv)) for the National Overview, and our 23-RTO Delhi extract ([`VAHAN_Delhi_RTO_ev_summary_20261019.csv`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/vahan/VAHAN_Delhi_RTO_ev_summary_20261019.csv)) for the Delhi Pilot.
  2. **RTO-to-District Crosswalk & Commercial Fleet Redistribution in Delhi:** Map the 13 geographic Delhi RTOs (`DL1` to `DL13`) to Delhi's districts, and distribute the centralized Burari commercial fleet (`DL51`, `DL52`, `DL53` = `64,723` commercial EVs) across districts in proportion to commercial demand attractors (`3,534` transit/commercial POIs in [`OSM_Delhi_demand_attractors_20261019.csv`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/context/OSM_Delhi_demand_attractors_20261019.csv)) or zone population, clearly documenting both raw RTO counts and redistributed district demand.

---

## 3. Administrative Boundary & Standardization Gaps

### Gap 3.1: Census 2011 (641 Districts) vs. 2026 Administrative Reality (~780+ Districts) & LGD Codes
- **Official Source URLs:**
  - Survey of India (`https://surveyofindia.gov.in`) & Bharat Maps (`https://bharatmaps.gov.in`)
  - Local Government Directory (`https://lgdirectory.gov.in`)
  - DataMeet (`https://github.com/datameet/maps`)
- **Exact Missing Fields:**
  - Openly redistributable 2026 district polygons incorporating post-2011 district bifurcations (e.g., Telangana's 33 districts vs. 10 in 2011; Andhra Pradesh's 26 districts; newly created districts in Rajasthan, Assam, Chhattisgarh, and Delhi's 11 revenue districts vs. 9 Census 2011 districts).
  - Standardized **Local Government Directory (LGD) State & District Codes** in BEE (`EV_PCS_Data_29277`), Switch Delhi, and VAHAN outputs.
- **Why Unavailable:**
  - Survey of India digital boundary shapefiles require individual National Geospatial Policy login/indemnity clearance (`surveyofindia.gov.in`) and cannot be fetched via unauthenticated scripts.
  - BEE's charger table uses free-text `State` (`46` distinct strings for 36 states/UTs due to casing/typos like `KERALA` vs `Kerala`, `Uttrakhand` vs `Uttarakhand`) and free-text `District` (`1,288` distinct strings including cities, tehsils, and spelling variants).
- **Manual Steps / Permissions Required:**
  - Register via Parichay / Survey of India portal (`https://onlinemaps.surveyofindia.gov.in`) to download updated 2024–2026 administrative boundary shapefiles with LGD codes.
- **Realistic Alternative / Analytical Mitigation:**
  1. **Point-in-Polygon Spatial Standardization (Bypassing String Joins):** Because **99.70% of BEE rows** (`39,522 / 39,641`) and **100% of geocoded Switch Delhi / OSM chargers** have decimal `(Latitude, Longitude)`, we do **not** rely on fragile district name string matching. Instead, we perform an exact spatial join (`Point-in-Polygon`) of all charger coordinates against [`Admin2.shp`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/boundaries/Admin2.shp) (`36` States/UTs) and [`2011_Dist.shp`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/boundaries/2011_Dist.shp) (`641` districts).
  2. **Deterministic State Name Normalization Table:** Map all `46` BEE state strings and `38` PIB OMC state strings to the exact `36` canonical `ST_NM` values in `Admin2.shp` and VAHAN.

---

## 4. Electricity Grid & Distribution Feeder Capacity Gaps

### Gap 4.1: Substation/Feeder Available Hosting Capacity (MVA) & DISCOM Sanctioned Load Data
- **Official Source URLs:**
  - Central Electricity Authority (`https://cea.nic.in/distribution-general/`)
  - Delhi DISCOMs (BSES Rajdhani, BSES Yamuna, Tata Power DDL)
- **Exact Missing Fields:**
  - `Available_Hosting_Capacity_MVA` / `Peak_Load_Utilization_%` at individual 66/11 kV and 33/11 kV distribution substations and 11 kV feeders.
  - `Transformer_Available_kVA` for distribution transformers (DTs) near proposed charging sites.
  - `Sanctioned_EV_Load_kW` per charging station in BEE and Switch Delhi datasets.
- **Why Unavailable:**
  - `https://cea.nic.in/distribution-general/` redirects to `https://cea.nic.in/wp-login.php` (HTTP 302 authentication wall).
  - Utility feeder loading and DT spare capacity are treated as restricted operational data by state DISCOMs (though BSES Rajdhani/Yamuna and TPDDL host interactive GIS portals for new connection applicants, bulk GeoJSON export is disabled).
  - In our OpenStreetMap power infrastructure extract for Delhi ([`OSM_Delhi_power_infrastructure_20261019.csv`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/electricity/OSM_Delhi_power_infrastructure_20261019.csv), `576` features: `341` substations, `194` transformers, `41` plants), **100%** have valid coordinates, but **78.65%** lack `voltage` tags and **99.31%** lack `rating` (MVA) tags.
- **Manual Steps / Permissions Required:**
  - Obtain DISCOM feeder loading data from the Delhi Electricity Regulatory Commission (DERC) tariff order filings or apply for academic research access with TPDDL / BSES GIS cells.
- **Realistic Alternative / Analytical Mitigation:**
  1. **Substation Proximity as Grid-Access Proxy:** Use the **341 mapped substations and 194 transformers** in [`OSM_Delhi_power_infrastructure_20261019.json`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/electricity/OSM_Delhi_power_infrastructure_20261019.json) to calculate **Distance to Nearest Substation/Transformer (`m`)** for every candidate charging zone in the Delhi Pilot. Sites within `<500m` of an existing substation require substantially lower upstream cable trenching and grid-upgrade capex.
  2. **Tariff & Fixed-Charge Economic Layer:** Combine substation proximity with state-wise EV tariff rates (`Rs/kWh`) and fixed demand charges (`Rs/kVA/month`) extracted from [`BEE_State_EV_Tariff_Annexure_A.pdf`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/electricity/BEE_State_EV_Tariff_Annexure_A.pdf) and technical connection standards from [`CEA_Technical_Standards_Connectivity_2019_Annexure_VI.pdf`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/electricity/CEA_Technical_Standards_Connectivity_2019_Annexure_VI.pdf).

---

## 5. Road Network, Traffic Volume, and Demographics Gaps

### Gap 5.1: Highway Traffic Counts (AADT), Commercial EV Corridor Flows, and Travel Speeds
- **Official Source URLs:**
  - NHAI / MoRTH Road Transport Year Book
  - OpenStreetMap (`https://download.geofabrik.de/asia/india.html`)
- **Exact Missing Fields:**
  - `AADT` (Annual Average Daily Traffic) and `EV_Share_of_Traffic` per highway segment.
  - Observed peak/off-peak `Average_Speed_kmph`.
  - Complete `lanes` (missing on `54.10%` of OSM Delhi major road segments) and `maxspeed` (missing on `71.16%` of OSM Delhi major road segments in [`OSM_Delhi_major_roads_20261019.csv`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/roads/OSM_Delhi_major_roads_20261019.csv)).
- **Why Unavailable:**
  - NHAI toll-plaza FASTag traffic volumes are not published as an open geospatial layer with link-level coordinates.
- **Realistic Alternative / Analytical Mitigation:**
  - Use **OSM Highway Hierarchy (`motorway`, `trunk`, `primary`, `secondary`)** (`8,087` segments in Delhi) weighted by **Demand Attractor Density** (`3,534` POIs across fuel stations, metro stations, bus terminals, parking lots, malls, hospitals, and industrial/commercial hubs in [`OSM_Delhi_demand_attractors_20261019.csv`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/context/OSM_Delhi_demand_attractors_20261019.csv)) and **Gridded Population Density** ([`WorldPop_ind_ppp_2020_1km_Aggregated.tif`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/demographics/WorldPop_ind_ppp_2020_1km_Aggregated.tif)) as a transparent composite proxy for corridor charging demand.

---

### Gap 5.2: Census of India Server Timeout & 2021/2026 Ward-Level Census Tables
- **Official Source URL:** `https://censusindia.gov.in` & `https://www.data.gov.in`
- **Exact Missing Fields:**
  - Post-2011 official decennial Census ward/town population and household vehicle ownership tables.
  - Direct anonymous API/CSV downloads from `data.gov.in` (which redirects download requests to `https://www.data.gov.in/user/login` via JanParichay SSO).
- **Why Unavailable:**
  - `https://censusindia.gov.in` timed out (`ConnectionTimeoutError` after 30s) during automated audit, and the decennial Census post-2011 has not yet been published.
  - `data.gov.in` enforces interactive user login + reason-for-download form submission before serving raw CSV files.
- **Realistic Alternative / Analytical Mitigation:**
  1. **State-Level 2025 Official Population & GSDP:** Use our extracted table [`NITI_IEMI_2025_State_Population_GSDP.csv`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/demographics/NITI_IEMI_2025_State_Population_GSDP.csv) from NITI Aayog's *India Electric Mobility Index 2025* report ([`NITI_Aayog_IEMI_2025.pdf`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/context/NITI_Aayog_IEMI_2025.pdf)), which compiles the **National Commission on Population (NCP) 2025 projected population**, **Area ($\text{km}^2$)**, and **MoSPI GSDP (INR Crores)** for 35 States/UTs (with Ladakh's population/area calculated from Census/Survey of India baselines).
  2. **Sub-District / Grid-Cell Population:** Use the downloaded **WorldPop 1km UN-Adjusted Population Raster** ([`WorldPop_ind_ppp_2020_1km_Aggregated.tif`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/raw/demographics/WorldPop_ind_ppp_2020_1km_Aggregated.tif), CC BY 4.0) scaled to 2025 NCP state totals to compute exact population density within any district, hex cell, or `1km` / `5km` charger catchment buffer.

---

## Summary Matrix of Gaps & Mitigations

| Gap ID | Domain | Missing Field / Dataset | Root Cause | Verified Mitigation in Project |
| :--- | :--- | :--- | :--- | :--- |
| **G-1.1** | National Chargers (BEE) | Unique `Station_ID`, `Operational_Status`, `Highway_Tag`, `Tariff` | Static PDF table of connector/charger rows; MHI does not centrally track NH/Tier-2/3 splits | Cluster by `(CPO, Location, Lat, Lon)` (`29,117` unique coords); apply PIB OMC operational ratios (`82.0%` national); spatial buffer (`500m`) on OSM highways |
| **G-1.2** | Pilot Chargers (Delhi) | `/openev/` live telemetry; coordinates for `121/318` swap stations; `103` missing regions | `/openev/` returns HTTP 502 Bad Gateway; swap operators omitted lat/lon on 121 rows | Use 770 geocoded Switch Delhi stations + 3,475 BEE Delhi rows; geocode 121 swap stations via 6-digit PIN + address; spatial join against `2011_Dist.shp` |
| **G-2.1** | EV Demand (VAHAN) | National district-level CSV; Delhi Burari (`DL51/52/53`) commercial RTO non-geographic concentration | JSF stateful session per state; commercial EVs registered at centralized Burari units (`64,723` EVs) | State-level VAHAN (`36` states, `10.69M` EVs) nationally; RTO-to-District crosswalk + POI-weighted commercial redistribution in Delhi Pilot |
| **G-3.1** | Boundaries | 2026 district polygons & LGD codes in BEE/VAHAN | Survey of India login gate; BEE uses free-text district/state names (`46` state strings, `1,288` district strings) | Spatial Point-in-Polygon join using verified coordinates (`99.70%` valid in BEE) onto `Admin2.shp` & `2011_Dist.shp` + canonical state lookup table |
| **G-4.1** | Grid / Electricity | Substation/feeder spare MVA hosting capacity | CEA `/wp-login.php` wall; DISCOM feeder capacity not public in bulk GIS | Proximity analysis to `576` mapped OSM substations/transformers in Delhi + state EV tariffs from BEE Annexure-A |
| **G-5.1** | Roads & Traffic | Link-level AADT traffic volume & complete `lanes`/`maxspeed` tags | No open NHAI link-level AADT shapefile; OSM tags optional | Combine OSM highway hierarchy (`8,087` Delhi major road ways) with `3,534` demand attractor POIs & WorldPop 1km raster |
| **G-5.2** | Demographics | `censusindia.gov.in` tables & anonymous `data.gov.in` downloads | Server timeout on `censusindia.gov.in`; JanParichay SSO login wall on `data.gov.in` | Extracted NCP 2025 state population & MoSPI GSDP from NITI IEMI 2025 PDF + WorldPop 1km GeoTIFF raster |
