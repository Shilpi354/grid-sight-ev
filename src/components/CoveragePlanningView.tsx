import React, { useMemo, useState } from 'react';
import {
  MapContainer,
  TileLayer,
  GeoJSON,
  Rectangle,
  Tooltip as LeafletTooltip,
} from 'react-leaflet';
import type { FeatureCollection } from 'geojson';
import {
  AlertTriangle,
  Calculator,
  CheckCircle2,
  Compass,
  FileSpreadsheet,
  Info,
  Layers,
  Sliders,
  Target,
  TrendingUp,
  Zap,
} from 'lucide-react';
import type { DelhiPilotBundle, NationalOverviewBundle } from '../types/data';
import {
  computeDelhiDistrictFutureRequirements,
  computeNationalStateFutureRequirements,
  CoverageNetworkBaseline,
  DAILY_VEHICLE_KWH,
  DEFAULT_SCENARIOS,
  EvaluatedGridCell,
  evaluateDelhiGridCoverage,
  GrowthScenarioConfig,
  GrowthScenarioId,
} from '../utils/planningEngine';
import { formatCompactIndian, formatNumber } from '../utils/formatters';

interface CoveragePlanningViewProps {
  delhiBundle: DelhiPilotBundle;
  delhiDistrictsGeoJson: FeatureCollection;
  nationalBundle: NationalOverviewBundle;
}

export const CoveragePlanningView: React.FC<CoveragePlanningViewProps> = ({
  delhiBundle,
  delhiDistrictsGeoJson,
  nationalBundle,
}) => {
  // Coverage Distance Rule State
  const [coverageRadiusKm, setCoverageRadiusKm] = useState<number>(1.5);
  const [networkBaseline, setNetworkBaseline] = useState<CoverageNetworkBaseline>('DC_FAST_ONLY');
  const [minDemandThreshold, setMinDemandThreshold] = useState<number>(22);
  const [selectedCell, setSelectedCell] = useState<EvaluatedGridCell | null>(null);

  // Future Growth Scenario State
  const [scenarioId, setScenarioId] = useState<GrowthScenarioId>('BASELINE');
  const [customConfig, setCustomConfig] = useState<GrowthScenarioConfig>(DEFAULT_SCENARIOS.BASELINE);
  const [supplyBaseline, setSupplyBaseline] = useState<'SWITCH_DELHI' | 'BEE_DELHI'>('BEE_DELHI');
  const [planningScopeTab, setPlanningScopeTab] = useState<'DELHI_DISTRICTS' | 'NATIONAL_STATES'>(
    'DELHI_DISTRICTS'
  );

  const handleSelectScenarioPreset = (id: GrowthScenarioId) => {
    setScenarioId(id);
    setCustomConfig({ ...DEFAULT_SCENARIOS[id] });
  };

  // Evaluate 2km x 2km spatial grid coverage across NCT of Delhi
  const coverageResult = useMemo(() => {
    return evaluateDelhiGridCoverage(
      delhiBundle.grid_cells_2km,
      coverageRadiusKm,
      networkBaseline,
      minDemandThreshold
    );
  }, [delhiBundle.grid_cells_2km, coverageRadiusKm, networkBaseline, minDemandThreshold]);

  const activeCell = selectedCell || coverageResult.topUnderservedCells[0] || coverageResult.evaluatedCells[0];

  // Compute Delhi 9-District Future Requirements
  const delhiRequirements = useMemo(() => {
    return computeDelhiDistrictFutureRequirements(
      delhiBundle.districts_summary,
      customConfig,
      supplyBaseline,
      true
    );
  }, [delhiBundle.districts_summary, customConfig, supplyBaseline]);

  const delhiTotals = useMemo(() => {
    return delhiRequirements.reduce(
      (acc, r) => ({
        currentEvs: acc.currentEvs + r.currentActiveEvs,
        projectedEvs: acc.projectedEvs + r.projectedActiveEvs,
        dailyPlugInKwh: acc.dailyPlugInKwh + r.dailyPublicPlugInKwh,
        dailySwapKwh: acc.dailySwapKwh + r.dailyPublicSwapKwh,
        existingStations: acc.existingStations + r.existingStations,
        existingPoints: acc.existingPoints + r.existingChargingPoints,
        existingAc: acc.existingAc + r.existingAcConnectors,
        existingDc: acc.existingDc + r.existingDcConnectors,
        existingSwap: acc.existingSwap + r.existingSwapDockets,
        reqAc: acc.reqAc + r.requiredTotalAcConnectors,
        reqDc: acc.reqDc + r.requiredTotalDcConnectors,
        reqConnectors: acc.reqConnectors + r.requiredTotalConnectors,
        reqPoints: acc.reqPoints + r.requiredTotalChargingPoints,
        reqStations: acc.reqStations + r.requiredTotalStations,
        reqSwap: acc.reqSwap + r.requiredTotalSwapDockets,
        netNewAc: acc.netNewAc + r.netNewAcConnectors,
        netNewDc: acc.netNewDc + r.netNewDcConnectors,
        netNewConnectors: acc.netNewConnectors + r.netNewConnectors,
        netNewPoints: acc.netNewPoints + r.netNewChargingPoints,
        netNewStations: acc.netNewStations + r.netNewStations,
        netNewSwap: acc.netNewSwap + r.netNewSwapDockets,
        addedKw: acc.addedKw + r.addedInstalledPowerKw,
      }),
      {
        currentEvs: 0,
        projectedEvs: 0,
        dailyPlugInKwh: 0,
        dailySwapKwh: 0,
        existingStations: 0,
        existingPoints: 0,
        existingAc: 0,
        existingDc: 0,
        existingSwap: 0,
        reqAc: 0,
        reqDc: 0,
        reqConnectors: 0,
        reqPoints: 0,
        reqStations: 0,
        reqSwap: 0,
        netNewAc: 0,
        netNewDc: 0,
        netNewConnectors: 0,
        netNewPoints: 0,
        netNewStations: 0,
        netNewSwap: 0,
        addedKw: 0,
      }
    );
  }, [delhiRequirements]);

  // Compute National 36-State Future Requirements
  const nationalRequirements = useMemo(() => {
    return computeNationalStateFutureRequirements(nationalBundle.states, customConfig).sort(
      (a, b) => b.projectedActiveEvs - a.projectedActiveEvs
    );
  }, [nationalBundle.states, customConfig]);

  return (
    <div className="view-container">
      {/* Methodological Transparency Banner */}
      <div className="integrity-banner">
        <div className="integrity-banner-left">
          <Calculator size={18} className="icon-sky" />
          <div>
            <strong>Explainable Coverage &amp; Capacity Planning Module:</strong> Does{' '}
            <strong>not</strong> assume any arbitrary universal EV-to-charger ratio. Instead, spatial coverage
            is evaluated over <strong>{coverageResult.totalCells} grid cells (2.0 km &times; 2.0 km)</strong>{' '}
            using explicit Haversine distance rules, and 2030 charger requirements are derived bottom-up from
            category-specific daily energy demand (<span className="mono">kWh/day</span>), public charging
            reliance %, and connector dispensing capacity—distinguishing{' '}
            <strong>Stations (Sites)</strong>, <strong>Charging Points (EVSE)</strong>,{' '}
            <strong>AC vs. DC Connectors (Nozzles)</strong>, and <strong>Battery Swap Dockets</strong>.
          </div>
        </div>
      </div>

      {/* Top Part: Spatial Coverage Rule & Underserved Grid Analysis */}
      <div className="control-bar">
        <div className="control-group">
          <label className="control-label">
            <Compass size={13} /> Selected Coverage Distance Rule (Radius)
          </label>
          <div className="radius-pills">
            {[0.5, 1.0, 1.5, 2.0, 3.0, 5.0].map((r) => (
              <button
                key={r}
                className={`pill-btn ${coverageRadiusKm === r ? 'pill-active' : ''}`}
                onClick={() => setCoverageRadiusKm(r)}
              >
                {r.toFixed(1)} km {r === 3.0 ? '(Delhi EV Policy)' : ''}
              </button>
            ))}
          </div>
        </div>

        <div className="control-group">
          <label className="control-label">
            <Layers size={13} /> Infrastructure Network Defining Coverage
          </label>
          <select
            className="select-input"
            value={networkBaseline}
            onChange={(e) => setNetworkBaseline(e.target.value as CoverageNetworkBaseline)}
          >
            <option value="DC_FAST_ONLY">
              DC Fast Chargers Only (&ge;15–25 kW in Switch Delhi + BEE)
            </option>
            <option value="SWITCH_DELHI_CHARGING">
              Switch Delhi EV Charging Stations Only (573 geocoded sites)
            </option>
            <option value="BATTERY_SWAPPING">
              Switch Delhi Battery Swapping Stations Only (197 geocoded sites)
            </option>
            <option value="BEE_DELHI">BEE Registry — Delhi Stations Only (1,909 sites)</option>
            <option value="ANY_OFFICIAL">
              Any Official Public Charger (Switch Delhi + BEE Combined)
            </option>
          </select>
        </div>

        <div className="control-group">
          <label className="control-label">
            <Sliders size={13} /> Priority Demand Score Threshold ({minDemandThreshold}/100)
          </label>
          <input
            type="range"
            min={5}
            max={60}
            step={1}
            value={minDemandThreshold}
            onChange={(e) => setMinDemandThreshold(Number(e.target.value))}
            className="range-slider"
          />
        </div>
      </div>

      {/* Coverage Analytical Summary Bar */}
      <div className="key-stats-strip">
        <div className="stat-pill">
          <span className="stat-pill-label">Coverage Catchment (&le;{coverageRadiusKm} km)</span>
          <span className="stat-pill-val mono text-teal">
            {coverageResult.coveredCells} / {coverageResult.totalCells} cells
          </span>
          <span className="stat-pill-detail">
            ({coverageResult.areaCoveredPct}% area • {coverageResult.populationCoveredPct}% pop)
          </span>
        </div>

        <div className="stat-pill">
          <span className="stat-pill-label">Demand Attractors</span>
          <span className="stat-pill-val mono text-sky">
            {coverageResult.poisCoveredPct}%
          </span>
          <span className="stat-pill-detail">
            3,534 POIs within catchment
          </span>
        </div>

        <div className="stat-pill">
          <span className="stat-pill-label">Priority Underserved</span>
          <span className="stat-pill-val mono text-rose">
            {coverageResult.underservedPriorityCells} zones
          </span>
          <span className="stat-pill-detail">
            {formatCompactIndian(coverageResult.populationInUnderservedPriority)} pop in actionable gap
          </span>
        </div>
      </div>

      {/* Split Grid: Left 2km x 2km Spatial Coverage Map + Right Priority Cell Inspector & Ranked List */}
      <div className="split-grid-main">
        <div className="panel map-panel">
          <div className="panel-header">
            <div>
              <h2 className="panel-title">
                <Target size={16} className="icon-amber" /> NCT of Delhi 2.0 km &times; 2.0 km Spatial Coverage
                &amp; Underserved Zone Map
              </h2>
              <p className="panel-subtitle">
                Rule: Cell centroid within <strong>{coverageRadiusKm.toFixed(1)} km</strong> of{' '}
                <strong>{networkBaseline}</strong> • Click any grid cell to inspect siting recommendations
              </p>
            </div>
            <div className="marker-key-inline">
              <span>
                <i className="key-dot" style={{ backgroundColor: '#10b981' }} /> Covered (&le;{coverageRadiusKm}
                km)
              </span>
              <span>
                <i className="key-dot" style={{ backgroundColor: '#ef4444' }} /> Underserved Priority Zone
              </span>
              <span>
                <i className="key-dot" style={{ backgroundColor: '#475569' }} /> Low-Demand Fringe (&gt;
                {coverageRadiusKm}km)
              </span>
            </div>
          </div>

          <div className="map-wrapper-national">
            <MapContainer
              center={[28.635, 77.185]}
              zoom={11}
              minZoom={9}
              maxZoom={15}
              scrollWheelZoom={true}
              style={{ height: '100%', width: '100%' }}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
                maxZoom={19}
              />

              <GeoJSON
                data={delhiDistrictsGeoJson}
                style={{
                  fillColor: 'transparent',
                  weight: 1.0,
                  color: '#94a3b8',
                  fillOpacity: 0,
                }}
              />

              {coverageResult.evaluatedCells.map((cell) => {
                const isSel = activeCell?.cell_id === cell.cell_id;
                let fillColor = '#f8fafc';
                let strokeColor = '#cbd5e1';
                let fillOpacity = 0.25;
                if (cell.isCovered) {
                  fillColor = '#10b981';
                  strokeColor = '#059669';
                  fillOpacity = 0.28;
                } else if (cell.isUnderservedPriority) {
                  fillColor = cell.priorityScore >= 40 ? '#b91c1c' : '#d97706';
                  strokeColor = cell.priorityScore >= 40 ? '#991b1b' : '#b45309';
                  fillOpacity = 0.50;
                }

                return (
                  <Rectangle
                    key={cell.cell_id}
                    bounds={cell.bounds}
                    pathOptions={{
                      color: isSel ? '#0f172a' : strokeColor,
                      weight: isSel ? 2.0 : 0.6,
                      fillColor,
                      fillOpacity,
                    }}
                    eventHandlers={{
                      click: () => setSelectedCell(cell),
                    }}
                  >
                    <LeafletTooltip direction="top">
                      <div style={{ fontFamily: 'Inter, sans-serif', fontSize: '12px' }}>
                        <strong>
                          {cell.cell_id} ({cell.district})
                        </strong>
                        <br />
                        Status:{' '}
                        <b>
                          {cell.isCovered
                            ? 'Covered'
                            : cell.isUnderservedPriority
                            ? 'UNDERSERVED PRIORITY'
                            : 'Uncovered Fringe'}
                        </b>
                        <br />
                        Distance to Selected Network: <b>{cell.selectedDistanceKm.toFixed(2)} km</b>
                        <br />
                        2025 Est. Population: <b>{cell.worldpop_2025_est.toLocaleString('en-IN')}</b>
                        <br />
                        Demand Attractors (POIs): <b>{cell.poi_count}</b> • Demand Score:{' '}
                        <b>{cell.demand_score}/100</b>
                      </div>
                    </LeafletTooltip>
                  </Rectangle>
                );
              })}
            </MapContainer>
          </div>
        </div>

        {/* Right: Selected Grid Cell Siting Recommendation & Top Underserved List */}
        <div className="panel state-inspector-panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">2.0 KM &times; 2.0 KM GRID CELL INSPECTOR</span>
              <h2 className="panel-title-lg">
                {activeCell ? `${activeCell.cell_id} — ${activeCell.district}` : 'Select a Grid Cell'}
              </h2>
            </div>
            {activeCell && (
              <span
                className={`badge ${
                  activeCell.isCovered
                    ? 'badge-teal'
                    : activeCell.isUnderservedPriority
                    ? 'badge-rose'
                    : 'badge-slate'
                }`}
              >
                {activeCell.isCovered
                  ? 'Covered'
                  : activeCell.isUnderservedPriority
                  ? 'Underserved Priority'
                  : 'Low-Demand Fringe'}
              </span>
            )}
          </div>

          {activeCell && (
            <>
              <div className="mini-grid-4">
                <div className="mini-stat-box">
                  <span className="mini-label">Dist. to Network</span>
                  <strong className="mono text-amber">{activeCell.selectedDistanceKm.toFixed(2)} km</strong>
                  <span className="mini-sub">Rule: &le;{coverageRadiusKm.toFixed(1)} km</span>
                </div>
                <div className="mini-stat-box">
                  <span className="mini-label">Est. Cell Pop.</span>
                  <strong className="mono">{formatCompactIndian(activeCell.worldpop_2025_est)}</strong>
                  <span className="mini-sub">WorldPop Scaled</span>
                </div>
                <div className="mini-stat-box">
                  <span className="mini-label">Demand Score</span>
                  <strong className="mono text-sky">{activeCell.demand_score} / 100</strong>
                  <span className="mini-sub">
                    {activeCell.poi_count} POIs • {activeCell.road_segments_count} road ways
                  </span>
                </div>
                <div className="mini-stat-box">
                  <span className="mini-label">Nearest Substation</span>
                  <strong className="mono">{activeCell.nearest_substation_m} m</strong>
                  <span className="mini-sub">Physical distance only</span>
                </div>
              </div>

              <div className="inspector-section">
                <h4 className="sub-heading">Multi-Network Distance Profile for {activeCell.cell_id}</h4>
                <div className="kv-grid">
                  <div>
                    <span className="kv-label">Nearest Switch Delhi Charging:</span>
                    <span className="kv-val mono">{activeCell.dist_switch_charging_km} km</span>
                  </div>
                  <div>
                    <span className="kv-label">Nearest Switch Delhi Swap:</span>
                    <span className="kv-val mono">{activeCell.dist_switch_swap_km} km</span>
                  </div>
                  <div>
                    <span className="kv-label">Nearest BEE Station:</span>
                    <span className="kv-val mono">{activeCell.dist_bee_station_km} km</span>
                  </div>
                  <div>
                    <span className="kv-label">Nearest DC Fast Charger:</span>
                    <span className="kv-val mono">{activeCell.dist_dc_fast_km} km</span>
                  </div>
                </div>
              </div>

              {activeCell.isUnderservedPriority && (
                <div className="fact-section fact-estimate">
                  <div className="fact-section-header">
                    <Zap size={14} className="icon-amber" />
                    <strong>CANDIDATE SITING RECOMMENDATION [Model Output]</strong>
                  </div>
                  <p style={{ fontSize: '12.5px', margin: '4px 0 6px' }}>
                    Priority Score: <strong className="mono">{activeCell.priorityScore}</strong>. Recommended
                    minimum infill deployment to close the {activeCell.selectedDistanceKm.toFixed(2)} km coverage
                    gap:
                  </p>
                  <div className="mini-grid-3">
                    <div className="mini-stat-box">
                      <span className="mini-label">New Stations</span>
                      <strong className="mono text-teal">{activeCell.recommendedStations} site(s)</strong>
                    </div>
                    <div className="mini-stat-box">
                      <span className="mini-label">AC Connectors</span>
                      <strong className="mono">{activeCell.recommendedAcConnectors} nozzles</strong>
                    </div>
                    <div className="mini-stat-box">
                      <span className="mini-label">DC Fast Nozzles</span>
                      <strong className="mono text-sky">{activeCell.recommendedDcConnectors} nozzles</strong>
                    </div>
                  </div>
                </div>
              )}

              <div className="inspector-section">
                <h4 className="sub-heading">
                  Top Ranked Underserved Priority Zones ({coverageResult.topUnderservedCells.length} found)
                </h4>
                <div className="table-scroll" style={{ maxHeight: '215px' }}>
                  <table className="data-table compact-table">
                    <thead>
                      <tr>
                        <th>Cell ID</th>
                        <th>District</th>
                        <th className="num">Dist (km)</th>
                        <th className="num">Pop (2025)</th>
                        <th className="num">POIs</th>
                        <th className="num">Priority</th>
                      </tr>
                    </thead>
                    <tbody>
                      {coverageResult.topUnderservedCells.slice(0, 15).map((c) => (
                        <tr
                          key={c.cell_id}
                          className={activeCell?.cell_id === c.cell_id ? 'tr-selected' : ''}
                          onClick={() => setSelectedCell(c)}
                        >
                          <td className="mono">{c.cell_id}</td>
                          <td>{c.district}</td>
                          <td className="num mono text-amber">{c.selectedDistanceKm.toFixed(2)}</td>
                          <td className="num mono">{formatCompactIndian(c.worldpop_2025_est)}</td>
                          <td className="num mono">{c.poi_count}</td>
                          <td className="num mono">
                            <strong>{c.priorityScore}</strong>
                          </td>
                        </tr>
                      ))}
                      {coverageResult.topUnderservedCells.length === 0 && (
                        <tr>
                          <td colSpan={6} style={{ textAlign: 'center', padding: '16px' }}>
                            All high-demand cells are covered within {coverageRadiusKm.toFixed(1)} km! Reduce
                            the coverage radius or switch to DC Fast Chargers Only to stress-test gaps.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Bottom Part: Configurable 2030 Future EV Growth & Charger Requirements Simulator */}
      <div className="panel">
        <div className="panel-header">
          <div>
            <h2 className="panel-title">
              <TrendingUp size={17} className="icon-teal" /> Configurable 2030 EV Growth Scenarios &amp;
              Future Charger Requirement Model
            </h2>
            <p className="panel-subtitle">
              Transparent energy-balance calculation from VAHAN baseline (19 Oct 2026) to 2030 — explicitly
              separating Stations, Charging Points (EVSE), AC Connectors, DC Fast Connectors, and Swap Dockets
            </p>
          </div>
          <div className="scenario-tabs">
            {(['LOW', 'BASELINE', 'HIGH'] as GrowthScenarioId[]).map((id) => (
              <button
                key={id}
                className={`pill-btn ${scenarioId === id ? 'pill-active' : ''}`}
                onClick={() => handleSelectScenarioPreset(id)}
              >
                {id === 'LOW' && 'Low Scenario (Conservative)'}
                {id === 'BASELINE' && 'Baseline Scenario (Policy)'}
                {id === 'HIGH' && 'High Scenario (Accelerated)'}
              </button>
            ))}
          </div>
        </div>

        {/* Documented Assumptions & Interactive Sliders */}
        <div className="assumptions-box">
          <div className="assumptions-col">
            <h4 className="sub-heading">1. 2026 &rarr; 2030 Fleet Growth Multipliers (Editable)</h4>
            <p className="tiny-note">{customConfig.description}</p>
            <div className="slider-grid">
              <label>
                <span>2W Fleet Multiplier: <b>{customConfig.multiplier2W.toFixed(2)}x</b></span>
                <input
                  type="range"
                  min={1.1}
                  max={4.0}
                  step={0.05}
                  value={customConfig.multiplier2W}
                  onChange={(e) =>
                    setCustomConfig({ ...customConfig, multiplier2W: Number(e.target.value) })
                  }
                />
              </label>
              <label>
                <span>3W Fleet Multiplier: <b>{customConfig.multiplier3W.toFixed(2)}x</b></span>
                <input
                  type="range"
                  min={1.1}
                  max={3.5}
                  step={0.05}
                  value={customConfig.multiplier3W}
                  onChange={(e) =>
                    setCustomConfig({ ...customConfig, multiplier3W: Number(e.target.value) })
                  }
                />
              </label>
              <label>
                <span>4W / LMV Multiplier: <b>{customConfig.multiplier4W.toFixed(2)}x</b></span>
                <input
                  type="range"
                  min={1.2}
                  max={4.5}
                  step={0.05}
                  value={customConfig.multiplier4W}
                  onChange={(e) =>
                    setCustomConfig({ ...customConfig, multiplier4W: Number(e.target.value) })
                  }
                />
              </label>
            </div>
          </div>

          <div className="assumptions-col">
            <h4 className="sub-heading">2. Public Charging Reliance &amp; Swap Share (Editable)</h4>
            <div className="slider-grid">
              <label>
                <span>
                  2W Public Charging Share:{' '}
                  <b>{Math.round(customConfig.publicChargingShare2W * 100)}%</b> (vs Home)
                </span>
                <input
                  type="range"
                  min={0.05}
                  max={0.6}
                  step={0.01}
                  value={customConfig.publicChargingShare2W}
                  onChange={(e) =>
                    setCustomConfig({ ...customConfig, publicChargingShare2W: Number(e.target.value) })
                  }
                />
              </label>
              <label>
                <span>
                  3W Public Charging Share:{' '}
                  <b>{Math.round(customConfig.publicChargingShare3W * 100)}%</b>
                </span>
                <input
                  type="range"
                  min={0.2}
                  max={0.85}
                  step={0.01}
                  value={customConfig.publicChargingShare3W}
                  onChange={(e) =>
                    setCustomConfig({ ...customConfig, publicChargingShare3W: Number(e.target.value) })
                  }
                />
              </label>
              <label>
                <span>
                  4W Public Charging Share:{' '}
                  <b>{Math.round(customConfig.publicChargingShare4W * 100)}%</b>
                </span>
                <input
                  type="range"
                  min={0.1}
                  max={0.75}
                  step={0.01}
                  value={customConfig.publicChargingShare4W}
                  onChange={(e) =>
                    setCustomConfig({ ...customConfig, publicChargingShare4W: Number(e.target.value) })
                  }
                />
              </label>
            </div>
          </div>

          <div className="assumptions-col">
            <h4 className="sub-heading">3. Documented Energy &amp; Dispensing Constants</h4>
            <ul className="compact-assumptions-list">
              <li>
                <span>Daily Vehicle Energy:</span>{' '}
                <strong className="mono">
                  2W: {DAILY_VEHICLE_KWH.ev2W} kWh | 3W: {DAILY_VEHICLE_KWH.ev3W} kWh | 4W:{' '}
                  {DAILY_VEHICLE_KWH.ev4W} kWh | Bus: {DAILY_VEHICLE_KWH.evBus} kWh
                </strong>
              </li>
              <li>
                <span>AC Connector Dispensing:</span>{' '}
                <strong className="mono">
                  4.2 kW avg &times; {customConfig.effectiveHoursPerDayAC}h ={' '}
                  {(4.2 * customConfig.effectiveHoursPerDayAC).toFixed(1)} kWh/day/nozzle
                </strong>
              </li>
              <li>
                <span>DC Fast Nozzle Dispensing:</span>{' '}
                <strong className="mono">
                  30 kW avg &times; {customConfig.effectiveHoursPerDayDC}h ={' '}
                  {(30 * customConfig.effectiveHoursPerDayDC).toFixed(0)} kWh/day/nozzle
                </strong>
              </li>
              <li>
                <span>Existing Supply Baseline (Delhi):</span>{' '}
                <select
                  className="select-input-xs"
                  value={supplyBaseline}
                  onChange={(e) => setSupplyBaseline(e.target.value as 'SWITCH_DELHI' | 'BEE_DELHI')}
                >
                  <option value="BEE_DELHI">Compare vs. BEE Delhi Registry (4,028 connectors)</option>
                  <option value="SWITCH_DELHI">Compare vs. Switch Delhi Portal (6,523 chg points)</option>
                </select>
              </li>
            </ul>
          </div>
        </div>

        {/* Scope Switcher: Delhi 9 Districts vs National 36 States */}
        <div className="planning-scope-bar">
          <div className="scope-buttons">
            <button
              className={`pill-btn ${planningScopeTab === 'DELHI_DISTRICTS' ? 'pill-active' : ''}`}
              onClick={() => setPlanningScopeTab('DELHI_DISTRICTS')}
            >
              NCT of Delhi Pilot — 9 Districts Requirement Matrix
            </button>
            <button
              className={`pill-btn ${planningScopeTab === 'NATIONAL_STATES' ? 'pill-active' : ''}`}
              onClick={() => setPlanningScopeTab('NATIONAL_STATES')}
            >
              National Overview — 36 States/UTs Requirement Matrix
            </button>
          </div>
          <span className="tiny-note">
            <Info size={13} /> All outputs below are <strong>scenario-dependent estimates</strong> conditioned
            on the assumptions above.
          </span>
        </div>

        {planningScopeTab === 'DELHI_DISTRICTS' ? (
          <div className="table-scroll">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Delhi District</th>
                  <th className="num">Oct 2026 EVs</th>
                  <th className="num">2030 Proj. EVs</th>
                  <th className="num">Daily Public kWh</th>
                  <th className="num">Existing Stations (Points)</th>
                  <th className="num">Existing AC / DC Nozzles</th>
                  <th className="num">2030 Req. AC Nozzles (Net New)</th>
                  <th className="num">2030 Req. DC Nozzles (Net New)</th>
                  <th className="num">2030 Req. Points [EVSE] (Net New)</th>
                  <th className="num">2030 Req. Stations (Net New)</th>
                  <th className="num">2030 Req. Swap Dockets</th>
                  <th className="num">Added Grid Load (MW)</th>
                </tr>
              </thead>
              <tbody>
                {delhiRequirements.map((r) => (
                  <tr key={r.geographyName}>
                    <td>
                      <strong>{r.geographyName}</strong>
                    </td>
                    <td className="num mono">{formatNumber(r.currentActiveEvs)}</td>
                    <td className="num mono">
                      <strong>{formatNumber(r.projectedActiveEvs)}</strong>
                    </td>
                    <td className="num mono">{formatNumber(r.dailyPublicPlugInKwh)} kWh</td>
                    <td className="num mono">
                      {formatNumber(r.existingStations)} ({formatNumber(r.existingChargingPoints)})
                    </td>
                    <td className="num mono">
                      {formatNumber(r.existingAcConnectors)} /{' '}
                      <span className="text-sky">{formatNumber(r.existingDcConnectors)}</span>
                    </td>
                    <td className="num mono">
                      {formatNumber(r.requiredTotalAcConnectors)}{' '}
                      <span className="text-teal">(+{formatNumber(r.netNewAcConnectors)})</span>
                    </td>
                    <td className="num mono">
                      {formatNumber(r.requiredTotalDcConnectors)}{' '}
                      <span className="text-sky">(+{formatNumber(r.netNewDcConnectors)})</span>
                    </td>
                    <td className="num mono">
                      {formatNumber(r.requiredTotalChargingPoints)}{' '}
                      <span className="text-amber">(+{formatNumber(r.netNewChargingPoints)})</span>
                    </td>
                    <td className="num mono">
                      <strong>{formatNumber(r.requiredTotalStations)}</strong> (+
                      {formatNumber(r.netNewStations)})
                    </td>
                    <td className="num mono">{formatNumber(r.requiredTotalSwapDockets)}</td>
                    <td className="num mono">{(r.addedInstalledPowerKw / 1000).toFixed(1)} MW</td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr className="tfoot-total">
                  <td>
                    <strong>NCT of Delhi Total</strong>
                  </td>
                  <td className="num mono">{formatNumber(delhiTotals.currentEvs)}</td>
                  <td className="num mono">{formatNumber(delhiTotals.projectedEvs)}</td>
                  <td className="num mono">{formatNumber(delhiTotals.dailyPlugInKwh)} kWh</td>
                  <td className="num mono">
                    {formatNumber(delhiTotals.existingStations)} ({formatNumber(delhiTotals.existingPoints)})
                  </td>
                  <td className="num mono">
                    {formatNumber(delhiTotals.existingAc)} / {formatNumber(delhiTotals.existingDc)}
                  </td>
                  <td className="num mono">
                    {formatNumber(delhiTotals.reqAc)} (+{formatNumber(delhiTotals.netNewAc)})
                  </td>
                  <td className="num mono">
                    {formatNumber(delhiTotals.reqDc)} (+{formatNumber(delhiTotals.netNewDc)})
                  </td>
                  <td className="num mono">
                    {formatNumber(delhiTotals.reqPoints)} (+{formatNumber(delhiTotals.netNewPoints)})
                  </td>
                  <td className="num mono">
                    {formatNumber(delhiTotals.reqStations)} (+{formatNumber(delhiTotals.netNewStations)})
                  </td>
                  <td className="num mono">{formatNumber(delhiTotals.reqSwap)}</td>
                  <td className="num mono">{(delhiTotals.addedKw / 1000).toFixed(1)} MW</td>
                </tr>
              </tfoot>
            </table>
          </div>
        ) : (
          <div className="table-scroll" style={{ maxHeight: '420px' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>State / UT</th>
                  <th className="num">Oct 2026 EVs</th>
                  <th className="num">2030 Proj. EVs</th>
                  <th className="num">Daily Public kWh</th>
                  <th className="num">BEE Existing Sites (Connectors)</th>
                  <th className="num">2030 Req. AC Nozzles (Net New)</th>
                  <th className="num">2030 Req. DC Nozzles (Net New)</th>
                  <th className="num">2030 Req. Points [EVSE]</th>
                  <th className="num">2030 Req. Stations (Net New)</th>
                  <th className="num">Added Power (MW)</th>
                </tr>
              </thead>
              <tbody>
                {nationalRequirements.map((r) => (
                  <tr key={r.geographyName}>
                    <td>
                      <strong>{r.geographyName}</strong>
                    </td>
                    <td className="num mono">{formatNumber(r.currentActiveEvs)}</td>
                    <td className="num mono">
                      <strong>{formatNumber(r.projectedActiveEvs)}</strong>
                    </td>
                    <td className="num mono">{formatNumber(r.dailyPublicPlugInKwh)} kWh</td>
                    <td className="num mono">
                      {formatNumber(r.existingStations)} (
                      {formatNumber(r.existingAcConnectors + r.existingDcConnectors)})
                    </td>
                    <td className="num mono">
                      {formatNumber(r.requiredTotalAcConnectors)}{' '}
                      <span className="text-teal">(+{formatNumber(r.netNewAcConnectors)})</span>
                    </td>
                    <td className="num mono">
                      {formatNumber(r.requiredTotalDcConnectors)}{' '}
                      <span className="text-sky">(+{formatNumber(r.netNewDcConnectors)})</span>
                    </td>
                    <td className="num mono">{formatNumber(r.requiredTotalChargingPoints)}</td>
                    <td className="num mono">
                      <strong>{formatNumber(r.requiredTotalStations)}</strong> (+
                      {formatNumber(r.netNewStations)})
                    </td>
                    <td className="num mono">{(r.addedInstalledPowerKw / 1000).toFixed(1)} MW</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
