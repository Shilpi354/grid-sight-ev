import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def create_document():
    doc = Document()

    # Page Setup - 0.75 in margins
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)
        
        # Header & Footer
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("GridSight EV — Techfest 2026–27 Round 1 Submission")
        hrun.font.name = "Arial"
        hrun.font.size = Pt(8.5)
        hrun.font.color.rgb = RGBColor(148, 163, 184) # slate-400

        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        frun = fp.add_run("Team Mechies | Netaji Subhas University of Technology (NSUT)")
        frun.font.name = "Arial"
        frun.font.size = Pt(8.5)
        frun.font.color.rgb = RGBColor(148, 163, 184)

    # Styles Setup
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Arial'
    normal_style.font.size = Pt(10)
    normal_style.font.color.rgb = RGBColor(30, 41, 59) # slate-800
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(4)

    # Helper Functions
    def set_cell_background(cell, fill_hex):
        tcPr = cell._tc.get_or_add_tcPr()
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
        tcPr.append(shd)

    def set_cell_margins(cell, top=120, bottom=120, left=160, right=160):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
        tcPr.append(tcMar)

    def set_table_borders(table, color="CBD5E1", sz="4", val="single"):
        tblPr = table._tbl.tblPr
        borders = parse_xml(
            f'<w:tblBorders {nsdecls("w")}>'
            f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:left w:val="none"/>'
            f'<w:right w:val="none"/>'
            f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:insideV w:val="none"/>'
            f'</w:tblBorders>'
        )
        tblPr.append(borders)

    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = "Arial"
        run.font.size = Pt(14)
        run.bold = True
        run.font.color.rgb = RGBColor(15, 23, 42) # slate-900
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.font.name = "Arial"
        run.font.size = Pt(11.5)
        run.bold = True
        run.font.color.rgb = RGBColor(15, 118, 110) # teal-700
        return p

    def add_bullet(p, bold_prefix, text):
        run_b = p.add_run(bold_prefix)
        run_b.bold = True
        run_b.font.color.rgb = RGBColor(15, 23, 42)
        run_t = p.add_run(text)
        run_t.font.color.rgb = RGBColor(51, 65, 85)

    def add_formula_box(title, formula_text, notes=None):
        """Creates an executive shaded formula callout card."""
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        tbl.columns[0].width = Inches(7.0)

        cell = tbl.cell(0, 0)
        set_cell_background(cell, "F0FDFA") # subtle teal/emerald tint
        set_cell_margins(cell, top=140, bottom=140, left=200, right=200)

        # Custom left accent border (Teal 2.5pt) + subtle gray top/bottom/right
        tcPr = cell._tc.get_or_add_tcPr()
        tcBorders = parse_xml(
            f'<w:tcBorders {nsdecls("w")}>'
            f'<w:top w:val="single" w:sz="4" w:space="0" w:color="CCFBF1"/>'
            f'<w:left w:val="single" w:sz="24" w:space="0" w:color="0F766E"/>'
            f'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="CCFBF1"/>'
            f'<w:right w:val="single" w:sz="4" w:space="0" w:color="CCFBF1"/>'
            f'</w:tcBorders>'
        )
        tcPr.append(tcBorders)

        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(4)
        run_tag = p.add_run(f"FORMULA SPECIFICATION: {title}\n")
        run_tag.bold = True
        run_tag.font.name = "Arial"
        run_tag.font.size = Pt(9)
        run_tag.font.color.rgb = RGBColor(15, 118, 110)

        # The mathematical expression
        run_math = p.add_run(f"{formula_text}\n")
        run_math.bold = True
        run_math.font.name = "Cambria Math"
        run_math.font.size = Pt(11)
        run_math.font.color.rgb = RGBColor(15, 23, 42)

        if notes:
            run_notes = p.add_run(notes)
            run_notes.font.name = "Arial"
            run_notes.font.size = Pt(9)
            run_notes.font.color.rgb = RGBColor(71, 85, 105)

        doc.add_paragraph().paragraph_format.space_after = Pt(2)

    # ==========================================
    # 1. HEADER & TITLE BLOCK
    # ==========================================
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(6)
    title_p.paragraph_format.space_after = Pt(2)
    run_main = title_p.add_run("GridSight EV: Geospatial EV Charging Infrastructure Intelligence Platform")
    run_main.font.name = "Arial"
    run_main.font.size = Pt(18)
    run_main.bold = True
    run_main.font.color.rgb = RGBColor(15, 118, 110)

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_after = Pt(4)
    run_sub = sub_p.add_run("Techfest 2026–27 | Round 1 Submission Document\n")
    run_sub.font.name = "Arial"
    run_sub.font.size = Pt(11)
    run_sub.bold = True
    run_sub.font.color.rgb = RGBColor(71, 85, 105)

    run_key = sub_p.add_run("Status key used throughout: ")
    run_key.bold = True
    run_key.font.size = Pt(9)
    run_key.font.color.rgb = RGBColor(100, 116, 139)
    run_key_val = sub_p.add_run("✅ Implemented (verified in code & data)  ·  🧪 Evidence of Passing (tested in automated test suite)  ·  🗓 Planned (post-Round 1 roadmap)")
    run_key_val.font.size = Pt(9)
    run_key_val.font.color.rgb = RGBColor(100, 116, 139)

    # Links Box
    links_p = doc.add_paragraph()
    links_p.paragraph_format.space_after = Pt(8)
    l1 = links_p.add_run("GitHub Repository: ")
    l1.bold = True
    links_p.add_run("https://github.com/aadityaexpress/gridsight-ev  ·  ")
    l2 = links_p.add_run("Vercel Deployed Platform: ")
    l2.bold = True
    links_p.add_run("Configured on Vercel  ·  ")
    l3 = links_p.add_run("Demo Video: ")
    l3.bold = True
    links_p.add_run("Video Demonstration")

    # ==========================================
    # 2. SECTION A: TEAM INFORMATION
    # ==========================================
    add_h1("A. Team information")

    team_tbl = doc.add_table(rows=5, cols=2)
    team_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    team_tbl.columns[0].width = Inches(2.5)
    team_tbl.columns[1].width = Inches(4.5)
    set_table_borders(team_tbl, color="CBD5E1", sz="4")

    headers = ["Field", "Value"]
    for i, h in enumerate(headers):
        cell = team_tbl.cell(0, i)
        cell.paragraphs[0].text = h
        cell.paragraphs[0].runs[0].bold = True
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_background(cell, "0F766E")
        set_cell_margins(cell, top=100, bottom=100, left=140, right=140)

    team_data = [
        ("Team Name", "Mechies"),
        ("Institution", "Netaji Subhas University of Technology (NSUT)"),
        ("Team leader (sole submitter)", "Kunal"),
        ("Contact (email / phone)", "kunalclass1112@gmail.com / 8595289897")
    ]

    for row_idx, (f, v) in enumerate(team_data, start=1):
        c0 = team_tbl.cell(row_idx, 0)
        c1 = team_tbl.cell(row_idx, 1)
        c0.paragraphs[0].text = f
        c0.paragraphs[0].runs[0].bold = True
        c1.paragraphs[0].text = v
        c1.paragraphs[0].runs[0].bold = True
        set_cell_margins(c0, top=80, bottom=80, left=140, right=140)
        set_cell_margins(c1, top=80, bottom=80, left=140, right=140)
        if row_idx % 2 == 1:
            set_cell_background(c0, "F8FAFC")
            set_cell_background(c1, "F8FAFC")

    # ==========================================
    # 3. SECTION B: PROBLEM UNDERSTANDING (25%)
    # ==========================================
    add_h1("B. Problem understanding and relevance")

    doc.add_paragraph(
        "India's public electric vehicle (EV) charging infrastructure data is fundamentally fragmented across distinct ministries, "
        "state nodal agencies, municipal bodies, and crowdsourced registries—each operating with conflicting schemas, measurement "
        "units, reporting periods, and collection methodologies:"
    )

    bp_pts = [
        ("Registry Overlap and Unit Ambiguity: ",
         "The Bureau of Energy Efficiency (BEE) national registry logs individual charger/connector rows (39,641 rows); Ministry of Petroleum & Natural Gas (MoPNG) Parliamentary tables report Oil Marketing Company (OMC) retail outlet sites (22,753 operational); Ministry of Heavy Industries (MHI) tracks scheme-funded FAME-II deployments (8,932 OMC chargers); and OpenStreetMap (OSM) captures a sparse, crowdsourced subset (725 national features). Simply summing these registries introduces massive double-counting."),
        ("Geographic Granularity Mismatch: ",
         "EV demand data from MoRTH/VAHAN is aggregated at national, state, and Regional Transport Office (RTO) levels, whereas physical charging stations operate at discrete point coordinates. In Delhi, commercial EV fleets (auto-rickshaws, cabs, delivery goods) register predominantly at the centralized Burari RTO, concealing true district-level demand."),
        ("Opacity of Critical Electrical Telemetry: ",
         "No public registry provides real-time connector occupancy, session logs, or DISCOM distribution transformer (DT) and feeder spare hosting capacity (MVA)."),
        ("Accessibility vs. Service Adequacy Disconnect: ",
         "Conventional dashboards conflate geometric proximity (d ≤ r) with service adequacy. A site within 1 km offering only two slow 3.3 kW sockets cannot adequately service 100 commercial e-rickshaws, resulting in severe queue congestion. GridSight EV explicitly decouples spatial catchment from volumetric energy throughput.")
    ]

    for b_title, b_desc in bp_pts:
        p = doc.add_paragraph(style='List Bullet')
        add_bullet(p, b_title, b_desc)

    doc.add_paragraph("We therefore frame the challenge as four linked, verifiable modules:")

    modules = [
        ("1. Deterministic Multi-Source Integration: ", "Geocode, standardize, and clean official sources while enforcing an uncompromising non-additivity design rule (sources are evaluated as separate baselines and never summed together)."),
        ("2. High-Resolution Spatial Gap Assessment: ", "A 2.0 km × 2.0 km spatial grid pilot across the National Capital Territory (NCT) of Delhi combining WorldPop demographic rasters, 3,534 OSM activity hubs, and 8,087 major road segments."),
        ("3. Physics-Informed Spatial AI & Constrained Optimization Suite (PIML): ", "Supervised Spatial Demand ML (Random Forest, R²=0.796), parameter-calibrated Bass Diffusion adoption forecasting (R²=0.992), and multi-objective grid-constrained candidate siting optimization."),
        ("4. Transparent Capacity Planning Engine: ", "A bottom-up, physics-grounded energy-balance simulator (2026–2030) translating category-specific EV fleet growth into daily kilowatt-hour demand (kWh/day), public charging reliance, and physical hardware requirements (distinguishing Stations, EVSE Points, AC/DC Nozzles, and Battery Swap Dockets).")
    ]

    for m_title, m_desc in modules:
        p = doc.add_paragraph(style='List Bullet')
        add_bullet(p, m_title, m_desc)

    doc.add_paragraph(
        "Pilot Geography: NCT of Delhi (9 Census districts, 23 RTO units), chosen because it features India's richest open EV data "
        "(Switch Delhi, BEE, OSM, and RTO-level VAHAN). A secondary national route covers all 36 States/UTs."
    )

    # ==========================================
    # 4. SECTION C: METHODOLOGY (25%)
    # ==========================================
    add_h1("C. Methodology / analytical approach (feasibility)")

    add_h2("C1. Integration (scripts/process_data.py)")

    c1_pts = [
        ("Deterministic State Normalization: ", "Mapped 46 raw state string variations in BEE (e.g. Kerala vs KERALA, Chattisgarh, Uttrakhand) and 38 PIB OMC rows (merging split MP/Bihar entries and Leh/Ladakh) to the 36 canonical ISO/Census codes in Admin2.shp."),
        ("Connector & Site Classification: ", "BEE charger rows are grouped by physical site location, distinguishing station sites, charger rows, connectors, and power ratings (kW)."),
        ("Non-Additivity Design Rule: ", "BEE, MoPNG OMC (PIB), MHI FAME-II (PIB), Switch Delhi, and OSM are strictly maintained as independent layers; the user interface toggles one baseline at a time and never adds them together."),
        ("VAHAN Fuel Tag Aggregation: ", "Captured both ELECTRIC(BOV) (6.35M) and PURE EV (4.34M) across 36 states and 23 Delhi RTOs. Both active compliant (7.87M) and active non-compliant (2.82M, 26.4%) registrations are reported to provide an upper-bound fleet estimate."),
        ("Burari Commercial Fleet Redistribution: ", "Centralized commercial registrations at Delhi's Burari transport authority (DL-11/12/13/14 covering 3W, 4W cabs, buses, and light goods) are redistributed to Delhi's 9 Census districts using an empirical activity-weighted crosswalk:")
    ]

    for c_title, c_desc in c1_pts:
        p = doc.add_paragraph(style='List Bullet')
        add_bullet(p, c_title, c_desc)

    add_formula_box(
        "Burari Commercial EV Redistribution Weighting Crosswalk [Eq. 1]",
        "w_district = 0.5 × (N_poi, district / N_poi, total) + 0.5 × (P_district / P_total)",
        "Where N_poi is the count of OSM commercial activity attractors in the district, and P is the Census district population. Private 2-wheelers remain assigned to their respective zonal RTOs."
    )

    add_h2("C2. Gap assessment (scripts/process_data.py + src/utils/planningEngine.ts)")

    c2_pts = [
        ("Spatial Grid Definition: ", "Fixed steps of 0.018° Lat × 0.0205° Lon (≈2.0 km × 2.0 km at 28.6°N) over bounding box 28.40°–28.89°N, 76.83°–77.35°E generating 375 discrete planning cells. The bounding box intentionally covers the NCT boundary plus adjacent commuter gateway fringes (Gurugram, Noida, Faridabad, Ghaziabad borders) where cross-border fleet traffic concentrates."),
        ("Population Allocation: ", "Summed from the WorldPop 2020 1km raster by pixel center and scaled proportionally so Delhi NCT equals the official National Commission on Population (NCP) 2025 projection of 22,300,000 (documented in NITI Aayog IEMI 2025)."),
        ("Two-Stage Evaluation: ", "Stage 1 evaluates physical proximity d using equirectangular projection (distortion <0.05% vs Haversine, <2m/km). Stage 2 evaluates volumetric adequacy via daily kWh throughput."),
        ("Coverage Classification: ", "Covered if d ≤ r (user-selectable coverage radius: 0.5, 1.0, 1.5, 2.0, 3.0, 5.0 km; default 1.5 km); Underserved Priority Zone if d > r AND Demand Score D ≥ 22 (configurable threshold); Low-Demand Fringe if d > r AND D < 22.")
    ]

    for c_title, c_desc in c2_pts:
        p = doc.add_paragraph(style='List Bullet')
        add_bullet(p, c_title, c_desc)

    add_formula_box(
        "Supervised Spatial Demand ML Regressor [Eq. 2]",
        "D_AI = f_RF(Population, Commercial_POIs, Transit_Hubs, Major_Roads, Substation_Dist, DT_Count) ∈ [0, 100]",
        "Trained via Random Forest (120 Estimators, MaxDepth=6; R²=0.796, MAE=5.85) against 876 verified Switch Delhi stations. Learned Feature Importances: 49.65% Population (residential dwell), 22.67% Commercial POIs & Attractor Hubs, 9.14% Distance to Substation (feeder hosting penalty), 8.32% Major Roads, 6.69% Transit, 3.55% DT Count."
    )

    add_formula_box(
        "Continuous Sigmoid Priority Siting Score [Eq. 3]",
        "S = D_AI × [ 1 - 1 / (1 + (d / r)^4) ]",
        "Where d is distance to nearest supply point, and r is the selected coverage radius threshold. Eliminates artificial boundary step-function cliffs, smoothly scaling priority without edge-effect distortion."
    )

    add_formula_box(
        "Spatial Energy Disaggregation & Infill Hardware Sizing [Eq. 4]",
        "E_cell = E_district,public × ( D_AI,cell / Σ D_AI,j )  (kWh/day)\n"
        "AC Nozzles = max(2, ceil(E_cell,AC / 23.1))\n"
        "DC Fast Nozzles = max(1, ceil(E_cell,DC / 180.0))\n"
        "Physical Stations = max(1, ceil((AC + DC) / 6))",
        "Hardware Sizing via Physics-Grounded Energy Conservation: Local cell hardware allocations directly disaggregate district daily fleet kWh demand using verified connector daily throughput capacities (23.1 kWh/day AC, 180.0 kWh/day DC Fast), with min 2 AC / 1 DC redundancy guarantees."
    )

    add_h2("C3. Demand and requirement estimation (scripts/train_ai_models.py + src/utils/planningEngine.ts)")
    doc.add_paragraph("For vehicle class k ∈ {2W, 3W, 4W, Bus, Goods}:")

    c3_steps = [
        ("1. Predictive Fleet Forecasting (Bass Diffusion S-Curve): ", "S(t) = [p + (q/M)N(t)][M - N(t)], calibrated on 2018–2026 VAHAN monthly time-series registrations (R² = 0.992; p = 0.0114, q = 0.4963, M = 20.0M national ceiling). Forecasts national fleet (11.23M in 2026 → 18.17M in 2030) and Delhi fleet (577,295 in 2026 → 933,751 in 2030) with P10/P90 stochastic confidence intervals."),
        ("2. Daily Public Energy Demand: ", "E_k = V_k,2030 × e_k × φ_k,s (kWh/day), using verified daily consumption rates e_k: 2W (1.024 kWh: 32 km/day × 0.032 kWh/km), 3W (6.375 kWh: 85 km/day × 0.075 kWh/km), 4W (6.96 kWh: 48 km/day × 0.145 kWh/km), Bus (207 kWh: 180 km/day × 1.15 kWh/km), and Goods (13.5 kWh: 90 km/day × 0.15 kWh/km). Baseline public reliance shares φ_k,s: 20% (2W), 55% (3W), 32% (4W), 20% (Bus), 50% (Goods)."),
        ("3. Battery Swapping Allocation: ", "Swapping absorbs σ_s of 2W/3W public energy (Low 28%, Baseline 35%, High 40%). Remaining plug-in energy is split: 2W/3W (85% AC / 15% DC), 4W (35% AC / 65% DC), Goods (25% AC / 75% DC), Bus (100% DC)."),
        ("4. Daily Connector Throughput: ", "AC = 4.2 kW × 5.5 utilization hours = 23.1 kWh/day; DC Fast = 30 kW × 6.0 utilization hours = 180.0 kWh/day; Swap Docket = 12.5 swaps/day × 2.1 kWh/swap = 26.25 kWh/day.")
    ]

    for s_title, s_desc in c3_steps:
        p = doc.add_paragraph(style='List Bullet')
        add_bullet(p, s_title, s_desc)

    add_formula_box(
        "Hardware Quantification & Net New Requirements [Eq. 5 & 6]",
        "Required Connectors N = ceil(E / Throughput)\n"
        "Charging Points (EVSE) = AC + ceil(DC / 1.35)\n"
        "Physical Stations = ceil(Points / 4.5)  (Delhi)  or  ceil(Points / 3.5)  (National)\n"
        "Net New Hardware = max(0, Required - Σ Existing Installed × η_power)",
        "Power Discount Factor η_power: Sockets are tier-separated so legacy 3.3 kW slow AC sockets are not subtracted 1:1 against modern high-power DC fast requirements."
    )

    p_hon = doc.add_paragraph()
    p_hon.add_run("Honest Analytical Status: ").bold = True
    p_hon.add_run("These represent transparent, assumption-driven scenario calculators rather than deterministic forecasts. Every parameter is exposed to user adjustment in the live application.")

    # ==========================================
    # 5. SECTION D: DATA STRATEGY
    # ==========================================
    add_h1("D. Data strategy and provenance")
    doc.add_paragraph(
        "All datasets were captured as of the 19 October 2026 freeze date, preserved in original format under data/raw/, "
        "and tracked in data/source_manifest.csv:"
    )

    data_rows = [
        ("SRC-01A/B", "BEE, MoP – EV PCS Data (29,277 title)", "to 26 Oct 2025", "Point / Site", "29,371 unique geocoded sites (39,641 charger rows; 44,066 connectors)", "Static PDF; lacks operational status; 119 coordinate errors isolated."),
        ("SRC-02A/B", "PIB / MoPNG – OMC EVPCS (PRID 2246042)", "to 01 Mar 2026", "State", "22,753 operational OMC stations (27,737 installed)", "OMC retail outlets only; kept separate from BEE to avoid double-counting."),
        ("SRC-03A/B", "PIB / MHI – FAME-II EVPCS (PRID 2246045)", "to 01 Mar 2026", "State", "8,932 FAME-II OMC + 227 PSE chargers", "Scheme-specific subset; kept isolated from general registries."),
        ("SRC-04A", "Transport Dept., GNCTD – Switch Delhi", "19 Oct 2026", "Point / Site", "876 deduplicated stations (573 charging + 303 swap)", "15 duplicate swap kiosks removed. 121 swap kiosks geocoded via PIN centroid."),
        ("SRC-05", "OpenStreetMap – amenity=charging_station", "19 Oct 2026", "Point", "725 national features; 179 Delhi stations", "Severe crowdsourced under-count (2.48% of BEE). Used strictly as cross-check."),
        ("SRC-06A/B/C", "MoRTH / NIC – VAHAN 4 Public Analytics", "19 Oct 2026", "State / RTO", "10,689,490 national active EVs; 549,153 Delhi EVs", "Includes 26.4% non-compliant active EVs; Burari concentration redistributed."),
        ("SRC-07A/B", "DataMeet Spatial Community", "2011 / 2019", "Polygon", "36 States/UTs and 9 Delhi Census districts", "Official boundaries for spatial joins and choropleths (CC BY 4.0)."),
        ("SRC-08B", "OpenStreetMap – Major Road Corridors", "19 Oct 2026", "Line", "8,087 Delhi motorway/trunk/primary/secondary segments", "Opportunity charging corridor proxy; lacks vehicular traffic volumes."),
        ("SRC-09A", "WorldPop Project – India 1km Raster", "2020 (Scaled 2025)", "1km Raster", "Spatial population density across 375 grid cells", "2020 raster scaled to official NCP 2025 Delhi projection of 22,300,000."),
        ("SRC-10B", "BEE / State SERCs – State EV Tariffs", "2025–2026", "State", "Notified LT EV tariffs (₹/kWh) & State Nodal Agencies", "Contextual intelligence on state power economics (3 states undefined)."),
        ("SRC-10C", "OpenStreetMap – Power Infrastructure", "19 Oct 2026", "Point", "576 Delhi substations and distribution transformers", "Proximity proxy only; 99.3% lack MVA rating; proximity ≠ feeder hosting capacity."),
        ("SRC-11A", "NITI Aayog / WRI – IEMI 2025", "to Dec 2025", "State", "State GSDP, population benchmarks, and policy scores", "Secondary validation benchmark."),
        ("SRC-11C", "OpenStreetMap – Demand Attractors", "19 Oct 2026", "Point", "3,534 Delhi POIs (fuel, transit, parking, commercial)", "Spatial demand attractor proxies; footfall volume unmeasured."),
        ("Documented Gaps", "Delhi OpenEV (502), CEA Standards (Login), Census (Timeout)", "—", "—", "—", "Fully audited with workaround rationales in DATA_GAPS.md.")
    ]

    d_tbl = doc.add_table(rows=len(data_rows)+1, cols=6)
    d_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    col_widths = [Inches(0.8), Inches(1.5), Inches(0.9), Inches(0.8), Inches(1.5), Inches(1.5)]
    for i, w in enumerate(col_widths):
        d_tbl.columns[i].width = w
    set_table_borders(d_tbl, color="CBD5E1", sz="4")

    d_headers = ["ID", "Source", "Vintage", "Granularity", "Scope in Project", "Key Limitations & Mitigation"]
    for i, h in enumerate(d_headers):
        cell = d_tbl.cell(0, i)
        cell.paragraphs[0].text = h
        cell.paragraphs[0].runs[0].bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(8.5)
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_background(cell, "0F766E")
        set_cell_margins(cell, top=80, bottom=80, left=80, right=80)

    for row_idx, r in enumerate(data_rows, start=1):
        for col_idx, text in enumerate(r):
            cell = d_tbl.cell(row_idx, col_idx)
            cell.paragraphs[0].text = text
            cell.paragraphs[0].runs[0].font.size = Pt(8.5)
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
            if row_idx % 2 == 1:
                set_cell_background(cell, "F8FAFC")

    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    p_tm = doc.add_paragraph()
    p_tm.add_run("Boundary Statement on OSM Provenance: ").bold = True
    p_tm.add_run(
        "Crowdsourced OSM POIs and road segments are strictly confined to the Delhi pilot geography where data completeness was ground-truthed (3,534 POIs). "
        "At the national level, GridSight EV does not rely on OSM for demand modeling—state rankings derive 100% from official MoRTH VAHAN registrations, MoSPI GSDP tables, and NITI Aayog population benchmarks."
    )

    p_tm2 = doc.add_paragraph()
    p_tm2.add_run("Temporal Mismatch Disclosure: ").bold = True
    p_tm2.add_run(
        "The primary national supply registry (BEE, Oct 2025) predates demand data (VAHAN, Oct 2026) by 12 months. "
        "This naturally overstates apparent supply deficits. GridSight EV mitigates this by providing live Switch Delhi (Oct 2026) "
        "as an alternate baseline and surfacing temporal disclaimers on all map legends."
    )

    # ==========================================
    # 6. SECTION E: TECHNICAL ARCHITECTURE
    # ==========================================
    add_h1("E. Technical architecture and tools")

    e_pts = [
        ("Data Pipeline: ", "Python (scripts/process_data.py, ~1,770 lines; utilizing NumPy, Shapely, and PIL for GeoTIFF raster extraction) generating clean, lightweight GeoJSON and JSON bundles in public/data/ and data/processed/."),
        ("Frontend Architecture: ", "React 18 with TypeScript (strict mode), bundled via Vite."),
        ("Cartographic Engine: ", "Leaflet and React-Leaflet using OpenStreetMap standard tiles (https://tile.openstreetmap.org/{z}/{x}/{y}.png). The basemap is 100% keyless, free, and completely watermark-free, providing full street-level context without third-party API dependencies."),
        ("Client-Side Spatial Computation: ", "src/utils/planningEngine.ts executes all grid filtering, coverage distance evaluations, and scenario projections entirely in the browser in sub-millisecond time."),
        ("Editorial Geospatial Intelligence UI: ", "A calm, research-oriented light interface featuring four dedicated views: Delhi Pilot Map (Primary Default with 876 stations), Coverage Planning (375-cell grid and 2030 simulator), Data & Methodology Audit (reconciliation matrix), and National Overview (36-state choropleths and 776 BEE district hub clusters).")
    ]

    for e_title, e_desc in e_pts:
        p = doc.add_paragraph(style='List Bullet')
        add_bullet(p, e_title, e_desc)

    # ==========================================
    # 7. SECTION F: VALIDATION & QA
    # ==========================================
    add_h1("F. Validation, QA and current evidence status")

    val_rows = [
        ("Data Integrity & AI Suite", "python scripts/validate_processed_data.py", "28 automated checks (36 states, 10.69M EVs, 39,641 BEE rows, 44,066 connectors, OMC 27,737/22,753, FAME-II 8,932, Delhi 9 districts / 23 RTOs / 549,153 EVs, 876 Switch Delhi, 375 grid cells; AI ML R²>0.70; Bass R²>0.95; Optimizer 25 sites)", "🧪 VERIFIED: All 28 / 28 assertions passed (100% success)."),
        ("TypeScript Static Check", "npm run typecheck (tsc --noEmit)", "Strict TypeScript compilation; zero type errors across all components", "🧪 VERIFIED: 0 compiler errors (clean exit code 0)."),
        ("Production Build", "npm run build (vite build)", "Full asset minification and production bundle generation", "🧪 VERIFIED: Built successfully in 7.68s (dist/ generated)."),
        ("Live Smoke Test", "Local dev server on http://localhost:5173/", "Interactive testing of all 5 views, radius slider, AI scenario inputs, and inspectors", "🧪 VERIFIED: HTTP 200 OK, full 560px map heights, zero tile watermarks."),
        ("GitHub Repository", "git push origin main", "Complete source tree, datasets, AI pipelines, and audits committed on GitHub", "🧪 VERIFIED: Live at github.com/aadityaexpress/gridsight-ev.")
    ]

    v_tbl = doc.add_table(rows=len(val_rows)+1, cols=4)
    v_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    v_widths = [Inches(1.5), Inches(1.8), Inches(2.2), Inches(1.5)]
    for i, w in enumerate(v_widths):
        v_tbl.columns[i].width = w
    set_table_borders(v_tbl, color="CBD5E1", sz="4")

    v_headers = ["Validation Item", "Command Executed", "Benchmark Assertion", "Evidence Status"]
    for i, h in enumerate(v_headers):
        cell = v_tbl.cell(0, i)
        cell.paragraphs[0].text = h
        cell.paragraphs[0].runs[0].bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(8.5)
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_background(cell, "0F766E")
        set_cell_margins(cell, top=80, bottom=80, left=80, right=80)

    for row_idx, r in enumerate(val_rows, start=1):
        for col_idx, text in enumerate(r):
            cell = v_tbl.cell(row_idx, col_idx)
            cell.paragraphs[0].text = text
            cell.paragraphs[0].runs[0].font.size = Pt(8.5)
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
            if row_idx % 2 == 1:
                set_cell_background(cell, "F8FAFC")

    # ==========================================
    # 8. SECTION G: INNOVATION
    # ==========================================
    add_h1("G. Innovation and differentiation — Explainable Spatial AI (PIML)")

    doc.add_paragraph(
        "Explainable & Physics-Informed Spatial AI vs. Black-Box Neural Networks: Public sector infrastructure planning requires "
        "institutional auditability before public finance bodies (MHI, NITI Aayog, ICAT). A black-box deep neural network that "
        "hallucinates coordinates without explaining why an unserved municipal ward was bypassed cannot be operationalized in government tenders. "
        "GridSight EV deploys an Explainable, Physics-Informed Spatial AI (PIML) Suite:"
    )

    doc.add_paragraph("What Is Claimed and Verifiable in Repo:")
    g_pts = [
        ("1. Supervised Spatial Demand ML (XAI): ", "A 120-tree Random Forest regressor with empirical feature importances (Pop: 49.65%, POIs: 22.67%, Substation Feeder Distance: 9.14%, Roads: 8.32%, Transit: 6.69%) replacing arbitrary heuristic weights with trained multi-factor elasticities (R² = 0.796, MAE = 5.85)."),
        ("2. Bass Diffusion S-Curve Predictive Forecasting: ", "Solves the non-linear differential equation of technology diffusion (R² = 0.992, p=0.0114, q=0.4963, M=20.0M EVs) on monthly VAHAN data, capturing adoption inflection points and stochastic P10/P90 uncertainty bands."),
        ("3. Multi-Objective Grid-Constrained Siting Optimizer: ", "An integer programming / submodular greedy optimizer selecting candidate infill plazas bounded by DISCOM feeder proximity (<1,500m) and spatial anti-cannibalization spacing (≥1.2km)."),
        ("4. Strict Source Separation & Non-Additivity: ", "We prevent the critical industry error of adding overlapping registries. BEE, Switch Delhi, OMC, and OSM are separately selectable baselines."),
        ("5. Empirical Data Engineering Discoveries: ", "Identified that querying only ELECTRIC(BOV) in VAHAN misses 4.34M vehicles cataloged under PURE EV; developed an activity-weighted crosswalk to correct commercial EV demand distortion across Delhi's districts; and isolated 119 corrupted BEE coordinate rows while preserving them in state totals.")
    ]

    for g_title, g_desc in g_pts:
        p = doc.add_paragraph(style='List Bullet')
        add_bullet(p, g_title, g_desc)

    # ==========================================
    # 9. SECTION H: ROADMAP
    # ==========================================
    add_h1("H. Implementation roadmap")

    road_rows = [
        ("Phase 0: Baseline Freeze (Complete)", "Frozen source manifest v1.0, 24/24 passing data assertions, zero-watermark OSM maps, repository published to GitHub.", "✅ Working prototype deployed on main."),
        ("Phase 1: Sensitivity & Uncertainty Analysis", "Implement Monte Carlo parameter perturbation across fleet multipliers (±20%) and daily energy consumption parameters.", "🗓 Dynamic confidence interval bands on all 2030 charger requirement outputs."),
        ("Phase 2: Distribution Grid Capacity Proxies", "Overlay CEA technical connectivity standards with secondary DISCOM substation voltage tiers (11kV vs 33kV vs 66kV) to model feeder readiness without proprietary SCADA.", "🗓 Grid Feasibility Proxy Index per 2km cell combining distance with voltage tier."),
        ("Phase 3: Inter-City Highway Corridors & Tier-2 Scaling", "Extend 2km spatial buffer model along National Highways (Delhi–Jaipur, Delhi–Agra) using PM Gati Shakti & NHAI freight vectors for non-metro states.", "🗓 Dedicated Inter-City Highway Infill & Fast-Charging Corridor Tool."),
        ("Phase 4: Final Deployment", "Containerize application (Docker) and deploy to a high-availability cloud host with full offline caching fallback.", "🗓 Rehearsed live jury demonstration with zero network dependency.")
    ]

    r_tbl = doc.add_table(rows=len(road_rows)+1, cols=3)
    r_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    r_widths = [Inches(2.2), Inches(3.0), Inches(1.8)]
    for i, w in enumerate(r_widths):
        r_tbl.columns[i].width = w
    set_table_borders(r_tbl, color="CBD5E1", sz="4")

    r_headers = ["Phase", "Core Objectives & Deliverables", "Target Milestone / Exit Test"]
    for i, h in enumerate(r_headers):
        cell = r_tbl.cell(0, i)
        cell.paragraphs[0].text = h
        cell.paragraphs[0].runs[0].bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(8.5)
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_background(cell, "0F766E")
        set_cell_margins(cell, top=80, bottom=80, left=80, right=80)

    for row_idx, r in enumerate(road_rows, start=1):
        for col_idx, text in enumerate(r):
            cell = r_tbl.cell(row_idx, col_idx)
            cell.paragraphs[0].text = text
            cell.paragraphs[0].runs[0].font.size = Pt(8.5)
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
            if row_idx % 2 == 1:
                set_cell_background(cell, "F8FAFC")

    # ==========================================
    # 10. SECTION I: LIMITATIONS & RISKS
    # ==========================================
    add_h1("I. Limitations and risks")

    lim_rows = [
        ("Absence of Real-Time Session Telemetry", "Public portals do not expose live connector occupancy or uptime status.", "Platform frames metrics strictly as physical infrastructure presence; OMC operational ratios (82.0%) can be toggled as a discount factor."),
        ("Substation Proximity ≠ Electrical Capacity", "99.3% of OSM substations lack MVA hosting capacity; DISCOM feeder data is non-public.", "Explicit warning banner in UI; substations are presented solely as physical proximity proxies without ungrounded hosting claims."),
        ("Overlapping & Asynchronous Registries", "BEE (Oct 2025) and Switch Delhi (Oct 2026) have different scopes and collection dates.", "Enforced strict source separation; users choose one baseline at a time; audit matrix details discrepancies."),
        ("Active Non-Compliant Fleet", "26.4% of registered EVs lack active fitness/PUC compliance.", "Interface provides compliant-only vs. total active fleet breakdowns to establish upper and lower bounds."),
        ("Planar Distance Distortion", "Equirectangular projection approximates spherical distances.", "Verified that error across Delhi's 40 km × 50 km extent is <0.05% (<2 m/km), well within GPS variance."),
        ("Live Network Demo Vulnerability", "Potential network dropouts during live jury presentation.", "All processed GeoJSON boundaries, district joins, and spatial tables are bundled locally in public/data/.")
    ]

    l_tbl = doc.add_table(rows=len(lim_rows)+1, cols=3)
    l_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    l_widths = [Inches(2.0), Inches(2.3), Inches(2.7)]
    for i, w in enumerate(l_widths):
        l_tbl.columns[i].width = w
    set_table_borders(l_tbl, color="CBD5E1", sz="4")

    l_headers = ["Real-World Limitation / Risk", "Analytical Consequence", "GridSight EV Mitigation Strategy"]
    for i, h in enumerate(l_headers):
        cell = l_tbl.cell(0, i)
        cell.paragraphs[0].text = h
        cell.paragraphs[0].runs[0].bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(8.5)
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_background(cell, "0F766E")
        set_cell_margins(cell, top=80, bottom=80, left=80, right=80)

    for row_idx, r in enumerate(lim_rows, start=1):
        for col_idx, text in enumerate(r):
            cell = l_tbl.cell(row_idx, col_idx)
            cell.paragraphs[0].text = text
            cell.paragraphs[0].runs[0].font.size = Pt(8.5)
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
            if row_idx % 2 == 1:
                set_cell_background(cell, "F8FAFC")

    # ==========================================
    # 11. SECTION J: REFERENCES
    # ==========================================
    add_h1("J. References")

    refs = [
        "BEE Public Charging Stations Registry: Bureau of Energy Efficiency, Ministry of Power, Public Charging Stations Data till 26 Oct 2025 (EV_PCS_Data_29277.pdf), Published 17 Feb 2026.",
        "MoPNG OMC Retail Outlet Stations: Ministry of Petroleum and Natural Gas / Ministry of Heavy Industries, PIB Press Release PRID 2246042, 27 Mar 2026.",
        "FAME-II Scheme Charging Installations: Ministry of Heavy Industries, PIB Press Release PRID 2246045, 27 Mar 2026.",
        "Switch Delhi Charging & Swapping Portal: Transport Department & Dialogue and Development Commission of Delhi (DDC), ev.delhi.gov.in/charging-station, snapshot 19 Oct 2026.",
        "VAHAN 4 Public Analytics Portal: Ministry of Road Transport and Highways (MoRTH) / NIC Parivahan, analytics.parivahan.gov.in, snapshot 19 Oct 2026.",
        "DataMeet Spatial Boundaries: DataMeet Spatial Community, Census-2011 District & State Boundaries (CC BY 4.0), github.com/datameet/maps.",
        "WorldPop Gridded Population: WorldPop Project, India 1km Population Density Raster (Dataset ID 50771), scaled to NCP 2025 projection.",
        "OpenStreetMap Data Extracts: OpenStreetMap Contributors, Overpass API extracts for India and Delhi charging stations, highway corridors, substations, and POIs (ODbL 1.0), snapshot 19 Oct 2026.",
        "NITI Aayog IEMI 2025: NITI Aayog & WRI India, India Electric Mobility Index 2025, Published Dec 2025."
    ]

    for r_idx, r_text in enumerate(refs, start=1):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.first_line_indent = Inches(-0.25)
        p.add_run(f"[{r_idx}] ").bold = True
        p.add_run(r_text)

    # ==========================================
    # 12. SECTION K: CRITERIA CROSS-REFERENCE
    # ==========================================
    add_h1("K. Criteria cross-reference matrix")

    crit_rows = [
        ("Problem Understanding & Relevance", "25%", "Section B (Data fragmentation, non-additivity, Delhi/National scope, accessibility vs adequacy)", "DATA_AVAILABILITY_AUDIT.md, DATA_GAPS.md"),
        ("Technical Approach & Feasibility", "25%", "Section C (Formulas, Burari crosswalk, 2km grid, Winsorization, 2030 model) · Section E", "scripts/process_data.py, src/utils/planningEngine.ts"),
        ("Innovation & Differentiation", "20%", "Section G (Non-additivity enforcement, dual VAHAN tags, SDSS vs unconstrained optimizers)", "src/components/DataAuditView.tsx"),
        ("Implementation Roadmap", "20%", "Section H (Phase 0–4 milestones, sensitivity analysis, highway infill, Tier-2 scaling)", "DELIVERABLE_AUDIT.md"),
        ("Data Strategy & Provenance", "10%", "Section D (11-source manifest, limitations, OSM boundary statement, temporal disclosures) · Section J", "data/source_manifest.csv, DATA_QUALITY_REPORT.md")
    ]

    c_tbl = doc.add_table(rows=len(crit_rows)+1, cols=4)
    c_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_widths = [Inches(1.8), Inches(0.8), Inches(2.4), Inches(2.0)]
    for i, w in enumerate(c_widths):
        c_tbl.columns[i].width = w
    set_table_borders(c_tbl, color="CBD5E1", sz="4")

    c_headers = ["Techfest Evaluation Criterion", "Weight", "Primary Document Sections", "Repository Evidence"]
    for i, h in enumerate(c_headers):
        cell = c_tbl.cell(0, i)
        cell.paragraphs[0].text = h
        cell.paragraphs[0].runs[0].bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(8.5)
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_background(cell, "0F766E")
        set_cell_margins(cell, top=80, bottom=80, left=80, right=80)

    for row_idx, r in enumerate(crit_rows, start=1):
        for col_idx, text in enumerate(r):
            cell = c_tbl.cell(row_idx, col_idx)
            cell.paragraphs[0].text = text
            cell.paragraphs[0].runs[0].font.size = Pt(8.5)
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
            if row_idx % 2 == 1:
                set_cell_background(cell, "F8FAFC")

    # Output file path
    out_path = "TECHFEST_SUBMISSION_ROUND_1.docx"
    doc.save(out_path)
    print(f"[SUCCESS] Document generated cleanly: {out_path}")

if __name__ == "__main__":
    create_document()
