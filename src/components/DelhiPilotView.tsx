import React, { useMemo, useState } from 'react';
import {
  MapContainer,
  TileLayer,
  GeoJSON,
  CircleMarker,
  Popup,
  Tooltip as LeafletTooltip,
} from 'react-leaflet';
import type { FeatureCollection, Feature } from 'geojson';
import type { Layer, PathOptions } from 'leaflet';
import {
  AlertTriangle,
  BatteryCharging,
  Building2,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Cpu,
  Database,
  Filter,
  HelpCircle,
  Info,
  Layers,
  MapPin,
  RefreshCw,
  Route,
  Search,
  SlidersHorizontal,
  X,
  Zap,
} from 'lucide-react';
import type {
  DelhiPilotBundle,
  DelhiStationRecord,
} from '../types/data';
import {
  formatCompactIndian,
  formatNumber,
  getChoroplethColor,
  PALETTE_AMBER_RED,
  PALETTE_INDIGO_CYAN,
  PALETTE_TEAL_EMERALD,
} from '../utils/formatters';

interface DelhiPilotViewProps {
  bundle: DelhiPilotBundle;
  districtsGeoJson: FeatureCollection;
  roadsGeoJson: FeatureCollection;
  onOpenPlanningView: () => void;
}

type DelhiSourceSelection = 'SWITCH_DELHI' | 'BEE' | 'OSM' | 'SWITCH_AND_BEE';
type StationTypeFilter = 'ALL' | 'Charging' | 'Battery Swapping';
type PowerClassFilter =
  | 'ALL'
  | 'DC Fast (>=15-25 kW)'
  | 'AC Fast (7-22 kW)'
  | 'AC Slow (<=3.3 kW)'
  | 'Battery Swapping';
type DistrictChoroplethMetric =
  | 'EV_DEMAND'
  | 'EVS_PER_POINT'
  | 'SWITCH_POINTS'
  | 'BEE_CONNECTORS'
  | 'POPULATION_2025';

export const DelhiPilotView: React.FC<DelhiPilotViewProps> = ({
  bundle,
  districtsGeoJson,
  roadsGeoJson,
  onOpenPlanningView,
}) => {
  // Station & Source Filters
  const [sourceSelection, setSourceSelection] = useState<DelhiSourceSelection>('SWITCH_DELHI');
  const [stationTypeFilter, setStationTypeFilter] = useState<StationTypeFilter>('ALL');
  const [powerClassFilter, setPowerClassFilter] = useState<PowerClassFilter>('ALL');
  const [selectedVendor, setSelectedVendor] = useState<string>('ALL');
  const [selectedDistrict, setSelectedDistrict] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [includePinEstimatedSwap, setIncludePinEstimatedSwap] = useState<boolean>(false);

  // Filter drawer / sidebar collapse for mobile and compact desktop view
  const [isFilterPanelOpen, setIsFilterPanelOpen] = useState<boolean>(true);

  // District Demand Join Mode (Verified Zonal RTO only vs Redistributed Commercial Estimate)
  const [useRedistributedCommercial, setUseRedistributedCommercial] = useState<boolean>(true);
  const [districtMetric, setDistrictMetric] = useState<DistrictChoroplethMetric>('EV_DEMAND');

  // Optional Contextual Map Layers
  const [showDistrictChoropleth, setShowDistrictChoropleth] = useState<boolean>(true);
  const [showMajorRoads, setShowMajorRoads] = useState<boolean>(false);
  const [showPowerGrid, setShowPowerGrid] = useState<boolean>(false);
  const [showDemandAttractors, setShowDemandAttractors] = useState<boolean>(false);
  const [poiCategoryFilter, setPoiCategoryFilter] = useState<string>('ALL');

  // Selected Station for Inspector Drawer
  const [selectedStation, setSelectedStation] = useState<DelhiStationRecord | null>(
    bundle.stations.switch_delhi[0] || null
  );

  // Combine stations according to active source filter (keeping sources clearly badged)
  const rawStationsForSource = useMemo(() => {
    switch (sourceSelection) {
      case 'SWITCH_DELHI':
        return bundle.stations.switch_delhi;
      case 'BEE':
        return bundle.stations.bee;
      case 'OSM':
        return bundle.stations.osm;
      case 'SWITCH_AND_BEE':
        return [...bundle.stations.switch_delhi, ...bundle.stations.bee];
    }
  }, [bundle.stations, sourceSelection]);

  const availableVendors = useMemo(() => {
    const counts: Record<string, number> = {};
    for (const s of rawStationsForSource) {
      counts[s.vendor] = (counts[s.vendor] || 0) + 1;
    }
    return Object.entries(counts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 35);
  }, [rawStationsForSource]);

  const filteredStations = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    return rawStationsForSource.filter((st) => {
      if (!includePinEstimatedSwap && st.coord_status === 'PIN_CENTROID_ESTIMATE') {
        return false;
      }
      if (stationTypeFilter !== 'ALL' && st.station_type !== stationTypeFilter) {
        return false;
      }
      if (powerClassFilter !== 'ALL' && st.power_class !== powerClassFilter) {
        return false;
      }
      if (selectedVendor !== 'ALL' && st.vendor !== selectedVendor) {
        return false;
      }
      if (selectedDistrict !== 'ALL' && st.district !== selectedDistrict) {
        return false;
      }
      if (q) {
        const hay = `${st.name} ${st.vendor} ${st.address} ${st.postal_code} ${st.charger_type} ${st.district}`.toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });
  }, [
    rawStationsForSource,
    includePinEstimatedSwap,
    stationTypeFilter,
    powerClassFilter,
    selectedVendor,
    selectedDistrict,
    searchQuery,
  ]);

  const filteredSummary = useMemo(() => {
    let chargingStations = 0;
    let swappingStations = 0;
    let totalPoints = 0;
    let dcConnectors = 0;
    let acConnectors = 0;
    let swapDockets = 0;
    for (const st of filteredStations) {
      if (st.station_type === 'Battery Swapping') {
        swappingStations += 1;
        swapDockets += st.swap_dockets || st.no_of_chargers;
      } else {
        chargingStations += 1;
        totalPoints += st.no_of_chargers;
        dcConnectors += st.dc_connectors;
        acConnectors += st.ac_connectors;
      }
    }
    return {
      totalStations: filteredStations.length,
      chargingStations,
      swappingStations,
      totalPoints,
      dcConnectors,
      acConnectors,
      swapDockets,
    };
  }, [filteredStations]);

  const districtsMap = useMemo(() => {
    const m: Record<string, (typeof bundle.districts_summary)[0]> = {};
    for (const d of bundle.districts_summary) {
      m[d.district] = d;
    }
    return m;
  }, [bundle.districts_summary]);

  const getDistrictValue = (dName: string): number | null => {
    const d = districtsMap[dName];
    if (!d) return null;
    const evCount = useRedistributedCommercial ? d.estimated_total_ev_demand : d.zonal_rto_ev_total;
    switch (districtMetric) {
      case 'EV_DEMAND':
        return evCount;
      case 'EVS_PER_POINT':
        return d.switch_delhi_charging_points > 0
          ? Number((evCount / d.switch_delhi_charging_points).toFixed(1))
          : null;
      case 'SWITCH_POINTS':
        return d.switch_delhi_charging_points;
      case 'BEE_CONNECTORS':
        return d.bee_connectors;
      case 'POPULATION_2025':
        return d.ncp_2025_population_est;
    }
  };

  const styleDistrictFeature = (feature?: Feature): PathOptions => {
    const dName = feature?.properties?.district as string;
    const isSel = selectedDistrict === dName;
    if (!showDistrictChoropleth) {
      return {
        fillColor: 'transparent',
        weight: isSel ? 2.0 : 1.0,
        color: isSel ? '#0f766e' : '#cbd5e1',
        fillOpacity: 0.04,
      };
    }
    const val = getDistrictValue(dName);
    let fillColor = '#f8fafc';
    if (districtMetric === 'EV_DEMAND') {
      fillColor = getChoroplethColor(val, [25000, 45000, 65000, 85000, 110000], PALETTE_INDIGO_CYAN);
    } else if (districtMetric === 'EVS_PER_POINT') {
      fillColor = getChoroplethColor(val, [40, 70, 110, 160, 220], PALETTE_AMBER_RED);
    } else if (districtMetric === 'SWITCH_POINTS' || districtMetric === 'BEE_CONNECTORS') {
      fillColor = getChoroplethColor(val, [200, 400, 650, 950, 1300], PALETTE_TEAL_EMERALD);
    } else {
      fillColor = getChoroplethColor(val, [800000, 1600000, 2400000, 3200000, 4200000], PALETTE_INDIGO_CYAN);
    }
    return {
      fillColor,
      weight: isSel ? 2.0 : 1.0,
      color: isSel ? '#0f766e' : '#94a3b8',
      fillOpacity: isSel ? 0.38 : 0.22,
    };
  };

  const onEachDistrictFeature = (feature: Feature, layer: Layer) => {
    const dName = feature.properties?.district as string;
    const d = districtsMap[dName];
    if (!d) return;
    const evTotal = useRedistributedCommercial ? d.estimated_total_ev_demand : d.zonal_rto_ev_total;
    layer.bindTooltip(
      `<div style="font-family: Inter, sans-serif; font-size: 11.5px; line-height: 1.45; color: #0f172a;">
        <strong style="color: #0f766e; font-size: 12.5px;">${d.district} District (NCT of Delhi)</strong><br/>
        <span>EV Demand (${useRedistributedCommercial ? 'Est. Total' : 'Direct Zonal RTO'}): <b>${evTotal.toLocaleString('en-IN')}</b></span><br/>
        <span>Switch Delhi: <b>${d.switch_delhi_charging_stations} chg + ${d.switch_delhi_swap_geocoded + d.switch_delhi_swap_pin_estimated} swap</b> (${d.switch_delhi_charging_points} pts)</span><br/>
        <span>BEE Registry: <b>${d.bee_stations} sites</b> (${d.bee_connectors} connectors)</span><br/>
        <span>Grid &amp; POIs: <b>${d.substations_count} substations • ${d.demand_attractors_count} POIs</b></span>
      </div>`,
      { sticky: true, direction: 'top' }
    );
    layer.on({
      click: () => setSelectedDistrict((prev) => (prev === dName ? 'ALL' : dName)),
    });
  };

  const styleRoadFeature = (feature?: Feature): PathOptions => {
    const hw = feature?.properties?.highway as string;
    if (hw === 'motorway') return { color: '#dc2626', weight: 2.0, opacity: 0.75 };
    if (hw === 'trunk') return { color: '#ea580c', weight: 1.5, opacity: 0.65 };
    if (hw === 'primary') return { color: '#d97706', weight: 1.2, opacity: 0.55 };
    return { color: '#94a3b8', weight: 0.8, opacity: 0.45 };
  };

  const filteredAttractors = useMemo(() => {
    if (!showDemandAttractors) return [];
    const list =
      poiCategoryFilter === 'ALL'
        ? bundle.overlays.demand_attractors
        : bundle.overlays.demand_attractors.filter((a) => a.category === poiCategoryFilter);
    return list.slice(0, 1000);
  }, [bundle.overlays.demand_attractors, showDemandAttractors, poiCategoryFilter]);

  // Active filters count
  const activeFiltersCount = useMemo(() => {
    let c = 0;
    if (sourceSelection !== 'SWITCH_DELHI') c++;
    if (stationTypeFilter !== 'ALL') c++;
    if (powerClassFilter !== 'ALL') c++;
    if (selectedVendor !== 'ALL') c++;
    if (selectedDistrict !== 'ALL') c++;
    if (searchQuery.trim() !== '') c++;
    if (includePinEstimatedSwap) c++;
    return c;
  }, [
    sourceSelection,
    stationTypeFilter,
    powerClassFilter,
    selectedVendor,
    selectedDistrict,
    searchQuery,
    includePinEstimatedSwap,
  ]);

  const resetFilters = () => {
    setSourceSelection('SWITCH_DELHI');
    setStationTypeFilter('ALL');
    setPowerClassFilter('ALL');
    setSelectedVendor('ALL');
    setSelectedDistrict('ALL');
    setSearchQuery('');
    setIncludePinEstimatedSwap(false);
  };

  return (
    <div className="view-container">
      {/* Primary Page Header & Subtitle */}
      <div className="page-header-row">
        <div>
          <h2 className="page-main-title">Delhi EV Charging Map</h2>
          <p className="page-main-description">
            Explore charging infrastructure, identify coverage gaps, and plan future charging locations.
          </p>
        </div>
        <div className="header-actions">
          <button className="btn-secondary-sm" onClick={() => setIsFilterPanelOpen(!isFilterPanelOpen)}>
            <SlidersHorizontal size={13} />
            <span>{isFilterPanelOpen ? 'Hide Filters' : 'Show Filters'}</span>
            {activeFiltersCount > 0 && <span className="filter-count-badge">{activeFiltersCount}</span>}
          </button>
          <button className="btn-primary-sm" onClick={onOpenPlanningView}>
            <Zap size={13} />
            <span>Coverage Planning</span>
          </button>
        </div>
      </div>

      {/* 3 Focused Key Statistics Bar */}
      <div className="key-stats-strip">
        <div className="stat-pill">
          <span className="stat-pill-label">Charging Locations</span>
          <span className="stat-pill-val mono text-teal">
            {formatNumber(filteredSummary.chargingStations)}
          </span>
          <span className="stat-pill-detail">
            {formatNumber(filteredSummary.totalPoints)} points • {formatNumber(filteredSummary.dcConnectors)} DC fast
          </span>
        </div>

        <div className="stat-pill">
          <span className="stat-pill-label">Battery Swapping Locations</span>
          <span className="stat-pill-val mono text-amber">
            {formatNumber(filteredSummary.swappingStations)}
          </span>
          <span className="stat-pill-detail">
            {formatNumber(filteredSummary.swapDockets)} dockets recorded
          </span>
        </div>

        <div className="stat-pill">
          <span className="stat-pill-label">Operational Status Coverage</span>
          <span className="stat-pill-val mono text-sky">100% Geocoded</span>
          <span className="stat-pill-detail">
            All 573 Switch Delhi charging sites verified • Static capacity reported
          </span>
        </div>
      </div>

      {/* Substation Hosting Capacity Warning */}
      {showPowerGrid && (
        <div className="alert-box alert-amber">
          <AlertTriangle size={15} />
          <div>
            <strong>Grid Infrastructure Disclaimer:</strong> The 576 mapped power features show physical locations
            only. Proximity to a substation or transformer does not prove available electrical hosting capacity, which
            requires DISCOM load-flow verification.
          </div>
        </div>
      )}

      {/* Workspace: Compact Sidebar on Left + Map in Center/Right */}
      <div className={`map-workspace-layout ${isFilterPanelOpen ? 'sidebar-open' : 'sidebar-closed'}`}>
        {/* Collapsible Left Filter & Control Sidebar */}
        {isFilterPanelOpen && (
          <aside className="filter-sidebar">
            <div className="sidebar-section-header">
              <span className="sidebar-title">
                <Filter size={13} /> Filter Infrastructure
              </span>
              {activeFiltersCount > 0 && (
                <button className="btn-link-xs" onClick={resetFilters}>
                  Reset ({activeFiltersCount})
                </button>
              )}
            </div>

            <div className="sidebar-control-group">
              <label className="sidebar-label">Search</label>
              <div className="search-input-wrapper">
                <Search size={13} className="search-icon" />
                <input
                  type="text"
                  className="search-input-field"
                  placeholder="Address, PIN, vendor, ID..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
                {searchQuery && (
                  <button className="search-clear-btn" onClick={() => setSearchQuery('')}>
                    <X size={12} />
                  </button>
                )}
              </div>
            </div>

            <div className="sidebar-control-group">
              <label className="sidebar-label">Station Type</label>
              <div className="segmented-control">
                <button
                  className={`segment-btn ${stationTypeFilter === 'ALL' ? 'segment-active' : ''}`}
                  onClick={() => setStationTypeFilter('ALL')}
                >
                  All
                </button>
                <button
                  className={`segment-btn ${stationTypeFilter === 'Charging' ? 'segment-active' : ''}`}
                  onClick={() => setStationTypeFilter('Charging')}
                >
                  Charging
                </button>
                <button
                  className={`segment-btn ${stationTypeFilter === 'Battery Swapping' ? 'segment-active' : ''}`}
                  onClick={() => setStationTypeFilter('Battery Swapping')}
                >
                  Swapping
                </button>
              </div>
            </div>

            <div className="sidebar-control-group">
              <label className="sidebar-label">Power &amp; Connector Class</label>
              <select
                className="select-input-sm"
                value={powerClassFilter}
                onChange={(e) => setPowerClassFilter(e.target.value as PowerClassFilter)}
              >
                <option value="ALL">All Power Classes</option>
                <option value="DC Fast (>=15-25 kW)">DC Fast (&ge;15–25 kW: CCS2 / DC-001)</option>
                <option value="AC Fast (7-22 kW)">AC Fast (7–22 kW: Type-2)</option>
                <option value="AC Slow (<=3.3 kW)">AC Slow / 3.3 kW LEV</option>
                <option value="Battery Swapping">Battery Swapping Dockets</option>
              </select>
            </div>

            <div className="sidebar-control-group">
              <label className="sidebar-label">Operator / Brand</label>
              <select
                className="select-input-sm"
                value={selectedVendor}
                onChange={(e) => setSelectedVendor(e.target.value)}
              >
                <option value="ALL">All Operators ({availableVendors.length})</option>
                {availableVendors.map(([vName, cnt]) => (
                  <option key={vName} value={vName}>
                    {vName} ({cnt})
                  </option>
                ))}
              </select>
            </div>

            <div className="sidebar-control-group">
              <label className="sidebar-label">District Filter</label>
              <select
                className="select-input-sm"
                value={selectedDistrict}
                onChange={(e) => setSelectedDistrict(e.target.value)}
              >
                <option value="ALL">All 9 Districts</option>
                {bundle.districts_summary.map((d) => (
                  <option key={d.district} value={d.district}>
                    {d.district}
                  </option>
                ))}
              </select>
            </div>

            <div className="sidebar-control-group">
              <label className="sidebar-label">Data Source</label>
              <select
                className="select-input-sm"
                value={sourceSelection}
                onChange={(e) => {
                  setSourceSelection(e.target.value as DelhiSourceSelection);
                  setSelectedVendor('ALL');
                }}
              >
                <option value="SWITCH_DELHI">Switch Delhi Official (876 stations)</option>
                <option value="BEE">BEE National Registry (1,909 sites)</option>
                <option value="OSM">OpenStreetMap (179 stations)</option>
                <option value="SWITCH_AND_BEE">Overlay: Switch Delhi + BEE</option>
              </select>
            </div>

            <div className="sidebar-control-group checkbox-block">
              <label className="checkbox-label-sm" title="Previews 121 swap kiosks at their verified PIN centroid">
                <input
                  type="checkbox"
                  checked={includePinEstimatedSwap}
                  onChange={(e) => setIncludePinEstimatedSwap(e.target.checked)}
                />
                <span>Include 121 PIN-estimated swap kiosks</span>
              </label>
            </div>

            <div className="sidebar-divider" />

            <div className="sidebar-section-header">
              <span className="sidebar-title">
                <Layers size={13} /> Map Overlays
              </span>
            </div>

            <div className="layer-checkbox-list">
              <label className="checkbox-label-sm">
                <input
                  type="checkbox"
                  checked={showDistrictChoropleth}
                  onChange={(e) => setShowDistrictChoropleth(e.target.checked)}
                />
                <span>District Demand Choropleth</span>
              </label>

              {showDistrictChoropleth && (
                <div className="nested-control">
                  <select
                    className="select-input-xs"
                    value={districtMetric}
                    onChange={(e) => setDistrictMetric(e.target.value as DistrictChoroplethMetric)}
                  >
                    <option value="EV_DEMAND">Metric: Active EV Fleet</option>
                    <option value="EVS_PER_POINT">Metric: EVs per Charger Point</option>
                    <option value="SWITCH_POINTS">Metric: Switch Delhi Points</option>
                    <option value="BEE_CONNECTORS">Metric: BEE Connectors</option>
                    <option value="POPULATION_2025">Metric: 2025 Population</option>
                  </select>
                </div>
              )}

              <label className="checkbox-label-sm">
                <input
                  type="checkbox"
                  checked={showMajorRoads}
                  onChange={(e) => setShowMajorRoads(e.target.checked)}
                />
                <span>Major Road Corridors</span>
              </label>

              <label className="checkbox-label-sm">
                <input
                  type="checkbox"
                  checked={showDemandAttractors}
                  onChange={(e) => setShowDemandAttractors(e.target.checked)}
                />
                <span>Demand Attractors (POIs)</span>
              </label>

              {showDemandAttractors && (
                <div className="nested-control">
                  <select
                    className="select-input-xs"
                    value={poiCategoryFilter}
                    onChange={(e) => setPoiCategoryFilter(e.target.value)}
                  >
                    <option value="ALL">All POIs (3,534)</option>
                    <option value="station">Metro/Rail (253)</option>
                    <option value="bus_station">Bus Depots (65)</option>
                    <option value="fuel">Fuel Pumps (386)</option>
                    <option value="parking">Parking Lots (705)</option>
                    <option value="commercial">Commercial (389)</option>
                  </select>
                </div>
              )}

              <label className="checkbox-label-sm">
                <input
                  type="checkbox"
                  checked={showPowerGrid}
                  onChange={(e) => setShowPowerGrid(e.target.checked)}
                />
                <span>Power Substations &amp; Transformers</span>
              </label>
            </div>
          </aside>
        )}

        {/* Center: Full Delhi Map */}
        <div className="map-canvas-container">
          <div className="map-legend-bar">
            <span className="legend-item">
              <i className="legend-indicator" style={{ backgroundColor: '#0284c7' }} /> DC Fast (&ge;15kW)
            </span>
            <span className="legend-item">
              <i className="legend-indicator" style={{ backgroundColor: '#0f766e' }} /> AC Charging
            </span>
            <span className="legend-item">
              <i className="legend-indicator" style={{ backgroundColor: '#d97706' }} /> Battery Swapping
            </span>
            {showPowerGrid && (
              <span className="legend-item">
                <i className="legend-indicator" style={{ backgroundColor: '#b91c1c' }} /> Substation (Location only)
              </span>
            )}
            <span className="legend-count mono">
              {filteredStations.length} of {rawStationsForSource.length} displayed
            </span>
          </div>

          <MapContainer
            center={[28.63, 77.19]}
            zoom={11}
            minZoom={9}
            maxZoom={17}
            scrollWheelZoom={true}
            style={{ height: '100%', width: '100%' }}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a> | GNCTD Switch Delhi'
              url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
            />

            {/* District Polygons */}
            <GeoJSON
              key={`dl-dist-${showDistrictChoropleth}-${districtMetric}-${useRedistributedCommercial}-${selectedDistrict}`}
              data={districtsGeoJson}
              style={styleDistrictFeature}
              onEachFeature={onEachDistrictFeature}
            />

            {/* Major Roads */}
            {showMajorRoads && (
              <GeoJSON
                key="dl-roads-overlay"
                data={roadsGeoJson}
                style={styleRoadFeature}
              />
            )}

            {/* POI Attractors */}
            {showDemandAttractors &&
              filteredAttractors.map((poi) => (
                <CircleMarker
                  key={`poi-${poi.osm_id}`}
                  center={[poi.latitude, poi.longitude]}
                  radius={3}
                  pathOptions={{
                    color: '#ffffff',
                    weight: 0.8,
                    fillColor: '#64748b',
                    fillOpacity: 0.70,
                  }}
                >
                  <LeafletTooltip direction="top">
                    <div style={{ fontSize: '11px' }}>
                      <strong>{poi.name}</strong> ({poi.category})
                    </div>
                  </LeafletTooltip>
                </CircleMarker>
              ))}

            {/* Power Grid Nodes */}
            {showPowerGrid &&
              bundle.overlays.power_nodes.map((pn) => (
                <CircleMarker
                  key={`pn-${pn.osm_id}`}
                  center={[pn.latitude, pn.longitude]}
                  radius={pn.power_type === 'substation' ? 5 : 3.5}
                  pathOptions={{
                    color: '#ffffff',
                    weight: 1.2,
                    fillColor: pn.power_type === 'substation' ? '#b91c1c' : '#ea580c',
                    fillOpacity: 0.85,
                  }}
                >
                  <Popup>
                    <div className="leaflet-custom-popup">
                      <div className="popup-badge badge-rose">
                        Power Infrastructure ({pn.power_type.toUpperCase()})
                      </div>
                      <h4>{pn.name}</h4>
                      <p>
                        <strong>Operator:</strong> {pn.operator}
                        <br />
                        <strong>Substation Type:</strong> {pn.substation_type}
                        <br />
                        <strong>Voltage:</strong> {pn.voltage} • <strong>Rating:</strong> {pn.rating}
                      </p>
                      <div className="popup-disclaimer">
                        <strong>Engineering note:</strong> Verified physical location only; available hosting
                        capacity is not disclosed in public data.
                      </div>
                    </div>
                  </Popup>
                </CircleMarker>
              ))}

            {/* Charging & Swapping Stations */}
            {filteredStations.map((st) => {
              const isSwap = st.station_type === 'Battery Swapping';
              const isDc = st.dc_connectors > 0;
              const isPinEst = st.coord_status === 'PIN_CENTROID_ESTIMATE';
              const fillColor = isSwap ? '#d97706' : isDc ? '#0284c7' : '#0f766e';
              const strokeColor =
                selectedStation?.id === st.id ? '#0f172a' : '#ffffff';
              const radius = selectedStation?.id === st.id ? 7.5 : isSwap ? 5 : isDc ? 5.5 : 4.5;

              return (
                <CircleMarker
                  key={st.id}
                  center={[st.latitude, st.longitude]}
                  radius={radius}
                  pathOptions={{
                    color: strokeColor,
                    weight: selectedStation?.id === st.id ? 2.5 : 1.2,
                    fillColor,
                    fillOpacity: isPinEst ? 0.55 : 0.90,
                    dashArray: isPinEst ? '2,2' : undefined,
                  }}
                  eventHandlers={{
                    click: () => setSelectedStation(st),
                  }}
                >
                  <Popup>
                    <div className="leaflet-custom-popup">
                      <div className="popup-header-tags">
                        <span className={`popup-badge ${isSwap ? 'badge-amber' : 'badge-teal'}`}>
                          {st.station_type}
                        </span>
                        <span className="popup-badge badge-slate">
                          {st.source}
                        </span>
                      </div>
                      <h4>{st.vendor}</h4>
                      <p className="popup-addr">{st.address}</p>
                      <div className="popup-grid">
                        <div>
                          <span>Connectors / Points:</span>{' '}
                          <strong>
                            {st.no_of_chargers} ({st.dc_connectors} DC / {st.ac_connectors} AC)
                          </strong>
                        </div>
                        <div>
                          <span>Charger Type:</span> <strong>{st.charger_type}</strong>
                        </div>
                        <div>
                          <span>Max Rating:</span>{' '}
                          <strong>{st.max_capacity_kw ? `${st.max_capacity_kw} kW` : 'Unspecified'}</strong>
                        </div>
                        <div>
                          <span>Tariff:</span> <strong>{st.cost_per_unit}</strong>
                        </div>
                        <div>
                          <span>Nearest Substation:</span>{' '}
                          <strong>
                            {st.nearest_substation_m !== null ? `${st.nearest_substation_m} m` : 'N/A'}
                          </strong>
                        </div>
                      </div>
                    </div>
                  </Popup>
                </CircleMarker>
              );
            })}
          </MapContainer>
        </div>

        {/* Right: Compact Station Inspector Drawer */}
        <aside className="inspector-sidebar">
          <div className="inspector-sidebar-header">
            <div>
              <span className="inspector-eyebrow">Station Details</span>
              <h3 className="inspector-title">
                {selectedStation ? selectedStation.vendor : 'Select Location'}
              </h3>
            </div>
            {selectedStation && (
              <span
                className={`badge-sm ${
                  selectedStation.station_type === 'Battery Swapping' ? 'badge-amber' : 'badge-teal'
                }`}
              >
                {selectedStation.station_type}
              </span>
            )}
          </div>

          {selectedStation ? (
            <div className="inspector-content">
              {/* Verified Facts */}
              <div className="audit-box box-verified">
                <div className="audit-box-header">
                  <CheckCircle2 size={13} className="icon-teal" />
                  <strong>Verified Facts ({selectedStation.source})</strong>
                  <span className="mono text-muted text-xs">{selectedStation.source_date}</span>
                </div>
                <div className="audit-kv-list">
                  <div className="audit-kv-row">
                    <span className="audit-k">Station ID</span>
                    <span className="audit-v mono">{selectedStation.id}</span>
                  </div>
                  <div className="audit-kv-row">
                    <span className="audit-k">Address</span>
                    <span className="audit-v">{selectedStation.address}</span>
                  </div>
                  <div className="audit-kv-row">
                    <span className="audit-k">PIN Code</span>
                    <span className="audit-v mono">{selectedStation.postal_code || 'Not in record'}</span>
                  </div>
                  <div className="audit-kv-row">
                    <span className="audit-k">Charger Type</span>
                    <span className="audit-v">{selectedStation.charger_type}</span>
                  </div>
                  <div className="audit-kv-row">
                    <span className="audit-k">Points / Capacity</span>
                    <span className="audit-v mono">
                      {selectedStation.no_of_chargers} points ({selectedStation.max_capacity_kw ? `${selectedStation.max_capacity_kw} kW` : 'Unspecified'})
                    </span>
                  </div>
                  <div className="audit-kv-row">
                    <span className="audit-k">Tariff</span>
                    <span className="audit-v mono">{selectedStation.cost_per_unit}</span>
                  </div>
                  <div className="audit-kv-row">
                    <span className="audit-k">Hours / Payment</span>
                    <span className="audit-v">
                      {selectedStation.timing} • {selectedStation.payment_modes || 'UPI/App'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Analytical Estimates */}
              <div className="audit-box box-estimate">
                <div className="audit-box-header">
                  <RefreshCw size={13} className="icon-sky" />
                  <strong>Analytical Estimates &amp; Proximity</strong>
                </div>
                <div className="audit-kv-list">
                  <div className="audit-kv-row">
                    <span className="audit-k">Coordinate Quality</span>
                    <span className="audit-v mono">
                      {selectedStation.coord_status === 'VERIFIED_COORDS'
                        ? 'Verified Coordinates'
                        : `PIN ${selectedStation.postal_code} Centroid Estimate`}
                    </span>
                  </div>
                  <div className="audit-kv-row">
                    <span className="audit-k">District (Spatial Join)</span>
                    <span className="audit-v">{selectedStation.district}</span>
                  </div>
                  <div className="audit-kv-row">
                    <span className="audit-k">Nearest Substation</span>
                    <span className="audit-v mono">
                      {selectedStation.nearest_substation_m !== null
                        ? `${selectedStation.nearest_substation_m} m`
                        : 'N/A'}
                    </span>
                  </div>
                  <div className="audit-kv-row">
                    <span className="audit-k">Nearest Major Road</span>
                    <span className="audit-v mono">
                      {selectedStation.nearest_highway_m !== null
                        ? `${selectedStation.nearest_highway_m} m`
                        : 'N/A'}
                    </span>
                  </div>
                </div>
              </div>

              {/* Unavailable Data */}
              <div className="audit-box box-unavailable">
                <div className="audit-box-header">
                  <HelpCircle size={13} className="icon-amber" />
                  <strong>Unavailable Telemetry</strong>
                </div>
                <ul className="unavailable-bullet-list">
                  <li>
                    <strong>Real-time availability:</strong> Live session status is not exposed by public APIs.
                  </li>
                  <li>
                    <strong>Grid capacity:</strong> DISCOM feeder loading and transformer spare MVA are non-public data.
                  </li>
                </ul>
              </div>
            </div>
          ) : (
            <div className="empty-inspector">
              <p>Click any station marker on the map to inspect verified fields and estimates.</p>
            </div>
          )}
        </aside>
      </div>

      {/* Secondary District Summary Table */}
      <div className="secondary-section">
        <div className="secondary-section-header">
          <div>
            <h3 className="section-title">Delhi Administrative Districts</h3>
            <p className="section-subtitle">
              EV fleet demand, Switch Delhi supply, and power infrastructure by Census district
            </p>
          </div>
          <div className="district-toggle-controls">
            <span className="control-label-inline">EV Demand Method:</span>
            <select
              className="select-input-xs"
              value={useRedistributedCommercial ? 'REDISTRIBUTED' : 'ZONAL_ONLY'}
              onChange={(e) => setUseRedistributedCommercial(e.target.value === 'REDISTRIBUTED')}
            >
              <option value="REDISTRIBUTED">
                Zonal + Redistributed Commercial [549k EVs]
              </option>
              <option value="ZONAL_ONLY">
                Direct Zonal RTO Registrations Only [484k EVs]
              </option>
            </select>
          </div>
        </div>

        <div className="table-scroll">
          <table className="data-table">
            <thead>
              <tr>
                <th>District</th>
                <th className="num">2025 Pop (Est.)</th>
                <th className="num">Zonal RTO EVs</th>
                <th className="num">Total EV Demand</th>
                <th className="num">Charging Sites</th>
                <th className="num">Swapping Sites</th>
                <th className="num">Charging Points</th>
                <th className="num">BEE Connectors</th>
                <th className="num">Substations</th>
              </tr>
            </thead>
            <tbody>
              {bundle.districts_summary.map((d) => (
                <tr
                  key={d.district}
                  className={selectedDistrict === d.district ? 'tr-selected' : ''}
                  onClick={() => setSelectedDistrict((prev) => (prev === d.district ? 'ALL' : d.district))}
                >
                  <td>
                    <strong>{d.district}</strong>
                  </td>
                  <td className="num mono">{formatCompactIndian(d.ncp_2025_population_est)}</td>
                  <td className="num mono">{formatNumber(d.zonal_rto_ev_total)}</td>
                  <td className="num mono">
                    <strong>{formatNumber(d.estimated_total_ev_demand)}</strong>
                  </td>
                  <td className="num mono text-teal">{d.switch_delhi_charging_stations}</td>
                  <td className="num mono text-amber">
                    {d.switch_delhi_swap_geocoded + d.switch_delhi_swap_pin_estimated}
                  </td>
                  <td className="num mono">{formatNumber(d.switch_delhi_charging_points)}</td>
                  <td className="num mono">{formatNumber(d.bee_connectors)}</td>
                  <td className="num mono">{d.substations_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
