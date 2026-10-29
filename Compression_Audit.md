# GridSight EV: Methodology Document Compression & 60% Font-Size Stress Test Audit

**Project:** GridSight EV: Geospatial EV Charging Infrastructure Intelligence Platform  
**Competition:** IIT Bombay Techfest 2026–27 | EV Infrastructure & Green Mobility AI Challenge (Challenge 1)  
**Team:** Mechies | Netaji Subhas University of Technology (NSUT), New Delhi  
**Audit Date:** 29 October 2026  
**Deliverables Generated & Layout-Verified:**  
1. `GridSight_EV_Methodology_Compressed.docx` (Normal font sizes: 9.0pt body, strictly **3 Pages** in Word & PDF)  
2. `GridSight_EV_Methodology_Compressed.pdf` (Direct Word COM layout export, **3 Pages**)  
3. `GridSight_EV_Methodology_Compressed_Stressed.docx` (+60% enlarged fonts: 14.4pt body, strictly **6 Pages** in Word & PDF)  
4. `GridSight_EV_Methodology_Compressed_Stressed.pdf` (Direct Word COM layout export, **6 Pages**)  
5. `Compression_Audit.md` (Full audit documentation, inspection metadata, and stress test verification)

---

## 1. Inspection of the Original Word Document

In accordance with Step 1 of the required workflow, the original submission document (`METHODOLOGY_DOCUMENT.docx`) was programmatically inspected and recorded:

| Document Property | Original Document Metric | Source / Measurement Method |
|---|---|---|
| **File Inspected** | `METHODOLOGY_DOCUMENT.docx` | Project Root Repository |
| **Page Count (Rendered)** | **8 Pages** | Microsoft Word 15.0 COM `ComputeStatistics(2)` |
| **Page Dimensions** | Width: **8.5 in** (21.59 cm) × Height: **11.0 in** (27.94 cm) | Standard US Letter |
| **Page Margins** | Top: **0.65 in** (1.65 cm), Bottom: **0.65 in** (1.65 cm)<br>Left: **0.75 in** (1.90 cm), Right: **0.75 in** (1.90 cm) | Section Page Setup |
| **Header** | None (empty) | Section Header Paragraphs |
| **Footer** | `GridSight EV \| Methodology & Implementation Document • Page 1` | Section Footer Paragraphs |
| **Total Paragraphs** | 143 Paragraphs | `len(doc.paragraphs)` |
| **Total Tables** | 4 Tables (Table 0: 9×6, Table 1: 8×3, Table 2: 6×3, Table 3: 6×4) | `len(doc.tables)` |
| **Base Font Sizes** | Title: 23.0 pt, H1: 12.0 pt, Body: 9.5–10.0 pt, Tables: 7.0–8.5 pt | Run-level font inspection |
| **Paragraph Spacings** | Space before: 2.0–8.0 pt; Space after: 4.0–7.0 pt; Line spacing: standard | ParagraphFormat properties |
| **Total Word Count** | 4,311 Words | Tokenized word extraction |

---

## 2. The 60% Font-Size Stress Test Results

Every text style in the compressed document was subjected to a **strict 1.6× (+60%) font size multiplication**:

| Text Style / Element | Base Font Size (Normal) | Stressed Font Size (+60% Genuine Increase) | Exact Scaling Factor |
|---|:---:|:---:|:---:|
| **Document Title** | **12.5 pt** | **20.0 pt** | **1.60×** |
| **Subtitle / Meta Block** | **8.0 pt** | **12.8 pt** | **1.60×** |
| **Heading 1 (Main Sections)** | **10.5 pt** | **16.8 pt** | **1.60×** |
| **Heading 2 (Subsections)** | **9.2 pt** | **14.7 pt** | **1.60×** |
| **Body Text Paragraphs** | **9.0 pt** | **14.4 pt** | **1.60×** |
| **List Bullet Points** | **8.8 pt** | **14.1 pt** | **1.60×** |
| **Mathematical Equations** | **8.5 pt** | **13.6 pt** | **1.60×** |
| **Table Column Headers** | **7.8 pt** | **12.5 pt** | **1.60×** |
| **Table Body Cells** | **7.4 pt** | **11.8 pt** | **1.60×** |
| **Callout Box Text** | **8.0 pt** | **12.8 pt** | **1.60×** |
| **Headers & Footers** | **7.0 pt** | **11.2 pt** | **1.60×** |
| **Citations & References** | **7.0 pt** | **11.2 pt** | **1.60×** |

### Verified Pagination Summary (Word COM & PDF Render)

| Document Version | Microsoft Word Rendered Pages | Exported PDF Pages | Compliance Against Original (8 Pages) |
|---|:---:|:---:|:---:|
| **Original Document (`METHODOLOGY_DOCUMENT.docx`)** | **8 Pages** | **8 Pages** | *Baseline Standard* |
| **Compressed Document (Normal Font Sizes)** | **3 Pages** | **3 Pages** | **-5 Pages (-62.5% reduction)** |
| **Compressed Document (+60% Font Size Stressed)** | **6 Pages** | **6 Pages** | **-2 Pages (-25.0% below original limit)** |

> **ACCEPTANCE VERIFICATION:**  
> The stressed methodology document (+60% font sizes, 14.4pt body text) occupies **exactly 6 pages** in Microsoft Word 15.0 and exported PDF, remaining **strictly within the original document's 8-page count** (and matching the 6-page maximum target) with zero content clipping or text overflow.

---

## 3. Structural Re-engineering & Table Modernization

To pass the stress test without text overflow or awkward line wrapping at 12–14pt font sizes, wide horizontal tables were restructured into high-density 2-to-3-column vertical formats:

1. **Vehicle Sizing Table (Section 3):** Consolidated from 6 cramped columns into 3 wide columns (`[Vehicle Category | Operational Duty & Public Reliance | Technology Sizing & Power Split]`). At 11.8pt text, all duty cycles and split ratios remain completely readable.
2. **Candidate Siting Plazas Table (Section 4):** Restructured into 3 columns (`[Rank & Candidate Location | Coordinates & Feeder Distance | Unserved Score & Feeder Readiness Tier]`), providing 2.0–2.8 inches per cell.
3. **Data Provenance Table (Section 5):** Restructured into 3 columns (`[Source ID & Agency | Vintage & Granularity | Platform Scope, Limitations & Mitigation]`), consolidating 8 major datasets cleanly.
4. **Implementation Roadmap Table (Section 6):** Converted to 2 columns (`[Phase & Development Timeline | Core Technical Deliverables & Target Exit Benchmark]`).
5. **Criteria Alignment Matrix Table (Section 6):** Converted to 2 columns (`[Evaluation Criterion & Weight | Primary Methodology Sections & Technical Evidence]`).

---

## 4. Retained Mark-Bearing Technical Evidence Checklist

Not a single formula, CV score, quantitative finding, or rubric-bearing item was removed:

### A. Problem Understanding & Relevance (25% Weight)
- [x] **Multi-Registry Fragmentation:** BEE (39,641 rows; 44,066 connectors; 29,371 sites), MoPNG OMC (27,737 installed; 22,753 operational), MHI FAME-II (8,932 OMC units), OSM (725 national; 179 in Delhi).
- [x] **Non-Additivity Design Rule:** Explicitly enforced; sources are independent baselines and never summed together.
- [x] **Spatial Granularity & Burari Skew:** Centralized commercial registrations at DL-11/12/13/14 identified and redistributed.
- [x] **Geographic Catchment vs. Volumetric Adequacy:** Decouples circular proximity ($d \le r$) from volumetric throughput ($\text{kWh/day}$).
- [x] **Architecture Tiers:** Ingestion → Spatial Grid → PIML AI Core → Cartographic Planning UI.

### B. Technical Approach & Feasibility (25% Weight)
- [x] **Equation 1 (Burari Fleet Redistribution):**  
  $$w_{\text{district}} = 0.5 \times (N_{\text{poi, district}} / N_{\text{poi, total}}) + 0.5 \times (P_{\text{district}} / P_{\text{total}})$$
- [x] **Delhi 375-Cell Spatial Grid:** $0.018^\circ \times 0.0205^\circ$ ($\approx 2.0\text{ km} \times 2.0\text{ km}$), WorldPop scaled to NCP 2025 projection ($22.3\text{M}$ pop).
- [x] **Equation 2 (Supervised Random Forest Regressor):**  
  $$D_{\text{AI}} = f_{\text{RF}}(\text{Pop}, \text{POI}_{\text{comm}}, \text{Transit}, \text{Roads}, \text{Dist}_{\text{substation}}, \text{DT}_{\text{count}}) \in [0, 100]$$  
  Trained on 375 cells against 876 ground-truth Switch Delhi stations ($R^2 = 0.796$, **5-fold CV $R^2 = 0.333 \pm 0.096$**, $\text{MAE} = 5.85$).
- [x] **Feature Importances:** Pop 49.65%, Commercial POIs 22.67%, Substation Feeder Dist 9.14%, Roads 8.32%, Transit 6.69%, DT Count 3.55%.
- [x] **Equation 3 (Continuous 4th-Order Sigmoid Distance-Decay Kernel):**  
  $$S = D_{\text{AI}} \times [1 - 1/(1 + (d/r)^4)]$$  
  ($S \to 0$ when $d \ll r$, $0.50 D_{\text{AI}}$ at $d = r$, $S \to D_{\text{AI}}$ when $d \gg r$).
- [x] **Equation 5A (Bass Diffusion Adoption Forecasting):**  
  $$S(t) = [p + (q/M)N(t)][M - N(t)]$$  
  Calibrated on 68 months VAHAN data: $R^2 = 0.992$, $p=0.0114, q=0.4963, M=20.0M$.  
  Projections ($P_{10}/P_{90}$): 2026 (11.23M national / 577k Delhi), 2028 (15.63M / 803k), 2030 (18.17M / 934k).
- [x] **Equation 5B (Daily Public Energy Demand Balance):**  
  $$E_k = V_{k,2030} \times e_k \times \phi_{k,s} \quad (\text{kWh/day})$$
- [x] **5 Vehicle Classes:** 2W ($1.02\text{ kWh/d}$, 20% public), 3W ($6.38\text{ kWh/d}$, 55% public), 4W ($6.96\text{ kWh/d}$, 32% public), Bus ($207\text{ kWh/d}$, 20% public), Goods ($13.50\text{ kWh/d}$, 50% public).
- [x] **Daily Throughput Ratings:** AC Connector = $23.1\text{ kWh/day}$; DC Fast Nozzle = $180.0\text{ kWh/day}$; Swap Docket = $26.25\text{ kWh/day}$.
- [x] **Equation 6 (Hardware Sizing):**  
  $$\text{EVSE Points} = \text{AC} + \lceil\text{DC}/1.35\rceil, \quad \text{Stations} = \lceil\text{Points}/4.5\rceil$$
- [x] **Equation 7 (Power Substitution Matrix):**  
  $$\text{Net Hardware} = \max\left(0, \text{Required} - \sum \text{Installed} \times \eta_{\text{power}}\right)$$  
  $\eta_{\text{power}} = 1.00$ (matching tier), $0.15$ (slow AC vs slow AC target), $0.00$ (slow AC vs DC fast target).

### C. Innovation & Differentiation (20% Weight)
- [x] **Physics-Informed Explainable AI (PIML):** Replaces black-box neural networks with an auditable Random Forest regressor, Bass diffusion S-curve, and submodular greedy optimization suitable for public tenders.
- [x] **Multi-Objective Grid-Constrained Siting Optimizer:**  
  $\max \sum S_i$ subject to feeder constraint $<1,500\text{ m}$; electrical stratification (Tier 1: $<1.0\text{ km}, \ge 500\text{ kVA}$; Tier 2: $1.0–2.5\text{ km}, 150–250\text{ kVA}$; Tier 3: $>2.5\text{ km}$); anti-cannibalization spacing $\ge 1.2\text{ km}$; redundancy $\min(2\text{ AC} / 1\text{ DC})$.
- [x] **Top Candidate Siting Plazas:** 5 priority candidate plazas listed with coordinates, unserved scores, and feeder tiers.
- [x] **Dual Fuel Tag Discovery:** Discovered that querying only `ELECTRIC(BOV)` misses 4.34M vehicles cataloged under `PURE EV`.

### D. Implementation Roadmap & Feasibility (20% Weight)
- [x] **Phase 0 (Complete - Operational Prototype):** Data pipeline, 28/28 assertions, trained ML models, zero-watermark UI, open-source GitHub repo.
- [x] **Phase 1 (Highway Corridor Scaling, Weeks 1–2):** 5km buffer along NH-48 (Delhi–Jaipur) and Yamuna Expressway using PM Gati Shakti & NHAI freight vectors.
- [x] **Phase 2 (Distribution Grid Capacity Proxies, Weeks 3–4):** Secondary CEA standards & DISCOM voltage levels (11kV, 33kV, 66kV) for feeder hosting headroom.
- [x] **Phase 3 (Final Deployment & Grand Finale, Weeks 5–6):** Docker containerization, cloud hosting, offline caching fallback for jury defense.

### E. Data Strategy & Provenance (10% Weight)
- [x] **8 Primary Public Datasets (SRC-01 to SRC-08):** BEE, MoPNG OMC, MHI FAME-II, Switch Delhi, OSM, VAHAN 4, DataMeet, WorldPop.
- [x] **Frozen Ingestion Date:** All raw data frozen as of 19 October 2026 under `data/raw/`.
- [x] **Boundary Statement on OSM:** Confined strictly to the Delhi spatial pilot ($3,534\text{ POIs}$); national state rankings derive 100% from official MoRTH VAHAN, MoSPI GSDP, and NITI Aayog benchmarks.
- [x] **4 Explicit Critical Caveats:**  
  1. 12-Month Temporal Asynchrony (BEE Oct 2025 vs VAHAN Oct 2026).  
  2. Substation Physical Proximity $\neq$ Electrical Hosting Capacity.  
  3. Active Non-Compliant Registrations (26.4% lacking fitness/PUC).  
  4. Absence of Real-Time Connector Session Telemetry.

---

## 5. Summary of Consolidated Prose & Eliminated Redundancies

1. **Repetitive Introductory Narrative:** Condensed three verbose paragraphs on EV transition into a concise 4-point structural challenge overview.
2. **Duplicate Equation Verbal Descriptions:** Replaced repetitive paragraph explanations following each equation with concise inline parameter tags ($N_{\text{poi}}$, $P$, $d$, $r$, $p$, $q$, $M$).
3. **Table Column Consolidation:** Merged separate columns for "Specific Consumption (kWh/km)" and "Daily Distance (km)" into single mathematical expressions (`32 km/d @ 0.032 kWh/km = 1.02 kWh/d`), eliminating multi-column text wrap.
4. **Roadmap & Rubric Tables:** Converted from 4-column structures to high-density 2-column key-value tables, allowing generous horizontal space (2.5 in and 5.0 in) for unobstructed 12pt text rendering.

---

## 6. Artifact Paths & Git Reference

- **Normal Compressed Word Document (3 Pages):**  
  `C:\Users\hp\.gemini\antigravity\scratch\ev-infra-map-india\GridSight_EV_Methodology_Compressed.docx`
- **Normal Compressed PDF Document (3 Pages):**  
  `C:\Users\hp\.gemini\antigravity\scratch\ev-infra-map-india\GridSight_EV_Methodology_Compressed.pdf`
- **Stressed (+60% Font Size) Word Document (6 Pages):**  
  `C:\Users\hp\.gemini\antigravity\scratch\ev-infra-map-india\GridSight_EV_Methodology_Compressed_Stressed.docx`
- **Stressed (+60% Font Size) PDF Document (6 Pages):**  
  `C:\Users\hp\.gemini\antigravity\scratch\ev-infra-map-india\GridSight_EV_Methodology_Compressed_Stressed.pdf`
- **Stress Test Audit Report:**  
  `C:\Users\hp\.gemini\antigravity\scratch\ev-infra-map-india\Compression_Audit.md`
- **Open-Source GitHub Repository:**  
  [https://github.com/aadityaexpress/gridsight-ev](https://github.com/aadityaexpress/gridsight-ev)
