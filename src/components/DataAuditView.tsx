import React from 'react';
import {
  AlertTriangle,
  CheckCircle2,
  Database,
  FileCheck2,
  FileText,
  Scale,
  ShieldAlert,
} from 'lucide-react';
import type { DelhiPilotBundle, NationalOverviewBundle } from '../types/data';
import { formatNumber } from '../utils/formatters';

interface DataAuditViewProps {
  nationalBundle: NationalOverviewBundle;
  delhiBundle: DelhiPilotBundle;
}

export const DataAuditView: React.FC<DataAuditViewProps> = ({
  nationalBundle,
  delhiBundle,
}) => {
  const natSrc = nationalBundle.metadata.sources;
  const dlSrc = delhiBundle.metadata.sources;

  return (
    <div className="view-container">
      <div className="integrity-banner">
        <div className="integrity-banner-left">
          <FileCheck2 size={18} className="icon-teal" />
          <div>
            <strong>Data Sources, Quality Audit &amp; Gap Documentation:</strong> Summarises all
            findings from <code>DATA_AVAILABILITY_AUDIT.md</code>, <code>DATA_GAPS.md</code>,{' '}
            <code>DATA_QUALITY_REPORT.md</code>, and <code>data/source_manifest.csv</code>. Original raw files
            are preserved untouched under <code>data/raw/</code>.
          </div>
        </div>
      </div>

      {/* Non-Additivity & Unit Reconciliation Matrix */}
      <div className="panel">
        <div className="panel-header">
          <div>
            <h2 className="panel-title">
              <Scale size={16} className="icon-sky" /> Master Source Reconciliation &amp; Non-Additivity Table
            </h2>
            <p className="panel-subtitle">
              Why BEE, MoPNG OMC, MHI FAME-II, Switch Delhi, and OpenStreetMap counts must never be summed
              together
            </p>
          </div>
        </div>
        <div className="table-scroll">
          <table className="data-table">
            <thead>
              <tr>
                <th>Dataset ID</th>
                <th>Source Organisation</th>
                <th>Reference / Vintage Date</th>
                <th>Geographic Scope</th>
                <th className="num">Reported Stations / Sites</th>
                <th className="num">Charger Rows / EVSE</th>
                <th className="num">Connectors / Nozzles</th>
                <th>Scope &amp; Compatibility Rule</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className="mono">SRC-01 (BEE)</td>
                <td>Bureau of Energy Efficiency (Ministry of Power)</td>
                <td className="mono">26 Oct 2025 (Pub: 17 Feb 2026)</td>
                <td>National (All 36 States/UTs)</td>
                <td className="num mono text-teal">
                  <strong>29,277</strong> (29,371 sites)
                </td>
                <td className="num mono">{formatNumber(natSrc.bee.raw_charger_rows)}</td>
                <td className="num mono">{formatNumber(natSrc.bee.total_connectors)}</td>
                <td>
                  Primary national geocoded registry (Govt + Private CPOs). Lacks operational status flag.
                </td>
              </tr>
              <tr>
                <td className="mono">SRC-02 (PIB OMC)</td>
                <td>MoPNG / MHI (PIB PRID 2246042)</td>
                <td className="mono">01 Mar 2026 (Pub: 27 Mar 2026)</td>
                <td>National (36 States/UTs)</td>
                <td className="num mono text-amber">
                  <strong>22,753 operational</strong> (27,737 inst.)
                </td>
                <td className="num mono">N/A (State table)</td>
                <td className="num mono">N/A</td>
                <td>
                  Covers Oil Marketing Companies (IOCL, BPCL, HPCL) only. Overlaps with 17,297 OMC rows in BEE.
                </td>
              </tr>
              <tr>
                <td className="mono">SRC-03 (PIB FAME-II)</td>
                <td>Ministry of Heavy Industries (PIB PRID 2246045)</td>
                <td className="mono">01 Mar 2026 (Pub: 27 Mar 2026)</td>
                <td>National (36 States/UTs)</td>
                <td className="num mono">
                  <strong>6,645 operational</strong> (9,332 sanct.)
                </td>
                <td className="num mono">8,932 OMC + 227 PSE</td>
                <td className="num mono">N/A</td>
                <td>
                  Scheme-specific subset funded under FAME-II. Overlaps with both OMC and BEE registries.
                </td>
              </tr>
              <tr>
                <td className="mono">SRC-04 (Switch Delhi)</td>
                <td>Transport Dept. / DDC, Govt. of NCT of Delhi</td>
                <td className="mono">19 Oct 2026 (Live Snapshot)</td>
                <td>NCT of Delhi Pilot</td>
                <td className="num mono text-teal">
                  <strong>{dlSrc.switch_delhi.deduplicated_stations}</strong> (891 raw)
                </td>
                <td className="num mono">{formatNumber(dlSrc.switch_delhi.total_charging_points)}</td>
                <td className="num mono">{formatNumber(dlSrc.switch_delhi.total_charging_points)}</td>
                <td>
                  Includes 573 Charging + 318 Battery Swapping stations (15 exact duplicates removed).
                </td>
              </tr>
              <tr>
                <td className="mono">SRC-05 (OSM)</td>
                <td>OpenStreetMap Contributors (Overpass ODbL 1.0)</td>
                <td className="mono">19 Oct 2026</td>
                <td>National (725) &amp; Delhi (179)</td>
                <td className="num mono">
                  <strong>725</strong> (179 in Delhi)
                </td>
                <td className="num mono">N/A (75.7% missing)</td>
                <td className="num mono">N/A (92.0% missing)</td>
                <td>
                  Crowdsourced reference (2.48% of BEE national count). Never used as national completeness
                  claim.
                </td>
              </tr>
              <tr>
                <td className="mono">SRC-06 (VAHAN4)</td>
                <td>MoRTH / NIC Parivahan Public Analytics</td>
                <td className="mono">19 Oct 2026</td>
                <td>36 States/UTs + 23 Delhi RTOs</td>
                <td className="num mono text-sky">
                  <strong>10,689,490 EVs</strong>
                </td>
                <td className="num mono">7,869,058 Compliant</td>
                <td className="num mono">2,820,432 Non-Compl.</td>
                <td>
                  Combines <code>ELECTRIC(BOV)</code> (6.35M) + <code>PURE EV</code> (4.34M). Excludes Strong
                  Hybrids.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Two-Column Audit Breakdown: Quality Checks vs Documented Data Gaps */}
      <div className="charts-grid-2">
        <div className="panel">
          <div className="panel-header">
            <h3 className="panel-title">
              <CheckCircle2 size={16} className="icon-teal" /> Data Validation &amp; Hygiene Transformations
            </h3>
          </div>
          <div className="audit-cards-stack">
            <div className="audit-finding-card">
              <strong>1. BEE Coordinate Validation (39,522 / 39,641 Valid in India Bbox)</strong>
              <p>
                Exactly 2 rows had blank Latitude (Row 25827 UJOY Raigad; Row 35953 HPCL Kannauj), 1 row had
                Excel <code>###########</code> column-width corruption in Longitude (Row 36796 IOCL Mathura),
                104 IOCL rows had <code>Latitude == Longitude</code> copy-paste errors, and 12 rows had digit
                typos outside India’s bounding box. All 119 anomalous rows are retained in state tabular totals
                and filtered from map pins.
              </p>
            </div>
            <div className="audit-finding-card">
              <strong>2. Canonical State &amp; District Spatial Standardization</strong>
              <p>
                Resolved all 46 raw state strings in BEE (e.g., <code>Kerala</code> vs <code>KERALA</code>,{' '}
                <code>Uttrakhand</code>, <code>Chattisgarh</code>) and 38 PIB OMC rows (merging Leh + Ladakh
                and split MP/Bihar rows) to the 36 canonical States/UTs in <code>Admin2.shp</code>. Assigned
                geocoded stations to districts via exact Point-in-Polygon containment rather than brittle free-text
                district matching.
              </p>
            </div>
            <div className="audit-finding-card">
              <strong>3. Switch Delhi Un-Geocoded Battery Swap Kiosks (121 of 318)</strong>
              <p>
                While 100% of Switch Delhi’s 573 EV charging stations have valid coordinates, 121 battery
                swapping stations lacked decimal Lat/Lon in the portal JSON. Using their verified 6-digit Delhi
                PIN codes (<code>110001–110097</code>), they are assigned to their exact Delhi district and
                flagged as <code>PIN_CENTROID_ESTIMATE</code> (excluded from default map pins unless toggled on).
              </p>
            </div>
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <h3 className="panel-title">
              <AlertTriangle size={16} className="icon-amber" /> Documented External Data Gaps &amp; Portal
              Restrictions
            </h3>
          </div>
          <div className="audit-cards-stack">
            <div className="audit-finding-card">
              <strong>Gap G-1: Delhi OpenEV Portal (HTTP 502 Bad Gateway)</strong>
              <p>
                <code>https://ev.delhi.gov.in/openev/</code> returned <code>502 Bad Gateway (nginx)</code>, and
                in <code>ev.delhi.gov.in/charging-station</code>, <code>available == no_of_chargers</code> on
                100% of rows. Live connector occupancy telemetry is therefore unavailable without backend GNCTD
                credentials.
              </p>
            </div>
            <div className="audit-finding-card">
              <strong>Gap G-2: CEA Distribution Portal Login Wall &amp; Utility Feeder MVA Capacity</strong>
              <p>
                <code>https://cea.nic.in/ev-charging-standards/</code> redirects to a login/captcha wall, and
                distribution transformer/feeder spare hosting capacity (MVA) is non-public DISCOM data. We use
                BEE Annexure-A tariffs, CEA 2019 connectivity standards, and 576 OSM substations/transformers
                (with an explicit disclaimer that proximity &ne; electrical capacity).
              </p>
            </div>
            <div className="audit-finding-card">
              <strong>Gap G-3: Census India Timeout &amp; OGD JanParichay Login</strong>
              <p>
                <code>censusindia.gov.in</code> timed out on port 80 and <code>data.gov.in</code> requires
                JanParichay SSO login for bulk exports. Mitigated using NITI Aayog’s IEMI 2025 extracted NCP
                2025 state population &amp; MoSPI GSDP table plus WorldPop’s 1km GeoTIFF raster (CC BY 4.0).
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
