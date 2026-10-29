#!/usr/bin/env python3
"""Builds the final GridSight EV methodology (DOCX + MD) from one content source.
Constraints: Arial everywhere, every font size >= 10 pt, <= 6 pages (verified separately via Word COM)."""
import re, os
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

OUT = r"C:\Users\hp\.gemini\antigravity\scratch\ev-infra-map-india"
BASE = Pt(10)
TEAL = RGBColor(15, 118, 110)
INK = RGBColor(15, 23, 42)

# ---------------------------------------------------------------- CONTENT
# markup: **bold**, _{sub}, ^{sup}
B = []
def h1(t): B.append(("h1", t))
def h2(t): B.append(("h2", t))
def p(t): B.append(("p", t))
def bl(items): B.append(("bl", items))
def eq(label, t): B.append(("eq", label, t))
def note(title, t): B.append(("note", title, t))
def tbl(head, rows, widths): B.append(("tbl", head, rows, widths))

TITLE = "GridSight EV: Geospatial EV Charging Infrastructure Intelligence Platform"
SUB = "Methodology Document | IIT Bombay Techfest 2026–27, Round 1 | Challenge 1: EV Infra Map India"
META = [("Team", "Mechies (NSUT, New Delhi)"), ("Leader", "Kunal, kunalclass1112@gmail.com"),
        ("Code", "github.com/aadityaexpress/gridsight-ev"), ("Data freeze", "19 October 2026")]

h1("1. Problem Understanding and Relevance (25%)")
p("India's public EV charging data is fragmented across ministries, agencies and crowdsourced maps, each with different units, dates and geographies. "
  "Planners therefore cannot answer the two questions that decide capital allocation: **where** is charging missing, and **how much capacity** is needed there. We identify four root problems:")
bl([
 "**Registry overlap and unit ambiguity.** BEE lists charger rows (39,641 rows, 44,066 connectors, 29,371 unique sites); MoPNG/OMC lists fuel-retail sites (27,737 installed, 22,753 operational); MHI lists FAME-II chargers (8,932); Switch Delhi lists 876 sites (573 charging, 303 swapping); OSM holds 725 national features (179 in Delhi). These are different units over overlapping assets, so summing them double-counts.",
 "**Geographic mismatch.** VAHAN demand is published by State and RTO, but chargers are points. In Delhi, commercial EVs (e-rickshaws, cabs, goods vehicles) register at Burari RTO (DL-11 to DL-14), which hides district-level demand.",
 "**Electrical opacity.** No public source gives feeder or transformer spare capacity or live connector occupancy.",
 "**Proximity is not adequacy.** A coverage circle (distance d ≤ radius r) says a charger is near, not that it can serve the fleet. Two 3.3 kW sockets within 1 km cannot serve 100 e-rickshaws that each need about 6.4 kWh/day.",
])
p("**Scope.** Delhi (NCT) is the detailed spatial pilot because it has the richest open EV data. The national layer covers all 36 States/UTs using official registrations only. "
  "**Intended use:** a decision-support tool for MHI, ICAT, DISCOMs and state nodal agencies to prioritise sites and size hardware.")

h1("2. Solution Overview and Implementation Status")
p("GridSight EV is a four-stage pipeline: **(1)** deterministic multi-source integration with a strict non-additivity rule; **(2)** a 375-cell Delhi gap grid separating geometric coverage from energy adequacy; "
  "**(3)** an explainable AI and optimisation layer (Random Forest demand model, Bass diffusion forecast, constrained siting); **(4)** a bottom-up capacity simulator for 2026–2030 that converts fleet growth into kWh/day and hardware counts. "
  "Processing runs in Python (`scripts/process_data.py`, `train_ai_models.py`); the React/TypeScript/Leaflet front end (`src/utils/planningEngine.ts`) recomputes coverage and scenarios in the browser on keyless OpenStreetMap tiles.")
note("Implemented vs planned",
 "**Implemented and verified (Phase 0):** 36-State demand choropleths; BEE, OMC, FAME-II, Switch Delhi and OSM as separate baselines; 375-cell grid; Random Forest; Bass forecast; 25-site siting optimiser; capacity simulator; 28/28 data assertions; deployed web app. "
 "**Planned (Phases 1–3):** highway corridors, DISCOM voltage-tier grid proxy, containerised offline deployment (Section 8).")

h1("3. Data Strategy and Provenance (10%)")
tbl(["Source (ID)", "Vintage / unit", "Role, limitation and treatment"], [
 ["BEE public charging registry (SRC-01)", "to 26 Oct 2025; site", "39,641 rows, 29,371 sites. Static PDF, no operating status; 119 bad coordinates isolated but kept in state totals."],
 ["MoPNG/OMC and MHI FAME-II, PIB (SRC-02/03)", "to 1 Mar 2026; State", "22,753 operational OMC sites; 8,932 FAME-II chargers. Scheme or retailer subsets, kept as separate layers."],
 ["Switch Delhi, GNCTD (SRC-04)", "19 Oct 2026; site", "876 sites after removing 15 duplicate kiosks; 121 swap kiosks geocoded to PIN centroid. Training target for the demand model."],
 ["OpenStreetMap (SRC-05, 08, 10C, 11C)", "19 Oct 2026; point/line", "179 Delhi stations (cross-check only), 8,087 road segments, 576 substations/transformers, 3,534 POIs. Crowdsourced; used only inside Delhi."],
 ["VAHAN 4, MoRTH (SRC-06)", "19 Oct 2026; State/RTO", "10,689,490 active EVs; 549,153 in Delhi. Includes 26.4% non-compliant active vehicles."],
 ["DataMeet boundaries (SRC-07); WorldPop 1 km (SRC-09)", "2011/2019; 2020 scaled to 2025", "36 State and 9 Delhi district polygons (CC BY 4.0). Population scaled to the NCP 2025 Delhi projection of 22.3 million."],
 ["NITI Aayog/WRI IEMI 2025; BEE/SERC tariffs (SRC-10B, 11A)", "2025; State", "Secondary benchmarks and tariff context only; three States have no notified tariff."],
], [Inches(2.05), Inches(1.45), Inches(3.6)])
bl([
 "**Non-additivity rule.** BEE, OMC, FAME-II, Switch Delhi and OSM are independent baselines; the interface shows one at a time and never adds them.",
 "**Two VAHAN fuel tags.** `ELECTRIC(BOV)` (6.35 M) alone misses `PURE EV` (4.34 M); both are combined. Compliant (7.87 M) and non-compliant (2.82 M) vehicles are shown separately to give lower and upper demand bounds.",
 "**State harmonisation.** 46 BEE and 38 PIB spelling variants are mapped to 36 canonical State codes. Raw files are kept under `data/raw/` and listed in `data/source_manifest.csv`. Gaps (Delhi OpenEV HTTP 502, CEA login, Census timeout) are logged in `DATA_GAPS.md`.",
 "**Boundary of OSM use.** National rankings use only VAHAN, MoSPI GSDP and NITI benchmarks, never OSM.",
])

h1("4. Technical Approach and Feasibility (25%)")
h2("4.1 Delhi spatial grid and demand redistribution")
p("The grid covers 28.40–28.89°N, 76.83–77.35°E in steps of 0.018° latitude × 0.0205° longitude (about 2 km × 2 km), giving **375 cells** that include commuter-fringe areas of Gurugram, Noida, Faridabad and Ghaziabad. "
  "Population is summed from WorldPop by pixel centre and scaled to 22.3 million. Distances use an equirectangular projection (error under 0.05% against Haversine, under 2 m/km). "
  "Burari-registered commercial EVs are spread over the 9 Census districts by an activity-and-population weight:")
eq("Eq. 1", "w_{district} = 0.5 · (N_{poi,district} / N_{poi,total}) + 0.5 · (P_{district} / P_{total})")
p("Here N_{poi} counts OSM commercial attractors and P is district population. Private two-wheelers stay with their zonal RTO.")
h2("4.2 Two-stage coverage logic")
p("**Stage 1 (proximity):** a cell is *Covered* if d ≤ r (r selectable 0.5–5 km, default 1.5 km); an *Underserved Priority Zone* if d > r and demand score D ≥ 22 (65th percentile); otherwise a *Low-Demand Fringe*. "
  "**Stage 2 (adequacy):** a covered cell is still flagged if installed daily kWh is below its modelled demand, so proximity cannot hide a capacity shortfall.")
h2("4.3 Explainable spatial demand model")
p("A Random Forest regressor (120 trees, depth 6) learns charging density from the 375 cells, using population, commercial POIs, attractor hubs, transit interchanges, road density, distance to feeder substation and local transformer count. "
  "The target is observed density of the 876 Switch Delhi sites. **In-sample R² = 0.796, MAE = 5.85, RMSE = 10.38; 5-fold cross-validated R² = 0.333 ± 0.096.** "
  "Importances: population 49.65%, commercial POIs 13.14%, attractor hubs 9.53%, feeder distance 9.14%, roads 8.32%, transit 6.69%, transformer count 3.55%.")
eq("Eq. 2", "D_{AI} = f_{RF}(Pop, POI, Transit, Roads, Dist_{substation}, DT_{count}) in [0, 100]")
p("**Interpretation and limit.** The wide gap between in-sample and cross-validated R² shows the model is a spatial prioritisation index, not a precise predictor: existing stations follow land and policy as well as demand. We report both scores and use D only to rank cells.")
h2("4.4 Continuous distance decay")
p("A hard cut-off makes priority jump at d = r. We use a smooth kernel instead:")
eq("Eq. 3", "S = D_{AI} · [ 1 − 1 / (1 + (d / r)^{4}) ]")
p("S → 0 when d is much smaller than r, S = 0.5·D_{AI} at d = r, and S → D_{AI} when d is much larger than r, so a user's radius slider changes rankings gradually.")
h2("4.5 Fleet forecast (Bass diffusion)")
p("The Bass model is fitted by non-linear least squares to 68 months of VAHAN registrations (2018–2026), R² = 0.992:")
eq("Eq. 4", "dN/dt = [ p + (q / M) · N(t) ] · [ M − N(t) ],   p = 0.0114,  q = 0.4963,  M = 20.0 million")
tbl(["Year", "National EVs (P10–P90)", "Delhi fleet"], [
 ["2026", "11.23 M (8.16–14.54 M)", "577,295"],
 ["2028", "15.63 M (12.23–18.71 M)", "803,300"],
 ["2030", "18.17 M (15.27–20.58 M)", "933,751"],
], [Inches(1.0), Inches(3.4), Inches(2.7)])
p("M is an assumed market ceiling, so bands are scenario ranges rather than statistical guarantees.")
h2("4.6 Energy balance and hardware sizing")
eq("Eq. 5", "E_{k} = V_{k,2030} · e_{k} · φ_{k}   (kWh/day),   k in {2W, 3W, 4W, Bus, Goods}")
tbl(["Class", "Daily energy e_k", "Public share φ", "Plug-in split (AC/DC)"], [
 ["2W", "32 km × 0.032 = 1.02 kWh", "20%", "85/15 (35% of energy swapped*)"],
 ["3W", "85 km × 0.075 = 6.38 kWh", "55%", "85/15 (35% swapped*)"],
 ["4W", "48 km × 0.145 = 6.96 kWh", "32%", "35/65"],
 ["Bus", "180 km × 1.15 = 207 kWh", "20%", "0/100"],
 ["Goods", "90 km × 0.15 = 13.5 kWh", "50%", "25/75"],
], [Inches(0.8), Inches(2.4), Inches(1.4), Inches(2.5)])
p("*Battery swapping absorbs 28% / 35% / 40% (low / baseline / high) of 2W and 3W public energy; the rest is plugged in. "
  "Daily throughput: AC connector 4.2 kW × 5.5 h = 23.1 kWh; DC nozzle 30 kW × 6 h = 180 kWh; swap dock 12.5 swaps × 2.1 kWh = 26.25 kWh.")
eq("Eq. 6", "Points = AC + ceil(DC / 1.35);  Stations = ceil(Points / 4.5);  Net new = max(0, Required − Σ Installed · η_{power})")
p("The substitution factor η_{power} is 1.0 when installed power meets the required tier, 0.15 for slow sockets against slow-AC need, and 0 for slow sockets against DC need, so legacy 3.3 kW points cannot hide a fast-charging gap. "
  "At cell level, district public energy is split in proportion to AI demand (E_{cell} = E_{district} · D_{AI,cell} / ΣD_{AI}) and sized as AC = max(2, ceil(E_{AC} / 23.1)), DC = max(1, ceil(E_{DC} / 180)), stations = ceil((AC + DC) / 6), which guarantees redundancy.")
h2("4.7 Constrained siting optimiser")
p("A greedy submodular algorithm selects K = 25 cells to maximise ΣS_{i}, subject to: **(a)** feeder-distance penalty beyond 1.5 km, with Tier 1 (< 1 km, ≥ 500 kVA proxy), Tier 2 (1–2.5 km, 150–250 kVA proxy) and Tier 3 (> 2.5 km); "
  "**(b)** minimum 1.2 km spacing between chosen sites to avoid cannibalisation; **(c)** the minimum-redundancy hardware rule above. Greedy selection carries the standard (1 − 1/e) guarantee for the unconstrained monotone submodular case; with the spacing and feeder constraints it is a heuristic, so we report it as such.")

h1("5. Innovation and Differentiation (20%)")
bl([
 "**Non-additive multi-registry design.** Overlapping registries are never summed; the audit matrix exposes the discrepancies. Most dashboards add them.",
 "**Proximity separated from adequacy.** Every cell carries both a distance state and an energy-capacity state.",
 "**Explainable AI instead of a black box.** Random Forest importances, a closed-form Bass curve and an auditable optimiser can be defended in a public tender; honest CV disclosure builds that trust.",
 "**Continuous decay kernel** removes the artificial cliff of coverage circles.",
 "**Power-tier substitution** stops legacy slow sockets offsetting fast-charging need; battery swapping is modelled as its own hardware class.",
 "**Data-engineering findings:** the second VAHAN fuel tag (+4.34 M vehicles), Burari redistribution, and 119 corrupted BEE coordinates isolated rather than silently dropped.",
])

h1("6. Results and Validation")
p("The optimiser returned 25 sites (14 Tier 1, 11 Tier 2). The five highest-ranked, by the optimiser's utility score, are below; hardware is the recommended installed count.")
tbl(["Rank / cell (district)", "Lat, Lon", "D_AI", "Nearest charger", "Substation", "Tier", "AC / DC / swap"], [
 ["1  DL-GRID-13-14 (West)", "28.643, 77.127", "65.6", "1.88 km", "1,116 m", "2", "58 / 10 / 40"],
 ["2  DL-GRID-10-14 (South West)", "28.589, 77.127", "33.4", "2.69 km", "724 m", "1", "30 / 5 / 21"],
 ["3  DL-GRID-09-11 (South West)", "28.571, 77.066", "51.7", "1.54 km", "979 m", "1", "46 / 8 / 32"],
 ["4  DL-GRID-14-19 (North)", "28.661, 77.230", "33.5", "2.10 km", "448 m", "1", "30 / 5 / 21"],
 ["5  DL-GRID-12-13 (West)", "28.625, 77.107", "49.2", "1.51 km", "1,496 m", "2", "44 / 7 / 30"],
], [Inches(2.0), Inches(1.15), Inches(0.5), Inches(0.9), Inches(0.85), Inches(0.4), Inches(1.3)])
bl([
 "**Data tests:** `python scripts/validate_processed_data.py` passes **28/28** assertions (36 States, 10.69 M EVs, 39,641 BEE rows, 44,066 connectors, OMC 27,737/22,753, FAME-II 8,932, Delhi 9 districts / 23 RTOs / 549,153 EVs, 876 Switch Delhi sites, 375 cells, RF R² > 0.70, Bass R² > 0.95, 25 optimised sites).",
 "**Software tests:** `tsc --noEmit` reports 0 errors; `vite build` succeeds (about 8–10 s); a local smoke test of all views returned HTTP 200.",
 "**Reproducibility:** frozen manifest, raw files, scripts and processed bundles are all in the public repository; the app bundles all data locally, so a demo needs no network.",
])

h1("7. Limitations and Risks")
tbl(["Limitation", "Consequence and mitigation"], [
 ["BEE (Oct 2025) is 12 months older than VAHAN (Oct 2026).", "National deficits look larger than reality. Switch Delhi (Oct 2026) is offered as a current baseline and map legends carry the date warning."],
 ["Substation distance is not hosting capacity; 99.3% of OSM substations carry no MVA rating.", "Distance is a proximity proxy only. kVA tiers are planning proxies, not DISCOM-verified; Phase 2 adds voltage tiers."],
 ["No public connector occupancy or session data.", "Results describe installed infrastructure, not utilisation. The 82% OMC operational ratio can be applied as a discount."],
 ["26.4% of active EVs lack current compliance.", "Compliant-only and total-active views give lower and upper demand bounds."],
 ["RF cross-validated R² is 0.333 (spatial autocorrelation, supply-driven siting).", "Used only to rank cells; sensitivity to the radius and threshold is exposed in the interface."],
 ["Bass ceiling M and energy parameters (km/day, kWh/km, shares) are assumptions.", "Parameters are visible and editable; bands and swapping low/baseline/high scenarios show sensitivity."],
 ["OSM completeness is uneven.", "OSM is confined to Delhi and never drives national results."],
], [Inches(2.9), Inches(4.2)])

h1("8. Implementation Roadmap (20%)")
tbl(["Phase", "Work and deliverable", "Exit test"], [
 ["0. Baseline (complete)", "Frozen manifest, integration pipeline, grid, RF, Bass, optimiser, simulator, deployed app.", "28/28 assertions; 0 type errors; app live."],
 ["1. Highway corridors (weeks 1–2)", "5 km buffers along NH-48 (Delhi–Jaipur) and Yamuna Expressway from PM Gati Shakti and NHAI data; DC-fast infill for inter-city freight.", "Corridor tool reproduces known stations and lists gaps."],
 ["2. Grid proxy (weeks 3–4)", "Combine CEA connectivity standards with DISCOM 11/33/66 kV tiers into a feasibility index per cell.", "Index replaces the distance-only proxy in the optimiser."],
 ["3. Hardening (weeks 5–6)", "Docker image, cloud hosting, offline cache, rehearsed demo.", "Full demo with no network dependency."],
], [Inches(1.75), Inches(3.55), Inches(1.8)])
p("**Feasibility:** every Phase 1–2 input is public or derivable, and each phase extends the existing Python and TypeScript modules rather than replacing them. "
  "**Scaling:** the same pipeline applies to any Indian city, since it needs only VAHAN RTO data, a registry, WorldPop and OSM.")

h1("9. Evaluation Criteria Map and References")
tbl(["Criterion (weight)", "Where evidenced"], [
 ["Problem Understanding and Relevance (25%)", "Sections 1, 3; `DATA_AVAILABILITY_AUDIT.md`, `DATA_GAPS.md`"],
 ["Technical Approach and Feasibility (25%)", "Sections 4, 6, 7; `train_ai_models.py`, `planningEngine.ts`"],
 ["Innovation and Differentiation (20%)", "Section 5; `AiStudioView.tsx`, `ai_optimization_results.json`"],
 ["Implementation Roadmap (20%)", "Sections 2, 8; `DELIVERABLE_AUDIT.md`"],
 ["Data Strategy and Provenance (10%)", "Sections 3, 7; `source_manifest.csv`, `DATA_QUALITY_REPORT.md`"],
], [Inches(2.9), Inches(4.2)])
REFS = ("[1] BEE, Ministry of Power, Public Charging Stations Data till 26 Oct 2025. "
 "[2] PIB PRID 2246042, MoPNG/MHI, OMC charging stations, 27 Mar 2026. "
 "[3] PIB PRID 2246045, MHI, FAME-II installations, 27 Mar 2026. "
 "[4] Transport Dept. and DDC, GNCTD, Switch Delhi registry, ev.delhi.gov.in, snapshot 19 Oct 2026. "
 "[5] MoRTH/NIC, VAHAN 4 Public Analytics, snapshot 19 Oct 2026. "
 "[6] DataMeet, Census-2011 boundaries (CC BY 4.0). "
 "[7] WorldPop, India 1 km population, scaled to NCP 2025. "
 "[8] OpenStreetMap contributors, Overpass extracts (ODbL 1.0), 19 Oct 2026. "
 "[9] NITI Aayog and WRI India, India Electric Mobility Index 2025. "
 "[10] Bass, F. M., A New Product Growth for Model Innovations, Management Science 15(5), 1969. "
 "[11] Nemhauser, Wolsey and Fisher, An analysis of approximations for maximizing submodular set functions, Math. Programming 14, 1978.")
B.append(("refs", REFS))

# ---------------------------------------------------------------- helpers
TOK = re.compile(r"(\*\*.+?\*\*|`.+?`|_\{.+?\}|\^\{.+?\})")

def split(t):
    out = []
    for part in TOK.split(t):
        if not part: continue
        if part.startswith("**"): out.append(("b", part[2:-2]))
        elif part.startswith("`"): out.append(("c", part[1:-1]))
        elif part.startswith("_{"): out.append(("sub", part[2:-1]))
        elif part.startswith("^{"): out.append(("sup", part[2:-1]))
        else: out.append(("t", part))
    return out

def style_run(r, size=BASE, bold=False, color=None, italic=False):
    r.font.name = "Arial"; r.font.size = size; r.bold = bold; r.italic = italic
    rpr = r._r.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts"); rpr.insert(0, rf)
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"): rf.set(qn(a), "Arial")
    if color is not None: r.font.color.rgb = color

def add_rich(par, text, size=BASE, bold=False, color=None):
    for kind, s in split(text):
        # no true sub/superscript: Word shrinks them below 10 pt, so they stay inline at full size
        if kind == "sub": s = "_" + s
        if kind == "sup": s = "^" + s
        r = par.add_run(s)
        style_run(r, size, bold or kind == "b", color)

def shade(cell, fill):
    cell._tc.get_or_add_tcPr().append(parse_xml(f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="{fill}"/>'))

def margins(cell, t=30, b=30, l=70, r=70):
    cell._tc.get_or_add_tcPr().append(parse_xml(
        f'<w:tcMar {nsdecls("w")}><w:top w:w="{t}" w:type="dxa"/><w:left w:w="{l}" w:type="dxa"/>'
        f'<w:bottom w:w="{b}" w:type="dxa"/><w:right w:w="{r}" w:type="dxa"/></w:tcMar>'))

def borders(table, color="94A3B8"):
    table._tbl.tblPr.append(parse_xml(
        f'<w:tblBorders {nsdecls("w")}>' + "".join(
            f'<w:{s} w:val="single" w:sz="4" w:space="0" w:color="{color}"/>'
            for s in ("top", "left", "bottom", "right", "insideH", "insideV")) + '</w:tblBorders>'))

def fix_order(doc):
    TC = ['tcW','gridSpan','vMerge','tcBorders','shd','noWrap','tcMar','vAlign']
    TB = ['tblStyle','tblW','jc','tblBorders','shd','tblLayout','tblCellMar','tblLook']
    def srt(el, order):
        kids = list(el)
        kids.sort(key=lambda c: order.index(c.tag.split('}')[1]) if c.tag.split('}')[1] in order else 99)
        for k in kids: el.remove(k)
        for k in kids: el.append(k)
    for t in doc.tables:
        srt(t._tbl.tblPr, TB)
        for row in t.rows:
            row._tr.get_or_add_trPr().append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
            for c in row.cells: srt(c._tc.get_or_add_tcPr(), TC)

# ---------------------------------------------------------------- DOCX
def build_docx(path):
    d = Document()
    s = d.sections[0]
    s.page_width, s.page_height = Inches(8.5), Inches(11)
    s.top_margin = s.bottom_margin = Inches(0.65)
    s.left_margin = s.right_margin = Inches(0.7)
    st = d.styles["Normal"]
    st.font.name = "Arial"; st.font.size = BASE
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
    st.paragraph_format.space_after = Pt(3); st.paragraph_format.line_spacing = 1.0
    for nm in ("List Bullet",):
        d.styles[nm].font.name = "Arial"; d.styles[nm].font.size = BASE

    hp = s.header.paragraphs[0]; hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    style_run(hp.add_run("GridSight EV | Techfest 2026–27 Round 1 | Methodology"), BASE, color=RGBColor(100, 116, 139))
    fp = s.footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    style_run(fp.add_run("Team Mechies, NSUT | Page "), BASE, color=RGBColor(100, 116, 139))
    r = fp.add_run(); style_run(r, BASE, color=RGBColor(100, 116, 139))
    for typ, txt in (("begin", None), (None, " PAGE "), ("end", None)):
        if typ:
            e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), typ); r._r.append(e)
        else:
            e = OxmlElement("w:instrText"); e.set(qn("xml:space"), "preserve"); e.text = txt; r._r.append(e)

    tp = d.add_paragraph(); tp.paragraph_format.space_after = Pt(1)
    style_run(tp.add_run(TITLE), Pt(14), True, TEAL)
    sp = d.add_paragraph(); sp.paragraph_format.space_after = Pt(3)
    style_run(sp.add_run(SUB), BASE, True, RGBColor(71, 85, 105))
    mt = d.add_table(rows=1, cols=4); mt.alignment = WD_TABLE_ALIGNMENT.CENTER; mt.autofit = False
    for i, (k, v) in enumerate(META):
        c = mt.cell(0, i); c.width = Inches(1.775); shade(c, "F1F5F9"); margins(c)
        pp = c.paragraphs[0]; pp.paragraph_format.space_after = Pt(0)
        style_run(pp.add_run(k + ": "), BASE, True, INK); style_run(pp.add_run(v), BASE)
    borders(mt)

    for blk in B:
        k = blk[0]
        if k == "h1":
            pp = d.add_paragraph(); pp.paragraph_format.space_before = Pt(7); pp.paragraph_format.space_after = Pt(2)
            pp.paragraph_format.keep_with_next = True
            style_run(pp.add_run(blk[1]), Pt(12), True, TEAL)
        elif k == "h2":
            pp = d.add_paragraph(); pp.paragraph_format.space_before = Pt(3); pp.paragraph_format.space_after = Pt(1)
            pp.paragraph_format.keep_with_next = True
            style_run(pp.add_run(blk[1]), BASE, True, INK)
        elif k == "p":
            pp = d.add_paragraph(); add_rich(pp, blk[1])
        elif k == "bl":
            for it in blk[1]:
                pp = d.add_paragraph(style="List Bullet"); pp.paragraph_format.space_after = Pt(1.5)
                add_rich(pp, it)
        elif k in ("eq", "note"):
            t = d.add_table(rows=1, cols=1); t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.autofit = False
            c = t.cell(0, 0); c.width = Inches(7.1); margins(c, 40, 40, 100, 100)
            shade(c, "F8FAFC" if k == "eq" else "F0FDFA")
            c._tc.get_or_add_tcPr().append(parse_xml(
                f'<w:tcBorders {nsdecls("w")}><w:left w:val="single" w:sz="18" w:space="0" w:color="0F766E"/></w:tcBorders>'))
            pp = c.paragraphs[0]; pp.paragraph_format.space_after = Pt(0)
            if k == "eq":
                style_run(pp.add_run(f"[{blk[1]}]  "), BASE, True, TEAL)
                add_rich(pp, blk[2], BASE, True, INK)
            else:
                style_run(pp.add_run(blk[1] + ". "), BASE, True, TEAL)
                add_rich(pp, blk[2])
            sep = d.add_paragraph(); sep.paragraph_format.space_after = Pt(0)
            sep.paragraph_format.line_spacing = Pt(3)
            style_run(sep.add_run(""), Pt(10))
        elif k == "tbl":
            head, rows, widths = blk[1:]
            t = d.add_table(rows=1 + len(rows), cols=len(head)); t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.autofit = False
            for ci, h in enumerate(head):
                c = t.cell(0, ci); c.width = widths[ci]; shade(c, "0F766E"); margins(c)
                pp = c.paragraphs[0]; pp.paragraph_format.space_after = Pt(0)
                style_run(pp.add_run(h), BASE, True, RGBColor(255, 255, 255))
            for ri, row in enumerate(rows):
                for ci, v in enumerate(row):
                    c = t.cell(ri + 1, ci); c.width = widths[ci]; margins(c)
                    shade(c, "F8FAFC" if ri % 2 else "FFFFFF")
                    pp = c.paragraphs[0]; pp.paragraph_format.space_after = Pt(0)
                    add_rich(pp, v)
            borders(t)
            sep = d.add_paragraph(); sep.paragraph_format.space_after = Pt(0); sep.paragraph_format.line_spacing = Pt(4)
            style_run(sep.add_run(""), Pt(10))
        elif k == "refs":
            h = d.add_paragraph(); h.paragraph_format.space_before = Pt(3)
            style_run(h.add_run("References"), BASE, True, INK)
            pp = d.add_paragraph(); add_rich(pp, blk[1])
    fix_order(d)
    d.save(path)

# ---------------------------------------------------------------- MD
def md_rich(t):
    out = ""
    for kind, s in split(t):
        if kind == "b": out += f"**{s}**"
        elif kind == "c": out += f"`{s}`"
        elif kind == "sub": out += f"<sub>{s}</sub>"
        elif kind == "sup": out += f"<sup>{s}</sup>"
        else: out += s.replace("|", "\\|")
    return out

def build_md(path):
    L = [f"# {TITLE}", "", f"**{SUB}**", "",
         "| " + " | ".join(k for k, _ in META) + " |", "|" + "---|" * len(META),
         "| " + " | ".join(md_rich(v) for _, v in META) + " |", ""]
    for blk in B:
        k = blk[0]
        if k == "h1": L += ["", f"## {blk[1]}", ""]
        elif k == "h2": L += [f"### {blk[1]}", ""]
        elif k == "p": L += [md_rich(blk[1]), ""]
        elif k == "bl": L += ["- " + md_rich(i) for i in blk[1]] + [""]
        elif k == "eq": L += [f"> **[{blk[1]}]** {md_rich(blk[2])}", ""]
        elif k == "note": L += [f"> **{blk[1]}.** {md_rich(blk[2])}", ""]
        elif k == "tbl":
            L += ["| " + " | ".join(blk[1]) + " |", "|" + "---|" * len(blk[1])]
            L += ["| " + " | ".join(md_rich(c) for c in r) + " |" for r in blk[2]] + [""]
        elif k == "refs": L += ["### References", "", md_rich(blk[1]), ""]
    open(path, "w", encoding="utf-8").write("\n".join(L))

if __name__ == "__main__":
    build_docx(os.path.join(OUT, "GridSight_EV_Methodology_Final.docx"))
    build_md(os.path.join(OUT, "GridSight_EV_Methodology_Final.md"))
    print("built")

