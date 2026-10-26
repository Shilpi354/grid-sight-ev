# 📊 GridSight EV — 7-Slide Pitch Deck (PPT Content)
**Event:** Techfest IIT Bombay 2026–27 | EV Infra & Green Mobility AI Challenge  
**Track:** Challenge 1 — EV Infra Map India (MHI & ICAT)  
**Team:** Mechies, Netaji Subhas University of Technology (NSUT), Delhi  
**Live Web Application:** `https://github.com/aadityaexpress/gridsight-ev`  

---

## Slide 1: Title & Executive Overview

### Slide Header
**GridSight EV: Physics-Grounded Geospatial Intelligence & AI Siting Platform**  
*Unified EV Charging Infrastructure Mapping, Demand Forecasting & Grid-Constrained Siting for India*

### Visual Layout
- **Left Column (60%):** Bold title, Team details (Team Mechies, NSUT), competition branding (Techfest IIT Bombay 2026–27, MHI, ICAT). Hero screenshot of the live web application showing the dual-view Delhi 2km planning grid alongside the National 36-State choropleth map.
- **Right Column (40%):** 3 High-Impact Executive Metric Badges:
  - 🟢 **100% Verified Real Data:** 10.68M VAHAN Active EVs • 44,066 BEE Connectors • 27,737 OMC Fuel Station EV Chargers.
  - 🧠 **Physics + AI Integration:** Spatial Random Forest Regressor ($R^2=0.796$) + Calibrated Bass Adoption S-Curve ($R^2=0.992$).
  - ⚡ **Production-Ready Prototype:** Fully implemented in React/TypeScript/Leaflet, 28/28 automated schema assertions passed, open-source on GitHub.

### Core Slide Content
- **The Core Mission:** Transitioning India from arbitrary, universal charger-to-EV ratios to a **demand-elastic, grid-constrained, category-disaggregated infrastructure planning system**.
- **Scope of Demonstration:** Tested and calibrated across the **375-cell spatial grid of NCT of Delhi**, architected for seamless scaling across **all 36 States and Union Territories**.

### 🎤 Speaker Notes (25 Seconds)
> "Good morning, respected jury members. We are Team Mechies from NSUT, presenting **GridSight EV** for Challenge 1: EV Infra Map India.
> India has crossed 10 million registered electric vehicles. Yet, charging infrastructure today is planned in institutional silos using arbitrary universal ratios that ignore where vehicles actually drive and where grid capacity exists. 
> GridSight EV solves this by fusing multi-source government registries with physics-grounded energy balance models and spatial machine learning, providing an end-to-end decision support platform for MHI, ICAT, and municipal planners."

---

## Slide 2: Problem Statement & Critical Industry Data Gaps

### Slide Header
**The EV Infrastructure Blind Spot: Why Planning in Silos Fails**  
*Current infrastructure deployment suffers from registry fragmentation, RTO registration skew, and arbitrary sizing formulas.*

### Visual Layout
- **3-Column Comparative Problem Cards:**
  - **Card 1: Registry Fragmentation & Double Counting**
  - **Card 2: RTO Registration Distortion (The Burari Anomaly)**
  - **Card 3: The Universal Ratio Fallacy ("1 Charger per 10 EVs")**

### Core Slide Content
- **1. Disconnected Registries:** 
  - Switch Delhi (876 stations), BEE (1,909 stations), and OMC Retail Pumps (27,737 stations) exist in separate portals with differing definitions of "Station", "EVSE Point", and "Connector Nozzle", creating massive duplicate counting risks.
- **2. The Commercial Fleet Distortion (Burari Skew):**
  - In Delhi, **over 35% of all commercial EVs (200k+ autos, e-rickshaws, and cabs) are registered at the single Burari Transport Authority (DL-1Y/1Z)**. Raw registration data falsely implies North Delhi has infinite charging demand, starving the rest of the city.
- **3. The Flaw of Universal Ratios:**
  - Prescribing "1 charger per 10 EVs" is mathematically broken in India. A commercial 3W consumes $6.4\text{ kWh/day}$ with 60% public reliance; an electric 2W consumes $1.0\text{ kWh/day}$ with 80% home charging. Universal ratios lead to stranded capital and severe grid overload.

### Jury Takeaway Callout
> ⚠️ **Key Problem:** Planners don't lack raw data—they lack unified spatial reconciliation, commercial fleet normalization, and physics-based energy disaggregation.

### 🎤 Speaker Notes (30 Seconds)
> "When evaluating India’s charging landscape, three major systemic gaps immediately emerge.
> First, infrastructure data is fragmented: GNCTD Switch Delhi, the BEE registry, and OMC oil company chargers all use different units and reporting standards, making nationwide visibility impossible without strict deduplication.
> Second, RTO registration skew: in Delhi, over 35% of commercial EVs are registered at a single RTO in Burari. Raw data would have you build all chargers in one neighborhood.
> And third, the industry standard of using universal charger-to-EV ratios completely fails because 2-wheelers, 3-wheelers, and commercial buses have wildly different daily kilowatt-hour demands and public charging reliance."

---

## Slide 3: Unified Data Architecture & Provenance Pipeline

### Slide Header
**Data Integration Architecture: 0% Synthetic Data, 100% Provenance**  
*Strict source separation, automated deduplication, and multi-layer GIS spatial enrichment.*

### Visual Layout
- **Process Flow Diagram (Left-to-Right):**
  - `[Raw Government Ingestion]` &rarr; `[Algorithmic Cleaning & Deduplication]` &rarr; `[Spatial Enrichment (WorldPop + OSM)]` &rarr; `[Validated Analytics Layer]`.
- **Bottom Summary Table:** 8 Verified Datasets with exact row counts, provenance, and validation status.

### Core Slide Content
- **Multi-Source Layer Integration:**
  - **MoRTH VAHAN (19 Oct 2026):** 10,689,490 national active EVs across 36 states; 549,153 Delhi EVs mapped to 23 zonal RTOs.
  - **BEE EVPCS Registry (26 Oct 2025):** 39,641 national charger rows reconciled into 44,066 connectors (1,909 stations in Delhi).
  - **GNCTD Switch Delhi (19 Oct 2026):** 876 verified stations (573 charging sites, 303 swap hubs; 121 PIN-estimated kiosks flagged).
  - **PIB MoPNG / MHI Official Releases (Mar 2026):** 27,737 OMC retail fuel station EV chargers (22,753 operational, 8,932 under FAME-II).
  - **Spatial Enrichment:** WorldPop 1km disaggregated population grids, OpenStreetMap road networks, and 3,534 verified POI attractors.
- **Automated Validation Invariant Engine:**
  - Verified via `scripts/validate_processed_data.py`: **28 out of 28 automated schema assertions pass at 100%** with zero `NaN` or unhandled nulls.

### Jury Takeaway Callout
> 🛡️ **Integrity Guarantee:** Zero synthetic chargers or fabricated coordinates. Public data gaps are explicitly badged rather than artificially filled.

### 🎤 Speaker Notes (25 Seconds)
> "Our data pipeline is built on uncompromising provenance. We ingested 8 official government datasets totaling over 10.6 million active VAHAN vehicles and 44,000 BEE connectors.
> We integrated official Ministry of Petroleum data tracking 27,737 Oil Marketing Company fuel station chargers—giving the first comprehensive view of highway corridor readiness.
> We enrich every geographic unit with WorldPop population estimates and 3,534 verified OpenStreetMap points of interest.
> Most importantly: zero synthetic data. Our automated test suite enforces 28 rigorous schema invariants, all passing at 100%."

---

## Slide 4: Delhi Pilot & Spatial Gap Prioritization

### Slide Header
**Spatial Discretization: 375-Cell Grid & Continuous Sigmoid Decay**  
*Moving beyond administrative boundaries to uniform 2.0 km × 2.0 km spatial catchment evaluation.*

### Visual Layout
- **Split Screen Layout:**
  - **Left (50%):** Screenshot of the Delhi 375-cell interactive grid map showing green (covered), red/amber (underserved priority), and dark grey (low-demand fringe) cells.
  - **Right (50%):** Algorithmic Formula Cards:
    - **Burari Redistribution Formula**
    - **Continuous Sigmoid Distance Decay Equation**

### Core Slide Content
- **1. The 375-Cell Spatial Discretization:**
  - Delhi's $1,483\text{ km}^2$ land area is partitioned into 375 uniform $2.0\text{ km} \times 2.0\text{ km}$ cells, evaluating physical centroids against four independent charging networks.
- **2. The Burari Fleet Normalization Model:**
  - Commercial vehicle registrations are redistributed across the 9 administrative districts via a 5-metric composite weight ($40\%\text{ Pop} + 30\%\text{ Roads} + 30\%\text{ POIs}$), eliminating the North Delhi data artifact.
- **3. Continuous Sigmoid Distance Decay Kernel:**
  - Traditional models use sharp buffer cutoffs that produce false boundary cliffs. GridSight introduces continuous sigmoid decay:
    $$\text{Priority Score } S = \text{Demand } D \times \left[1 - \frac{1}{1 + (d/r)^4}\right]$$
  - Smoothly penalizes deficit as distance $d$ exceeds radius $r$, eliminating edge artifacts.

### Jury Takeaway Callout
> 🎯 **Planning Impact:** Planners can stress-test Delhi's $3.0\text{ km}$ policy target versus $1.0\text{ km}$ rapid access in real time, identifying exactly which zones suffer genuine demand deficits.

### 🎤 Speaker Notes (25 Seconds)
> "In our Delhi Pilot, we divide the capital into 375 uniform two-kilometer grid cells.
> To fix the Burari commercial distortion, our algorithm re-apportions commercial fleets across the 9 districts based on real population and road infrastructure.
> Furthermore, instead of relying on unrealistic circular buffer cutoffs where a charger 10 meters outside a boundary suddenly counts as zero, we formulated a Continuous Sigmoid Distance Decay kernel.
> Planners can toggle catchment radii from 0.5 to 5.0 kilometers and instantly isolate the priority underserved zones where high commercial demand intersects severe supply deficits."

---

## Slide 5: Machine Learning & Predictive S-Curve Adoption

### Slide Header
**Explainable Spatial ML & Non-Linear Fleet Diffusion**  
*Supervised Random Forest Regressor ($R^2=0.796$) + Calibrated Bass Adoption S-Curve ($R^2=0.992$).*

### Visual Layout
- **Left (50%): Spatial Demand ML Feature Importance Chart:**
  - Horizontal bar chart showing empirical weights derived from 120 estimators:
    - Population Density (WorldPop): **49.65%**
    - Commercial & Activity POIs: **22.67%**
    - Substation Feeder Distance: **9.14%**
    - Major Road Density: **8.32%**
    - Transit Interchanges: **6.69%**
    - Substation / DT Count: **3.55%**
- **Right (50%): Bass Diffusion Adoption S-Curve (2018–2030):**
  - Graph showing historical curve inflection and future projection with $P_{10}/P_{90}$ stochastic bands, projecting **~933,751 active Delhi EVs by 2030**.

### Core Slide Content
- **1. Supervised Random Forest Regressor:**
  - Replaces arbitrary heuristic weights with empirical elasticities learned from ground-truth charging presence across the 375 grid cells ($R^2 = 0.796, \text{MAE} = 5.85$).
  - Proves that demographic density and commercial trip attractors govern over 72% of charging demand elasticity.
- **2. Bass Diffusion Technology Diffusion Model:**
  - Fits the non-linear differential adoption equation:
    $$F(t) = M \times \frac{1 - e^{-(p+q)t}}{1 + \frac{q}{p}e^{-(p+q)t}}$$
  - Parameters calibrated to VAHAN registrations: Innovation $p=0.0114$, Imitation $q=0.4963$, Market Ceiling $M=20.0\text{M}$ EVs. Captures market tipping points that static linear CAGR completely ignores.

### Jury Takeaway Callout
> 💡 **White-Box Explainability:** Every feature weight and adoption parameter is auditable, eliminating black-box uncertainty.

### 🎤 Speaker Notes (30 Seconds)
> "GridSight introduces two critical predictive intelligence components.
> First, our Supervised Spatial Random Forest Regressor. By training 120 decision trees against verified charging density, the model proves empirically that population density and commercial activity hubs drive over 72% of demand elasticity, while feeder proximity contributes 9%.
> Second, for fleet growth, linear forecasts fail to model technology adoption. We calibrated the Bass Diffusion S-Curve model on VAHAN registration time series with an R-squared of 0.992, capturing the market tipping point and projecting approximately 933,000 active Delhi EVs by 2030 with stochastic P10 and P90 confidence intervals."

---

## Slide 6: Multi-Objective Siting & Bottom-Up Capacity Simulator

### Slide Header
**Constrained Siting Optimizer & Bottom-Up 2030 Sizing Engine**  
*Submodular greedy candidate siting bounded by 11kV/33kV grid feeder proximity ($<1.5\text{ km}$) and anti-cannibalization spacing ($\ge 1.2\text{ km}$).*

### Visual Layout
- **Left (50%): 25 AI-Optimized Candidate Hubs Map & Table:**
  - Map overlay of 25 optimal charging plazas categorized by Electrical Feeder Tiers:
    - **Tier 1:** Substation $<1\text{ km}$ ($\ge 500\text{ kVA}$ spare feeder capacity, $250\text{ kW}$ max hosting)
    - **Tier 2:** Substation $1.0–2.5\text{ km}$ ($150–250\text{ kVA}$ capacity, $120\text{ kW}$ max hosting)
    - **Tier 3:** Substation $>2.5\text{ km}$ (Requires dedicated DT upgrade)
- **Right (50%): Bottom-Up 2030 Capacity Sizing Matrix:**
  - Breakdown table separating **Stations**, **EVSE Charging Points**, **AC Nozzles**, **DC Fast Guns**, and **Swap Dockets**.

### Core Slide Content
- **1. Grid-Constrained Siting Optimization:**
  - Formulated as submodular greedy optimization maximizing unserved demand deficit while enforcing electrical grid capacity ($<1.5\text{ km}$ to nearest DISCOM substation) and spatial anti-cannibalization spacing ($\ge 1.2\text{ km}$).
- **2. Bottom-Up Energy Balance Simulator (No Arbitrary Ratios):**
  - Sizing is driven strictly by daily vehicle energy consumption:
    - 2W: $1.02\text{ kWh/day}$ | 3W: $6.38\text{ kWh/day}$ | 4W: $6.96\text{ kWh/day}$ | Bus: $207.0\text{ kWh/day}$
  - Divides segmented public kWh demand by connector daily throughput:
    - **AC Nozzle:** $4.2\text{ kW} \times 5.5\text{h} = 23.1\text{ kWh/day}$
    - **DC Fast Gun:** $30.0\text{ kW} \times 6.0\text{h} = 180.0\text{ kWh/day}$
    - **Battery Swap:** $13\text{ swaps/day} \times 2.1\text{ kWh} = 27.3\text{ kWh/day}$

### Jury Takeaway Callout
> ⚙️ **Engineering Rigor:** Sizing hardware by actual kilowatt-hours dispensed ensures DISCOM transformers are never overloaded and capital expenditure is accurately budgeted.

### 🎤 Speaker Notes (30 Seconds)
> "When recommending where to build, an algorithm that ignores the power grid is useless.
> Our Siting Optimizer selects the top 25 optimal charging plazas across Delhi using submodular greedy optimization, strictly bounded by substation feeder proximity under 1.5 kilometers and minimum spacing of 1.2 kilometers to prevent cannibalization.
> Furthermore, in our 2030 Capacity Simulator, we abandon universal ratios entirely. We compute bottom-up daily kilowatt-hour demand for every vehicle category, public reliance percentages, and connector throughput.
> Planners see explicit requirements for physical Stations, EVSE Points, AC vs DC fast nozzles, Battery Swap dockets, and the exact added grid load in megawatts."

---

## Slide 7: Nationwide Scalability Roadmap, Live Demo & Impact

### Slide Header
**National Scalability Roadmap: From Delhi Pilot to Bharat EV Grid**  
*A complete, decision-ready GIS web platform supporting MHI, ICAT, and State Urban Development bodies.*

### Visual Layout
- **Top Row (40%): Live Implementation Proof (Screenshots):**
  - 🌙 One-click High-Contrast Dark Mode toggle for 24/7 utility control rooms.
  - Interactive District/State matrices, CSV data export, and zero-watermark responsive mapping.
- **Bottom Row (60%): 4-Phase National Scaling Roadmap:**
  - **Phase 0 (Complete):** Delhi pilot, 36-state national registry, spatial ML regressor, open GitHub repo.
  - **Phase 1 (Q1-Q2 2027):** Tier-1 Metros (Mumbai, Bengaluru, Chennai, Hyderabad) + Golden Quadrilateral highway corridors.
  - **Phase 2 (Q3-Q4 2027):** Automated DISCOM GIS feeder integration + dynamic tariff & utilization ingestion.
  - **Phase 3 (2028):** Real-time telematics API integration with PM E-DRIVE & national CPO networks.

### Core Slide Content
- **Challenge Alignment & Deliverables Complete:**
  - ✅ **Working Web Platform:** Deployed, interactive, responsive client-side SPA.
  - ✅ **Unified GIS Mapping:** Multi-network deduplicated coverage with spatial filtering.
  - ✅ **Explainable Methodology:** Full provenance documentation & automated validation suite.
  - ✅ **Actionable Siting Module:** 25 ranked candidate plazas with electrical feasibility tiers.
- **Target Institutional Users:**
  - **Ministry of Heavy Industries (MHI):** Capital subsidy allocation under PM E-DRIVE.
  - **ICAT & State Transport Departments:** Fleet electrification targets & RTO zoning.
  - **DISCOMs & Utilities:** Feeder hosting capacity planning and transformer upgrade budgeting.

### Jury Takeaway Callout
> 🚀 **Verdict:** GridSight EV turns fragmented spreadsheets into actionable, physics-grounded infrastructure decisions. Ready for Delhi today; architected for India tomorrow.

### 🎤 Speaker Notes (25 Seconds)
> "To conclude, GridSight EV satisfies every Round 1 and Round 2 deliverable for Challenge 1.
> The prototype is fully built, production-compiled, and open-source on GitHub—featuring a one-click high-contrast Dark Mode designed for utility control rooms.
> Our modular data architecture allows any municipality or state transport department to drop in local RTO counts and substation locations to immediately generate coverage maps, identify unserved gaps, and size 2030 charging hardware.
> GridSight EV transforms fragmented data into defensible, transparent, and actionable infrastructure planning. 
> Thank you, and we welcome your questions."

---

## 📋 Presentation Delivery Tips for Team Mechies

| Presentation Dimension | Best Practice Recommendation |
| :--- | :--- |
| **Total Speaking Time** | Exactly **3 minutes 15 seconds to 3 minutes 30 seconds** (leaves ample time for jury Q&A). |
| **Visual Hierarchy** | Keep slide backgrounds clean (white or deep navy), using **Teal (`#0f766e`)** for infrastructure, **Sky Blue (`#0284c7`)** for DC fast chargers, and **Amber (`#d97706`)** for Battery Swapping. |
| **Slide Numbers** | Always display "Slide X of 7" in the bottom right corner for jury reference during questions. |
| **Live Demo Transition** | If the jury asks for a live demo during Q&A, open `http://localhost:5173/` and immediately demonstrate: (1) The Burari fleet redistribution toggle, (2) The Spatial ML vs Heuristic button in Coverage Planning, and (3) The Dark Mode switch. |
