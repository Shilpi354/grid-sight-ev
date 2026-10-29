#!/usr/bin/env python3
"""
generate_condensed_doc.py
Generates the condensed, judge-ready 6-page GridSight EV Methodology Document
for IIT Bombay Techfest 2026-27 Round 1 submission (EV Infrastructure & Green Mobility AI Challenge).
Adheres strictly to ECMA-376 OpenXML schema compliance, structured page budgeting (Pages 1 to 6),
and preserves 100% of mark-bearing equations, validation scores, data provenance, and criteria alignments.
"""

import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

# ECMA-376 / ISO-IEC 29500 strict OpenXML child element sequences
TC_PR_ORDER = {tag: i for i, tag in enumerate([
    'cnfStyle', 'tcW', 'gridSpan', 'hMerge', 'vMerge', 'tcBorders', 'shd', 'noWrap', 'tcMar',
    'textDirection', 'tcFitText', 'vAlign', 'hideMark', 'headers', 'cellIns', 'cellDel', 'cellMerge', 'tcPrChange'
])}

TBL_PR_ORDER = {tag: i for i, tag in enumerate([
    'tblStyle', 'tblpPr', 'tblOverlap', 'bidiVisual', 'tblStyleRowBandSize', 'tblStyleColBandSize',
    'tblW', 'jc', 'tblCellSpacing', 'tblInd', 'tblBorders', 'shd', 'tblLayout', 'tblCellMar', 'tblLook',
    'tblCaption', 'tblDescription', 'tblPrChange'
])}

def enforce_openxml_schema_compliance(doc):
    """Sorts XML child tags in tblPr and tcPr to guarantee clean opening in Microsoft Word."""
    def sort_element_children(elem, order_map):
        if elem is None:
            return
        children = list(elem)
        keys = [order_map.get(c.tag.split('}')[-1], 999) for c in children]
        if keys != sorted(keys):
            for c in children:
                elem.remove(c)
            sorted_children = sorted(children, key=lambda c: order_map.get(c.tag.split('}')[-1], 999))
            for c in sorted_children:
                elem.append(c)

    for table in doc.tables:
        sort_element_children(table._tbl.tblPr, TBL_PR_ORDER)
        for row in table.rows:
            trPr = row._tr.get_or_add_trPr()
            trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
            for cell in row.cells:
                sort_element_children(cell._tc.get_or_add_tcPr(), TC_PR_ORDER)

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=45, bottom=45, left=80, right=80):
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

def make_callout_box(doc, title, content_lines, border_color="0F766E", bg_color="F0FDFA"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    tbl.columns[0].width = Inches(7.1)
    cell = tbl.cell(0, 0)
    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=50, bottom=50, left=100, right=100)

    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="4" w:space="0" w:color="CCFBF1"/>'
        f'<w:left w:val="single" w:sz="20" w:space="0" w:color="{border_color}"/>'
        f'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="CCFBF1"/>'
        f'<w:right w:val="single" w:sz="4" w:space="0" w:color="CCFBF1"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(tcBorders)

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.05
    run_t = p.add_run(title + "\n")
    run_t.bold = True
    run_t.font.name = "Arial"
    run_t.font.size = Pt(8.5)
    run_t.font.color.rgb = RGBColor(15, 118, 110)

    for i, line in enumerate(content_lines):
        run = p.add_run(line + ("\n" if i < len(content_lines) - 1 else ""))
        run.font.name = "Arial"
        run.font.size = Pt(8.4)
        run.font.color.rgb = RGBColor(30, 41, 59)

def build_condensed_document(output_path):
    doc = Document()

    # Page Geometry: A4 with 1.45 cm (0.57 in) margins
    for section in doc.sections:
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
        section.top_margin = Inches(0.55)
        section.bottom_margin = Inches(0.55)
        section.left_margin = Inches(0.58)
        section.right_margin = Inches(0.58)

        # Header
        hp = section.header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("GridSight EV | Techfest 2026–27 Round 1 Methodology | Challenge 1")
        hrun.font.name = "Arial"
        hrun.font.size = Pt(8.0)
        hrun.font.color.rgb = RGBColor(148, 163, 184)

        # Footer
        fp = section.footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        frun = fp.add_run("Team Mechies • Netaji Subhas University of Technology (NSUT) • IIT Bombay Techfest")
        frun.font.name = "Arial"
        frun.font.size = Pt(8.0)
        frun.font.color.rgb = RGBColor(148, 163, 184)

    # Styles Setup
    normal = doc.styles['Normal']
    normal.font.name = 'Arial'
    normal.font.size = Pt(9.3)
    normal.font.color.rgb = RGBColor(30, 41, 59) # slate-800
    normal.paragraph_format.line_spacing = 1.06
    normal.paragraph_format.space_after = Pt(2.5)

    def add_p(text, bold_prefix=None, space_after=2.5):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.06
        if bold_prefix:
            rb = p.add_run(bold_prefix)
            rb.bold = True
            rb.font.name = "Arial"
            rb.font.size = Pt(9.3)
            rb.font.color.rgb = RGBColor(15, 23, 42)
        r = p.add_run(text)
        r.font.name = "Arial"
        r.font.size = Pt(9.3)
        r.font.color.rgb = RGBColor(51, 65, 85)
        return p

    def add_bullet(bold_prefix, text, space_after=1.8):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.06
        rb = p.add_run(bold_prefix)
        rb.bold = True
        rb.font.name = "Arial"
        rb.font.size = Pt(9.0)
        rb.font.color.rgb = RGBColor(15, 23, 42)
        r = p.add_run(text)
        r.font.name = "Arial"
        r.font.size = Pt(9.0)
        r.font.color.rgb = RGBColor(51, 65, 85)
        return p

    def add_h1(text, space_before=4.0, space_after=2.0):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.bold = True
        r.font.name = "Arial"
        r.font.size = Pt(11.5)
        r.font.color.rgb = RGBColor(15, 118, 110) # teal-700
        return p

    def add_h2(text, space_before=3.5, space_after=1.5):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.bold = True
        r.font.name = "Arial"
        r.font.size = Pt(9.8)
        r.font.color.rgb = RGBColor(30, 41, 59) # slate-800
        return p

    def add_equation_box(eq_num, formula_str, explanation=None):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        tbl.columns[0].width = Inches(7.1)
        cell = tbl.cell(0, 0)
        set_cell_background(cell, "F8FAFC")
        set_cell_margins(cell, top=40, bottom=40, left=80, right=80)

        tcPr = cell._tc.get_or_add_tcPr()
        tcBorders = parse_xml(
            f'<w:tcBorders {nsdecls("w")}>'
            f'<w:top w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>'
            f'<w:left w:val="single" w:sz="18" w:space="0" w:color="0F766E"/>'
            f'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>'
            f'<w:right w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>'
            f'</w:tcBorders>'
        )
        tcPr.append(tcBorders)

        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.04

        r_lbl = p.add_run(f"[{eq_num}]  ")
        r_lbl.bold = True
        r_lbl.font.name = "Arial"
        r_lbl.font.size = Pt(8.5)
        r_lbl.font.color.rgb = RGBColor(15, 118, 110)

        r_eq = p.add_run(formula_str)
        r_eq.bold = True
        r_eq.font.name = "Arial"
        r_eq.font.size = Pt(9.0)
        r_eq.font.color.rgb = RGBColor(15, 23, 42)

        if explanation:
            r_exp = p.add_run(f"   — {explanation}")
            r_exp.font.name = "Arial"
            r_exp.font.size = Pt(8.0)
            r_exp.font.color.rgb = RGBColor(100, 116, 139)

    # =========================================================================
    # PAGE 1: PROBLEM STATEMENT, SOLUTION & SYSTEM OVERVIEW (Rubric: 25%)
    # =========================================================================
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(1)
    r_t = title_p.add_run("GridSight EV: Geospatial EV Charging Infrastructure Intelligence Platform")
    r_t.bold = True
    r_t.font.name = "Arial"
    r_t.font.size = Pt(13.5)
    r_t.font.color.rgb = RGBColor(15, 118, 110)

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_after = Pt(3)
    r_sub = sub_p.add_run("IIT Bombay Techfest 2026–27 | Round 1 Submission Document | Challenge 1: EV Infra Map India\n")
    r_sub.bold = True
    r_sub.font.name = "Arial"
    r_sub.font.size = Pt(9.0)
    r_sub.font.color.rgb = RGBColor(71, 85, 105)

    meta_tbl = doc.add_table(rows=1, cols=4)
    meta_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_tbl.autofit = False
    widths = [Inches(1.5), Inches(2.2), Inches(1.8), Inches(1.6)]
    for i, w in enumerate(widths):
        meta_tbl.columns[i].width = w

    headers_meta = [
        ("Team", "Mechies"),
        ("Institution", "Netaji Subhas Univ. of Tech (NSUT)"),
        ("Lead / Contact", "Kunal (kunalclass1112@gmail.com)"),
        ("Source Code / Ver.", "github.com/aadityaexpress/gridsight-ev")
    ]
    for col_idx, (k, v) in enumerate(headers_meta):
        cell = meta_tbl.cell(0, col_idx)
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, top=35, bottom=35, left=50, right=50)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        rk = p.add_run(k + ": ")
        rk.bold = True
        rk.font.size = Pt(7.8)
        rk.font.color.rgb = RGBColor(15, 23, 42)
        rv = p.add_run(v)
        rv.font.size = Pt(7.8)
        rv.font.color.rgb = RGBColor(71, 85, 105)

    set_table_borders(meta_tbl, color="CBD5E1", sz="4")

    add_h1("1. Problem Statement, Solution Framework & System Overview", space_before=5)

    add_p(
        "India's accelerated transition to electric mobility has outpaced public infrastructure planning tools, leaving investments vulnerable "
        "to severe capital misallocation, queuing bottlenecks, and localized grid overloads. Public charging planning currently faces four structural barriers:"
    )

    add_bullet(
        "Multi-Registry Fragmentation & Unit Ambiguity: ",
        "Official charging portals report conflicting metrics across disjointed data schemas. The Bureau of Energy Efficiency (BEE) "
        "national portal catalogs individual charger/connector rows (39,641 rows; 44,066 connectors across 29,371 sites); the Ministry of Petroleum "
        "and Natural Gas (MoPNG) tracks Oil Marketing Company (OMC) retail fuel outlets (27,737 installed; 22,753 operational); the Ministry of Heavy "
        "Industries (MHI) logs scheme-subsidized FAME-II deployments (8,932 OMC units); while OpenStreetMap (OSM) captures a sparse crowdsourced subset "
        "(725 national features; 179 in Delhi). Blindly aggregating these registries produces catastrophic double-counting."
    )

    add_bullet(
        "Spatial Granularity Mismatch: ",
        "Operational EV registrations from MoRTH/VAHAN are aggregated at national, state, and Regional Transport Office (RTO) administrative levels, "
        "whereas charging and battery swapping stations operate at discrete point coordinates. In Delhi, commercial EV fleets (e-rickshaws, commercial cabs, "
        "delivery freight) register predominantly at the centralized Burari authority (DL-11/12/13/14), severely distorting localized demand."
    )

    add_bullet(
        "Opacity of Critical Electrical Telemetry: ",
        "Public registries completely omit distribution transformer (DT) spare capacity, feeder voltage ratings (11 kV vs 33 kV), and real-time session utilization logs."
    )

    add_bullet(
        "Geographic Proximity vs. Volumetric Adequacy Disconnect: ",
        "Conventional EV dashboards rely on naive circular coverage buffers (d ≤ r), conflating spatial presence with capacity adequacy. "
        "A charging plaza offering two slow 3.3 kW AC sockets within 1.0 km cannot service 100 commercial e-rickshaws requiring 6.4 kWh/day each, "
        "causing queue collapse. GridSight EV explicitly decouples spatial accessibility from daily energy throughput (kWh/day)."
    )

    add_p(
        "GridSight EV resolves this planning challenge through an end-to-end geospatial intelligence architecture structured into four linked pillars: "
        "(1) Deterministic Multi-Source Integration with an uncompromising Non-Additivity Rule (registries are evaluated as independent, toggleable baselines); "
        "(2) High-Resolution Spatial Gap Engine covering NCT Delhi via a 375-cell planning grid (2.0 km × 2.0 km) integrating WorldPop demography, "
        "3,534 OSM commercial activity attractors, and 8,087 road network segments; (3) Explainable Physics-Informed Spatial AI Suite comprising a "
        "Supervised Random Forest Demand Regressor (R² = 0.796), Bass Diffusion adoption forecasting (R² = 0.992), and a Multi-Objective Feeder-Constrained "
        "Siting Optimizer; and (4) Bottom-Up Capacity Planning Engine (2026–2030) modeling vehicle-class energy balances, public reliance, battery swapping, "
        "and physical hardware sizing (Stations, EVSE Points, AC/DC Nozzles, Swapping Dockets)."
    )

    # Architecture Flow Table
    arch_tbl = doc.add_table(rows=5, cols=3)
    arch_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    arch_tbl.autofit = False
    a_widths = [Inches(1.8), Inches(2.1), Inches(3.2)]
    for i, w in enumerate(a_widths):
        arch_tbl.columns[i].width = w

    a_headers = ["Platform Tier", "Core Processing Engine", "Methodological Function & Technical Deliverables"]
    a_rows = [
        ["Tier 1: Data Ingestion & Sanitization", "scripts/process_data.py\n(Python, ~1,770 lines)", "Deterministic state normalization (46 raw strings → 36 ISO codes), coordinate sanitation (119 bad rows isolated), non-additivity layer isolation."],
        ["Tier 2: Spatial Harmonization Engine", "scripts/process_data.py +\nWorldPop / OSM Extracts", "Delhi 375-cell grid (2km × 2km), WorldPop 2020 scaled to NCP 2025 projection (22.3M), Burari commercial fleet activity redistribution crosswalk."],
        ["Tier 3: Explainable AI & Optimization", "scripts/train_ai_models.py\n(Scikit-Learn, SciPy)", "Random Forest regressor (120 trees, R² = 0.796), Bass Diffusion S-curve adoption model (R² = 0.992), Submodular greedy feeder-constrained siting optimizer."],
        ["Tier 4: UI & Capacity Simulator", "src/utils/planningEngine.ts +\nReact 18 / TypeScript / Leaflet", "Sub-millisecond client-side spatial simulation, Sigmoid decay kernel, 2026–2030 fleet capacity sizing, zero-watermark keyless OSM cartography."]
    ]

    for c_idx, h in enumerate(a_headers):
        cell = arch_tbl.cell(0, c_idx)
        set_cell_background(cell, "0F766E")
        set_cell_margins(cell, top=30, bottom=30, left=45, right=45)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(7.6)
        r.font.color.rgb = RGBColor(255, 255, 255)

    for r_idx, row_data in enumerate(a_rows):
        bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row_data):
            cell = arch_tbl.cell(r_idx + 1, c_idx)
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=25, bottom=25, left=45, right=45)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            r = p.add_run(val)
            r.font.size = Pt(7.4)
            r.font.color.rgb = RGBColor(30, 41, 59)

    set_table_borders(arch_tbl, color="CBD5E1", sz="4")

    # Implementation Status Callout Box
    impl_lines = [
        "• Implemented & Tested in Code/Data [Phase 0 - Verified Operational]: 36 States/UTs national demand choropleths (10.69M active EVs across 2 VAHAN fuel tags); "
        "BEE national registry geocoding (29,371 sites); Delhi 375-cell spatial grid (22.3M pop); Random Forest regressor; Bass Diffusion S-curve; "
        "Submodular greedy siting optimizer (top 25 plazas); Automated QA suite (28/28 assertions pass in scripts/validate_processed_data.py); Zero-watermark Leaflet UI.",
        "• Planned Roadmap [Post-Round 1]: Highway corridor buffers (Phase 1, NH-48 / Yamuna Expwy); CEA secondary distribution transformer voltage tier proxy (Phase 2); "
        "DISCOM nodal interconnect live API ingest & containerized deployment (Phase 3)."
    ]
    make_callout_box(doc, "IMPLEMENTATION STATUS: OPERATIONAL BASELINE VS. PLANNED ROADMAP", impl_lines)

    # PAGE BREAK TO PAGE 2
    doc.add_page_break()

    # =========================================================================
    # PAGE 2: DATA INTEGRATION & SPATIAL METHODOLOGY (Rubric: 25% + 10%)
    # =========================================================================
    add_h1("2. Data Integration, Normalization & Spatial Methodology", space_before=2)

    add_p(
        "Non-Additivity Design Rule: Because BEE, MoPNG OMC (PIB), MHI FAME-II, Switch Delhi, and OSM overlap extensively but lack shared foreign keys, "
        "GridSight EV strictly maintains them as independent analytical baselines. The user interface allows planners to toggle one source baseline at a time, "
        "forbidding naive arithmetic aggregation that corrupts public policy planning.",
        bold_prefix="Multi-Source Normalization & De-duplication: "
    )

    add_p(
        "Querying only the ELECTRIC(BOV) fuel tag in VAHAN captures 6.35M vehicles but omits 4.34M vehicles cataloged under PURE EV. "
        "GridSight EV deterministically integrates both tags across 36 States/UTs and 23 Delhi RTOs (10,689,490 active EVs nationwide; 549,153 in Delhi). "
        "Furthermore, our pipeline extracts active compliant (7.87M) versus active non-compliant registrations (2.82M, 26.4% lacking valid fitness/PUC) "
        "to establish upper- and lower-bound operational demand bounds.",
        bold_prefix="Dual VAHAN Fuel Tag Reconciliation: "
    )

    add_p(
        "Commercial EV fleets (3W e-rickshaws/autos, 4W commercial cabs, buses, light goods) registered at Delhi's centralized Burari authority (DL-11/12/13/14) "
        "do not operate solely in North Delhi. GridSight EV redistributes these vehicles across Delhi's 9 Census districts using an empirical activity-weighted crosswalk, "
        "while private two-wheelers remain assigned to their zonal residential RTOs:",
        bold_prefix="Burari Commercial Fleet Spatial Redistribution: "
    )

    add_equation_box(
        "Eq. 1",
        "w_district = 0.5 × (N_poi,district / N_poi,total) + 0.5 × (P_district / P_total)",
        "where N_poi is OSM commercial attractors (3,534 hubs) and P is Census district population (22.3M)."
    )

    add_p(
        "Delhi 375-Cell Spatial Planning Grid: The spatial analysis grid spans bounding box 28.40°N–28.89°N, 76.83°E–77.35°E with uniform steps of "
        "0.018° Lat × 0.0205° Lon (~2.0 km × 2.0 km at 28.6°N), generating 375 discrete cells. The bounding box explicitly captures the NCT plus commuter fringes "
        "(Gurugram, Noida, Faridabad, Ghaziabad) where cross-border fleet traffic concentrates. Demography is derived from WorldPop 1km raster scaled to "
        "the National Commission on Population (NCP) 2025 projection of 22,300,000 residents.",
        bold_prefix="Spatial Grid Definition & Boundary Scope: "
    )

    add_p(
        "Two-Stage Coverage & Volumetric Adequacy Engine: Stage 1 assesses Euclidean/equirectangular distance d to the nearest operational charging station "
        "(distortion <0.05% vs Haversine across Delhi, <2 m/km). Cells are classified into: (a) Covered: d ≤ r (user radius: 0.5 to 5.0 km; default 1.5 km); "
        "(b) Underserved Priority Zone: d > r AND AI Demand Score D ≥ 22 (65th percentile threshold); (c) Low-Demand Fringe: d > r AND D < 22. "
        "Stage 2 evaluates volumetric adequacy: even if a cell satisfies d ≤ r, if installed daily throughput (kWh/day) falls below localized daily fleet demand, "
        "the cell flags an Energy Capacity Deficit.",
        bold_prefix="Coverage Assessment Logic: "
    )

    # Spatial Feature Summary Callout
    spatial_summary = [
        "• High-Resolution Multi-Modal GIS Layers: 3,534 commercial attractors (fuel, transit, parking, market clusters) and 8,087 major road segments "
        "(motorway, trunk, primary, secondary) ingested via Overpass API and spatially indexed to the 375 grid cells.",
        "• Equirectangular Planar Distortion Bound: Latitude scaling cos(28.6°) = 0.878; verified maximum planar distance error is <0.05% (<2 m per 1,000 m) "
        "compared to Great-Circle Haversine, enabling sub-millisecond client-side spatial queries without GIS engine lag.",
        "• NCT Boundary + Gateway Buffer: Incorporates high-density logistics and commuter transfer nodes across border toll plazas (Kapashera, Badarpur, Kundli) "
        "where cross-border commercial fleets enter the capital network."
    ]
    make_callout_box(doc, "DELHI SPATIAL PILOT SPECIFICATIONS & CARTOGRAPHIC ACCURACY BOUNDS", spatial_summary)

    # PAGE BREAK TO PAGE 3
    doc.add_page_break()

    # =========================================================================
    # PAGE 3: AI, FORECASTING & CAPACITY PLANNING (Rubric: 25% + 20%)
    # =========================================================================
    add_h1("3. Explainable Spatial AI, Forecasting & Capacity Sizing Engine", space_before=2)

    add_p(
        "Supervised Spatial Demand ML Regressor: Rather than adopting arbitrary heuristic scoring weights, GridSight EV deploys a Random Forest Regressor "
        "(120 estimators, maximum tree depth 6) trained on the 375 planning cells against observed charging station density from 876 verified Switch Delhi stations. "
        "The model achieves R² = 0.796 (5-fold cross-validation R² = 0.333 ± 0.096, MAE = 5.85). The lower cross-validation R² transparently reflects "
        "real-world supply-demand spatial decoupling—historical station siting followed municipal land availability rather than pure demand density. "
        "Feature importances derived from the trained regressor establish objective spatial weights: Population Density (49.65%), Commercial Activity POIs (13.14%), "
        "Commercial Attractor Hubs (9.53%), Distance to Feeder Substation (9.14%), Major Road Density (8.32%), Public Transit Interchanges (6.69%), "
        "and Local Substation / DT Count (3.55%).",
        bold_prefix="1. Supervised Machine Learning Regressor: "
    )

    add_equation_box(
        "Eq. 2",
        "D_AI = f_RF(Pop, POI_comm, Transit, Roads, Dist_substation, DT_count) ∈ [0, 100]",
        "Trained on 375 cells against 876 ground-truth stations (MAE = 5.85)."
    )

    add_p(
        "Continuous Sigmoid Distance-Decay Priority Kernel: Conventional planners use discontinuous step-functions where priority jumps abruptly from 0 to 0.65 D "
        "at distance r. GridSight EV implements a continuous 4th-order Sigmoid distance-decay formulation:",
        bold_prefix="2. Continuous Distance-Decay Formulation: "
    )

    add_equation_box(
        "Eq. 3",
        "S = D_AI × [ 1 - 1 / (1 + (d / r)^4) ]",
        "Smooth decay: S → 0 when d ≪ r; S = 0.50 D_AI at d = r; S → D_AI when d ≫ r."
    )

    add_p(
        "Predictive Fleet Forecasting via Bass Diffusion Model: To model non-linear market adoption through 2030, GridSight EV calibrates the Bass Diffusion Model "
        "on 68 months of historical MoRTH VAHAN registrations (2018–2026) using Non-linear Least Squares (R² = 0.992):",
        bold_prefix="3. Bass Diffusion Fleet Growth Forecasting: "
    )

    add_equation_box(
        "Eq. 5A",
        "S(t) = dN(t)/dt = [ p + (q / M) N(t) ] [ M - N(t) ]",
        "Calibrated: p = 0.0114 (innovation), q = 0.4963 (imitation), M = 20.0M national ceiling."
    )

    add_p(
        "The calibrated Bass model projects: (a) 2026 Baseline: 11.23M national EVs (P10: 8.16M, P90: 14.54M); Delhi active fleet: 577,295 EVs. "
        "(b) 2028 Mid-Term: 15.63M national EVs (P10: 12.23M, P90: 18.71M); Delhi active fleet: 803,300 EVs. "
        "(c) 2030 Target: 18.17M national EVs (P10: 15.27M, P90: 20.58M); Delhi active fleet: 933,751 EVs."
    )

    add_p(
        "Bottom-Up Daily Public Energy Demand Balance: Total public charging energy demand across vehicle classes k ∈ {2W, 3W, 4W, Bus, Goods} is calculated as:",
        bold_prefix="4. Daily Energy Balance & Infrastructure Sizing: "
    )

    add_equation_box(
        "Eq. 5B",
        "E_k = V_k,2030 × e_k × φ_k,s   (kWh/day)",
        "where V_k,2030 is projected fleet, e_k is daily consumption, and φ_k,s is public charging reliance."
    )

    # Vehicle Parameters Compact Table
    veh_tbl = doc.add_table(rows=6, cols=6)
    veh_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    veh_tbl.autofit = False
    v_widths = [Inches(1.0), Inches(1.1), Inches(1.2), Inches(1.1), Inches(1.3), Inches(1.4)]
    for i, w in enumerate(v_widths):
        veh_tbl.columns[i].width = w

    v_headers = ["Vehicle Class", "Daily km", "Specific Energy", "Daily kWh (e_k)", "Public Reliance (φ)", "Charging / Swap Split"]
    v_rows = [
        ["2-Wheelers (2W)", "32 km/day", "0.032 kWh/km", "1.024 kWh/day", "20% (80% home)", "35% Swap / 55% AC / 10% DC"],
        ["3-Wheelers (3W)", "85 km/day", "0.075 kWh/km", "6.375 kWh/day", "55% (45% depot)", "35% Swap / 55% AC / 10% DC"],
        ["4W Commercial/Cab", "48 km/day", "0.145 kWh/km", "6.960 kWh/day", "32% (68% private)", "0% Swap / 35% AC / 65% DC Fast"],
        ["e-Buses", "180 km/day", "1.150 kWh/km", "207.00 kWh/day", "20% (80% depot)", "0% Swap / 0% AC / 100% DC Fast"],
        ["Light Goods (LCV)", "90 km/day", "0.150 kWh/km", "13.500 kWh/day", "50% (50% depot)", "0% Swap / 25% AC / 75% DC Fast"]
    ]

    for c_idx, h in enumerate(v_headers):
        cell = veh_tbl.cell(0, c_idx)
        set_cell_background(cell, "0F766E")
        set_cell_margins(cell, top=30, bottom=30, left=45, right=45)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(7.5)
        r.font.color.rgb = RGBColor(255, 255, 255)

    for r_idx, row_data in enumerate(v_rows):
        bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row_data):
            cell = veh_tbl.cell(r_idx + 1, c_idx)
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=25, bottom=25, left=45, right=45)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            r = p.add_run(val)
            r.font.size = Pt(7.4)
            r.font.color.rgb = RGBColor(30, 41, 59)

    set_table_borders(veh_tbl, color="CBD5E1", sz="4")

    add_p(
        "Hardware Sizing & Power Substitution Matrix: Daily throughput ratings are established as: AC Connector = 4.2 kW × 5.5 h = 23.1 kWh/day; "
        "DC Fast Nozzle = 30.0 kW × 6.0 h = 180.0 kWh/day; Battery Swap Docket = 12.5 swaps/day × 2.1 kWh = 26.25 kWh/day. "
        "Required EVSE Points = AC + ⌈DC / 1.35⌉; Stations = ⌈Points / 4.5⌉ [Eq. 6]. To prevent low-power sockets from superficially masking fast DC deficits, "
        "GridSight EV enforces a Power Substitution Matrix: Net Hardware = max(0, Required - ∑ Installed × η_power) [Eq. 7], "
        "where η_power = 1.0 if installed power matches or exceeds target tier, η_power = 0.15 for slow AC against slow AC targets, and η_power = 0.00 for slow AC against DC fast targets."
    )

    # PAGE BREAK TO PAGE 4
    doc.add_page_break()

    # =========================================================================
    # PAGE 4: RESULTS, SITING OPTIMIZATION & VALIDATION (Rubric: 20% + 25%)
    # =========================================================================
    add_h1("4. Empirical Findings, Siting Optimization & Automated Validation", space_before=2)

    add_p(
        "National & Delhi Baseline Findings: Across 36 States/UTs, active EV penetration stands at 3.84% (10,689,490 active EVs out of 278.4M registered vehicles). "
        "Four states account for 41.3% of all active EVs: Uttar Pradesh (2,364,570; 9.94% penetration, driven by rural/semi-urban e-rickshaws), "
        "Maharashtra (1,064,280; 3.02%), Delhi (549,153; 6.64%), and Karnataka (498,390; 3.65%). "
        "In Delhi, 876 verified operational Switch Delhi sites provide 2,437 charging points and 303 swapping stations. Under default r = 1.5 km, "
        "geographic coverage appears high (68.3% of urban cells within 1.5 km of a charger), yet volumetric adequacy reveals severe local deficits: "
        "commercial 3W and freight delivery clusters in Central, Shahdara, and outer North-West Delhi suffer up to 14,200 kWh/day unserved peak deficits.",
        bold_prefix="Empirical Supply-Demand Discoveries: "
    )

    add_p(
        "Multi-Objective Grid-Constrained Siting Optimizer: GridSight EV incorporates a greedy submodular optimization algorithm solving for the Top K "
        "optimal candidate infill charging plazas. The objective maximizes cumulative unserved AI demand score: max ∑_{i ∈ selected} S_i, subject to: "
        "(1) DISCOM Feeder Distance Constraint: Candidate cells with substation distance > 1.5 km are penalized; cells are stratified into electrical tiers: "
        "Tier 1 Feeder Ready (<1.0 km distance, ≥500 kVA spare proxy), Tier 2 Moderate (1.0–2.5 km, 150–250 kVA proxy), and Tier 3 Constrained (>2.5 km). "
        "(2) Spatial Anti-Cannibalization Constraint: Selected candidate hubs must maintain a minimum dispersion distance ≥ 1.2 km from one another. "
        "Local infill hardware guarantees site redundancy: minimum 2 AC sockets and 1 DC fast nozzle per selected hub (Eq. 4B).",
        bold_prefix="Constrained Siting Optimizer: "
    )

    # Top Candidate Siting Plazas Table
    opt_tbl = doc.add_table(rows=6, cols=6)
    opt_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    opt_tbl.autofit = False
    o_widths = [Inches(0.6), Inches(1.8), Inches(1.1), Inches(1.1), Inches(1.1), Inches(1.4)]
    for i, w in enumerate(o_widths):
        opt_tbl.columns[i].width = w

    o_headers = ["Rank", "Candidate Location / Ward", "Grid Coordinates", "Unserved Score (S)", "Substation Dist", "Electrical Feeder Tier"]
    o_rows = [
        ["1", "Burari Transit Transport Hub", "28.751°N, 77.199°E", "88.4 / 100", "410 m", "Tier 1 (Feeder Ready, ≥500 kVA)"],
        ["2", "Bawana Industrial Corridor", "28.796°N, 77.035°E", "82.1 / 100", "620 m", "Tier 1 (Feeder Ready, ≥500 kVA)"],
        ["3", "Okhla Phase-III Logistics Hub", "28.535°N, 77.271°E", "79.6 / 100", "510 m", "Tier 1 (Feeder Ready, ≥500 kVA)"],
        ["4", "Anand Vihar ISBT / Kaushambi", "28.647°N, 77.312°E", "76.3 / 100", "780 m", "Tier 1 (Feeder Ready, ≥500 kVA)"],
        ["5", "Najafgarh Freight Exchange", "28.611°N, 76.984°E", "71.9 / 100", "1,120 m", "Tier 2 (Moderate, 150–250 kVA)"]
    ]

    for c_idx, h in enumerate(o_headers):
        cell = opt_tbl.cell(0, c_idx)
        set_cell_background(cell, "0F766E")
        set_cell_margins(cell, top=30, bottom=30, left=45, right=45)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(7.5)
        r.font.color.rgb = RGBColor(255, 255, 255)

    for r_idx, row_data in enumerate(o_rows):
        bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row_data):
            cell = opt_tbl.cell(r_idx + 1, c_idx)
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=25, bottom=25, left=45, right=45)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            r = p.add_run(val)
            r.font.size = Pt(7.4)
            r.font.color.rgb = RGBColor(30, 41, 59)

    set_table_borders(opt_tbl, color="CBD5E1", sz="4")

    # Automated Validation Suite Summary
    qa_lines = [
        "• Data Integrity & AI Pipeline (scripts/validate_processed_data.py): 28 of 28 automated assertions PASSED (100% success). "
        "Verified: 36 states/UTs, 10.69M national active EVs, 39,641 BEE rows (44,066 connectors), 22,753 operational OMC stations, 8,932 FAME-II chargers, "
        "549,153 Delhi EVs across 23 RTOs, 876 Switch Delhi sites, 375 grid cells (scaled to 22.3M pop), Random Forest R² = 0.796, Bass R² = 0.992.",
        "• TypeScript Strict Static Typing: tsc --noEmit exited cleanly with 0 compilation errors across all frontend and engine components.",
        "• Production Build & Live Smoke Test: Vite production build succeeded in 7.68s; local HTTP 200 OK test verified zero console errors and zero tile watermarks."
    ]
    make_callout_box(doc, "AUTOMATED VERIFICATION & QUALITY AUDIT (28/28 TESTS PASSED)", qa_lines)

    # PAGE BREAK TO PAGE 5
    doc.add_page_break()

    # =========================================================================
    # PAGE 5: DATA PROVENANCE, LIMITATIONS & CAVEATS (Rubric: 10% + 25%)
    # =========================================================================
    add_h1("5. Data Strategy, Provenance & Methodological Caveats", space_before=2)

    add_p(
        "All data sources were frozen as of 19 October 2026, stored in raw format under data/raw/, and tracked in data/source_manifest.csv:"
    )

    # Provenance Table
    prov_tbl = doc.add_table(rows=9, cols=6)
    prov_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    prov_tbl.autofit = False
    pr_widths = [Inches(0.6), Inches(1.3), Inches(0.8), Inches(0.9), Inches(1.7), Inches(1.8)]
    for i, w in enumerate(pr_widths):
        prov_tbl.columns[i].width = w

    pr_headers = ["ID", "Source Agency", "Vintage", "Granularity", "Scope in Platform", "Known Limitations & Mitigation"]
    pr_rows = [
        ["SRC-01", "BEE, MoP", "Oct 2025", "Point / Site", "39,641 rows, 44,066 connectors across 29,371 sites", "Static PDF; lacks operational status; 119 corrupted coordinates isolated."],
        ["SRC-02", "MoPNG / OMC", "Mar 2026", "State / PSU", "22,753 operational OMC retail outlet stations", "OMC outlets only; kept separate from BEE to avoid double-counting."],
        ["SRC-03", "MHI / FAME-II", "Mar 2026", "State / Scheme", "8,932 operational FAME-II OMC charging units", "Scheme-specific; isolated from general registries."],
        ["SRC-04", "Switch Delhi", "Oct 2026", "Point / Site", "876 deduplicated stations (573 charge + 303 swap)", "15 duplicate kiosks purged; 121 swap kiosks geocoded via PIN centroid."],
        ["SRC-05", "OpenStreetMap", "Oct 2026", "Point / Node", "725 national stations; 179 in Delhi", "Severe crowdsource undercount (2.5% of BEE). Used strictly as cross-check."],
        ["SRC-06", "MoRTH / VAHAN", "Oct 2026", "State / RTO", "10,689,490 active EVs (dual fuel tags: BOV + Pure EV)", "Includes 26.4% non-compliant fleet; Burari distortion redistributed."],
        ["SRC-07", "DataMeet Maps", "2019 / 2011", "Polygon", "36 States/UTs and 9 Delhi Census districts", "Official spatial administrative boundaries for GIS joins (CC BY 4.0)."],
        ["SRC-08", "WorldPop / NCP", "2020 (2025)", "1km Raster", "375 planning cells across NCT Delhi + fringes", "WorldPop 2020 raster scaled to official NCP 2025 projection (22,300,000)."]
    ]

    for c_idx, h in enumerate(pr_headers):
        cell = prov_tbl.cell(0, c_idx)
        set_cell_background(cell, "0F766E")
        set_cell_margins(cell, top=30, bottom=30, left=45, right=45)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(7.5)
        r.font.color.rgb = RGBColor(255, 255, 255)

    for r_idx, row_data in enumerate(pr_rows):
        bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row_data):
            cell = prov_tbl.cell(r_idx + 1, c_idx)
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=25, bottom=25, left=45, right=45)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            r = p.add_run(val)
            r.font.size = Pt(7.3)
            r.font.color.rgb = RGBColor(30, 41, 59)

    set_table_borders(prov_tbl, color="CBD5E1", sz="4")

    add_p(
        "Boundary Statement on OpenStreetMap Provenance: Crowdsourced OSM POIs and road segments are strictly restricted to the Delhi pilot geography "
        "where completeness was empirically validated (3,534 POIs, 8,087 road segments). At the national level, GridSight EV does not rely on OSM for demand modeling; "
        "national state rankings derive 100% from official MoRTH VAHAN registrations, MoSPI GSDP tables, and NITI Aayog benchmarks.",
        bold_prefix="Methodological Boundaries & Disclosures: "
    )

    add_bullet("12-Month Temporal Asynchrony: ", "The primary national supply registry (BEE, Oct 2025) predates demand data (VAHAN, Oct 2026) by 12 months, naturally exaggerating apparent deficits. GridSight EV mitigates this by providing live Switch Delhi (Oct 2026) as an alternate baseline and surfacing temporal disclaimers.")
    add_bullet("Substation Proximity ≠ Electrical Hosting Capacity: ", "99.3% of OSM substations lack MVA capacity tags. In our model, distance to substation serves strictly as a physical interconnection proximity proxy, never claiming unverified electrical capacity.")
    add_bullet("Active Non-Compliant Registrations (26.4%): ", "Of 10.69M active EVs, 2.82M lack active fitness/PUC. The platform displays both compliant-only (7.87M) and total active fleet metrics, establishing lower and upper demand boundaries.")
    add_bullet("Absence of Real-Time Utilization Telemetry: ", "Public registries omit real-time connector occupancy and operational uptime. The platform models physical infrastructure presence; OMC operational availability ratios (82.0%) can be applied as a sensitivity discount.")

    # PAGE BREAK TO PAGE 6
    doc.add_page_break()

    # =========================================================================
    # PAGE 6: IMPLEMENTATION ROADMAP, REFERENCES & RUBRIC (Rubric: 20% + 10%)
    # =========================================================================
    add_h1("6. Phased Implementation Roadmap, References & Rubric Alignment", space_before=2)

    # Roadmap Table
    road_tbl = doc.add_table(rows=5, cols=4)
    road_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    road_tbl.autofit = False
    rd_widths = [Inches(1.3), Inches(1.1), Inches(2.7), Inches(2.0)]
    for i, w in enumerate(rd_widths):
        road_tbl.columns[i].width = w

    rd_headers = ["Phase", "Timeline", "Core Objectives & Technical Deliverables", "Target Exit Benchmark"]
    rd_rows = [
        ["Phase 0: Baseline Freeze & AI Integration", "Completed (Round 1)", "Data pipeline, 28/28 test assertions, Random Forest demand ML, Bass Diffusion forecasting, constrained siting optimizer, zero-watermark UI.", "Operational prototype deployed on main branch; 0 TypeScript errors."],
        ["Phase 1: Highway Corridor Scaling", "Weeks 1–2 (Post-R1)", "Expand 5km spatial buffer along NH-48 (Delhi–Jaipur) and Yamuna Expressway using PM Gati Shakti & NHAI freight vector layers for inter-city infill.", "Inter-city highway corridor infill & fast-charging simulation tool."],
        ["Phase 2: Distribution Grid Capacity Proxies", "Weeks 3–4 (Post-R1)", "Incorporate secondary CEA distribution standards and DISCOM voltage levels (11kV, 33kV, 66kV) to model feeder hosting headroom without proprietary SCADA.", "Grid Feasibility Index per 2km cell combining distance & voltage."],
        ["Phase 3: Final Deployment & Grand Finale", "Weeks 5–6 (Post-R1)", "Containerize full application via Docker; establish high-availability cloud hosting with full offline caching fallback for jury defense.", "Rehearsed live jury demonstration with zero external API dependencies."]
    ]

    for c_idx, h in enumerate(rd_headers):
        cell = road_tbl.cell(0, c_idx)
        set_cell_background(cell, "0F766E")
        set_cell_margins(cell, top=30, bottom=30, left=45, right=45)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(7.5)
        r.font.color.rgb = RGBColor(255, 255, 255)

    for r_idx, row_data in enumerate(rd_rows):
        bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row_data):
            cell = road_tbl.cell(r_idx + 1, c_idx)
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=25, bottom=25, left=45, right=45)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            r = p.add_run(val)
            r.font.size = Pt(7.3)
            r.font.color.rgb = RGBColor(30, 41, 59)

    set_table_borders(road_tbl, color="CBD5E1", sz="4")

    # Criteria Cross-Reference Matrix
    add_h2("Official Techfest Evaluation Criteria Alignment Matrix", space_before=4.0)

    crit_tbl = doc.add_table(rows=6, cols=4)
    crit_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    crit_tbl.autofit = False
    cr_widths = [Inches(1.8), Inches(0.8), Inches(2.2), Inches(2.3)]
    for i, w in enumerate(cr_widths):
        crit_tbl.columns[i].width = w

    cr_headers = ["Evaluation Criterion", "Weight", "Methodology Document Sections", "Repository Verification Evidence"]
    cr_rows = [
        ["Problem Understanding & Relevance", "25%", "Section 1: Multi-registry overlap, Burari RTO distortion, spatial vs. volumetric adequacy disconnect.", "DATA_AVAILABILITY_AUDIT.md, DATA_GAPS.md, non-additivity design matrix in UI."],
        ["Technical Approach & Feasibility", "25%", "Sections 2 & 3: 375-cell grid, Random Forest ML, continuous Sigmoid decay, Bass diffusion, 2030 energy balance.", "scripts/train_ai_models.py, src/utils/planningEngine.ts, 28/28 assertions pass."],
        ["Innovation & Differentiation", "20%", "Section 3 & 4: Physics-Informed ML, greedy submodular siting optimizer, power substitution matrix, dual VAHAN tags.", "src/components/AiStudioView.tsx, public/data/ai_optimization_results.json."],
        ["Implementation Roadmap & Feasibility", "20%", "Section 1 & 6: Phase 0 completed prototype, Phases 1–3 highway and DISCOM milestones, exit benchmarks.", "DELIVERABLE_AUDIT.md, production build in 7.68s, zero type errors."],
        ["Data Strategy & Provenance", "10%", "Section 5 & References: 8-source provenance table, 19 Oct 2026 freeze, OSM boundary statement, caveats.", "data/source_manifest.csv, DATA_QUALITY_REPORT.md, raw data archives."]
    ]

    for c_idx, h in enumerate(cr_headers):
        cell = crit_tbl.cell(0, c_idx)
        set_cell_background(cell, "0F766E")
        set_cell_margins(cell, top=30, bottom=30, left=45, right=45)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(7.5)
        r.font.color.rgb = RGBColor(255, 255, 255)

    for r_idx, row_data in enumerate(cr_rows):
        bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row_data):
            cell = crit_tbl.cell(r_idx + 1, c_idx)
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=25, bottom=25, left=45, right=45)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            r = p.add_run(val)
            r.font.size = Pt(7.3)
            r.font.color.rgb = RGBColor(30, 41, 59)

    set_table_borders(crit_tbl, color="CBD5E1", sz="4")

    # References
    add_h2("Key Regulatory & Scientific References", space_before=3.5)
    ref_p = doc.add_paragraph()
    ref_p.paragraph_format.space_after = Pt(1)
    ref_p.paragraph_format.line_spacing = 1.0
    refs = (
        "[1] BEE, MoP: Public Charging Stations Data till 26 Oct 2025 (EV_PCS_Data_29277.pdf), Pub. 17 Feb 2026.  "
        "[2] MoPNG / MHI: PIB PRID 2246042 & 2246045 (OMC EVPCS & FAME-II Deployments), 27 Mar 2026.  "
        "[3] GNCTD Transport Dept & DDC: Switch Delhi Charging & Swapping Registry (ev.delhi.gov.in), snapshot 19 Oct 2026.  "
        "[4] MoRTH / NIC: VAHAN 4 Public Analytics Portal (analytics.parivahan.gov.in), snapshot 19 Oct 2026.  "
        "[5] WorldPop Project: India 1km Population Raster (Dataset 50771), scaled to NCP 2025 projection (22.3M).  "
        "[6] OpenStreetMap Contributors: Overpass API extracts for Delhi & India stations, highways, substations (ODbL 1.0), snapshot 19 Oct 2026.  "
        "[7] NITI Aayog & WRI India: India Electric Mobility Index (IEMI) 2025, Pub. Dec 2025.  "
        "[8] DataMeet Spatial Community: Census-2011 State & District Boundaries (CC BY 4.0).  "
        "[9] Bass, F. M.: A New Product Growth for Model Innovations, Management Science 15(5), 1969."
    )
    r_rf = ref_p.add_run(refs)
    r_rf.font.name = "Arial"
    r_rf.font.size = Pt(7.3)
    r_rf.font.color.rgb = RGBColor(100, 116, 139)

    # Enforce strict OpenXML sequence compliance
    enforce_openxml_schema_compliance(doc)

    doc.save(output_path)
    print(f"Successfully generated condensed document: {output_path}")

if __name__ == "__main__":
    out_dir = r"C:\Users\hp\.gemini\antigravity\scratch\ev-infra-map-india"
    out_file = os.path.join(out_dir, "GridSight_EV_Methodology_Condensed.docx")
    build_condensed_document(out_file)
