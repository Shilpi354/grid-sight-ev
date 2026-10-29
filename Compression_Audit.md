# GridSight EV: Methodology Document Compression & Evidence Audit

**Project:** GridSight EV: Geospatial EV Charging Infrastructure Intelligence Platform  
**Competition:** IIT Bombay Techfest 2026–27 | EV Infrastructure & Green Mobility AI Challenge (Challenge 1)  
**Team:** Mechies | Netaji Subhas University of Technology (NSUT)  
**Deliverables Generated:**  
1. `GridSight_EV_Methodology_Condensed.docx` (Microsoft Word A4, strictly 6 pages)  
2. `GridSight_EV_Methodology_Condensed.pdf` (Direct Word COM layout export, strictly 6 pages)  
3. `Compression_Audit.md` (Evidence audit, page budgeting, and rubric verification)

---

## 1. Page Budget & Length Reduction Summary

| Metric | Original Submission Document | Condensed Methodology Document | Change / Variance | Evaluation Status |
|---|:---:|:---:|:---:|:---:|
| **Word Page Count (Computed via Word COM)** | **19–20 Pages** (standard template layout) | **6 Pages** (strictly budgeted A4) | **~68.4% page length reduction** | **Target Achieved (5–6 Page Limit Met)** |
| **PDF Page Count (Layout Export)** | **19–20 Pages** | **6 Pages** | **6 Pages exactly** | **No orphan lines or table overflows** |
| **Total Word Count** | **4,311 Words** | **3,182 Words** | **-1,129 Words (-26.2% net text reduction)** | **High information density preserved** |
| **Typography & Grid Geometry** | 1.15 line spacing, 14pt H1, 1-inch margins | 1.06 line spacing, 9.3pt body, 0.58-in margins | Compact editorial grid | 100% ECMA-376 Schema Compliant |
| **Mathematical Equations** | 7 standalone equation blocks | 7 integrated high-contrast equation cards | All equations retained (Eq. 1 to 7) | 100% Preserved |
| **Tables & Data Matrices** | 7 tables (frequent multi-page splitting) | 6 consolidated tables (zero cross-page splits) | Self-contained on their respective pages | 0 Split Table Headers |

---

## 2. Page-by-Page Content & Architecture Layout

The condensed document is structured into six dedicated, self-contained single-page chapters directly mirroring the official Techfest judging requirements:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ PAGE 1: Problem Statement, Solution Framework & System Overview             │
│ • Challenge Context: Multi-registry overlap, unit ambiguity, Burari skew    │
│ • Proximity vs Volumetric Adequacy Disconnect (spatial vs energy gap)       │
│ • 4-Pillar Platform Framework & Delhi Spatial Pilot Boundary Scope          │
│ • Platform Architecture Flow Table (Tiers 1 to 4: Ingestion to UI)          │
│ • Implementation Status Callout: Verified Operational vs Planned Roadmap    │
├─────────────────────────────────────────────────────────────────────────────┤
│ PAGE 2: Data Integration, Normalization & Spatial Methodology               │
│ • Non-Additivity Design Rule (Registries are never summed together)         │
│ • Dual VAHAN Fuel Tag Reconciliation: ELECTRIC(BOV) [6.35M] + PURE EV [4.34M]│
│ • Burari Commercial Fleet Spatial Redistribution & Equation Box [Eq. 1]     │
│ • Delhi 375-Cell Spatial Planning Grid (2km × 2km, WorldPop 22.3M pop)      │
│ • Two-Stage Coverage Assessment (Euclidean proximity d ≤ r vs energy deficit)│
│ • Cartographic Specifications Callout (Haversine <0.05% error, gateway hubs)│
├─────────────────────────────────────────────────────────────────────────────┤
│ PAGE 3: Explainable Spatial AI, Forecasting & Capacity Sizing Engine        │
│ • Supervised Random Forest Regressor & Equation Box [Eq. 2] (R² = 0.796)     │
│   - 5-Fold Cross-Validation R² = 0.333 ± 0.096, MAE = 5.85 (Fully Disclosed)│
│   - Feature Importances: Pop 49.65%, POI 22.67%, Feeder 9.14%, Roads 8.32%  │
│ • Continuous Sigmoid Distance-Decay Kernel & Equation Box [Eq. 3]           │
│ • Bass Diffusion Adoption Model & Equation Box [Eq. 5A] (R² = 0.992)        │
│   - Calibrated Parameters: p = 0.0114, q = 0.4963, M = 20.0M ceiling         │
│   - Projections with P10/P90 Bands: 2026 (11.23M), 2028 (15.63M), 2030 (18.17M)│
│ • Bottom-Up Daily Public Energy Demand Balance & Equation Box [Eq. 5B]      │
│ • Vehicle Parameters & Consumption Table (2W, 3W, 4W, Bus, Goods)           │
│ • Daily Throughput (AC 23.1, DC 180.0, Swap 26.25 kWh/day) & Hardware [Eq. 6]│
│ • Power Substitution Matrix [Eq. 7] (η_power = 1.00, 0.15, 0.00)            │
├─────────────────────────────────────────────────────────────────────────────┤
│ PAGE 4: Empirical Findings, Siting Optimization & Automated Validation      │
│ • National 36 States/UTs Findings: 10.69M EVs (3.84% penetration); UP, MH,  │
│   DL, KA lead; rural/semi-urban e-rickshaw vs urban 2W/4W divide            │
│ • Delhi Baseline: 876 Switch Delhi sites (573 charge + 303 swap, 2,437 pts) │
│ • Spatial vs Volumetric Gap: 68.3% circular coverage vs 14,200 kWh/day peak │
│ • Multi-Objective Grid-Constrained Siting Optimizer (Greedy submodular)     │
│   - Feeder Proximity Constraint (<1.5 km) & Electrical Tiers (Tier 1 to 3)  │
│   - Spatial Anti-Cannibalization Constraint (≥1.2 km dispersion)            │
│ • Top Candidate Siting Plazas Table (Burari, Bawana, Okhla, Anand Vihar)    │
│ • Automated QA & Verification Callout (28/28 assertions pass in Python,     │
│   0 TypeScript compiler errors, 7.68s Vite build, HTTP 200 OK smoke test)   │
├─────────────────────────────────────────────────────────────────────────────┤
│ PAGE 5: Data Strategy, Provenance & Methodological Caveats                  │
│ • 8-Source Data Provenance Table (BEE, MoPNG, MHI FAME-II, Switch Delhi,    │
│   OSM, VAHAN 4, DataMeet Boundaries, WorldPop Gridded Population)           │
│ • Boundary Statement on OSM Provenance (confined to Delhi; national 100%   │
│   official MoRTH/MoSPI/NITI data)                                           │
│ • Methodological Boundaries & Disclosures:                                  │
│   - 12-Month Temporal Asynchrony (BEE Oct 2025 vs VAHAN Oct 2026)           │
│   - Substation Physical Proximity ≠ Electrical Hosting Capacity             │
│   - Active Non-Compliant Registrations (26.4% lacking fitness/PUC)          │
│   - Absence of Real-Time Utilization Session Telemetry                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ PAGE 6: Phased Implementation Roadmap, References & Rubric Alignment        │
│ • Phased Implementation Roadmap Table:                                      │
│   - Phase 0: Baseline Freeze & AI Integration (Completed - Round 1)         │
│   - Phase 1: Highway Corridor Scaling (Weeks 1–2, NH-48 / Yamuna Expwy)     │
│   - Phase 2: Distribution Grid Capacity Proxies (Weeks 3–4, CEA tiers)      │
│   - Phase 3: Final Deployment & Grand Finale Defense (Weeks 5–6, Docker)    │
│ • Official Techfest Evaluation Criteria Alignment Matrix:                   │
│   - Problem Understanding & Relevance (25%)                                 │
│   - Technical Approach & Feasibility (25%)                                  │
│   - Innovation & Differentiation (20%)                                      │
│   - Implementation Roadmap & Feasibility (20%)                              │
│   - Data Strategy & Provenance (10%)                                        │
│ • Key Regulatory & Scientific References ([1] to [9] complete citations)    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Retained Mark-Bearing Technical Evidence Checklist

Every critical metric, formula, and finding required by the Techfest evaluation rubric was systematically tracked and preserved:

### A. Problem Understanding & Relevance (25%)
- [x] **Registry Non-Additivity Rule:** Explicitly stated and detailed. BEE (39,641 rows; 44,066 connectors across 29,371 sites), MoPNG OMC (27,737 installed; 22,753 operational), MHI FAME-II (8,932 OMC units), Switch Delhi (876 sites), and OSM (725 national features; 179 in Delhi) are strictly maintained as independent selectable baselines.
- [x] **Burari Commercial Fleet Concentration:** Documented registration skew where commercial fleets register at DL-11/12/13/14, obscuring localized municipal demand.
- [x] **Geographic Proximity vs. Volumetric Adequacy Disconnect:** Distinguishes circular geometric catchment ($d \le r$) from volumetric throughput ($\text{kWh/day}$), resolving queue collapse scenarios.
- [x] **Dual Geographic Scope:** Complete coverage of NCT Delhi (375 planning cells, 9 Census districts, 23 RTOs) and National scope across 36 States/UTs.

### B. Technical Approach & Feasibility (25%)
- [x] **Equation 1 (Burari Fleet Redistribution Crosswalk):**  
  $$w_{\text{district}} = 0.5 \times \left(\frac{N_{\text{poi, district}}}{N_{\text{poi, total}}}\right) + 0.5 \times \left(\frac{P_{\text{district}}}{P_{\text{total}}}\right)$$
- [x] **Delhi 375-Cell Spatial Grid:** $0.018^\circ\text{ Lat} \times 0.0205^\circ\text{ Lon}$ ($\approx 2.0\text{ km} \times 2.0\text{ km}$) over bounding box $28.40^\circ\text{–}28.89^\circ\text{N}, 76.83^\circ\text{–}77.35^\circ\text{E}$.
- [x] **WorldPop Scaling:** 2020 raster scaled to official National Commission on Population (NCP) 2025 projection of $22,300,000$.
- [x] **Equation 2 (Supervised Random Forest Spatial Demand ML):**  
  $$D_{\text{AI}} = f_{\text{RF}}\Big(\text{Pop}, \text{POI}_{\text{comm}}, \text{Transit}, \text{Roads}, \text{Dist}_{\text{substation}}, \text{DT}_{\text{count}}\Big) \in [0, 100]$$
- [x] **Random Forest Validation Metrics & Transparent Disclosure:**  
  120 estimators, depth 6, $R^2 = 0.796$, **5-Fold Cross-Validation $R^2 = 0.333 \pm 0.096$**, $\text{MAE} = 5.85$. Honest disclosure of spatial autocorrelation and municipal siting bias.
- [x] **Empirical Feature Importances:** Pop Density (49.65%), Commercial Activity POIs (13.14%), Commercial Attractor Hubs (9.53%), Substation Feeder Distance (9.14%), Major Roads (8.32%), Public Transit Interchanges (6.69%), DT Count (3.55%).
- [x] **Equation 3 (Continuous 4th-Order Sigmoid Distance-Decay Kernel):**  
  $$S = D_{\text{AI}} \times \left[ 1 - \frac{1}{1 + \left(\frac{d}{r}\right)^4} \right]$$
  Eliminates artificial step-function cliffs ($S \to 0$ when $d \ll r$, $S = 0.50 D_{\text{AI}}$ at $d = r$, $S \to D_{\text{AI}}$ when $d \gg r$).
- [x] **Equation 5A (Bass Diffusion Adoption Forecasting):**  
  $$S(t) = \frac{d N(t)}{dt} = \left[ p + \frac{q}{M} N(t) \right] [M - N(t)]$$  
  Calibrated on 68 months VAHAN data: $R^2 = 0.992$, $p = 0.0114$, $q = 0.4963$, $M = 20.0\text{M}$ national ceiling.
- [x] **S-Curve Projections ($P_{10}/P_{90}$ Bands):**  
  - 2026: 11.23M National ($P_{10}: 8.16\text{M}, P_{90}: 14.54\text{M}$); Delhi: 577,295.  
  - 2028: 15.63M National ($P_{10}: 12.23\text{M}, P_{90}: 18.71\text{M}$); Delhi: 803,300.  
  - 2030: 18.17M National ($P_{10}: 15.27\text{M}, P_{90}: 20.58\text{M}$); Delhi: 933,751.
- [x] **Equation 5B (Daily Public Energy Demand Balance):**  
  $$E_k = V_{k,2030} \times e_k \times \phi_{k,s} \quad (\text{kWh/day})$$
- [x] **Vehicle Consumption & Public Reliance Parameters:**  
  Full table with 2W ($1.024\text{ kWh/day}$, 20% public), 3W ($6.375\text{ kWh/day}$, 55% public), 4W ($6.960\text{ kWh/day}$, 32% public), Bus ($207.00\text{ kWh/day}$, 20% public), Goods ($13.50\text{ kWh/day}$, 50% public).
- [x] **Daily Throughput Ratings:**  
  AC Connector = $23.1\text{ kWh/day}$ ($4.2\text{ kW} \times 5.5\text{ h}$); DC Fast Nozzle = $180.0\text{ kWh/day}$ ($30.0\text{ kW} \times 6.0\text{ h}$); Battery Swap Docket = $26.25\text{ kWh/day}$ ($12.5\text{ swaps} \times 2.1\text{ kWh}$).
- [x] **Equation 6 (Hardware Sizing):**  
  $$\text{EVSE Points} = \text{AC} + \left\lceil\frac{\text{DC}}{1.35}\right\rceil, \quad \text{Stations} = \left\lceil\frac{\text{Points}}{4.5}\right\rceil$$
- [x] **Equation 7 & Power Substitution Matrix:**  
  $$\text{Net Hardware} = \max\left(0, \text{Required} - \sum \text{Installed} \times \eta_{\text{power}}\right)$$  
  $\eta_{\text{power}} = 1.00$ (matching/exceeding tier), $0.15$ (slow AC against slow AC targets), $0.00$ (slow AC against DC fast targets).

### C. Innovation & Differentiation (20%)
- [x] **Physics-Informed Explainable AI (PIML):** Substituted uninterpretable black-box neural networks with an auditable Random Forest regressor, Bass diffusion S-curve, and submodular greedy optimization suitable for public tenders.
- [x] **Multi-Objective Grid-Constrained Siting Optimizer:**  
  - Objective: $\max \sum_{i \in \text{selected}} S_i$.  
  - Feeder distance constraint: $<1,500\text{ m}$; electrical stratification: Tier 1 ($<1.0\text{ km}, \ge 500\text{ kVA}$), Tier 2 ($1.0\text{–}2.5\text{ km}, 150\text{–}250\text{ kVA}$), Tier 3 ($>2.5\text{ km}$).  
  - Anti-cannibalization constraint: $\ge 1.2\text{ km}$ minimum spatial dispersion between selected candidate plazas.  
  - Redundancy guarantee: $\min(2\text{ AC} / 1\text{ DC})$ per infill hub (Eq. 4B).
- [x] **Candidate Plazas Table:** Top 5 priority sites listed with coordinates, unserved scores, substation distances, and feeder readiness tiers.
- [x] **Dual Fuel Tag Discovery:** Identified that querying only `ELECTRIC(BOV)` misses 4.34M vehicles cataloged under `PURE EV`.

### D. Implementation Roadmap & Feasibility (20%)
- [x] **Phase 0 (Complete - Operational Prototype):** Data pipeline, 28/28 assertions, trained ML models, zero-watermark UI, open-source GitHub repo.
- [x] **Phase 1 (Highway Corridor Scaling, Weeks 1–2):** 5km buffer along NH-48 (Delhi–Jaipur) and Yamuna Expressway using PM Gati Shakti & NHAI freight vectors.
- [x] **Phase 2 (Distribution Grid Capacity Proxies, Weeks 3–4):** Secondary CEA standards & DISCOM voltage levels (11kV, 33kV, 66kV) for feeder hosting headroom.
- [x] **Phase 3 (Final Deployment & Grand Finale, Weeks 5–6):** Docker containerization, cloud hosting, offline caching fallback for jury defense.

### E. Data Strategy & Provenance (10%)
- [x] **Data Provenance Table:** 8 primary datasets (SRC-01 to SRC-08) with source agency, vintage, granularity, scope, and mitigations.
- [x] **Frozen Ingestion Date:** All raw data frozen as of 19 October 2026 under `data/raw/`.
- [x] **Boundary Statement on OSM:** Confined strictly to the Delhi spatial pilot ($3,534\text{ POIs}$); national state rankings derive 100% from official MoRTH VAHAN, MoSPI GSDP, and NITI Aayog benchmarks.
- [x] **4 Explicit Critical Caveats:**  
  1. 12-Month Temporal Asynchrony (BEE Oct 2025 vs VAHAN Oct 2026).  
  2. Substation Physical Proximity $\neq$ Electrical Hosting Capacity.  
  3. Active Non-Compliant Registrations (26.4% lacking fitness/PUC).  
  4. Absence of Real-Time Connector Session Telemetry.

---

## 4. Quality Assurance, Build & Validation Verification

| Verification Check | Target Standard | Observed Result | Status |
|---|---|---|:---:|
| **Automated Data & AI Tests** | 28/28 assertions in `validate_processed_data.py` | 28 / 28 assertions passed (100% success) | **PASSED** |
| **Strict TypeScript Typecheck** | Zero compiler errors (`tsc --noEmit`) | 0 errors across all UI & engine files | **PASSED** |
| **Production Build** | Clean Vite production bundle | Built successfully in 7.68 seconds (`dist/`) | **PASSED** |
| **Word COM Layout Rendering** | Strictly 5–6 pages (Microsoft Word A4) | **Exactly 6.0 pages in Microsoft Word 15.0** | **PASSED** |
| **Direct PDF Export** | Identical page-for-page visual flow | **Exactly 6.0 pages in PDF** (0 orphaned headers) | **PASSED** |
| **OpenXML Schema Compliance** | Valid ECMA-376 `tcPr` / `tblPr` element sequence | Sorted XML sequences; 0 Word opening warnings | **PASSED** |

---

## 5. Artifact Paths & Git Repository Reference

- **Condensed Microsoft Word Document:**  
  `C:\Users\hp\.gemini\antigravity\scratch\ev-infra-map-india\GridSight_EV_Methodology_Condensed.docx`
- **Condensed PDF Document:**  
  `C:\Users\hp\.gemini\antigravity\scratch\ev-infra-map-india\GridSight_EV_Methodology_Condensed.pdf`
- **Methodology Audit Report:**  
  `C:\Users\hp\.gemini\antigravity\scratch\ev-infra-map-india\Compression_Audit.md`
- **Open-Source GitHub Repository:**  
  [https://github.com/aadityaexpress/gridsight-ev](https://github.com/aadityaexpress/gridsight-ev)
