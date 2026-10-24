# 🎬 GridSight EV — 2.5-Minute Video Demonstration Script

**Target Duration:** 2 minutes 30 seconds (~380 words)  
**Tone:** Confident, analytical, urgent, and technically rigorous  
**Target Audience:** Hackathon Jury & Technical Evaluators (Techfest IIT Bombay 2026–27)

---

## ⏱️ Video Timeline & Scene Breakdown

### **[0:00 – 0:25] Scene 1: The Hook — The Illusion of EV Infrastructure Planning**

| Time | Visual / Screen Action | Spoken Audio (Word-for-Word Voiceover) |
| :--- | :--- | :--- |
| **0:00** | **Title Card**: *GridSight EV: Geospatial Infrastructure Intelligence*. Cut immediately to full-screen web app at `http://localhost:5173/`. | *"India has over 10 million registered electric vehicles. Yet, every single week, EV drivers face dead chargers, 45-minute queues, and massive charging deserts.* |
| **0:12** | Cursor hovers across the Delhi map, highlighting high-density central clusters versus complete charging voids in outer peri-urban zones. | *Why? Because India’s charging infrastructure is still planned using arbitrary universal ratios, blind heuristics, and siloed government registries.* |
| **0:20** | Focus cursor on the top brand mark **GridSight EV**. | *Meet **GridSight EV** — India’s first physics-grounded, machine-learning-driven spatial intelligence platform for EV infrastructure planning."* |

---

### **[0:25 – 0:55] Scene 2: Delhi Pilot — Truth in Multi-Source Data Integration**

| Time | Visual / Screen Action | Spoken Audio (Word-for-Word Voiceover) |
| :--- | :--- | :--- |
| **0:25** | Click the **Delhi Map** tab. In the left sidebar, toggle between **Switch Delhi (876 sites)** and **BEE Registry (1,909 sites)**. | *"We begin in the National Capital Territory of Delhi. Rather than relying on synthetic data or single dashboards, GridSight ingests and deduplicates 876 GNCTD Switch Delhi sites, 1,909 BEE stations, and OpenStreetMap nodes.* |
| **0:40** | Enable the **District Demand Choropleth** overlay. Zoom into North Delhi / Burari. | *We pair this with 549,000 MoRTH VAHAN registrations across 23 zonal RTOs — solving the classic Burari commercial fleet distortion using an algorithmic 5-metric redistribution model.* |
| **0:48** | Check the **🧠 AI Siting Candidates (Top 25)** box in the sidebar. Distinctive purple markers illuminate across Delhi. | *Right on this map, you can overlay the top 25 AI-optimized charging plazas, sized down to the exact kilowatt."* |

---

### **[0:55 – 1:20] Scene 3: National Overview — 36-State Sizing & Corridor Readiness**

| Time | Visual / Screen Action | Spoken Audio (Word-for-Word Voiceover) |
| :--- | :--- | :--- |
| **0:55** | Click the 2nd tab: **National Overview**. The interactive 36-state India choropleth appears. | *"Moving to our second tab — the National Overview. Here, we track all 36 States and Union Territories.* |
| **1:05** | Hover over Maharashtra, Karnataka, and Uttar Pradesh. Click Maharashtra to open the state inspector drawer. | *Evaluators can cross-reference 10.68 million active EVs against 44,000 BEE connectors and 27,700 Oil Marketing Company retail fuel pumps. No guesswork: every state displays verified EVs-per-charger ratios and highway corridor readiness."* |

---

### **[1:20 – 1:55] Scene 4: Coverage Planning — Machine Learning Demand & Sigmoid Decay**

| Time | Visual / Screen Action | Spoken Audio (Word-for-Word Voiceover) |
| :--- | :--- | :--- |
| **1:20** | Click the 3rd tab: **Coverage Planning**. Show the 375-cell (2.0 km × 2.0 km) grid. | *"Now, the core engine: Coverage and Capacity Planning. Delhi is discretized into 375 uniform 2-kilometer grid cells.* |
| **1:30** | In the top **Native AI Optimization Engine** bar, toggle between **[🧠 Spatial ML Regressor (R²=0.796)]** and **[⚡ Baseline Heuristic]**. | *Watch this: with one click, we switch from a traditional static heuristic to our 6-feature Spatial Random Forest Regressor — trained on ground-truth charging points with an R-squared of 0.796.* |
| **1:42** | Toggle the **Sigmoid Distance Decay Kernel**. | *We replace arbitrary distance cliffs with continuous sigmoid decay: $S = D \times [1 - 1 / (1 + (d/r)^4)]$.* |
| **1:48** | In the 2030 future growth presets, click **[🧠 AI Bass S-Curve (R²=0.992)]**. | *And in our 2030 simulator, our calibrated Bass Diffusion S-curve forecasts 933,000 Delhi EVs, deriving required AC nozzles, DC fast guns, and swap dockets bottom-up from category-specific daily kilowatt-hour demand."* |

---

### **[1:55 – 2:15] Scene 5: AI Studio & One-Click Dark Mode**

| Time | Visual / Screen Action | Spoken Audio (Word-for-Word Voiceover) |
| :--- | :--- | :--- |
| **1:55** | Click the 4th tab: **AI & Optimization**. Scroll smoothly through the feature importance chart and the 25 Siting Plazas table. | *"In the AI Studio, evaluators have complete mathematical transparency: Random Forest feature importances, Bass adoption inflection curves, and our Submodular Greedy Siting Optimizer.* |
| **2:05** | Click a candidate plaza row to inspect its substation feeder proximity (<1.5 km) and grid hosting capacity. | *Every recommended plaza is constrained by physical 11kV/33kV substation feeder proximity and anti-cannibalization spacing.* |
| **2:12** | Click the **🌙 Dark Mode** toggle in the top-right header. The entire UI and Leaflet map instantly invert into high-contrast dark cartography. | *And for control-room operators, a single click switches the entire platform into custom high-contrast dark cartography."* |

---

### **[2:15 – 2:35] Scene 6: Conclusion — Decision-Ready Intelligence**

| Time | Visual / Screen Action | Spoken Audio (Word-for-Word Voiceover) |
| :--- | :--- | :--- |
| **2:15** | Click the **Data & Methodology** tab, showcasing the verified provenance table and 28 passing pipeline assertions. | *"Zero synthetic data. Complete mathematical explainability. Proven against live government portals.* |
| **2:25** | Return to the live map with 25 AI candidate hubs glowing. Show final slide: *GridSight EV \| Team Mechies, NSUT \| Techfest IIT Bombay 2026–27*. | *GridSight EV turns raw government spreadsheets into actionable infrastructure decisions. Ready for Delhi today; scalable across India tomorrow. Thank you."* |

---

## 🎥 Recording & Presentation Checklist

- [ ] **Display Setup:** Resolution set to `1920x1080` (Full HD), browser zoom at `90%` or `100%`.
- [ ] **Starting State:** Clean refresh on `http://localhost:5173/`, starting on `Delhi Map` in **Light Mode**.
- [ ] **Mouse Control:** Smooth, deliberate cursor movements with 1-second pauses on important metric cards.
- [ ] **Audio Delivery:** Speak at a steady pace (~135–145 words per minute), emphasizing technical keywords (*"R-squared 0.796"*, *"Submodular Greedy"*, *"Sigmoid decay"*, *"Zero synthetic data"*).
- [ ] **Dark Mode Moment:** Give the Dark Mode toggle a distinct 1.5-second beat so the visual contrast lands cleanly on screen.
