# GridSight EV: Geospatial EV Charging Infrastructure Intelligence Platform
## Analytical Methodology & Implementation Document

**Competition:** Techfest IIT Bombay 2026–27  
**Track:** Challenge 1 — EV Infra Map India (Ministry of Heavy Industries & ICAT)  
**Team Name:** Mechies  
**Institution:** Netaji Subhas University of Technology (NSUT), New Delhi  
**Team Leader & Submitter:** Kunal (`kunalclass1112@gmail.com` | `+91 8595289897`)  
**Repository:** [https://github.com/aadityaexpress/gridsight-ev](https://github.com/aadityaexpress/gridsight-ev)  

---

### Executive Document Status & Audit Key
- ✅ **Fully Implemented:** Functioning and verified in production TypeScript/Python codebase and live interactive platform.
- 🧪 **Validated:** Passed through automated data invariant tests (28 of 28 passing assertions, zero null/NaN crashes).
- 🗓 **Roadmap:** Scheduled for Phase 1–3 expansion (inter-city freight corridors, automated SCADA telematics).

---

## 1. Problem Understanding & Relevance (25%)

### 1.1 The Fragmented Reality of Indian EV Charging Data
Public EV charging deployment in India is severely constrained by institutional fragmentation across central ministries, state nodal agencies, municipal bodies, and crowdsourced registries:

1. **Registry Unit Ambiguity & Overlap:**  
   The Bureau of Energy Efficiency (BEE) national registry logs individual charger/connector rows (39,641 rows); Ministry of Petroleum & Natural Gas (MoPNG) Parliamentary releases track Oil Marketing Company (OMC) retail fuel stations (27,737 installed, 22,753 operational); Ministry of Heavy Industries (MHI) tracks capital-subsidized FAME-II deployments (8,932 OMC installations); and OpenStreetMap (OSM) captures a sparse crowdsourced sample (725 national features). Naively summing these registries causes massive double-counting and distorts public capital allocation.
2. **Geographic Granularity & Registration Skew (The Burari Anomaly):**  
   EV registration data from MoRTH VAHAN 4 is aggregated by State and Regional Transport Office (RTO) jurisdictions, whereas chargers are discrete geographic coordinates. In Delhi, commercial EV fleets (e-autos, e-rickshaws, app cabs, delivery goods) register predominantly at the centralized Burari Transport Authority (DL-1Y/1Z), representing over 35% of all commercial EVs in the capital. Raw data creates an artificial demand illusion in North Delhi while starving the remaining 8 districts.
3. **The Universal Ratio Fallacy ("1 Charger per 10 EVs"):**  
   Conventional planning applies static international EV-to-charger ratios. In India, this assumption is mathematically invalid: an electric 2-wheeler consumes $\sim 1.02\text{ kWh/day}$ with 80% home charging reliance, whereas a commercial 3-wheeler consumes $\sim 6.38\text{ kWh/day}$ with 55% public reliance. Universal ratios lead to stranded capital, unserved commercial demand, and distribution transformer overload.
4. **Physical Presence vs. Volumetric Service Adequacy:**  
   A spatial location within $1\text{ km}$ offering two slow $3.3\text{ kW}$ sockets cannot adequately serve 80 commercial e-rickshaws. GridSight EV explicitly decouples spatial accessibility catchment from volumetric energy throughput ($\text{kWh/day}$).

```
                     ┌─────────────────────────────────────────────────────────┐
                     │            CHALLENGE 1: CORE PLANNING PROBLEM           │
                     └────────────────────────────┬────────────────────────────┘
                                                  │
         ┌────────────────────────────────────────┼────────────────────────────────────────┐
         │                                        │                                        │
         ▼                                        ▼                                        ▼
┌─────────────────────────┐            ┌──────────────────────┐            ┌──────────────────────────────┐
│  REGISTRY FRAGMENTATION │            │  RTO SPATIAL SKEW    │            │  UNIVERSAL RATIO FALLACY     │
│  BEE vs OMC vs Switch   │            │  Burari (DL-1Y) 35%  │            │  Conflating 2W / 3W / 4W     │
│  Double-counting risk   │            │  Commercial EV Skew  │            │  Ignoring kWh consumption    │
└────────────┬────────────┘            └──────────┬───────────┘            └──────────────┬───────────────┘
             │                                    │                                       │
             └────────────────────────────────────┼───────────────────────────────────────┘
                                                  │
                                                  ▼
                     ┌─────────────────────────────────────────────────────────┐
                     │           GRIDSIGHT EV METHODOLOGICAL ENGINE            │
                     │  1. Non-Additive Multi-Source Spatial Reconciliation    │
                     │  2. Burari Activity-Weighted Fleet Redistribution       │
                     │  3. 375-Cell Spatial Grid with Sigmoid Distance Decay   │
                     │  4. Supervised Spatial ML Regressor (Random Forest)     │
                     │  5. Bass Diffusion Fleet Forecasting S-Curve            │
                     │  6. Bottom-Up Daily kWh Energy Balance Hardware Sizing  │
                     │  7. Submodular Greedy Grid-Constrained Siting Optimizer │
                     └─────────────────────────────────────────────────────────┘
```

---

## 2. Data Strategy, Provenance & Quality Assurance (10%)

### 2.1 The Non-Additivity Design Rule
To eliminate duplicate counting, GridSight EV enforces an uncompromising architectural principle: **different registries are maintained as independent analytical baselines and never summed together**. The user interface allows planners to toggle one baseline at a time (e.g., Switch Delhi vs. BEE Registry vs. OMC Retail Pumps vs. Combined Verification).

### 2.2 Comprehensive Source Manifest (Data Freeze: 19 October 2026)

| ID | Dataset & Authority | Vintage | Geometry | Scale & Scope | Limitation & Engineering Treatment |
|:---|:---|:---:|:---:|:---|:---|
| **SRC-01** | **BEE National EVPCS Registry** (MoP) | 26 Oct 2025 | Point | 29,371 sites (39,641 charger rows; 44,066 connectors) across 36 States/UTs. | Static registry; lacks operational uptime; 119 corrupted coordinate rows isolated and corrected. |
| **SRC-02** | **PIB / MoPNG OMC EVPCS** (PRID 2246042) | 01 Mar 2026 | State | 27,737 installed OMC retail fuel pump chargers (22,753 operational). | Retail fuel stations only; kept isolated from BEE to prevent double counting. |
| **SRC-03** | **PIB / MHI FAME-II EVPCS** (PRID 2246045) | 01 Mar 2026 | State | 8,932 FAME-II OMC installations + 227 public agency chargers. | Scheme-specific capital subsidy subset; tracked independently. |
| **SRC-04** | **GNCTD Switch Delhi Portal** (DDC Delhi) | 19 Oct 2026 | Point | 876 verified stations (573 charging stations, 303 battery swap hubs). | 15 duplicate kiosk rows removed; 121 swap kiosks lacking street coords geocoded via verified PIN centroid. |
| **SRC-05** | **MoRTH VAHAN 4 Portal** | 19 Oct 2026 | State / RTO | 10,689,490 active national EVs; 549,153 Delhi EVs across 23 zonal RTOs. | Ingested dual tags: `ELECTRIC(BOV)` (6.35M) + `PURE EV` (4.34M); compliant (7.87M) & non-compliant (2.82M). |
| **SRC-06** | **OpenStreetMap Contributors** | 19 Oct 2026 | Multi | 8,087 major road vectors, 3,534 POIs, 576 substations/transformers. | Confined strictly to Delhi pilot; crowdsourced data is never used for national state rankings. |
| **SRC-07** | **WorldPop 1km Population Grid** | Scaled 2025 | Raster | 375 spatial planning grid cells over Delhi NCT ($2.0\text{ km} \times 2.0\text{ km}$). | 2020 raster pixel sums scaled to National Commission on Population 2025 Delhi target ($22,300,000$). |
| **SRC-08** | **DataMeet Spatial Community** | 2019 | Polygon | 36 States/UTs and 9 Delhi Census district boundaries (CC BY 4.0). | Standardized boundary polygons used for spatial containment joins. |

### 2.3 Automated Invariant Testing Suite
Before any dataset enters the client web application, it must pass `scripts/validate_processed_data.py`. All **28 of 28 assertions pass at 100%**:
- National state sum checks ($N=36$; $\sum \text{VAHAN} = 10,689,490$; $\sum \text{BEE Rows} = 39,641$; $\sum \text{OMC} = 27,737$).
- Delhi district sum checks ($N=9$; $\sum \text{RTO} = 549,153$; $\text{Switch Deduplicated} = 876$).
- Statistical sanity bounds (Spatial ML $R^2 > 0.70$; Bass S-Curve $R^2 > 0.95$; Sited Hubs $= 25$).

---

## 3. Technical Approach & Analytical Methodology (25%)

### 3.1 Burari Commercial Fleet Activity Normalization
To resolve the Burari RTO registration distortion (where DL-1Y/1Z commercial registrations concentrate artificially), GridSight EV reallocates commercial vehicles (3-wheelers, 4-wheeler cabs, electric delivery goods) across Delhi's 9 districts using an empirical activity crosswalk:

$$\mathbf{w_{\text{district}} = 0.40 \cdot \left(\frac{P_{\text{district}}}{P_{\text{total}}}\right) + 0.30 \cdot \left(\frac{L_{\text{roads, district}}}{L_{\text{roads, total}}}\right) + 0.30 \cdot \left(\frac{N_{\text{poi, district}}}{N_{\text{poi, total}}}\right)} \quad \text{[Eq. 1]}$$

*Where $P$ is the 2025 Census population, $L_{\text{roads}}$ is total major road centerline length, and $N_{\text{poi}}$ is the count of commercial and transport POIs. Private 2-wheelers remain assigned to their verified zonal RTOs.*

### 3.2 Spatial Grid Discretization (375 Planning Cells)
The NCT of Delhi is discretized into 375 uniform cells of $0.018^\circ\text{ Lat} \times 0.0205^\circ\text{ Lon}$ ($\approx 2.0\text{ km} \times 2.0\text{ km}$). The bounding box ($28.40^\circ\text{–}28.89^\circ\text{N}, 76.83^\circ\text{–}77.35^\circ\text{E}$) encompasses the municipal boundary plus cross-border commuter freight gateways (Gurugram, Noida, Faridabad, Ghaziabad borders).

### 3.3 Supervised Spatial Demand ML Regressor
Rather than relying on arbitrary heuristic weights, GridSight EV trains a **Supervised Random Forest Regressor** (120 trees, max depth 6) across all 375 planning cells against observed charging infrastructure density:

$$\mathbf{D_{\text{AI}} = f_{\text{RF}}\Big(\text{Pop}, \text{POI}_{\text{comm}}, \text{Transit}, \text{Roads}, \text{Dist}_{\text{substation}}, \text{DT}_{\text{count}}\Big) \in [0, 100]} \quad \text{[Eq. 2]}$$

**Empirical Feature Importance Distribution ($R^2 = 0.796, \text{MAE} = 5.85$):**
- **Population Density (WorldPop):** **49.65%** (overnight residential charging elasticity)
- **Commercial & Activity POIs:** **22.67%** (daytime dwell and opportunity charging)
- **Distance to Feeder Substation:** **9.14%** (distribution grid interconnection readiness)
- **Major Road Network Density:** **8.32%** (in-transit charging volume)
- **Public Transit Interchanges:** **6.69%** (multi-modal fleet aggregation)
- **Local Substation / DT Count:** **3.55%** (low-voltage feeder redundancy)

### 3.4 Continuous Sigmoid Distance-Decay Kernel
To eliminate artificial boundary cliffs where priority previously jumped discontinuously across a fixed circular buffer ($d = r$), GridSight EV introduces a continuous **Sigmoid Distance-Decay Formulation**:

$$\mathbf{S = D_{\text{AI}} \cdot \left[ 1 - \frac{1}{1 + \left(\frac{d}{r}\right)^4} \right]} \quad \text{[Eq. 3]}$$

- When $d \ll r$: $S \to 0$ (smoothly zero within adequate catchment).
- When $d = r$: $S = 0.50 \cdot D_{\text{AI}}$ (half-maximum transition at threshold).
- When $d \gg r$: $S \to D_{\text{AI}}$ (full priority deficit penalty outside catchment).

### 3.5 Predictive Fleet Adoption: Bass Diffusion S-Curve Model
To replace static linear multipliers with a realistic non-linear technology adoption trajectory, GridSight EV calibrates the **Bass Diffusion Model** on historical VAHAN national registration time-series:

$$\mathbf{F(t) = M \cdot \frac{1 - e^{-(p+q)t}}{1 + \frac{q}{p}e^{-(p+q)t}}} \quad \text{[Eq. 4]}$$

- **Calibrated Parameters ($R^2 = 0.992$):**
  - **Innovation Coefficient ($p$):** $0.0114$ (policy-driven adoption, subsidies, early adopters)
  - **Imitation Coefficient ($q$):** $0.4963$ (word-of-mouth, charging network visibility, peer effects)
  - **National Market Ceiling ($M$):** $20.0\text{ Million EVs}$
- **Trajectory Forecasts (National & Delhi Fleet with $P_{10}/P_{90}$ Bands):**
  - **2026 Baseline:** National $10.69\text{M}$ EVs; Delhi active fleet: $\mathbf{549,153\text{ EVs}}$.
  - **2028 Horizon:** National $15.63\text{M}$ EVs ($P_{10}: 12.23\text{M}, P_{90}: 18.71\text{M}$); Delhi active fleet: $\mathbf{803,300\text{ EVs}}$.
  - **2030 Horizon:** National $18.17\text{M}$ EVs ($P_{10}: 15.27\text{M}, P_{90}: 20.58\text{M}$); Delhi active fleet: $\mathbf{933,751\text{ EVs}}$.

### 3.6 Bottom-Up Volumetric Energy Balance & Hardware Sizing
For each vehicle category $k \in \{\text{2W}, \text{3W}, \text{4W}, \text{Bus}, \text{Goods}\}$:

$$\mathbf{E_k = V_{k,2030} \cdot e_k \cdot \phi_{k,s} \quad (\text{kWh/day})} \quad \text{[Eq. 5]}$$

- **Daily Driving Energy Rates ($e_k$):**  
  2W: $1.024\text{ kWh}$ ($32\text{ km} \times 0.032\text{ kWh/km}$) | 3W: $6.375\text{ kWh}$ ($85\text{ km} \times 0.075\text{ kWh/km}$) | 4W: $6.96\text{ kWh}$ ($48\text{ km} \times 0.145\text{ kWh/km}$) | Bus: $207.0\text{ kWh}$ ($180\text{ km} \times 1.15\text{ kWh/km}$) | Goods: $13.5\text{ kWh}$ ($75\text{ km} \times 0.18\text{ kWh/km}$).
- **Public Charging Share ($\phi_{k,s}$):**  
  2W: 20% | 3W: 55% | 4W: 35% | Bus: 20% (depot-backed) | Goods: 50%.
- **Battery Swapping Split ($\sigma_s$):**  
  Absorbs 35% of 2W/3W public energy. Remaining plug-in energy splits into AC Type-2/LEV sockets vs. DC Fast CCS2/DC-001 guns.
- **Daily Connector Throughput Capacities:**  
  - $\text{AC Connector} = 4.2\text{ kW} \times 5.5\text{h} = 23.1\text{ kWh/day}$
  - $\text{DC Fast Nozzle} = 30.0\text{ kW} \times 6.0\text{h} = 180.0\text{ kWh/day}$
  - $\text{Swap Docket} = 13\text{ swaps/day} \times 2.1\text{ kWh} = 27.3\text{ kWh/day}$

$$\mathbf{\text{Required Connectors} = \left\lceil \frac{E_{\text{public}}}{\text{Throughput}} \right\rceil, \quad \text{EVSE Points} = \text{AC} + \left\lceil \frac{\text{DC}}{1.35} \right\rceil, \quad \text{Stations} = \left\lceil \frac{\text{EVSE Points}}{4.5} \right\rceil} \quad \text{[Eq. 6]}$$

$$\mathbf{\text{Net New Hardware} = \max\left(0, \text{Required Hardware} - \sum \text{Existing Installed} \cdot \eta_{\text{power}}\right)} \quad \text{[Eq. 7]}$$

*Where $\eta_{\text{power}}$ is a power-substitution matrix preventing slow $3.3\text{ kW}$ sockets from discounting high-power DC fast requirements.*

### 3.7 Submodular Greedy Grid-Constrained Siting Optimizer
To select optimal candidate locations, GridSight EV executes a submodular greedy optimizer bounded by spatial and electrical constraints:
- **Objective:** $\max \sum_{i \in \text{Selected}} S_i \cdot (0.6 + 0.4 \cdot \text{GridFeasibility}_i)$.
- **Feeder Distance Constraint:** Sites are classified into Feeder Tiers based on physical distance to nearest $11\text{kV}/33\text{kV}$ substation:
  - **Tier-1 (<1.0 km):** $\ge 500\text{ kVA}$ spare capacity proxy ($250\text{ kW}$ max hosting capacity).
  - **Tier-2 (1.0–2.5 km):** $150\text{–}250\text{ kVA}$ spare capacity proxy ($120\text{ kW}$ max hosting capacity).
  - **Tier-3 (>2.5 km):** Feeder constrained; requires dedicated distribution transformer upgrade ($60\text{ kW}$ max hosting capacity).
- **Spatial Anti-Cannibalization Constraint:** $\text{Haversine}(i, j) \ge 1.2\text{ km}$ for all pairs of selected candidate hubs $(i, j)$.

---

## 4. Innovation & Technical Soundness (20%)

| Innovation Dimension | Conventional Industry Practice | GridSight EV Innovation |
|:---|:---|:---|
| **Data Architecture** | Blindly merges BEE, OMC, and crowdsourced data, inflating charger counts by 40–60%. | **Strict Non-Additivity Design Rule:** Sources are preserved as independent selectable baselines with zero duplicate counting. |
| **Fleet Demand Mapping** | Treats RTO registrations as literal local demand, creating massive false demand spikes at central RTOs. | **Burari Fleet Redistribution Algorithm (Eq. 1):** Reallocates 200k+ commercial EVs across 9 districts by population and POIs. |
| **Spatial Gap Prioritization** | Arbitrary circular step buffers ($d \le r$) causing boundary cliff instability. | **Continuous Sigmoid Distance-Decay Kernel (Eq. 3):** Smooth, continuous priority decay eliminating threshold artifacts. |
| **Adoption Modeling** | Static, arbitrary linear annual compound growth rates (CAGR). | **Calibrated Bass Diffusion S-Curve (Eq. 4):** Non-linear adoption model ($R^2=0.992$) capturing market tipping points with $P_{10}/P_{90}$ bands. |
| **Hardware Sizing** | Universal "1 charger per 10 EVs" ratio across all vehicle segments. | **Physics-Grounded Bottom-Up Energy Simulator (Eq. 5–7):** Disaggregates daily kWh by segment into Stations, EVSE, AC/DC Nozzles, and Swap Dockets. |
| **Grid Siting Feasibility** | Assumes power is infinitely available at all geographic points. | **Submodular Optimizer with Substation Feeder Tiers:** Restricts siting by 11kV/33kV substation proximity and hosting limits. |
| **Utility Operational UI** | Standard light dashboards unsuited for control-room monitoring. | **One-Click Cartographic Dark Mode:** Inverts Leaflet cartography while preserving distinct marker colors with `localStorage` persistence. |

---

## 5. Software Architecture & Implementation Verification

### 5.1 Architecture Stack
- **Frontend Core:** React 18, TypeScript (strict mode), Vite 5.
- **Cartographic Subsystem:** Leaflet 1.9, React-Leaflet 4, keyless OpenStreetMap tile server (zero third-party API dependencies or watermarks).
- **Mathematical Computation Engine:** `src/utils/planningEngine.ts` executes all grid filtering, coverage distance evaluations, sigmoid decay functions, and scenario projections synchronously in the client browser in $<15\text{ milliseconds}$.
- **Data & AI Pipelines:** Python 3 (`scripts/process_data.py`, `scripts/train_ai_models.py`, `scripts/validate_processed_data.py`).

### 5.2 Five-Tab Institutional Navigation Structure
1. **Delhi Map:** Street-level visualization of 876 Switch Delhi and 1,909 BEE stations, power class filters, Burari redistribution toggle, and 25 AI candidate hub overlays.
2. **National Overview:** 36 States/UTs choropleth map, 10.68M VAHAN active EVs, 44K BEE connectors, and 27,737 OMC retail fuel station chargers.
3. **Coverage Planning:** 375-cell spatial coverage map, live toggle between Spatial ML Regressor and baseline heuristic, continuous Sigmoid decay, and 2030 future capacity simulator.
4. **AI & Optimization Studio:** Dedicated view for the Spatial Random Forest Regressor (feature importance bars), Bass Diffusion S-curve adoption curves, and Constrained Siting Optimizer.
5. **Data & Methodology:** Full audit trail, source reconciliation matrix, documented data gaps, and 28 passing schema assertions.

### 5.3 Build and Execution Verification
- `npx tsc --noEmit`: 0 compiler errors (strict mode).
- `npm run build`: Production bundle transformed (1,622 modules in 9.66s, `dist/` ready).
- `python scripts/validate_processed_data.py`: **28 / 28 assertions passed (100%)**.
- Open-source repository: Deployed and maintained on GitHub (`aadityaexpress/gridsight-ev`).

---

## 6. Implementation Roadmap (20%)

```
┌───────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 GRIDSIGHT EV IMPLEMENTATION ROADMAP                                   │
└───────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                   │
  ┌────────────────────────────────────────────────┼─────────────────────────────────────────────────┐
  │ PHASE 0: BASELINE & PROTOTYPE (COMPLETED)      │ PHASE 1: HIGHWAY CORRIDORS (Q1–Q2 2027)         │
  │ • 375-cell Delhi pilot & 36-state overview     │ • 5km spatial buffers along NH-48 & NH-44       │
  │ • 876 Switch Delhi, 1,909 BEE, 27.7K OMC pumps │ • Golden Quadrilateral inter-city infill        │
  │ • Spatial Random Forest & Bass Diffusion model │ • Top-5 Tier-1 Metros (Mumbai, Bengaluru, etc.) │
  │ • 28/28 automated validation assertions passed │ • PM Gati Shakti freight vector ingestion       │
  └────────────────────────────────────────────────┼─────────────────────────────────────────────────┘
                                                   │
  ┌────────────────────────────────────────────────┼─────────────────────────────────────────────────┐
  │ PHASE 2: DISCOM GRID INTEGRATION (Q3–Q4 2027)  │ PHASE 3: LIVE TELEMATICS & SCALE (2028)         │
  │ • Direct 11kV/33kV distribution feeder GIS     │ • PM E-DRIVE live charger API telemetry         │
  │ • Real-time substation spare MVA capacity maps │ • Dynamic tariff & utilization tracking         │
  │ • Dynamic transformer upgrade costing          │ • Pan-India municipal ward automated sizing     │
  │ • Time-of-Day (ToD) tariff optimization        │ • Open API for CPOs, OEMs, and city planners    │
  └────────────────────────────────────────────────┴─────────────────────────────────────────────────┘
```

---

## 7. Limitations, Boundary Statements & Risk Mitigation

| Practical Limitation / Risk | Analytical Consequence | GridSight EV Engineering Treatment |
|:---|:---|:---|
| **Absence of Real-Time Session Logs** | Public registries do not expose live occupancy, session duration, or connector downtime. | Platform frames metrics strictly as physical infrastructure presence; provides OMC operational availability discount factor (82.0%). |
| **Substation Proximity $\neq$ Electrical Capacity** | Physical distance to a substation does not guarantee spare distribution capacity ($\text{kVA}$). | Explicit disclaimer on UI; substations are treated as physical proximity proxies with Feeder Feasibility Tiers (1/2/3). |
| **Registry Temporal Asynchrony** | BEE registry (Oct 2025) predates MoRTH VAHAN (Oct 2026) by 12 months. | Enforces strict source separation; users choose one baseline at a time; temporal mismatch disclaimers surfaced on legends. |
| **Active Non-Compliant Fleet** | 26.4% of registered EVs lack active fitness/PUC compliance. | Provides both active compliant (7.87M) and total registered (10.68M) breakdowns to establish upper and lower bounds. |
| **Planar Projection Approximation** | Equirectangular planar approximation across Delhi grid cells. | Mathematical verification proves distortion is $<0.05\%$ ($<2\text{ m/km}$ across Delhi's $50\text{ km}$ extent), well within GPS tolerances. |

---

## 8. Alignment with Evaluation Rubric

| Criterion | Weight | Primary Methodology Section | Codebase & Technical Evidence |
|:---|:---:|:---|:---|
| **Problem Understanding & Relevance** | **25%** | **Section 1 & 2** (Fragmentation, Burari RTO skew, universal ratio failure, non-additivity) | `DATA_AVAILABILITY_AUDIT.md`, `src/components/DelhiPilotView.tsx` |
| **Technical Approach & Feasibility** | **25%** | **Section 3** (Spatial ML Regressor, Sigmoid decay, Bass S-curve, bottom-up kWh sizing) | `scripts/train_ai_models.py`, `src/utils/planningEngine.ts` |
| **Innovation & Differentiation** | **20%** | **Section 3 & 4** (PIML Explainable AI, continuous distance decay, OMC fuel pump integration) | `src/components/CoveragePlanningView.tsx`, `AiStudioView.tsx` |
| **Implementation Roadmap** | **20%** | **Section 6** (Phase 0 complete, Phase 1–3 highway corridors, DISCOM SCADA, PM E-DRIVE) | `scripts/validate_processed_data.py`, `PRESENTATION_SLIDES.md` |
| **Planned Data Strategy** | **10%** | **Section 2 & 7** (8 official datasets, source separation, OSM boundary statement, 28 assertions) | `data/source_manifest.csv`, `DATA_QUALITY_REPORT.md` |

---

### Verification & Submission Notice
*This methodology document reflects the working, production-compiled codebase of GridSight EV on branch `main` at commit `0fbb9a0`. All mathematical formulations, source manifests, data assertions, and architectural designs described herein are independently reproducible and verified.*
