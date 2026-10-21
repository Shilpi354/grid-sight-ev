# GridSight EV — Techfest 2026–27 Round 1 Submission

**Status key used throughout:**  
✅ **Implemented** (verified in code & data) · 🧪 **Evidence of Passing** (tested in automated test suite) · 🗓 **Planned** (post-Round 1 roadmap)

---

## A. Team information

| Field | Value |
|---|---|
| Team Name | [TEAM TO CONFIRM] |
| Team ID | [TEAM TO CONFIRM] |
| Institution | [TEAM TO CONFIRM] |
| Team leader (sole submitter) | [TEAM TO CONFIRM] |
| Contact (email / phone) | [TEAM TO CONFIRM] |

---

## B. Problem Understanding and Relevance (25%)

India's public electric vehicle (EV) charging infrastructure data is fragmented across distinct ministries, state nodal agencies, municipal bodies, and crowdsourced registries—each operating with conflicting schemas, measurement units, reporting periods, and collection methodologies:

- **Registry Overlap and Unit Ambiguity:** The Bureau of Energy Efficiency (BEE) national registry logs individual charger/connector rows (39,641 rows); Ministry of Petroleum & Natural Gas (MoPNG) Parliamentary tables report Oil Marketing Company (OMC) retail outlet sites (22,753 operational); Ministry of Heavy Industries (MHI) tracks scheme-funded FAME-II deployments (8,932 OMC chargers); and OpenStreetMap (OSM) captures a sparse, crowdsourced subset (725 national features). Simply summing these registries introduces massive double-counting.
- **Geographic Granularity Mismatch:** EV demand data from MoRTH/VAHAN is aggregated at national, state, and Regional Transport Office (RTO) levels, whereas physical charging stations operate at discrete point coordinates. In Delhi, commercial EV fleets (auto-rickshaws, cabs, delivery goods) register predominantly at the centralized Burari RTO, concealing true district-level demand.
- **Opacity of Critical Electrical Telemetry:** No public registry provides real-time connector occupancy, session logs, or DISCOM distribution transformer (DT) and feeder spare hosting capacity ($\text{MVA}$).

### The Three-Pillar Platform Framework
To address this without relying on synthetic assumptions or fabricated download links, **GridSight EV** structures the problem into three linked modules:

1. **Deterministic Multi-Source Integration:** Geocode, standardize, and clean official sources while enforcing an uncompromising **non-additivity design rule** (sources are evaluated as separate baselines and never summed together).
2. **High-Resolution Spatial Gap Assessment:** A $2.0\text{ km} \times 2.0\text{ km}$ spatial grid pilot across the National Capital Territory (NCT) of Delhi combining WorldPop demographic rasters, 3,534 OSM activity hubs, and 8,087 major road segments.
3. **Transparent Capacity Planning Engine:** A bottom-up, physics-grounded energy-balance simulator (2026–2030) translating category-specific EV fleet growth into daily kilowatt-hour demand ($\text{kWh/day}$), public charging reliance, and physical hardware requirements (distinguishing Stations, EVSE Points, AC/DC Nozzles, and Battery Swap Dockets).

**Pilot Geography:** NCT of Delhi (9 Census districts, 23 RTO units), selected as the primary view because it features India's richest open EV data (Switch Delhi, BEE, OSM, and RTO-level VAHAN). A secondary national route covers all 36 States/UTs.

---

## C. Methodology & Analytical Approach (Feasibility 25%)

```mermaid
flowchart TD
    subgraph S1["1. Data Ingestion & Hygiene (Python)"]
        D1["BEE PDF Registry (39,641 rows)"] --> P1["Coordinate Audit & State Name Normalisation"]
        D2["Switch Delhi Portal (891 rows)"] --> P2["Deduplication (876 sites: 573 Chg / 303 Swap)"]
        D3["VAHAN 4 Public Analytics (10.69M EVs)"] --> P3["BOV + Pure EV Union & Burari RTO Redistribution"]
        D4["Spatial Rasters & OSM Networks"] --> P4["WorldPop 1km + 3,534 POIs + 8,087 Road Segments"]
    end

    subgraph S2["2. Spatial & Planning Engine"]
        P1 & P2 & P4 --> M1["Delhi 2km Grid Engine (375 Cells)"]
        M1 --> M2["Demand Score (D) & Equirectangular Distance (d)"]
        M2 --> M3["Priority Siting Score (S) & Hardware Sizing"]
        P3 --> E1["Category Energy Demand Model (2W/3W/4W/Bus/Goods)"]
        E1 --> E2["2030 Scenario Simulator (AC / DC / Swap Requirements)"]
    end

    subgraph S3["3. Interactive Platform (React + TypeScript + Leaflet)"]
        M3 --> UI1["NCT Delhi Primary Map & Grid Inspector"]
        E2 --> UI2["Coverage & Simulator Workspace"]
        P1 & P2 & P3 --> UI3["National 36-State Overview & Audit Matrix"]
    end
```

### C1. Integration (✅ `scripts/process_data.py`)
- **Deterministic State Normalization:** Mapped 46 raw state string variations in BEE (e.g., `Kerala` vs `KERALA`, `Chattisgarh`, `Uttrakhand`) and 38 PIB OMC rows (merging split MP/Bihar entries and Leh/Ladakh) to the 36 canonical ISO/Census codes in `Admin2.shp`.
- **Connector & Site Classification:** BEE charger rows are grouped by physical site location, distinguishing station sites, charger rows, connectors, and power ratings ($\text{kW}$).
- **Non-Additivity Design Rule:** BEE, MoPNG OMC (PIB), MHI FAME-II (PIB), Switch Delhi, and OSM are strictly maintained as independent layers; the user interface toggles one baseline at a time and never adds them together.
- **VAHAN Fuel Tag Aggregation:** Captured both `ELECTRIC(BOV)` (6.35M) and `PURE EV` (4.34M) across 36 states and 23 Delhi RTOs. Both active compliant (7.87M) and active non-compliant (2.82M, 26.4%) registrations are reported to provide an upper-bound fleet estimate.
- **Burari Commercial Fleet Redistribution:** Centralized commercial registrations at Delhi's Burari transport authority (DL-11/12/13/14 covering 3W, 4W cabs, buses, and light goods) are redistributed to Delhi's 9 Census districts using an empirical activity-weighted crosswalk:
  $$w_{\text{district}} = 0.5 \cdot \left(\frac{N_{\text{poi, district}}}{N_{\text{poi, total}}}\right) + 0.5 \cdot \left(\frac{P_{\text{district}}}{P_{\text{total}}}\right)$$
  *(Personal 2-wheelers remain assigned to their local zonal RTOs).*

---

### C2. Gap Assessment (✅ `scripts/process_data.py` + `src/utils/planningEngine.ts`)

- **Spatial Grid Definition:** Fixed steps of $0.018^\circ\text{ Lat} \times 0.0205^\circ\text{ Lon}$ ($\approx 2.0\text{ km} \times 2.0\text{ km}$ at $28.6^\circ\text{N}$) spanning $28.40^\circ\text{–}28.89^\circ\text{N}, 76.83^\circ\text{–}77.35^\circ\text{E}$ generating **375 discrete planning cells**. The bounding box intentionally covers the NCT boundary plus adjacent commuter gateway fringes (Gurugram, Noida, Faridabad, Ghaziabad borders) where cross-border fleet traffic concentrates.
- **Composite Cell Demand Score ($D \in [0, 100]$):**
  $$D = 100 \cdot \left[ 0.45 \cdot \min\left(1, \frac{P}{0.65 \cdot P_{\max}}\right) + 0.35 \cdot \min\left(1, \frac{N_{\text{poi}}}{0.50 \cdot N_{\text{poi},\max}}\right) + 0.20 \cdot \min\left(1, \frac{N_{\text{road}}}{0.50 \cdot N_{\text{road},\max}}\right) \right]$$
  - **Population ($P$):** Summed from the WorldPop 2020 1km raster by pixel center and scaled proportionally so Delhi NCT equals the official **National Commission on Population (NCP) 2025 projection of 22,300,000** (documented in NITI Aayog IEMI 2025).
  - **Demand Attractors ($N_{\text{poi}}$):** Count of 12 OSM POI categories (fuel pumps, metro stations, bus depots, commercial markets, parking lots).
  - **Road Centroids ($N_{\text{road}}$):** Centroids of OSM motorway, trunk, primary, and secondary road segments within the cell.
- **Distance to Supply ($d$):** Evaluated from cell centroid to the nearest station under a chosen baseline (Any Official, Switch Delhi only, BEE only, DC Fast only, or Battery Swap only). Calculated using an equirectangular planar projection ($dx = d\lambda \cdot 111,320 \cdot \cos(\phi), dy = d\phi \cdot 111,320$). Over Delhi's compact bounding box ($\approx 40\text{ km} \times 50\text{ km}$), distortion relative to spherical Haversine is $<0.05\%$ ($<2\text{ meters per kilometer}$), guaranteeing sub-millisecond client-side recalculation during interactive filtering.
- **Coverage Classification:**
  - **Covered:** Centroid distance $d \le r$ (user-selectable coverage radius: $0.5, 1.0, 1.5, 2.0, 3.0, 5.0\text{ km}$; default $1.5\text{ km}$).
  - **Underserved Priority Zone:** Uncovered ($d > r$) **AND** Demand Score $D \ge 22$ (configurable threshold).
  - **Low-Demand Fringe:** Uncovered ($d > r$) **AND** Demand Score $D < 22$.
- **Priority Siting Score ($S$):** For uncovered cells, priority scales with both unmet demand and distance from the network:
  $$S = D \cdot \left[0.65 + 0.35 \cdot \min\left(2, \frac{d - r}{\max(0.5, r)}\right)\right]$$
- **Indicative Infill Hardware Sizing (Heuristic):**
  $$\text{AC Nozzles} = \max\left(2, \text{round}\left(\frac{D}{12}\right)\right)$$
  $$\text{DC Fast Nozzles} = \max\left(1, \text{round}\left(\frac{D + 4 \cdot N_{\text{transit}}}{25}\right)\right)$$
  $$\text{Physical Stations} = \max\left(1, \left\lceil \frac{\text{AC} + \text{DC}}{6} \right\rceil\right)$$

---

### C3. Demand and Requirement Estimation (✅ `src/utils/planningEngine.ts`)

For vehicle class $k \in \{\text{2W}, \text{3W}, \text{4W}, \text{Bus}, \text{Goods}\}$ and scenario $s \in \{\text{Low}, \text{Baseline}, \text{High}\}$:

1. **Projected Active EV Fleet (2026 $\rightarrow$ 2030):**
   $$V_{k,2030} = \text{round}(V_{k,\text{now}} \cdot m_{k,s})$$
   Multipliers $m_{k,s}$ reflect category-specific VAHAN compound growth trajectories (Baseline: 2W $\times 2.20$, 3W $\times 1.90$, 4W $\times 2.35$, Bus $\times 2.40$, Goods $\times 2.30$).
2. **Daily Public Energy Demand ($E_k$ in $\text{kWh/day}$):**
   $$E_k = V_{k,2030} \cdot e_k \cdot \phi_{k,s}$$
   - **Per-vehicle daily energy ($e_k$):** $1.024\text{ kWh}$ (2W: $32\text{ km/day} \times 0.032\text{ kWh/km}$); $6.375\text{ kWh}$ (3W: $85\text{ km/day} \times 0.075\text{ kWh/km}$); $6.96\text{ kWh}$ (4W: $48\text{ km/day} \times 0.145\text{ kWh/km}$); $207.0\text{ kWh}$ (Bus: $180\text{ km/day} \times 1.15\text{ kWh/km}$); $13.5\text{ kWh}$ (Goods: $90\text{ km/day} \times 0.15\text{ kWh/km}$).
   - **Public charging reliance share ($\phi_{k,s}$):** Baseline values: 2W (20%), 3W (55%), 4W (32%), Bus (20% en-route), Goods (50%).
3. **Battery Swapping Allocation:** Swapping absorbs $\sigma_s$ of 2W/3W public energy (Low: 28%, Baseline: 35%, High: 40%). Remaining plug-in energy is split: 2W/3W (85% AC / 15% DC), 4W (35% AC / 65% DC), Goods (25% AC / 75% DC), Bus (100% DC).
4. **Daily Connector Dispensing Throughput:**
   - $\text{AC Connector} = 4.2\text{ kW} \times 5.5\text{ utilization hours} = 23.1\text{ kWh/day}$
   - $\text{DC Fast Nozzle} = 30.0\text{ kW} \times 6.0\text{ utilization hours} = 180.0\text{ kWh/day}$
   - $\text{Swap Docket} = 12.5\text{ swaps/day} \times 2.1\text{ kWh/swap} = 26.25\text{ kWh/day}$
5. **Hardware Quantification & Net New Additions:**
   $$N = \left\lceil \frac{E}{\text{Throughput}} \right\rceil, \quad \text{Charging Points (EVSE)} = \text{AC} + \left\lceil \frac{\text{DC}}{1.35} \right\rceil, \quad \text{Stations} = \left\lceil \frac{\text{Points}}{4.5} \right\rceil$$
   $$\text{Net New} = \max(0, \text{Required} - \text{Existing Installed})$$

*Honest Analytical Status: These represent transparent, assumption-driven scenario calculators rather than deterministic forecasts. Every parameter is exposed to user adjustment in the live application.*

---

## D. Data Strategy and Provenance (10%)

All datasets were captured as of the **19 October 2026** freeze date, preserved in original format under `data/raw/`, and tracked in `data/source_manifest.csv`:

| Dataset ID | Source (Organization – Title) | Vintage | Granularity | Scope & Application | Key Limitations & Mitigation |
|---|---|---|---|---|---|
| **SRC-01A/B** | BEE, Ministry of Power – *EV Public Charging Stations Data* (`EV_PCS_Data_29277.pdf`) | to 26 Oct 2025 *(Pub: 17 Feb 2026)* | Point / Site | 29,371 unique geocoded sites (39,641 charger rows; 44,066 connectors) | Static PDF; lacks operational status; 119 coordinate errors isolated from map pins. |
| **SRC-02A/B** | PIB / MoPNG – *OMC EVPCS* (PRID 2246042) | to 01 Mar 2026 *(Pub: 27 Mar 2026)* | State | 22,753 operational OMC stations (27,737 installed) | OMC retail outlets only; kept separate from BEE to avoid double-counting. |
| **SRC-03A/B** | PIB / MHI – *FAME-II EVPCS* (PRID 2246045) | to 01 Mar 2026 *(Pub: 27 Mar 2026)* | State | 8,932 FAME-II OMC + 227 PSE chargers | Scheme-specific subset; kept isolated from general registries. |
| **SRC-04A** | Transport Dept., GNCTD – *Switch Delhi Portal* | 19 Oct 2026 *(Live Portal)* | Point / Site | 876 deduplicated stations (573 EV charging + 303 battery swap) | 15 duplicate swap kiosks removed. 121 swap kiosks geocoded via verified PIN centroid. |
| **SRC-05** | OpenStreetMap (Overpass API) – `amenity=charging_station` | 19 Oct 2026 | Point | 725 national features; 179 Delhi stations | Severe crowdsourced under-count (2.48% of BEE). Used strictly as cross-reference. |
| **SRC-06A/B/C** | MoRTH / NIC – *VAHAN 4 Public Analytics* | 19 Oct 2026 | State / RTO | 10,689,490 national active EVs; 549,153 Delhi EVs | Includes 26.4% non-compliant active EVs; Burari commercial concentration redistributed. |
| **SRC-07A/B** | DataMeet Spatial Community | 2011 / 2019 | Polygon | 36 States/UTs and 9 Delhi Census districts | Official boundaries for point-in-polygon containment and choropleths (CC BY 4.0). |
| **SRC-08B** | OpenStreetMap (Overpass API) – Major Highway Network | 19 Oct 2026 | Line | 8,087 Delhi motorway/trunk/primary/secondary segments | Opportunity charging corridor proxy; lacks vehicular traffic volumes. |
| **SRC-09A** | WorldPop Project – *India 1km Population Density Raster* | 2020 *(Scaled to 2025)* | 1km Raster | Spatial population density across 375 grid cells | 2020 raster scaled to official NCP 2025 Delhi projection of 22,300,000. |
| **SRC-10B** | BEE / State SERCs – *State EV Tariff Annexure A* | 2025–2026 | State | Notified LT EV tariffs (₹/kWh) & State Nodal Agencies | Contextual intelligence on state power economics (3 states undefined). |
| **SRC-10C** | OpenStreetMap (Overpass API) – Power Infrastructure | 19 Oct 2026 | Point | 576 Delhi substations and distribution transformers | Proximity proxy only; 99.3% lack MVA rating; proximity $\neq$ feeder hosting capacity. |
| **SRC-11A** | NITI Aayog / WRI – *India Electric Mobility Index 2025* | to Dec 2025 | State | State GSDP, population benchmarks, and policy scores | Secondary validation benchmark. |
| **SRC-11C** | OpenStreetMap (Overpass API) – Demand Attractors | 19 Oct 2026 | Point | 3,534 Delhi POIs (fuel, transit, parking, commercial) | Spatial demand attractor proxies; footfall volume unmeasured. |
| **Documented Gaps** | Delhi OpenEV (`502 Bad Gateway`), CEA EV Standards (`Login Wall`), Census India (`Timeout`) | — | — | — | Fully audited with workaround rationales in `DATA_GAPS.md`. |

**Temporal Mismatch Disclosure:** The primary national supply registry (BEE, Oct 2025) predates demand data (VAHAN, Oct 2026) by 12 months. This naturally overstates apparent supply deficits. GridSight EV mitigates this by providing live Switch Delhi (Oct 2026) as an alternate baseline and surfacing temporal disclaimers on all map legends.

---

## E. Technical Architecture and Tools

- **Data Pipeline:** Python (`scripts/process_data.py`, ~1,770 lines; utilizing NumPy, Shapely, and PIL for GeoTIFF raster extraction) generating clean, lightweight GeoJSON and JSON bundles in `public/data/` and `data/processed/`.
- **Frontend Architecture:** React 18 with TypeScript (strict mode), bundled via Vite.
- **Cartographic Engine:** Leaflet and React-Leaflet using **OpenStreetMap standard tiles** (`https://tile.openstreetmap.org/{z}/{x}/{y}.png`). The basemap is **100% keyless, free, and completely watermark-free**, providing full street-level context without third-party API dependencies.
- **Client-Side Spatial Computation:** `src/utils/planningEngine.ts` executes all grid filtering, coverage distance evaluations, and scenario projections entirely in the browser in sub-millisecond time.
- **Editorial Geospatial Intelligence UI:** A calm, research-oriented light interface featuring four dedicated views:
  1. **Delhi Pilot Map (Primary Default):** Immediate street-level access to 876 charging and swapping locations with operator, power, and layer toggles.
  2. **Coverage Planning:** The 375-cell spatial coverage map, underserved priority rankings, and 2030 future capacity simulator.
  3. **Data & Methodology Audit:** Complete non-additivity reconciliation matrix and external data gap register.
  4. **National Overview:** 36-state EV demand choropleths, 776 BEE district hub clusters, and state deep-dive profiles.

---

## F. Validation, QA and Evidence Status

| Validation Item | Command Executed | Benchmark Assertion | Evidence Status |
|---|---|---|---|
| **Data Integrity Suite** | `python scripts/validate_processed_data.py` | 24 automated checks (36 states, 10,689,490 EVs, 39,641 BEE rows, 44,066 connectors, OMC 27,737/22,753, FAME-II 8,932, Delhi 9 districts / 23 RTOs / 549,153 EVs, 876 Switch Delhi, 375 grid cells) | 🧪 **VERIFIED: All 24 / 24 assertions passed (100% success).** |
| **TypeScript Static Check** | `npm run typecheck` (`tsc --noEmit`) | Strict TypeScript compilation; zero type errors across all components | 🧪 **VERIFIED: 0 compiler errors (clean exit code 0).** |
| **Production Build** | `npm run build` (`vite build`) | Full asset minification and production bundle generation | 🧪 **VERIFIED: Built successfully in 8.12s (`dist/` generated).** |
| **Live Smoke Test** | Local dev server on `http://localhost:5173/` | Interactive testing of all 4 views, radius slider, scenario inputs, and inspectors | 🧪 **VERIFIED: HTTP 200 OK, full 560px map heights, zero tile watermarks.** |
| **GitHub Repository** | `git push origin main` | Complete source tree, datasets, and audits committed on GitHub | 🧪 **VERIFIED: Live at [github.com/aadityaexpress/gridsight-ev](https://github.com/aadityaexpress/gridsight-ev).** |

---

## G. Innovation and Differentiation (20%) — Grounded

- **What Is Not Claimed:** We do not claim a speculative proprietary black-box AI algorithm. Siting and capacity projections are transparent, reproducible heuristics based on open spatial data and energy physics.
- **What Is Claimed and Verifiable in Repo:**
  1. **Strict Source Separation & Non-Additivity:** We prevent the critical industry error of adding overlapping registries. BEE, Switch Delhi, OMC, and OSM are separately selectable baselines.
  2. **Empirical Data Engineering Discoveries:**
     - *VAHAN Dual Fuel Labels:* Documented that querying only `ELECTRIC(BOV)` misses 4.34M vehicles cataloged under `PURE EV`.
     - *Burari Centralization Correction:* Developed an activity-weighted crosswalk to correct commercial EV demand distortion across Delhi's districts.
     - *BEE Coordinate Hygiene:* Isolated 119 anomalous rows (copy-paste Lat=Lon, Excel corruptions) while preserving them in state totals.
  3. **Assumption-Exposed Scenario Simulator:** Every parameter (utilization hours, kW throughput, daily km, swapping shares) is configurable in real time, avoiding arbitrary static EV-to-charger ratios.
  4. **Radical Transparency:** Dedicated *Data Audit* view exposes API outages (OpenEV 502, Census timeout) and alerts planners that substation proximity does not equal DISCOM feeder hosting capacity.

---

## H. Implementation Roadmap through the Grand Finale (20%)

```mermaid
flowchart LR
    P0["Phase 0: Freeze & Deploy"] --> P1["Phase 1: Sensitivity Bands"]
    P1 --> P2["Phase 2: Grid Hosting Proxies"]
    P2 --> P3["Phase 3: Highway Corridors"]
    P3 --> P4["Phase 4: Grand Finale Rehearsal"]
```

| Phase | Core Objectives & Deliverables | Target Milestone / Exit Test |
|---|---|---|
| **Phase 0: Baseline Freeze (Complete)** | Frozen source manifest v1.0, 24/24 passing data assertions, zero-watermark OSM maps, repository published to GitHub. | ✅ Working prototype deployed on `main`. |
| **Phase 1: Sensitivity & Uncertainty Analysis** | Implement Monte Carlo parameter perturbation across fleet multipliers ($\pm 20\%$) and daily energy consumption parameters. | Dynamic confidence interval bands on all 2030 charger requirement outputs. |
| **Phase 2: Distribution Grid Capacity Proxies** | Overlay CEA technical connectivity standards with secondary DISCOM substation data to model feeder readiness. | Grid Hosting Feasibility Index per 2km cell combining distance with estimated spare capacity. |
| **Phase 3: Inter-City Highway Corridors** | Extend the 2km spatial buffer model along National Highways connecting Delhi to Jaipur, Agra, and Chandigarh. | Dedicated Inter-City Highway Infill & Fast-Charging Corridor Tool. |
| **Phase 4: Grand Finale Deployment** | Containerize application (Docker) and deploy to a high-availability cloud host with full offline caching fallback. | Rehearsed live jury demonstration with zero network dependency. |

---

## I. Limitations and Risks

| Real-World Limitation / Risk | Analytical Consequence | GridSight EV Mitigation Strategy |
|---|---|---|
| **Absence of Real-Time Session Telemetry** | Public portals do not expose live connector occupancy or uptime status. | Platform frames metrics strictly as *physical infrastructure presence*; OMC operational ratios ($82.0\%$) can be toggled as a discount factor. |
| **Substation Proximity $\neq$ Electrical Capacity** | 99.3% of OSM substations lack MVA hosting capacity; DISCOM feeder data is non-public. | Explicit warning banner in UI; substations are presented solely as physical proximity proxies without ungrounded hosting claims. |
| **Overlapping & Asynchronous Registries** | BEE (Oct 2025) and Switch Delhi (Oct 2026) have different scopes and collection dates. | Enforced strict source separation; users choose one baseline at a time; audit matrix details discrepancies. |
| **Active Non-Compliant Fleet** | 26.4% of registered EVs lack active fitness/PUC compliance. | Interface provides compliant-only vs. total active fleet breakdowns to establish upper and lower bounds. |
| **Planar Distance Distortion** | Equirectangular projection approximates spherical distances. | Verified that error across Delhi's $40\text{ km} \times 50\text{ km}$ extent is $<0.05\%$ ($<2\text{ m/km}$), well within GPS variance. |
| **Live Network Demo Vulnerability** | Potential network dropouts during live jury presentation. | All processed GeoJSON boundaries, district joins, and spatial tables are bundled locally in `public/data/`. |

---

## J. References

1. **BEE Public Charging Stations Registry:** Bureau of Energy Efficiency, Ministry of Power, *Public Charging Stations Data till 26 Oct 2025* (`EV_PCS_Data_29277.pdf`), Published 17 Feb 2026.
2. **MoPNG OMC Retail Outlet Stations:** Ministry of Petroleum and Natural Gas / Ministry of Heavy Industries, *PIB Press Release PRID 2246042*, 27 Mar 2026.
3. **FAME-II Scheme Charging Installations:** Ministry of Heavy Industries, *PIB Press Release PRID 2246045*, 27 Mar 2026.
4. **Switch Delhi Charging & Swapping Portal:** Transport Department & Dialogue and Development Commission of Delhi (DDC), `ev.delhi.gov.in/charging-station`, snapshot 19 Oct 2026.
5. **VAHAN 4 Public Analytics Portal:** Ministry of Road Transport and Highways (MoRTH) / NIC Parivahan, `analytics.parivahan.gov.in`, snapshot 19 Oct 2026.
6. **DataMeet Spatial Boundaries:** DataMeet Spatial Community, Census-2011 District & State Boundaries (CC BY 4.0), `github.com/datameet/maps`.
7. **WorldPop Gridded Population:** WorldPop Project, *India 1km Population Density Raster* (Dataset ID 50771), scaled to NCP 2025 projection.
8. **OpenStreetMap Data Extracts:** OpenStreetMap Contributors, Overpass API extracts for India and Delhi charging stations, highway corridors, substations, and POIs (ODbL 1.0), snapshot 19 Oct 2026.
9. **NITI Aayog IEMI 2025:** NITI Aayog & WRI India, *India Electric Mobility Index 2025*, Published Dec 2025.

---

## K. Criteria Cross-Reference Matrix

| Techfest Evaluation Criterion | Weight | Primary Document Sections | Repository Evidence |
|:---|:---:|:---|:---|
| **Problem Understanding & Relevance** | **25%** | **Section B** (Data fragmentation, non-additivity, Delhi/National scope) | [`DATA_AVAILABILITY_AUDIT.md`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/DATA_AVAILABILITY_AUDIT.md), [`DATA_GAPS.md`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/DATA_GAPS.md) |
| **Technical Approach & Feasibility** | **25%** | **Section C** (Formulas, Burari crosswalk, 2km grid, 2030 model) · **Section E** | [`scripts/process_data.py`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/scripts/process_data.py), [`src/utils/planningEngine.ts`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/src/utils/planningEngine.ts) |
| **Innovation & Differentiation** | **20%** | **Section G** (Non-additivity enforcement, dual VAHAN tags, scenario transparency) | [`src/components/DataAuditView.tsx`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/src/components/DataAuditView.tsx) |
| **Implementation Roadmap** | **20%** | **Section H** (Phase 0–4 milestones, sensitivity analysis, highway infill) | [`DELIVERABLE_AUDIT.md`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/DELIVERABLE_AUDIT.md) |
| **Data Strategy & Provenance** | **10%** | **Section D** (11-source manifest, limitations, temporal disclosures) · **Section J** | [`data/source_manifest.csv`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/data/source_manifest.csv), [`DATA_QUALITY_REPORT.md`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/DATA_QUALITY_REPORT.md) |
