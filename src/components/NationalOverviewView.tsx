import React, { useMemo, useState } from 'react';
import { MapContainer, TileLayer, GeoJSON, CircleMarker, Tooltip as LeafletTooltip } from 'react-leaflet';
import type { FeatureCollection, Feature } from 'geojson';
import type { Layer, PathOptions } from 'leaflet';
import {
  Activity,
  AlertTriangle,
  BarChart3,
  BatteryCharging,
  CheckCircle2,
  Database,
  Filter,
  Info,
  Layers,
  MapPin,
  Navigation,
  ShieldAlert,
  Zap,
} from 'lucide-react';
import type { NationalOverviewBundle, NationalStateRecord } from '../types/data';
import {
  formatCompactIndian,
  formatNumber,
  getChoroplethColor,
  PALETTE_AMBER_RED,
  PALETTE_INDIGO_CYAN,
  PALETTE_TEAL_EMERALD,
} from '../utils/formatters';

interface NationalOverviewViewProps {
  bundle: NationalOverviewBundle;
  indiaGeoJson: FeatureCollection;
  onSelectDelhiPilot: () => void;
}

type VehicleCategoryFilter = 'ALL' | '2W' | '3W' | '4W' | 'BUS' | 'GOODS';
type ChargerSourceFilter = 'BEE' | 'PIB_OMC' | 'PIB_FAME2' | 'OSM';
type ChoroplethMetric =
  | 'EVS_PER_STATION'
  | 'EVS_PER_CONNECTOR'
  | 'ACTIVE_EVS'
  | 'CHARGER_COUNT'
  | 'OMC_OPERATIONAL_PCT'
  | 'TARIFF_LT';

export const NationalOverviewView: React.FC<NationalOverviewViewProps> = ({
  bundle,
  indiaGeoJson,
  onSelectDelhiPilot,
}) => {
  const [vehicleCategory, setVehicleCategory] = useState<VehicleCategoryFilter>('ALL');
  const [chargerSource, setChargerSource] = useState<ChargerSourceFilter>('BEE');
  const [choroplethMetric, setChoroplethMetric] = useState<ChoroplethMetric>('EVS_PER_STATION');
  const [showHubClusters, setShowHubClusters] = useState<boolean>(true);
  const [selectedStateCode, setSelectedStateCode] = useState<string>('DL');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [tableSortBy, setTableSortBy] = useState<'ev' | 'chargers' | 'ratio' | 'omc_pct'>('ev');

  const statesByCode = useMemo(() => {
    const map: Record<string, NationalStateRecord> = {};
    for (const st of bundle.states) {
      map[st.state_code] = st;
    }
    return map;
  }, [bundle.states]);

  const selectedState = statesByCode[selectedStateCode] || bundle.states[0];

  // Category-specific EV getter
  const getCategoryEvCount = (st: NationalStateRecord, cat: VehicleCategoryFilter): number => {
    switch (cat) {
      case '2W':
        return st.ev_2w;
      case '3W':
        return st.ev_3w;
      case '4W':
        return st.ev_4w_lmv_pv;
      case 'BUS':
        return st.ev_bus;
      case 'GOODS':
        return st.ev_goods;
      default:
        return st.total_ev_active;
    }
  };

  // Source-specific station/charger getter (strictly separated, never summed)
  const getSourceChargerCount = (st: NationalStateRecord, src: ChargerSourceFilter): number => {
    switch (src) {
      case 'BEE':
        return st.bee_unique_stations;
      case 'PIB_OMC':
        return st.omc_operational_total;
      case 'PIB_FAME2':
        return st.fame2_omc_installed;
      case 'OSM':
        return st.osm_charging_stations;
    }
  };

  const getMetricValue = (st: NationalStateRecord): number | null => {
    const evCount = getCategoryEvCount(st, vehicleCategory);
    const stationCount = getSourceChargerCount(st, chargerSource);
    switch (choroplethMetric) {
      case 'EVS_PER_STATION':
        return stationCount > 0 ? Number((evCount / stationCount).toFixed(1)) : null;
      case 'EVS_PER_CONNECTOR':
        return st.bee_total_connectors > 0
          ? Number((evCount / st.bee_total_connectors).toFixed(1))
          : null;
      case 'ACTIVE_EVS':
        return evCount;
      case 'CHARGER_COUNT':
        return stationCount;
      case 'OMC_OPERATIONAL_PCT':
        return st.omc_installed_total > 0 ? st.omc_operational_pct : null;
      case 'TARIFF_LT':
        return st.ev_tariff_lt_rs_kwh;
    }
  };

  const getMetricColor = (val: number | null): string => {
    switch (choroplethMetric) {
      case 'EVS_PER_STATION':
        return getChoroplethColor(val, [120, 250, 450, 800, 1500], PALETTE_AMBER_RED);
      case 'EVS_PER_CONNECTOR':
        return getChoroplethColor(val, [80, 180, 320, 600, 1200], PALETTE_AMBER_RED);
      case 'ACTIVE_EVS':
        return getChoroplethColor(val, [15000, 75000, 250000, 500000, 900000], PALETTE_INDIGO_CYAN);
      case 'CHARGER_COUNT':
        return getChoroplethColor(val, [100, 400, 1000, 2000, 3500], PALETTE_TEAL_EMERALD);
      case 'OMC_OPERATIONAL_PCT':
        return getChoroplethColor(
          val,
          [55, 70, 80, 88, 94],
          ['#ef4444', '#f97316', '#f59e0b', '#14b8a6', '#10b981', '#059669']
        );
      case 'TARIFF_LT':
        return getChoroplethColor(val, [4.5, 5.5, 6.5, 7.5, 8.5], PALETTE_AMBER_RED);
    }
  };

  // National aggregate for selected category & source
  const nationalTotals = useMemo(() => {
    let evSum = 0;
    let stationSum = 0;
    for (const st of bundle.states) {
      evSum += getCategoryEvCount(st, vehicleCategory);
      stationSum += getSourceChargerCount(st, chargerSource);
    }
    return {
      evSum,
      stationSum,
      evPerStation: stationSum > 0 ? (evSum / stationSum).toFixed(1) : 'N/A',
      evPerBeeConnector: (evSum / bundle.metadata.sources.bee.total_connectors).toFixed(1),
    };
  }, [bundle, vehicleCategory, chargerSource]);

  const filteredAndSortedStates = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    const list = bundle.states.filter(
      (s) => !q || s.state_name.toLowerCase().includes(q) || s.state_code.toLowerCase().includes(q)
    );
    return list.sort((a, b) => {
      if (tableSortBy === 'ev') {
        return getCategoryEvCount(b, vehicleCategory) - getCategoryEvCount(a, vehicleCategory);
      }
      if (tableSortBy === 'chargers') {
        return getSourceChargerCount(b, chargerSource) - getSourceChargerCount(a, chargerSource);
      }
      if (tableSortBy === 'omc_pct') {
        return b.omc_operational_pct - a.omc_operational_pct;
      }
      const ra = getSourceChargerCount(a, chargerSource) > 0
        ? getCategoryEvCount(a, vehicleCategory) / getSourceChargerCount(a, chargerSource)
        : -1;
      const rb = getSourceChargerCount(b, chargerSource) > 0
        ? getCategoryEvCount(b, vehicleCategory) / getSourceChargerCount(b, chargerSource)
        : -1;
      return rb - ra;
    });
  }, [bundle.states, searchQuery, tableSortBy, vehicleCategory, chargerSource]);

  const top12StatesForChart = useMemo(() => {
    return [...bundle.states]
      .sort((a, b) => getCategoryEvCount(b, vehicleCategory) - getCategoryEvCount(a, vehicleCategory))
      .slice(0, 12);
  }, [bundle.states, vehicleCategory]);

  const styleGeoJsonFeature = (feature?: Feature): PathOptions => {
    const code = feature?.properties?.state_code as string;
    const st = statesByCode[code];
    const isSelected = code === selectedStateCode;
    const val = st ? getMetricValue(st) : null;
    return {
      fillColor: getMetricColor(val),
      weight: isSelected ? 2.2 : 0.8,
      opacity: 1,
      color: isSelected ? '#0f766e' : '#cbd5e1',
      fillOpacity: isSelected ? 0.80 : 0.65,
    };
  };

  const onEachStateFeature = (feature: Feature, layer: Layer) => {
    const code = feature.properties?.state_code as string;
    const st = statesByCode[code];
    if (!st) return;
    const evVal = getCategoryEvCount(st, vehicleCategory);
    const chgVal = getSourceChargerCount(st, chargerSource);
    const ratio = chgVal > 0 ? (evVal / chgVal).toFixed(1) : 'N/A';

    layer.bindTooltip(
      `<div style="font-family: Inter, sans-serif; font-size: 11.5px; line-height: 1.45; color: #0f172a;">
        <strong style="font-size: 12.5px; color: #0f766e;">${st.state_name} (${st.state_code})</strong><br/>
        <span>Active EVs (${vehicleCategory}): <b>${evVal.toLocaleString('en-IN')}</b></span><br/>
        <span>Stations (${chargerSource}): <b>${chgVal.toLocaleString('en-IN')}</b></span><br/>
        <span>BEE Connectors: <b>${st.bee_total_connectors.toLocaleString('en-IN')}</b> (${st.bee_dc_connectors} DC)</span><br/>
        <span>EVs per Station: <b>${ratio}</b></span>
      </div>`,
      { sticky: true, direction: 'top' }
    );

    layer.on({
      click: () => setSelectedStateCode(code),
    });
  };

  const categoryLabels: Record<VehicleCategoryFilter, string> = {
    ALL: 'All Active EVs (10.69M)',
    '2W': '2-Wheelers (6.08M)',
    '3W': '3-Wheelers / e-Rickshaw (3.78M)',
    '4W': '4-Wheelers / LMV (7.40L)',
    BUS: 'Electric Buses (21,530)',
    GOODS: 'Electric Goods (52,521)',
  };

  const sourceMeta: Record<
    ChargerSourceFilter,
    { title: string; date: string; scopeNote: string; badgeColor: string }
  > = {
    BEE: {
      title: 'BEE National EVPCS Registry (Best-Supported Geocoded)',
      date: '26 Oct 2025 (Published 17 Feb 2026)',
      scopeNote:
        '29,277 filename stations (29,371 deduplicated sites; 39,641 charger rows; 44,066 connectors). Static registry; does not include live operational status.',
      badgeColor: 'badge-teal',
    },
    PIB_OMC: {
      title: 'MoPNG / MHI Oil Marketing Companies (OMC Operational)',
      date: '01 Mar 2026 (PIB PRID 2246042)',
      scopeNote:
        '22,753 operational out of 27,737 installed (82.03% operational) across IOCL, BPCL, HPCL. Excludes private CPOs. Do NOT sum with BEE.',
      badgeColor: 'badge-amber',
    },
    PIB_FAME2: {
      title: 'MHI FAME-II Scheme-Funded OMC Chargers',
      date: '01 Mar 2026 (PIB PRID 2246045)',
      scopeNote:
        '8,932 FAME-II OMC chargers installed by state (6,645 operational of 9,332 sanctioned nationally). Subsidized subset of OMC/BEE.',
      badgeColor: 'badge-purple',
    },
    OSM: {
      title: 'OpenStreetMap Crowdsourced (amenity=charging_station)',
      date: '19 Oct 2026 (ODbL 1.0)',
      scopeNote:
        '725 community-mapped features across India (2.48% of BEE count; heavily skewed toward Delhi & Kerala). Supplemental reference only.',
      badgeColor: 'badge-blue',
    },
  };

  return (
    <div className="view-container">
      {/* Top Source & Non-Additivity Banner */}
      <div className="integrity-banner">
        <div className="integrity-banner-left">
          <ShieldAlert size={18} className="icon-amber" />
          <div>
            <strong>Strict Source Separation Active:</strong> Official BEE Registry (
            <span className="mono">29,277</span> stations / <span className="mono">44,066</span> connectors,{' '}
            <em>26 Oct 2025</em>), MoPNG OMC (<span className="mono">22,753</span> operational of{' '}
            <span className="mono">27,737</span> installed, <em>01 Mar 2026</em>), MHI FAME-II (
            <span className="mono">6,645</span> operational of <span className="mono">9,332</span> sanctioned,{' '}
            <em>01 Mar 2026</em>), and OSM (<span className="mono">725</span> features, <em>19 Oct 2026</em>)
            have distinct scopes and reporting dates and are <strong>never summed together</strong>.
          </div>
        </div>
        <button className="btn-pilot-cta" onClick={onSelectDelhiPilot}>
          <Navigation size={15} />
          Explore NCT of Delhi Detailed Pilot &rarr;
        </button>
      </div>

      {/* Integrated National Summary Strip */}
      <div className="key-stats-strip">
        <div className="stat-pill">
          <span className="stat-pill-label">Active EV Fleet ({vehicleCategory})</span>
          <span className="stat-pill-val mono text-teal">
            {formatNumber(nationalTotals.evSum)}
          </span>
          <span className="stat-pill-detail">
            {vehicleCategory === 'ALL'
              ? '10.69M National (VAHAN)'
              : `${((100 * nationalTotals.evSum) / bundle.metadata.sources.vahan.total_active_ev).toFixed(1)}% of total`}
          </span>
        </div>

        <div className="stat-pill">
          <span className="stat-pill-label">BEE Stations</span>
          <span className="stat-pill-val mono text-sky">
            {formatNumber(bundle.metadata.sources.bee.deduplicated_site_count)} sites
          </span>
          <span className="stat-pill-detail">
            {formatNumber(bundle.metadata.sources.bee.total_connectors)} connectors ({formatNumber(bundle.metadata.sources.bee.raw_charger_rows)} rows)
          </span>
        </div>

        <div className="stat-pill">
          <span className="stat-pill-label">OMC Operational</span>
          <span className="stat-pill-val mono text-amber">
            22,753 / 27,737
          </span>
          <span className="stat-pill-detail">
            82.0% operational (PIB MoPNG)
          </span>
        </div>

        <div className="stat-pill">
          <span className="stat-pill-label">National Ratio</span>
          <span className="stat-pill-val mono">
            {nationalTotals.evPerStation} EVs / stn
          </span>
          <span className="stat-pill-detail">
            {nationalTotals.evPerBeeConnector} EVs / BEE nozzle
          </span>
        </div>
      </div>

      {/* Filter & Map Control Bar */}
      <div className="control-bar">
        <div className="control-group">
          <label className="control-label">
            <Filter size={13} /> EV Category (VAHAN)
          </label>
          <select
            className="select-input"
            value={vehicleCategory}
            onChange={(e) => setVehicleCategory(e.target.value as VehicleCategoryFilter)}
          >
            {Object.entries(categoryLabels).map(([k, label]) => (
              <option key={k} value={k}>
                {label}
              </option>
            ))}
          </select>
        </div>

        <div className="control-group">
          <label className="control-label">
            <Database size={13} /> Charger Registry Source (Kept Separate)
          </label>
          <select
            className="select-input"
            value={chargerSource}
            onChange={(e) => setChargerSource(e.target.value as ChargerSourceFilter)}
          >
            <option value="BEE">BEE National Registry (29,371 sites / 44,066 connectors)</option>
            <option value="PIB_OMC">MoPNG OMC Operational Only (22,753 stations)</option>
            <option value="PIB_FAME2">MHI FAME-II OMC Installed (8,932 chargers)</option>
            <option value="OSM">OpenStreetMap Crowdsourced (725 features)</option>
          </select>
        </div>

        <div className="control-group">
          <label className="control-label">
            <Layers size={13} /> State Choropleth Metric
          </label>
          <select
            className="select-input"
            value={choroplethMetric}
            onChange={(e) => setChoroplethMetric(e.target.value as ChoroplethMetric)}
          >
            <option value="EVS_PER_STATION">EVs per Station (Selected Category &amp; Source)</option>
            <option value="EVS_PER_CONNECTOR">EVs per BEE Connector (44,066 Nozzles)</option>
            <option value="ACTIVE_EVS">Total Active EVs (Selected Category)</option>
            <option value="CHARGER_COUNT">Total Stations (Selected Source)</option>
            <option value="OMC_OPERATIONAL_PCT">OMC Operational Commissioning % (PIB)</option>
            <option value="TARIFF_LT">State LT EV Energy Tariff (₹/kWh)</option>
          </select>
        </div>

        <div className="control-group checkbox-group">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={showHubClusters}
              onChange={(e) => setShowHubClusters(e.target.checked)}
            />
            <span>Show BEE District Hub Clusters ({bundle.district_hub_clusters.length} hubs)</span>
          </label>
        </div>
      </div>

      {/* Main Split Grid: Left Interactive India Map + Right State Inspector */}
      <div className="split-grid-main">
        {/* Left: National Interactive Map */}
        <div className="panel map-panel">
          <div className="panel-header">
            <div>
              <h2 className="panel-title">
                <MapPin size={16} className="icon-sky" /> National EV Demand &amp; Charging Coverage Map (36
                States/UTs)
              </h2>
              <p className="panel-subtitle">
                {sourceMeta[chargerSource].title} • Reference: <strong>{sourceMeta[chargerSource].date}</strong>
              </p>
            </div>
            <span className={`badge ${sourceMeta[chargerSource].badgeColor}`}>{chargerSource}</span>
          </div>

          <div className="map-wrapper-national">
            <MapContainer
              center={[22.5, 80.2]}
              zoom={5}
              minZoom={4}
              maxZoom={11}
              scrollWheelZoom={true}
              style={{ height: '100%', width: '100%' }}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors | Boundaries: DataMeet (CC BY 4.0)'
                url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
                maxZoom={19}
              />

              <GeoJSON
                key={`${vehicleCategory}-${chargerSource}-${choroplethMetric}-${selectedStateCode}`}
                data={indiaGeoJson}
                style={styleGeoJsonFeature}
                onEachFeature={onEachStateFeature}
              />

              {showHubClusters &&
                bundle.district_hub_clusters.slice(0, 400).map((hub) => {
                  const radius = Math.max(3.5, Math.min(18, Math.sqrt(hub.unique_stations) * 0.85));
                  const dcShare = hub.total_connectors > 0 ? hub.dc_connectors / hub.total_connectors : 0;
                  const color = dcShare >= 0.35 ? '#0284c7' : '#0f766e';
                  return (
                    <CircleMarker
                      key={hub.id}
                      center={[hub.latitude, hub.longitude]}
                      radius={radius}
                      pathOptions={{
                        color: '#ffffff',
                        weight: 1,
                        fillColor: color,
                        fillOpacity: 0.85,
                      }}
                      eventHandlers={{
                        click: () => setSelectedStateCode(hub.state_code),
                      }}
                    >
                      <LeafletTooltip direction="top">
                        <div style={{ fontFamily: 'Inter, sans-serif', fontSize: '12px' }}>
                          <strong>
                            {hub.district}, {hub.state_name}
                          </strong>
                          <br />
                          BEE Unique Stations: <b>{hub.unique_stations.toLocaleString('en-IN')}</b> (
                          {hub.charger_rows} rows)
                          <br />
                          Connectors: <b>{hub.total_connectors.toLocaleString('en-IN')}</b> ({hub.dc_connectors}{' '}
                          DC / {hub.ac_connectors} AC)
                          <br />
                          Rated Capacity: <b>{hub.total_power_kw.toLocaleString('en-IN')} kW</b>
                          <br />
                          Lead CPO: <b>{hub.top_cpo}</b>
                        </div>
                      </LeafletTooltip>
                    </CircleMarker>
                  );
                })}
            </MapContainer>

            {/* Map Legend Overlay */}
            <div className="map-legend">
              <div className="legend-title">
                {choroplethMetric === 'EVS_PER_STATION' && 'EVs per Station (High = Underserved)'}
                {choroplethMetric === 'EVS_PER_CONNECTOR' && 'EVs per BEE Connector'}
                {choroplethMetric === 'ACTIVE_EVS' && 'Active Registered EVs'}
                {choroplethMetric === 'CHARGER_COUNT' && 'Public Charging Stations'}
                {choroplethMetric === 'OMC_OPERATIONAL_PCT' && 'OMC Operational % (01 Mar 2026)'}
                {choroplethMetric === 'TARIFF_LT' && 'State LT EV Tariff (₹/kWh)'}
              </div>
              <div className="legend-scale">
                {(choroplethMetric === 'EVS_PER_STATION' ||
                  choroplethMetric === 'EVS_PER_CONNECTOR' ||
                  choroplethMetric === 'TARIFF_LT') &&
                  PALETTE_AMBER_RED.map((c, i) => (
                    <span key={i} className="legend-box" style={{ backgroundColor: c }} />
                  ))}
                {choroplethMetric === 'ACTIVE_EVS' &&
                  PALETTE_INDIGO_CYAN.map((c, i) => (
                    <span key={i} className="legend-box" style={{ backgroundColor: c }} />
                  ))}
                {choroplethMetric === 'CHARGER_COUNT' &&
                  PALETTE_TEAL_EMERALD.map((c, i) => (
                    <span key={i} className="legend-box" style={{ backgroundColor: c }} />
                  ))}
                {choroplethMetric === 'OMC_OPERATIONAL_PCT' &&
                  ['#ef4444', '#f97316', '#f59e0b', '#14b8a6', '#10b981', '#059669'].map((c, i) => (
                    <span key={i} className="legend-box" style={{ backgroundColor: c }} />
                  ))}
              </div>
              <div className="legend-labels">
                <span>Low</span>
                <span>Medium</span>
                <span>High</span>
              </div>
              {showHubClusters && (
                <div className="legend-hub-note">
                  <span className="dot-cyan" /> DC-heavy District Hub &nbsp;|&nbsp;{' '}
                  <span className="dot-teal" /> AC-dominant Hub
                </div>
              )}
            </div>
          </div>

          <div className="source-footnote">
            <Info size={14} /> {sourceMeta[chargerSource].scopeNote}
          </div>
        </div>

        {/* Right: Selected State Inspector Panel */}
        <div className="panel state-inspector-panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">STATE / UT DEEP-DIVE INSPECTOR</span>
              <h2 className="panel-title-lg">
                {selectedState.state_name} <span className="mono badge-code">{selectedState.state_code}</span>
              </h2>
            </div>
            {selectedState.state_code === 'DL' && (
              <button className="btn-primary-sm" onClick={onSelectDelhiPilot}>
                Open Delhi Pilot Map &rarr;
              </button>
            )}
          </div>

          {selectedState.vahan_note && (
            <div className="alert-box alert-amber">
              <AlertTriangle size={15} />
              <span>{selectedState.vahan_note}</span>
            </div>
          )}

          {/* State Multi-Source Charger Reconciliation Table */}
          <div className="inspector-section">
            <h3 className="section-heading">
              <BatteryCharging size={14} /> Separate Charging Infrastructure Registries
            </h3>
            <div className="mini-grid-4">
              <div className="mini-stat-box">
                <span className="mini-label">BEE Unique Sites</span>
                <strong className="mono text-teal">{formatNumber(selectedState.bee_unique_stations)}</strong>
                <span className="mini-sub">
                  {formatNumber(selectedState.bee_raw_charger_rows)} rows •{' '}
                  {formatNumber(selectedState.bee_total_connectors)} nozzles
                </span>
              </div>
              <div className="mini-stat-box">
                <span className="mini-label">BEE AC / DC Split</span>
                <strong className="mono text-sky">
                  {formatNumber(selectedState.bee_dc_connectors)} DC
                </strong>
                <span className="mini-sub">
                  {formatNumber(selectedState.bee_ac_connectors)} AC •{' '}
                  {formatNumber(selectedState.bee_total_power_kw, 0)} kW
                </span>
              </div>
              <div className="mini-stat-box">
                <span className="mini-label">PIB OMC Operational</span>
                <strong className="mono text-amber">
                  {formatNumber(selectedState.omc_operational_total)}
                </strong>
                <span className="mini-sub">
                  of {formatNumber(selectedState.omc_installed_total)} installed (
                  {selectedState.omc_operational_pct}%)
                </span>
              </div>
              <div className="mini-stat-box">
                <span className="mini-label">FAME-II / OSM</span>
                <strong className="mono">
                  {formatNumber(selectedState.fame2_omc_installed)} /{' '}
                  {formatNumber(selectedState.osm_charging_stations)}
                </strong>
                <span className="mini-sub">FAME-II OMC / OSM mapped</span>
              </div>
            </div>
          </div>

          {/* State VAHAN Active EV Fleet Breakdown */}
          <div className="inspector-section">
            <div className="section-header-row">
              <h3 className="section-heading">
                <Activity size={14} /> VAHAN Active EV Fleet ({formatNumber(selectedState.total_ev_active)})
              </h3>
              <span className="tiny-badge">
                {selectedState.non_compliant_share_pct}% Active Non-Compliant
              </span>
            </div>

            <div className="category-bars">
              {[
                { label: '2-Wheelers (2W)', count: selectedState.ev_2w, color: '#38bdf8' },
                { label: '3-Wheelers (3W)', count: selectedState.ev_3w, color: '#2dd4bf' },
                { label: '4-Wheelers / LMV', count: selectedState.ev_4w_lmv_pv, color: '#818cf8' },
                { label: 'Electric Goods', count: selectedState.ev_goods, color: '#f59e0b' },
                { label: 'Electric Buses', count: selectedState.ev_bus, color: '#f43f5e' },
              ].map((item) => {
                const pct =
                  selectedState.total_ev_active > 0
                    ? (100 * item.count) / selectedState.total_ev_active
                    : 0;
                return (
                  <div key={item.label} className="cat-bar-row">
                    <div className="cat-bar-meta">
                      <span>{item.label}</span>
                      <span className="mono">
                        {formatNumber(item.count)} ({pct.toFixed(1)}%)
                      </span>
                    </div>
                    <div className="cat-bar-track">
                      <div
                        className="cat-bar-fill"
                        style={{ width: `${Math.max(1.5, pct)}%`, backgroundColor: item.color }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Annual Registration Trend Sparkbars (2018-2026) */}
          <div className="inspector-section">
            <h3 className="section-heading">
              <BarChart3 size={14} /> Annual EV Registration Trajectory (VAHAN 2018–2026 YTD)
            </h3>
            <div className="sparkbar-chart">
              {selectedState.yearwise_trend
                .filter((y) => y.year >= 2018)
                .map((item, _, arr) => {
                  const maxVal = Math.max(...arr.map((a) => a.registrations), 1);
                  const heightPct = Math.max(4, Math.round((item.registrations / maxVal) * 100));
                  return (
                    <div key={item.year} className="sparkbar-col" title={`${item.year}: ${formatNumber(item.registrations)} EVs`}>
                      <div className="sparkbar-val mono">{formatCompactIndian(item.registrations)}</div>
                      <div className="sparkbar-track">
                        <div className="sparkbar-fill" style={{ height: `${heightPct}%` }} />
                      </div>
                      <div className="sparkbar-year">{String(item.year).slice(2)}</div>
                    </div>
                  );
                })}
            </div>
          </div>

          {/* Top CPOs & Connector Types + Tariff & SNA */}
          <div className="inspector-two-col">
            <div>
              <h4 className="sub-heading">Top CPOs in {selectedState.state_code} (BEE Rows)</h4>
              <ul className="compact-list">
                {selectedState.bee_top_cpos.slice(0, 5).map((c) => (
                  <li key={c.cpo}>
                    <span>{c.cpo}</span>
                    <span className="mono">{formatNumber(c.rows)}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h4 className="sub-heading">Connector Mix (BEE Nozzles)</h4>
              <ul className="compact-list">
                {selectedState.bee_connector_breakdown.slice(0, 5).map((c) => (
                  <li key={c.type}>
                    <span>{c.type}</span>
                    <span className="mono">{formatNumber(c.connectors)}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="tariff-sna-box">
            <div>
              <span className="mini-label">Notified EV Tariff (BEE Annexure-A):</span>{' '}
              <strong className="mono">{selectedState.ev_tariff_energy}</strong> (Fixed:{' '}
              <span className="mono">{selectedState.ev_tariff_fixed}</span>)
            </div>
            <div>
              <span className="mini-label">State Nodal Agency (SNA):</span>{' '}
              <strong>{selectedState.state_nodal_agency}</strong>
            </div>
            <div>
              <span className="mini-label">Demographics (NITI IEMI 2025):</span> Pop:{' '}
              <strong className="mono">{formatCompactIndian(selectedState.ncp_2025_population)}</strong> •
              Area: <strong className="mono">{formatNumber(selectedState.area_sq_km)} km²</strong> • GSDP:{' '}
              <strong className="mono">
                {selectedState.gsdp_inr_crore ? `₹${formatNumber(selectedState.gsdp_inr_crore)} Cr` : 'N/A'}
              </strong>
            </div>
          </div>
        </div>
      </div>

      {/* Comparative Charts Section */}
      <div className="charts-grid-2">
        <div className="panel">
          <div className="panel-header">
            <div>
              <h3 className="panel-title">
                Top 12 States by Active EV Fleet ({vehicleCategory}) vs. {chargerSource} Stations
              </h3>
              <p className="panel-subtitle">
                Click any state row to inspect its detailed profile on the map and inspector
              </p>
            </div>
          </div>
          <div className="horiz-chart-list">
            {top12StatesForChart.map((st) => {
              const evVal = getCategoryEvCount(st, vehicleCategory);
              const maxEv = Math.max(1, getCategoryEvCount(top12StatesForChart[0], vehicleCategory));
              const chgVal = getSourceChargerCount(st, chargerSource);
              const ratio = chgVal > 0 ? (evVal / chgVal).toFixed(0) : 'N/A';
              return (
                <div
                  key={st.state_code}
                  className={`horiz-chart-row ${st.state_code === selectedStateCode ? 'row-selected' : ''}`}
                  onClick={() => setSelectedStateCode(st.state_code)}
                >
                  <div className="horiz-state-name">
                    <strong>{st.state_name}</strong>
                    <span className="mono text-muted">{ ratio } EVs/stn</span>
                  </div>
                  <div className="horiz-bars-wrap">
                    <div className="horiz-bar-line">
                      <div
                        className="horiz-bar-ev"
                        style={{ width: `${Math.max(2, (evVal / maxEv) * 100)}%` }}
                      />
                      <span className="mono horiz-val">{formatCompactIndian(evVal)} EVs</span>
                    </div>
                    <div className="horiz-bar-line">
                      <div
                        className="horiz-bar-chg"
                        style={{ width: `${Math.max(2, Math.min(100, (chgVal / 6500) * 100))}%` }}
                      />
                      <span className="mono horiz-val text-teal">{formatNumber(chgVal)} stns</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* OMC Commissioning Gap & Data Quality Summary Panel */}
        <div className="panel">
          <div className="panel-header">
            <div>
              <h3 className="panel-title">
                <Zap size={15} className="icon-amber" /> Data Quality, Unit Reconciliation &amp; OMC
                Commissioning Audit
              </h3>
              <p className="panel-subtitle">
                Verified findings from pre-coding audit of BEE (1,159 pages) and Parliamentary Replies (Mar
                2026)
              </p>
            </div>
          </div>

          <div className="audit-cards-stack">
            <div className="audit-finding-card">
              <div className="audit-card-title">
                <CheckCircle2 size={15} className="icon-teal" />
                <strong>1. Why 39,641 BEE Rows = 29,277 Stations = 44,066 Connectors</strong>
              </div>
              <p>
                In <code>BEE_EV_PCS_Data_29277_20251026.pdf</code>, each row represents a charger unit/connector
                group rather than a site. Exactly <strong>8,428 rows (21.26%)</strong> are exact duplicates
                representing multiple identical single-nozzle chargers at the same station. Clustering by{' '}
                <code>(CPO, Location, Lat, Lon)</code> recovers <strong>29,371 unique sites</strong> (29,117
                unique coordinate pairs) and <strong>44,066 total connectors</strong>.
              </p>
            </div>

            <div className="audit-finding-card">
              <div className="audit-card-title">
                <AlertTriangle size={15} className="icon-amber" />
                <strong>2. OMC Installed vs. Operational Gap (17.97% Uncommissioned Backlog)</strong>
              </div>
              <p>
                BEE’s PDF lacks an operational status flag. Cross-checking against MoPNG’s Lok Sabha reply (
                <code>PIB PRID 2246042</code>, as of 01 Mar 2026) proves that out of{' '}
                <strong>27,737 installed OMC stations</strong>, only <strong>22,753 (82.03%)</strong> are
                operational—with severe grid-energization lags in Ladakh (10.0%), Puducherry (41.4%),
                Meghalaya (55.0%), and Goa (67.8%).
              </p>
            </div>

            <div className="audit-finding-card">
              <div className="audit-card-title">
                <Info size={15} className="icon-sky" />
                <strong>3. Coordinate Hygiene &amp; VAHAN Dual Fuel Label Discovery</strong>
              </div>
              <p>
                In BEE, <strong>39,522 / 39,641 rows (99.70%)</strong> have valid India coordinates;{' '}
                <strong>104 IOCL rows</strong> had <code>Latitude == Longitude</code> copy-paste errors and are
                excluded from map pins while preserved in state tabular totals. In VAHAN, battery EVs are split
                across <code>ELECTRIC(BOV)</code> (6.35M) and <code>PURE EV</code> (4.34M); both are combined
                here while Strong/Petrol Hybrids (2.05M) are excluded.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Complete 36-State Interactive Comparison Table */}
      <div className="panel">
        <div className="panel-header">
          <div>
            <h3 className="panel-title">All 36 States &amp; Union Territories — Comparative Matrix</h3>
            <p className="panel-subtitle">
              Showing separate columns for VAHAN Active EVs (19 Oct 2026), BEE Unique Sites &amp; Connectors
              (26 Oct 2025), PIB OMC Operational (01 Mar 2026), FAME-II (01 Mar 2026), and OSM (19 Oct 2026)
            </p>
          </div>
          <div className="table-controls">
            <input
              type="text"
              className="search-input"
              placeholder="Filter state/UT..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <select
              className="select-input-sm"
              value={tableSortBy}
              onChange={(e) => setTableSortBy(e.target.value as 'ev' | 'chargers' | 'ratio' | 'omc_pct')}
            >
              <option value="ev">Sort: Active EVs (High &rarr; Low)</option>
              <option value="chargers">Sort: Stations (High &rarr; Low)</option>
              <option value="ratio">Sort: EVs per Station (High &rarr; Low)</option>
              <option value="omc_pct">Sort: OMC Operational %</option>
            </select>
          </div>
        </div>

        <div className="table-scroll">
          <table className="data-table">
            <thead>
              <tr>
                <th>State / UT</th>
                <th className="num">Active EVs ({vehicleCategory})</th>
                <th className="num">2W Share</th>
                <th className="num">3W Share</th>
                <th className="num">4W / LMV</th>
                <th className="num">BEE Unique Sites</th>
                <th className="num">BEE Connectors (DC)</th>
                <th className="num">PIB OMC Oper / Inst</th>
                <th className="num">FAME-II OMC</th>
                <th className="num">OSM Mapped</th>
                <th className="num">EVs / BEE Site</th>
                <th className="num">LT EV Tariff</th>
              </tr>
            </thead>
            <tbody>
              {filteredAndSortedStates.map((st) => {
                const evVal = getCategoryEvCount(st, vehicleCategory);
                const sh2w = st.total_ev_active > 0 ? ((100 * st.ev_2w) / st.total_ev_active).toFixed(0) : '0';
                const sh3w = st.total_ev_active > 0 ? ((100 * st.ev_3w) / st.total_ev_active).toFixed(0) : '0';
                return (
                  <tr
                    key={st.state_code}
                    className={st.state_code === selectedStateCode ? 'tr-selected' : ''}
                    onClick={() => setSelectedStateCode(st.state_code)}
                  >
                    <td>
                      <strong>{st.state_name}</strong>{' '}
                      <span className="mono text-muted">({st.state_code})</span>
                      {st.state_code === 'DL' && <span className="pilot-pill">PILOT</span>}
                    </td>
                    <td className="num mono">
                      <strong>{formatNumber(evVal)}</strong>
                    </td>
                    <td className="num mono">{sh2w}%</td>
                    <td className="num mono">{sh3w}%</td>
                    <td className="num mono">{formatNumber(st.ev_4w_lmv_pv)}</td>
                    <td className="num mono text-teal">
                      <strong>{formatNumber(st.bee_unique_stations)}</strong>
                    </td>
                    <td className="num mono">
                      {formatNumber(st.bee_total_connectors)}{' '}
                      <span className="text-sky">({formatNumber(st.bee_dc_connectors)})</span>
                    </td>
                    <td className="num mono">
                      {formatNumber(st.omc_operational_total)} / {formatNumber(st.omc_installed_total)}{' '}
                      <span className="text-amber">({st.omc_operational_pct}%)</span>
                    </td>
                    <td className="num mono">{formatNumber(st.fame2_omc_installed)}</td>
                    <td className="num mono">{formatNumber(st.osm_charging_stations)}</td>
                    <td className="num mono">
                      <strong>{st.evs_per_bee_station ?? 'N/A'}</strong>
                    </td>
                    <td className="num mono">
                      {st.ev_tariff_lt_rs_kwh ? `₹${st.ev_tariff_lt_rs_kwh.toFixed(2)}` : 'Not def.'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
