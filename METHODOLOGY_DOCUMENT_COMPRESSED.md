# GridSight EV: Geospatial EV Charging Infrastructure Intelligence Platform

**IIT Bombay Techfest 2026–27 | Round 1 Submission Document**  
**Track:** Challenge 1 — EV Infra Map India (Ministry of Heavy Industries & ICAT)  

---

### Submission Metadata & Team Information

| Parameter | Project & Submitter Specification |
|---|---|
| **Team Name** | **Mechies** |
| **Institution** | **Netaji Subhas University of Technology (NSUT), New Delhi** |
| **Team Leader & Submitter** | **Kunal** (`kunalclass1112@gmail.com` \| +91 8595289897) |
| **Open-Source Codebase** | [github.com/aadityaexpress/gridsight-ev](https://github.com/aadityaexpress/gridsight-ev) |
| **Live Deployed Platform** | [gridsight-ev.vercel.app](https://gridsight-ev-git-main-aadityaexpress-projects.vercel.app/) |
| **Automated Verification** | **28 / 28 Automated Assertions Passed** (`scripts/validate_processed_data.py`) |
| **Implementation Status** | **Phase 0 Operational** (Round 1 Verified) • **Phases 1–3 Planned Roadmap** |

---

## 1. Problem Statement, Relevance & System Architecture (25% Rubric Weight)

India's accelerated transition to electric mobility has outpaced public planning tools, leaving infrastructure investments vulnerable to severe capital misallocation, queuing bottlenecks, and localized grid overloads. Public charging planning currently faces four fundamental structural barriers:

1. **Multi-Registry Fragmentation & Unit Ambiguity:** Official charging registries report non-interoperable metrics across disconnected data schemas:
   - **BEE (Ministry of Power):** Catalogs individual charger/connector rows (39,641 rows; 44,066 connectors across 29,371 unique geocoded sites).
   - **MoPNG (PIB PRID 2246042):** Tracks Oil Marketing Company (OMC) retail fuel outlet stations (27,737 installed; 22,753 operational).
   - **MHI / FAME-II (PIB PRID 2246045):** Logs scheme-subsidized deployments (8,932 OMC units).
   - **OpenStreetMap (OSM):** Captures a sparse crowdsourced subset (725 national features; 179 in Delhi).  
   *Analytical Failure:* Blindly aggregating these registries produces catastrophic double-counting.
2. **Spatial Granularity Mismatch:** Operational EV registrations from MoRTH/VAHAN are aggregated at national, state, and Regional Transport Office (RTO) administrative levels, whereas charging and battery swapping stations operate at discrete point coordinates. In Delhi, commercial EV fleets (e-rickshaws, commercial cabs, delivery freight) register predominantly at the centralized Burari authority (DL-11/12/13/14), severely distorting localized municipal demand.
3. **Opacity of Critical Electrical Telemetry:** Public registries completely omit distribution transformer (DT) spare capacity, feeder voltage ratings (11 kV vs 33 kV), and real-time session utilization logs.
4. **Geographic Catchment vs. Volumetric Adequacy Disconnect:** Conventional EV planning dashboards rely on naive circular coverage buffers ($d \le r$), conflating spatial proximity with service adequacy. A charging plaza offering two slow 3.3 kW AC sockets within 1.0 km cannot service 100 commercial e-rickshaws requiring 6.4 kWh/day each, causing severe queue collapse. GridSight EV explicitly decouples spatial accessibility from daily energy throughput ($\text{kWh/day}$).

### Four-Tier Platform Architecture

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ Tier 1: Deterministic Multi-Source Ingestion & Sanitization Engine                     │
│ • State string normalization (46 raw variants → 36 canonical ISO codes in Admin2.shp)  │
│ • Coordinate sanitization (119 corrupted rows isolated); Non-Additivity Layer Enforcer │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ Tier 2: Spatial Harmonization & Demographic Scaling Engine                             │
│ • Delhi 375-cell planning grid (2.0 km × 2.0 km at 0.018° Lat × 0.0205° Lon)          │
│ • WorldPop 1km raster scaled to NCP 2025 projection (22,300,000 residents)             │
│ • Burari commercial fleet activity-weighted redistribution crosswalk                   │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ Tier 3: Explainable Physics-Informed Spatial AI & Constrained Optimization Suite      │
│ • Supervised Random Forest Demand Regressor (120 estimators, depth 6, R² = 0.796)      │
│ • Continuous 4th-Order Sigmoid Distance-Decay Kernel (smooth boundary transitions)     │
│ • Bass Diffusion Innovation Adoption Model (R² = 0.992, p=0.0114, q=0.4963, M=20.0M)   │
│ • Multi-Objective Submodular Siting Optimizer (feeder proximity + anti-cannibalization)│
├────────────────────────────────────────────────────────────────────────────────────────┤
│ Tier 4: Bottom-Up Capacity Simulator & Cartographic Planning UI                        │
│ • Vehicle-class daily energy balance, public reliance, and battery swapping absorption │
│ • Physical hardware sizing (Stations, EVSE Points, AC/DC Nozzles, Swapping Dockets)    │
│ • Zero-watermark, keyless Leaflet cartography with sub-millisecond client simulation    │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

> **IMPLEMENTATION STATUS: OPERATIONAL BASELINE VS. PLANNED ROADMAP**  
> • **Phase 0 (Verified Operational - Round 1 Submission):** 36 States/UTs demand choropleths (10.69M active EVs across 2 VAHAN fuel tags); BEE geocoded sites (29,371); Delhi 375-cell grid (22.3M pop); Random Forest regressor ($R^2 = 0.796$); Bass Diffusion S-curve ($R^2 = 0.992$); Greedy submodular optimizer (top 25 candidate plazas); Automated QA suite (28/28 assertions pass in `scripts/validate_processed_data.py`); Zero-watermark Leaflet UI.  
> • **Planned Roadmap (Post-Round 1):** Highway corridor buffers (Phase 1, NH-48 / Yamuna Expwy); CEA secondary distribution transformer voltage tier proxy (Phase 2); DISCOM nodal interconnect live API ingest & containerized deployment (Phase 3).

---

## 2. Data Integration, Normalization & Spatial Methodology (25% + 10% Rubric Weight)

### Multi-Source Normalization & Non-Additivity Design Rule
Because BEE, MoPNG OMC (PIB), MHI FAME-II, Switch Delhi, and OSM overlap extensively but lack shared foreign keys, GridSight EV strictly maintains them as independent analytical baselines. The user interface allows planners to toggle one source baseline at a time, forbidding naive arithmetic summation that corrupts infrastructure planning.

### Dual VAHAN Fuel Tag Reconciliation
Querying only the `ELECTRIC(BOV)` fuel tag in VAHAN captures 6.35M vehicles but omits 4.34M vehicles cataloged under `PURE EV`. GridSight EV deterministically integrates both tags across 36 States/UTs and 23 Delhi RTOs (10,689,490 active EVs nationwide; 549,153 in Delhi). Furthermore, our pipeline extracts active compliant (7.87M) versus active non-compliant registrations (2.82M, 26.4% lacking valid fitness/PUC) to establish upper- and lower-bound operational demand boundaries.

### Burari Commercial Fleet Spatial Redistribution
Commercial EV fleets (3W e-rickshaws/autos, 4W commercial cabs, buses, light goods) registered at Delhi's centralized Burari authority (DL-11/12/13/14) do not operate solely in North Delhi. GridSight EV redistributes these vehicles across Delhi's 9 Census districts using an empirical activity-weighted crosswalk:

$$\mathbf{w_{\text{district}} = 0.5 \times \left(\frac{N_{\text{poi, district}}}{N_{\text{poi, total}}}\right) + 0.5 \times \left(\frac{P_{\text{district}}}{P_{\text{total}}}\right)} \quad \text{[Eq. 1]}$$

*Where $N_{\text{poi}}$ is the count of OSM commercial activity attractors (3,534 hubs), and $P$ is the Census district population (scaled to 22.3M). Private two-wheelers remain assigned to their zonal residential RTOs.*

### Delhi 375-Cell Spatial Planning Grid
The spatial analysis grid spans bounding box $28.40^\circ\text{–}28.89^\circ\text{N}, 76.83^\circ\text{–}77.35^\circ\text{E}$ with uniform steps of $0.018^\circ\text{ Lat} \times 0.0205^\circ\text{ Lon}$ ($\approx 2.0\text{ km} \times 2.0\text{ km}$ at $28.6^\circ\text{N}$), generating 375 discrete cells. The bounding box explicitly captures the NCT plus commuter fringes (Gurugram, Noida, Faridabad, Ghaziabad) where cross-border fleet traffic concentrates. Demography is derived from WorldPop 1km raster scaled to the National Commission on Population (NCP) 2025 projection of 22,300,000 residents.

### Two-Stage Coverage & Volumetric Adequacy Engine
- **Stage 1 (Geometric Catchment):** Assesses Euclidean/equirectangular distance $d$ to the nearest operational charging station (distortion $<0.05\%$ vs Haversine across Delhi, $<2\text{ m/km}$). Cells are classified into:
  - *Covered:* $d \le r$ (user-selectable radius: 0.5 to 5.0 km; default 1.5 km).
  - *Underserved Priority Zone:* $d > r$ **AND** AI Demand Score $D \ge 22$ (65th percentile threshold).
  - *Low-Demand Fringe:* $d > r$ **AND** $D < 22$.
- **Stage 2 (Volumetric Adequacy):** Even if a cell satisfies $d \le r$, if installed daily throughput ($\text{kWh/day}$) falls below localized daily fleet demand, the cell flags an **Energy Capacity Deficit**.

---

## 3. Explainable Spatial AI, Forecasting & Capacity Sizing Engine (25% + 20% Rubric Weight)

### 1. Supervised Machine Learning Regressor
Rather than adopting arbitrary heuristic scoring weights, GridSight EV deploys a **Random Forest Regressor** (120 estimators, maximum tree depth 6) trained on the 375 planning cells against observed charging station density from 876 verified Switch Delhi stations. The model achieves **$R^2 = 0.796$** (**honest 5-fold cross-validation $R^2 = 0.333 \pm 0.096$**, $\text{MAE} = 5.85$). The lower cross-validation $R^2$ transparently reflects real-world supply-demand spatial decoupling—historical station siting followed municipal land availability rather than pure demand density.

$$\mathbf{D_{\text{AI}} = f_{\text{RF}}\Big(\text{Pop}, \text{POI}_{\text{comm}}, \text{Transit}, \text{Roads}, \text{Dist}_{\text{substation}}, \text{DT}_{\text{count}}\Big) \in [0, 100]} \quad \text{[Eq. 2]}$$

**Empirical Feature Importances Derived from Trained Regressor:**
- **Population Density (WorldPop):** **49.65%** (residential dwell and overnight charging)
- **Commercial Activity POIs:** **13.14%** (daytime dwell and opportunity charging)
- **Commercial Attractor Hubs:** **9.53%** (high-turnover fleet aggregation)
- **Distance to Feeder Substation:** **9.14%** (physical feeder interconnection penalty)
- **Major Road Network Density:** **8.32%** (en-route corridor transit)
- **Public Transit Interchanges:** **6.69%** (multi-modal opportunity charging)
- **Local Substation / DT Count:** **3.55%** (low-voltage grid readiness)

### 2. Continuous Sigmoid Distance-Decay Formulation
To eliminate artificial step-function cliffs where priority previously jumped abruptly from 0 to $0.65D$ at boundary distance $d = r$, GridSight EV implements a continuous 4th-order Sigmoid distance-decay formulation:

$$\mathbf{S = D_{\text{AI}} \times \left[ 1 - \frac{1}{1 + \left(\frac{d}{r}\right)^4} \right]} \quad \text{[Eq. 3]}$$

*Mathematical Behavior:* When $d \ll r$, $S \to 0$ (smoothly zero inside coverage catchment); when $d = r$, $S = 0.50 \cdot D_{\text{AI}}$; and when $d \gg r$, $S \to D_{\text{AI}}$, scaling smoothly without boundary instability.

### 3. Bass Diffusion Fleet Growth Forecasting
To model non-linear market adoption through 2030, GridSight EV calibrates the Bass Diffusion Model on 68 months of historical MoRTH VAHAN registrations (2018–2026) using Non-linear Least Squares ($R^2 = 0.992$):

$$\mathbf{S(t) = \frac{dN(t)}{dt} = \left[ p + \frac{q}{M} N(t) \right] [M - N(t)]} \quad \text{[Eq. 5A]}$$

- **Calibrated Parameters:** $p = 0.0114$ (innovation), $q = 0.4963$ (imitation), $M = 20.0\text{ Million EVs}$ (national market ceiling).
- **S-Curve Projections with Stochastic Confidence Bands ($P_{10}$ to $P_{90}$):**
  - **2026 Baseline:** National 11.23M EVs ($P_{10}: 8.16\text{M}, P_{90}: 14.54\text{M}$); Delhi active fleet: **577,295 EVs**.
  - **2028 Trajectory:** National 15.63M EVs ($P_{10}: 12.23\text{M}, P_{90}: 18.71\text{M}$); Delhi active fleet: **803,300 EVs**.
  - **2030 Horizon:** National 18.17M EVs ($P_{10}: 15.27\text{M}, P_{90}: 20.58\text{M}$); Delhi active fleet: **933,751 EVs**.

### 4. Daily Public Energy Demand Balance
For vehicle class $k \in \{\text{2W}, \text{3W}, \text{4W}, \text{Bus}, \text{Goods}\}$:

$$\mathbf{E_k = V_{k,2030} \times e_k \times \phi_{k,s} \quad (\text{kWh/day})} \quad \text{[Eq. 5B]}$$

*Where $V_{k,2030}$ is the projected active fleet, $e_k$ is daily energy consumption, and $\phi_{k,s}$ is public charging reliance.*

#### Vehicle Operational Duty Cycles & Technology Sizing Matrix

| Vehicle Category | Operational Duty & Public Reliance ($\phi$) | Technology Sizing & Power Split |
|---|---|---|
| **2-Wheelers (2W)** | $32\text{ km/d} \times 0.032\text{ kWh/km} = 1.024\text{ kWh/d}$ \| 20% Public (80% home) | 35% Battery Swap / 55% Slow AC / 10% DC |
| **3-Wheelers (3W)** | $85\text{ km/d} \times 0.075\text{ kWh/km} = 6.375\text{ kWh/d}$ \| 55% Public (45% depot) | 35% Battery Swap / 55% Slow AC / 10% DC |
| **4W Commercial / Cab** | $48\text{ km/d} \times 0.145\text{ kWh/km} = 6.960\text{ kWh/d}$ \| 32% Public (68% private) | 0% Swap / 35% Slow AC / 65% DC Fast |
| **e-Buses** | $180\text{ km/d} \times 1.150\text{ kWh/km} = 207.00\text{ kWh/d}$ \| 20% Public (80% depot) | 0% Swap / 0% Slow AC / 100% High-Power DC |
| **Light Commercial Goods** | $90\text{ km/d} \times 0.150\text{ kWh/km} = 13.500\text{ kWh/d}$ \| 50% Public (50% depot) | 0% Swap / 25% Slow AC / 75% DC Fast |

### 5. Hardware Sizing & Power Substitution Matrix
Daily connector throughput ratings:
- $\text{AC Connector} = 4.2\text{ kW} \times 5.5\text{ h} = 23.1\text{ kWh/day}$
- $\text{DC Fast Nozzle} = 30.0\text{ kW} \times 6.0\text{ h} = 180.0\text{ kWh/day}$
- $\text{Battery Swap Docket} = 12.5\text{ swaps/day} \times 2.1\text{ kWh} = 26.25\text{ kWh/day}$

$$\mathbf{\text{EVSE Points} = \text{AC} + \left\lceil \frac{\text{DC}}{1.35} \right\rceil, \quad \text{Stations} = \left\lceil \frac{\text{Points}}{4.5} \right\rceil} \quad \text{[Eq. 6]}$$

$$\mathbf{\text{Net Hardware} = \max\left(0, \text{Required} - \sum \text{Installed} \times \eta_{\text{power}}\right)} \quad \text{[Eq. 7]}$$

*Power Substitution Matrix ($\eta_{\text{power}}$):* To prevent legacy slow $3.3\text{ kW}$ AC sockets from masking high-power DC fast requirements, $\eta_{\text{power}} = 1.00$ when power matches or exceeds the required tier, $\eta_{\text{power}} = 0.15$ for slow sockets evaluated against slow AC targets, and $\eta_{\text{power}} = 0.00$ when slow sockets are evaluated against DC fast charging requirements.  
*Infill Site Redundancy Constraint:* Local infill connectors guarantee $\min(2\text{ AC} / 1\text{ DC})$ per infill hub [Eq. 4B] so that a single broken nozzle does not take a candidate station offline.

---

## 4. Empirical Findings, Siting Optimization & Validation (20% + 25% Rubric Weight)

### Empirical Supply-Demand Findings
- **National Overview (36 States/UTs):** Active EV penetration stands at 3.84% (10,689,490 active EVs out of 278.4M registered vehicles). Four states account for 41.3% of all active EVs: Uttar Pradesh (2,364,570; 9.94% penetration, commercial 3W dominant), Maharashtra (1,064,280; 3.02%), Delhi (549,153; 6.64%), and Karnataka (498,390; 3.65%).
- **Delhi Pilot Baseline:** 876 verified operational Switch Delhi sites provide 2,437 charging points and 303 swapping stations. Under default $r = 1.5\text{ km}$, geographic circular coverage is 68.3%, yet volumetric analysis reveals unserved peak deficits up to **14,200 kWh/day** in Central, Shahdara, and outer North-West freight clusters.

### Multi-Objective Grid-Constrained Siting Optimizer
A submodular greedy algorithm maximizes cumulative unserved AI demand score: $\max \sum_{i \in \text{selected}} S_i$, subject to:
1. **Feeder Distance Constraint:** Candidate cells with substation distance $> 1,500\text{ m}$ are penalized; stratified into:
   - *Tier 1 (Feeder Ready):* $<1.0\text{ km}$ distance, $\ge 500\text{ kVA}$ spare proxy.
   - *Tier 2 (Moderate):* $1.0\text{–}2.5\text{ km}$ distance, $150\text{–}250\text{ kVA}$ spare proxy.
   - *Tier 3 (Constrained):* $>2.5\text{ km}$ distance.
2. **Spatial Anti-Cannibalization Constraint:** Minimum dispersion distance $\ge 1.2\text{ km}$ between candidate hubs.
3. **Infill Redundancy Guarantee:** Minimum 2 AC sockets and 1 DC fast nozzle per selected hub (Eq. 4B).

#### Top Priority Candidate Siting Plazas

| Rank & Candidate Location | Coordinates & Substation Feeder Distance | Unserved Demand Score & Feeder Readiness Tier |
|---|---|---|
| **1. Burari Transport Hub** | $28.751^\circ\text{N}, 77.199^\circ\text{E}$ \| 410 m to Substation | Unserved Score: **88.4 / 100** \| **Tier 1 (Feeder Ready, $\ge 500\text{ kVA}$)** |
| **2. Bawana Industrial Corridor** | $28.796^\circ\text{N}, 77.035^\circ\text{E}$ \| 620 m to Substation | Unserved Score: **82.1 / 100** \| **Tier 1 (Feeder Ready, $\ge 500\text{ kVA}$)** |
| **3. Okhla Phase-III Logistics Hub** | $28.535^\circ\text{N}, 77.271^\circ\text{E}$ \| 510 m to Substation | Unserved Score: **79.6 / 100** \| **Tier 1 (Feeder Ready, $\ge 500\text{ kVA}$)** |
| **4. Anand Vihar ISBT Hub** | $28.647^\circ\text{N}, 77.312^\circ\text{E}$ \| 780 m to Substation | Unserved Score: **76.3 / 100** \| **Tier 1 (Feeder Ready, $\ge 500\text{ kVA}$)** |
| **5. Najafgarh Freight Exchange** | $28.611^\circ\text{N}, 76.984^\circ\text{E}$ \| 1,120 m to Substation | Unserved Score: **71.9 / 100** \| **Tier 2 (Moderate, $150\text{–}250\text{ kVA}$)** |

> **AUTOMATED VERIFICATION & QUALITY AUDIT (28/28 TESTS PASSED)**  
> • **Data Integrity & AI Test Suite:** All 28 / 28 automated assertions PASSED (100% success in `scripts/validate_processed_data.py`). Verified: 36 states/UTs, 10.69M active EVs, 39,641 BEE rows (44,066 connectors), 22,753 OMC stations, 8,932 FAME-II units, 876 Switch Delhi sites, 375 grid cells (22.3M pop), Random Forest $R^2 = 0.796$, Bass $R^2 = 0.992$.  
> • **TypeScript Strict Static Typing:** `tsc --noEmit` exited cleanly with 0 compilation errors across all frontend and engine components.  
> • **Production Build & Live Smoke Test:** Vite production build succeeded in 7.68s; local HTTP 200 OK test verified zero console errors and zero tile watermarks.

---

## 5. Data Strategy, Provenance & Methodological Caveats (10% + 25% Rubric Weight)

All data sources were frozen as of **19 October 2026**, preserved in original format under `data/raw/`, and tracked in `data/source_manifest.csv`:

### Data Provenance Matrix

| Source ID & Agency | Vintage & Granularity | Platform Scope, Known Limitations & Mitigation |
|---|---|---|
| **SRC-01: BEE, Ministry of Power** | Oct 2025 \| Point / Site | 39,641 rows (44,066 connectors across 29,371 unique geocoded sites). PDF extract; lacks live operational status; 119 corrupted coordinates isolated. |
| **SRC-02: MoPNG / OMC (PIB)** | Mar 2026 \| State / PSU | 22,753 operational OMC fuel retail outlet stations (27,737 installed). Kept strictly isolated from BEE to prevent double-counting. |
| **SRC-03: MHI / FAME-II (PIB)** | Mar 2026 \| State / Scheme | 8,932 operational FAME-II OMC charging units. Scheme-specific subset; maintained as independent selectable layer. |
| **SRC-04: Switch Delhi (GNCTD)** | Oct 2026 \| Point / Site | 876 deduplicated stations (573 charging + 303 swap). 15 duplicate kiosks purged; 121 swap kiosks geocoded via PIN centroid. |
| **SRC-05: OpenStreetMap (Overpass)** | Oct 2026 \| Point / Node | 725 national stations (179 in Delhi). Severe crowdsourced undercount (2.5% of BEE); used strictly as cross-check. |
| **SRC-06: MoRTH / VAHAN 4** | Oct 2026 \| State / RTO | 10,689,490 active EVs (dual fuel tags: `ELECTRIC(BOV)` + `PURE EV`). Burari distortion redistributed; compliant vs non-compliant bound. |
| **SRC-07: DataMeet Community** | 2019/2011 \| Polygon | Official 36 State/UT and 9 Delhi Census boundaries used for spatial GIS joins and choropleths (CC BY 4.0). |
| **SRC-08: WorldPop / NCP** | 2020 (2025) \| 1km Raster | Spatial population density across 375 grid cells. 2020 raster scaled to official NCP 2025 projection (22,300,000 residents). |

### Methodological Boundaries & Disclosures
- **Boundary Statement on OpenStreetMap Provenance:** Crowdsourced OSM POIs and road vectors are strictly confined to the Delhi pilot geography where data was ground-truthed ($3,534\text{ POIs}$, $8,087\text{ roads}$). At the national level, GridSight EV does not rely on OSM; state demand rankings derive 100% from official MoRTH VAHAN registrations, MoSPI GSDP tables, and NITI Aayog benchmarks.
- **12-Month Temporal Asynchrony:** The primary national supply registry (BEE, Oct 2025) predates demand data (VAHAN, Oct 2026) by 12 months, naturally exaggerating apparent deficits. GridSight EV mitigates this by providing live Switch Delhi (Oct 2026) as an alternate baseline and surfacing temporal disclaimers on map legends.
- **Substation Proximity $\neq$ Electrical Hosting Capacity:** 99.3% of OSM substations lack MVA capacity tags. In our model, distance to substation serves strictly as a physical interconnection proximity proxy, never claiming unverified electrical capacity.
- **Active Non-Compliant Registrations (26.4%):** Of 10.69M active EVs, 2.82M lack active fitness/PUC compliance. The platform displays both compliant-only (7.87M) and total active fleet metrics, establishing lower and upper demand boundaries.
- **Absence of Real-Time Utilization Telemetry:** Public registries omit real-time connector occupancy and operational uptime. The platform models physical infrastructure presence; OMC operational availability ratios (82.0%) can be toggled as a sensitivity discount.

---

## 6. Phased Implementation Roadmap, References & Rubric Alignment (20% + 10% Rubric Weight)

### Phased Development Roadmap

| Phase & Development Timeline | Core Technical Deliverables & Target Exit Benchmark |
|---|---|
| **Phase 0: Baseline Freeze & AI Core**<br>*(Completed - Round 1 Submission)* | Data pipeline, 28/28 test assertions, Random Forest demand ML, Bass Diffusion forecasting, constrained siting optimizer, zero-watermark Leaflet UI.<br>**Exit Benchmark:** *Operational prototype deployed on main branch; 0 TypeScript compiler errors.* |
| **Phase 1: Highway Corridor Scaling**<br>*(Weeks 1–2 Post-Round 1)* | Expand 5km spatial buffer along NH-48 (Delhi–Jaipur) and Yamuna Expressway using PM Gati Shakti & NHAI freight vector layers for inter-city infill and fast-charging simulation.<br>**Exit Benchmark:** *Dedicated inter-city highway corridor infill & fast-charging simulation tool.* |
| **Phase 2: Distribution Grid Capacity Proxies**<br>*(Weeks 3–4 Post-Round 1)* | Incorporate secondary CEA distribution standards and DISCOM voltage levels (11kV, 33kV, 66kV) to model feeder hosting headroom without proprietary SCADA.<br>**Exit Benchmark:** *Grid Feasibility Index per 2km cell combining physical distance with voltage tier.* |
| **Phase 3: Final Deployment & Grand Finale**<br>*(Weeks 5–6 Post-Round 1)* | Containerize application via Docker; establish high-availability cloud hosting with full offline caching fallback for jury defense.<br>**Exit Benchmark:** *Rehearsed live jury demonstration with zero external API dependencies.* |

### Official Techfest Evaluation Criteria Alignment Matrix

| Evaluation Criterion & Weight | Primary Methodology Document Sections & Technical Evidence |
|---|---|
| **Problem Understanding & Relevance (25%)** | **Section 1:** Multi-registry overlap, non-additivity design rule, Burari RTO commercial distortion, spatial catchment vs. volumetric energy adequacy disconnect.<br>*Repository Evidence:* `DATA_AVAILABILITY_AUDIT.md`, `DATA_GAPS.md`, interactive non-additivity matrix in UI. |
| **Technical Approach & Feasibility (25%)** | **Sections 2 & 3:** 375-cell spatial planning grid, Random Forest ML regressor, continuous Sigmoid decay kernel, Bass diffusion forecasting, 2030 bottom-up energy balance.<br>*Repository Evidence:* `scripts/train_ai_models.py`, `src/utils/planningEngine.ts`, 28/28 assertions pass. |
| **Innovation & Differentiation (20%)** | **Sections 3 & 4:** Physics-Informed ML (PIML), submodular greedy siting optimizer, power substitution matrix, dual VAHAN fuel tags discovery.<br>*Repository Evidence:* `src/components/AiStudioView.tsx`, `public/data/ai_optimization_results.json`. |
| **Implementation Roadmap & Feasibility (20%)** | **Sections 1 & 6:** Phase 0 completed operational prototype, Phases 1–3 highway corridor and DISCOM voltage milestones, exit benchmarks.<br>*Repository Evidence:* `DELIVERABLE_AUDIT.md`, production build in 7.68s, 0 TypeScript compiler errors. |
| **Data Strategy & Provenance (10%)** | **Section 5 & References:** 8-source provenance table, 19 Oct 2026 frozen manifest, OSM boundary statement, 4 critical caveats.<br>*Repository Evidence:* `data/source_manifest.csv`, `DATA_QUALITY_REPORT.md`, raw data archives. |

### Key Regulatory & Scientific References

- **[1] BEE Public Charging Stations Registry:** Bureau of Energy Efficiency, Ministry of Power, *Public Charging Stations Data till 26 Oct 2025* (`EV_PCS_Data_29277.pdf`), Published 17 Feb 2026.
- **[2] MoPNG OMC Retail Outlet Stations:** Ministry of Petroleum and Natural Gas / Ministry of Heavy Industries, *PIB Press Release PRID 2246042*, 27 Mar 2026.
- **[3] FAME-II Scheme Charging Installations:** Ministry of Heavy Industries, *PIB Press Release PRID 2246045*, 27 Mar 2026.
- **[4] Switch Delhi Charging & Swapping Portal:** Transport Department & Dialogue and Development Commission of Delhi (DDC), `ev.delhi.gov.in/charging-station`, snapshot 19 Oct 2026.
- **[5] VAHAN 4 Public Analytics Portal:** Ministry of Road Transport and Highways (MoRTH) / NIC Parivahan, `analytics.parivahan.gov.in`, snapshot 19 Oct 2026.
- **[6] DataMeet Spatial Boundaries:** DataMeet Spatial Community, *Census-2011 District & State Boundaries* (CC BY 4.0), `github.com/datameet/maps`.
- **[7] WorldPop Gridded Population:** WorldPop Project, *India 1km Population Density Raster* (Dataset ID 50771), scaled to NCP 2025 projection.
- **[8] OpenStreetMap Data Extracts:** OpenStreetMap Contributors, Overpass API extracts for India and Delhi charging stations, highway corridors, substations, and POIs (ODbL 1.0), snapshot 19 Oct 2026.
- **[9] Bass Innovation Diffusion Model:** Bass, F. M., *A New Product Growth for Model Innovations*, Management Science 15(5), 1969, pp. 215–227.

---

### Verification and File Access

- **Markdown File in Project:** [`METHODOLOGY_DOCUMENT_COMPRESSED.md`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/METHODOLOGY_DOCUMENT_COMPRESSED.md)
- **Compressed Word Document (3 Pages):** [`GridSight_EV_Methodology_Compressed.docx`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/GridSight_EV_Methodology_Compressed.docx)
- **Compressed PDF Document (3 Pages):** [`GridSight_EV_Methodology_Compressed.pdf`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/GridSight_EV_Methodology_Compressed.pdf)
- **Stressed (+60% Font Size) Word Document (6 Pages):** [`GridSight_EV_Methodology_Compressed_Stressed.docx`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/GridSight_EV_Methodology_Compressed_Stressed.docx)
- **Stressed (+60% Font Size) PDF Document (6 Pages):** [`GridSight_EV_Methodology_Compressed_Stressed.pdf`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/GridSight_EV_Methodology_Compressed_Stressed.pdf)
- **Full Stress Test & Evidence Audit:** [`Compression_Audit.md`](file:///C:/Users/hp/.gemini/antigravity/scratch/ev-infra-map-india/Compression_Audit.md)
- **GitHub Repository:** [https://github.com/aadityaexpress/gridsight-ev](https://github.com/aadityaexpress/gridsight-ev)
