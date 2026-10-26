# 🎬 GridSight EV — Official Video Demonstration Script (3 Minutes)

**Project:** GridSight EV — Geospatial Infrastructure Intelligence & AI Siting Platform  
**Team:** Mechies, NSUT | **Challenge:** Techfest IIT Bombay 2026–27 (Challenge 1: EV Infra Map India)  
**Target Duration:** 2 minutes 45 seconds – 3 minutes (~420 spoken words)  
**Style:** Confident, articulate, fast-paced, highly technical, and jury-focused  

---

## ⏱️ Master Video Timeline

```
[0:00 - 0:25]  Scene 1: The Hook — Why EV Infrastructure Planning Fails
[0:25 - 0:55]  Scene 2: Delhi Pilot — Multi-Source Deduplication & Burari Fleet Correction
[0:55 - 1:25]  Scene 3: National Overview — 36 States & 27.7K OMC Fuel Pump Chargers
[1:25 - 2:05]  Scene 4: Coverage Planning — Spatial ML Regressor, Sigmoid Decay & Bottom-Up Sizing
[2:05 - 2:35]  Scene 5: AI Studio & Optimization — Feature Importance, Bass S-Curve & Dark Mode
[2:35 - 2:55]  Scene 6: Data Integrity & Closing Verdict
```

---

## 🎥 Scene-by-Scene Script & Demonstration Guide

### **[0:00 – 0:25] Scene 1: The Hook — Why EV Infrastructure Planning Fails**

| Time | On-Screen Action (What to Record) | Voiceover Narration (What to Say) |
| :--- | :--- | :--- |
| **0:00** | Start full-screen on `http://localhost:5173/` on **Delhi Map** in Light Mode. Cursor hovers over high-density central Delhi station clusters. | *"India has crossed 10 million registered electric vehicles. Yet, urban charging infrastructure is in crisis: massive queues at prime hubs, while outer corridors remain complete charging deserts.* |
| **0:12** | Pull out slightly to show outer peripheral zones with zero chargers. | *Why? Because planning still relies on a broken assumption: the arbitrary universal EV-to-charger ratio. It ignores where vehicles actually drive, where grid capacity exists, and where battery swapping dominates.* |
| **0:20** | Cursor points to the brand header: **GridSight EV**. | *Welcome to **GridSight EV** — India’s first physics-grounded, machine-learning-driven spatial intelligence platform for EV infrastructure planning."* |

---

### **[0:25 – 0:55] Scene 2: Delhi Pilot — Multi-Source Deduplication & Burari Fleet Correction**

| Time | On-Screen Action (What to Record) | Voiceover Narration (What to Say) |
| :--- | :--- | :--- |
| **0:25** | On the **Delhi Map**, cycle the **Data Source** dropdown: Switch Delhi (876 sites) &rarr; BEE (1,909 sites) &rarr; Overlay. Open Power Class filter. | *"We start with the NCT of Delhi. Rather than relying on a single registry or synthetic data, GridSight ingests and deduplicates 876 official Switch Delhi sites, 1,909 BEE stations, and OpenStreetMap nodes — cleanly distinguishing DC Fast, AC Type-2, slow LEV, and Battery Swapping.* |
| **0:38** | Toggle the **Include 121 PIN-estimated swap kiosks** checkbox (dashed circles appear). | *We geocode verified locations and explicitly badge 121 PIN-centroid estimated kiosks to preserve absolute cartographic honesty.* |
| **0:44** | In sidebar, toggle **Redistributed Commercial Demand (Burari Correction)**. Show choropleth shifting. | *Crucially, we solve the famous **Burari Fleet Distortion** — where over 35% of Delhi’s commercial EVs are registered at a single RTO. Our 5-metric spatial algorithm reallocates commercial fleets across all 9 districts by population, road density, and commercial activity.* |
| **0:50** | Click on one station to show the side inspector: vendor, tariff, exact AC/DC connector count, and distance to nearest 11kV substation. | *Click any station to inspect its multi-network profile and physical substation proximity."* |

---

### **[0:55 – 1:25] Scene 3: National Overview — 36 States & 27.7K OMC Fuel Pump Chargers**

| Time | On-Screen Action (What to Record) | Voiceover Narration (What to Say) |
| :--- | :--- | :--- |
| **0:55** | Click the 2nd tab: **National Overview**. The interactive 36-state India choropleth appears. | *"Switching to tab two: the **National Overview**, tracking all 36 States and Union Territories.* |
| **1:05** | Hover over Maharashtra, Uttar Pradesh, and Karnataka. Click Maharashtra to open the state inspector drawer. | *Here, 10.68 million active VAHAN EVs are cross-referenced against 44,066 BEE registered connectors. But we go one critical step further:* |
| **1:13** | Highlight the OMC metric card in the top summary bar: **27,737 OMC Retail EV Pumps**. | *We integrate official Ministry of Petroleum data tracking **27,737 Oil Marketing Company fuel station chargers**, including 8,932 FAME-II supported installations. Planners can instantly evaluate real highway corridor readiness and true vehicle-to-charger deficits without double counting."* |

---

### **[1:25 – 2:05] Scene 4: Coverage Planning — Spatial ML Regressor, Sigmoid Decay & Bottom-Up Sizing**

| Time | On-Screen Action (What to Record) | Voiceover Narration (What to Say) |
| :--- | :--- | :--- |
| **1:25** | Click the 3rd tab: **Coverage Planning**. Show the 375-cell (2km × 2km) spatial grid covering Delhi. | *"Tab three is our decision engine: **Coverage & Capacity Planning**. Delhi is discretized into 375 uniform 2.0 km × 2.0 km planning cells.* |
| **1:33** | Click the **Radius Pills** (`1.5 km` &rarr; `3.0 km Delhi EV Policy`). Point to the **Native AI Engine Bar**. | *Planners can stress-test coverage using explicit Haversine rules. In our Native AI bar, watch what happens when we switch from the baseline linear heuristic to our **Spatial ML Regressor**:* |
| **1:42** | Click **[🧠 Spatial ML Regressor (R²=0.796)]**. Grid cell colors and priority scores update live. | *Trained on ground-truth infrastructure across 7 spatial features, the Random Forest model captures non-linear demand attractors that fixed rules completely miss.* |
| **1:48** | Toggle **[Sigmoid Kernel (Continuous)]**. | *We replace artificial step-buffer cliffs with a continuous sigmoid distance decay kernel: $S = D \times [1 - 1 / (1 + (d/r)^4)]$.* |
| **1:53** | Scroll down to the **2030 Future Simulator**. Click **[🧠 AI Bass S-Curve (R²=0.992)]**. | *Below, our **2030 Capacity Simulator** abandons arbitrary EV-to-charger ratios entirely. Using a calibrated Bass Diffusion S-curve forecasting 933,000 Delhi EVs, it computes bottom-up kilowatt-hour demand by vehicle segment — explicitly sizing physical **Stations**, **EVSE Charging Points**, **AC vs DC Nozzles**, and **Battery Swap Dockets**."* |

---

### **[2:05 – 2:35] Scene 5: AI Studio & Optimization — Feature Importance, Bass S-Curve & Dark Mode**

| Time | On-Screen Action (What to Record) | Voiceover Narration (What to Say) |
| :--- | :--- | :--- |
| **2:05** | Click the 4th tab: **AI & Optimization**. Show the **Spatial ML** tab with feature importance bars. | *"In the **AI Studio**, we provide full white-box explainability. The Random Forest feature importances prove that population density and commercial POIs drive 72% of charging demand elasticity, with feeder proximity contributing 9%.* |
| **2:14** | Switch to sub-tab **Bass Adoption Model**. Show the S-curve with $P_{10}/P_{90}$ stochastic bands. | *Our Bass Diffusion model ($R^2=0.992$, innovation $p=0.0114$, imitation $q=0.4963$) models the true non-linear S-curve transition.* |
| **2:20** | Switch to sub-tab **Constrained Siting Optimizer**. Click Candidate Hub #1. | *Our **Constrained Siting Optimizer** selects the top 25 candidate plazas across Delhi — constrained by 11kV/33kV substation feeder proximity under 1.5 km and anti-cannibalization spacing.* |
| **2:28** | Click the **🌙 Dark Mode** toggle in the top-right header. The entire UI and Leaflet map instantly invert into high-contrast dark cartography! | *And for 24/7 utility control rooms, a single click transitions the entire application and Leaflet cartography into high-contrast Dark Mode."* |

---

### **[2:35 – 2:55] Scene 6: Data Integrity & Closing Verdict**

| Time | On-Screen Action (What to Record) | Voiceover Narration (What to Say) |
| :--- | :--- | :--- |
| **2:35** | Click the 5th tab: **Data & Methodology**. Scroll through the source reconciliation table and 28 passing assertions. | *"Tab five documents our complete provenance trail across 8 government registries, with zero synthetic data and 28 automated schema assertions passing at 100%.* |
| **2:45** | Return to **Delhi Map** with the 25 purple AI Candidate Plazas glowing over the dark cartography. | *GridSight EV transforms chaotic spreadsheets into defensible, physics-grounded infrastructure decisions. Ready for Delhi today; architected for India tomorrow.* |
| **2:52** | Hold on final title screen: **GridSight EV | Team Mechies, NSUT | Techfest IIT Bombay 2026–27**. | *Thank you."* |

---

## 📋 Recording & Screen Capture Master Checklist

- [ ] **Display Resolution:** Record at `1920x1080` (Full HD). Set browser zoom to `90%` so map controls, sidebar, and right inspector drawer are all visible without excessive scrolling.
- [ ] **Starting Position:** Start on `http://localhost:5173/`, tab: **Delhi Map**, theme: **Light Mode**.
- [ ] **Mouse Flow:**
  - `0:25–0:50`: Smoothly click source dropdown, check the PIN-estimated swap checkbox, toggle Burari redistribution, and click 1 station marker.
  - `0:55–1:20`: Click **National Overview**, hover over 2 states, click Maharashtra, and highlight the OMC metric pill.
  - `1:25–2:00`: Click **Coverage Planning**, click radius `3.0 km`, click `[🧠 Spatial ML Regressor]`, click `[Sigmoid Kernel]`, scroll to 2030 simulator and click `[🧠 AI Bass S-Curve]`.
  - `2:05–2:30`: Click **AI & Optimization**, click through the 3 sub-tabs, then click **🌙 Dark Mode** in the header.
  - `2:35–2:55`: Click **Data & Methodology**, then return to **Delhi Map** for the closing shot.
- [ ] **Pacing:** Speak at ~140 words per minute with clear enunciation of key metrics (*"27,737 OMC pumps"*, *"R-squared 0.796"*, *"375 grid cells"*, *"Burari correction"*).
