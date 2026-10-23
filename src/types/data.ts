import type { FeatureCollection } from 'geojson';

export interface YearTrendItem {
  year: number;
  registrations: number;
}

export interface CpoCountItem {
  cpo: string;
  rows: number;
}

export interface ConnectorCountItem {
  type: string;
  connectors: number;
}

export interface NationalStateRecord {
  state_code: string;
  state_name: string;
  admin2_name: string;
  // VAHAN Active EV Fleet (19 Oct 2026)
  vahan_date: string;
  total_ev_active: number;
  ev_2w: number;
  ev_3w: number;
  ev_4w_lmv_pv: number;
  ev_bus: number;
  ev_goods: number;
  ev_other: number;
  fuel_electric_bov: number;
  fuel_pure_ev: number;
  fuel_plugin_hybrid_ev: number;
  fuel_solar: number;
  fuel_hydrogen: number;
  status_active_compliant: number;
  status_active_non_compliant: number;
  non_compliant_share_pct: number;
  vahan_note: string | null;
  subcategories: Record<string, number>;
  yearwise_trend: YearTrendItem[];
  // BEE EVPCS Registry (26 Oct 2025) - kept strictly separate
  bee_date: string;
  bee_unique_stations: number;
  bee_unique_coords: number;
  bee_raw_charger_rows: number;
  bee_exact_duplicate_rows: number;
  bee_valid_bbox_rows: number;
  bee_invalid_coord_rows: number;
  bee_lat_eq_lon_rows: number;
  bee_total_connectors: number;
  bee_ac_connectors: number;
  bee_dc_connectors: number;
  bee_total_power_kw: number;
  bee_govt_rows: number;
  bee_private_rows: number;
  bee_omc_rows: number;
  bee_raw_state_strings: string[];
  bee_top_cpos: CpoCountItem[];
  bee_connector_breakdown: ConnectorCountItem[];
  // PIB MoPNG OMC Registry (01 Mar 2026) - kept strictly separate
  omc_date: string;
  omc_installed_total: number;
  omc_decommissioned: number;
  omc_operational_total: number;
  omc_operational_pct: number;
  omc_fy_trend: Record<string, number>;
  // PIB MHI FAME-II OMC Installed (01 Mar 2026) - kept strictly separate
  fame2_date: string;
  fame2_omc_installed: number;
  // OpenStreetMap Crowdsourced (19 Oct 2026) - kept strictly separate
  osm_date: string;
  osm_charging_stations: number;
  // Demographics, Tariffs & SNA Context
  area_sq_km: number | null;
  ncp_2025_population: number | null;
  gsdp_inr_crore: number | null;
  ev_tariff_fixed: string;
  ev_tariff_energy: string;
  ev_tariff_lt_rs_kwh: number | null;
  ev_tariff_ht_rs_kwh: number | null;
  state_nodal_agency: string;
  // Derived Analytical Indicators
  evs_per_bee_station: number | null;
  evs_per_bee_connector: number | null;
  ev_4w_per_dc_connector: number | null;
  bee_stations_per_100k_pop: number | null;
  bee_stations_per_1000_sq_km: number | null;
  est_operational_bee_stations: number;
}

export interface NationalDistrictCluster {
  id: string;
  state_code: string;
  state_name: string;
  district: string;
  latitude: number;
  longitude: number;
  unique_stations: number;
  charger_rows: number;
  total_connectors: number;
  dc_connectors: number;
  ac_connectors: number;
  total_power_kw: number;
  top_cpo: string;
  top_cpo_rows: number;
}

export interface NationalOverviewBundle {
  metadata: {
    generated_at: string;
    sources: {
      vahan: {
        organisation: string;
        reference_date: string;
        total_active_ev: number;
        active_compliant: number;
        active_non_compliant: number;
        fuel_labels_included: string[];
        fuel_labels_excluded: string[];
      };
      bee: {
        organisation: string;
        dataset: string;
        reference_date: string;
        published_date: string;
        filename_station_count: number;
        deduplicated_site_count: number;
        unique_coord_pairs: number;
        raw_charger_rows: number;
        exact_duplicate_rows: number;
        total_connectors: number;
        valid_bbox_rows: number;
        invalid_coord_rows: number;
        lat_eq_lon_iocl_rows: number;
      };
      pib_omc: {
        organisation: string;
        reference_date: string;
        published_date: string;
        installed_total: number;
        decommissioned_total: number;
        operational_total: number;
        operational_pct: number;
      };
      pib_fame2: {
        organisation: string;
        reference_date: string;
        published_date: string;
        total_sanctioned: number;
        total_operational: number;
        omc_installed: number;
        pse_installed: number;
        pse_entities: Array<Record<string, string>>;
      };
      osm: {
        organisation: string;
        reference_date: string;
        mapped_features: number;
      };
    };
    national_vahan_overview: {
      extraction_date: string;
      all_fuels_breakdown: Record<string, number>;
      ev_subcategories: Record<string, number>;
      ev_classes: Record<string, number>;
    };
  };
  states: NationalStateRecord[];
  district_hub_clusters: NationalDistrictCluster[];
}

export interface DelhiStationRecord {
  id: string;
  portal_id?: string | null;
  osm_id?: string;
  source: 'SWITCH_DELHI' | 'BEE' | 'OSM';
  source_date: string;
  station_type: 'Charging' | 'Battery Swapping';
  vendor: string;
  govt_private?: string;
  name: string;
  address: string;
  postal_code: string;
  district: string;
  portal_region?: string | null;
  latitude: number;
  longitude: number;
  coord_status: 'VERIFIED_COORDS' | 'PIN_CENTROID_ESTIMATE';
  charger_rows_merged?: number;
  no_of_chargers: number;
  total_connectors: number;
  dc_connectors: number;
  ac_connectors: number;
  swap_dockets?: number | null;
  max_capacity_kw: number | null;
  total_capacity_kw: number | null;
  charger_type: string;
  power_class: string;
  cost_per_unit: string;
  cost_per_unit_inr?: number | null;
  timing: string;
  payment_modes?: string;
  staff?: string;
  nearest_substation_m: number | null;
  nearest_highway_m: number | null;
}

export interface DelhiDistrictSummary {
  district: string;
  census_code: number;
  area_sq_km: number;
  worldpop_2020: number;
  ncp_2025_population_est: number;
  mapped_rtos: string[];
  zonal_rto_ev_total: number;
  zonal_rto_2w: number;
  zonal_rto_3w: number;
  zonal_rto_4w: number;
  zonal_rto_bus: number;
  zonal_rto_goods: number;
  redistributed_burari_commercial_ev: number;
  estimated_total_ev_demand: number;
  estimated_ev_2w: number;
  estimated_ev_3w: number;
  estimated_ev_4w: number;
  estimated_ev_bus: number;
  estimated_ev_goods: number;
  switch_delhi_charging_stations: number;
  switch_delhi_swap_geocoded: number;
  switch_delhi_swap_pin_estimated: number;
  switch_delhi_total_stations: number;
  switch_delhi_charging_points: number;
  switch_delhi_dc_points: number;
  switch_delhi_ac_points: number;
  switch_delhi_swap_dockets: number;
  bee_stations: number;
  bee_charger_rows: number;
  bee_connectors: number;
  bee_dc_connectors: number;
  bee_ac_connectors: number;
  bee_total_kw: number;
  osm_stations: number;
  substations_count: number;
  transformers_count: number;
  demand_attractors_count: number;
  major_road_ways_count: number;
  centroid_lat: number;
  centroid_lon: number;
  evs_per_switch_delhi_point: number;
  evs_per_bee_connector: number;
}

export interface DelhiRtoRecord {
  rto_code: string;
  rto_num: number;
  rto_name: string;
  total_ev_active: number;
  ev_2w: number;
  ev_3w: number;
  ev_4w_lmv_pv: number;
  ev_bus: number;
  ev_goods: number;
  is_centralized_commercial_unit: boolean;
  is_fitness_center_only: boolean;
}

export interface DelhiGridCell {
  cell_id: string;
  district: string;
  center_lat: number;
  center_lon: number;
  bounds: [[number, number], [number, number]];
  worldpop_2025_est: number;
  poi_count: number;
  transit_hub_count: number;
  commercial_poi_count: number;
  road_segments_count: number;
  substations_in_cell: number;
  nearest_substation_m: number;
  dist_switch_charging_km: number;
  dist_switch_swap_km: number;
  dist_bee_station_km: number;
  dist_dc_fast_km: number;
  dist_any_official_km: number;
  switch_stations_in_cell: number;
  switch_points_in_cell: number;
  bee_stations_in_cell: number;
  bee_connectors_in_cell: number;
  dc_connectors_in_cell: number;
  demand_score: number;
  ai_demand_score?: number;
  ai_predicted_kwh_day?: number;
}

export interface DelhiPowerNode {
  osm_id: string;
  power_type: 'substation' | 'transformer' | 'plant' | string;
  substation_type: string;
  name: string;
  operator: string;
  voltage: string;
  rating: string;
  district: string;
  latitude: number;
  longitude: number;
}

export interface DelhiDemandAttractor {
  osm_id: string;
  category: string;
  name: string;
  operator: string;
  district: string;
  latitude: number;
  longitude: number;
}

export interface DelhiPilotBundle {
  metadata: {
    pilot_geography: string;
    generated_at: string;
    niti_iemi_2025_rank: number;
    niti_iemi_2025_score: number;
    area_sq_km: number;
    ncp_2025_population: number;
    vahan_active_ev_total: number;
    vahan_zonal_rto_ev_total: number;
    vahan_burari_commercial_ev_total: number;
    sources: {
      switch_delhi: {
        url: string;
        reference_date: string;
        raw_records: number;
        exact_duplicates_removed: number;
        deduplicated_stations: number;
        charging_stations: number;
        battery_swapping_stations: number;
        verified_coord_stations: number;
        pin_centroid_estimated_swap_stations: number;
        total_charging_points: number;
      };
      bee_delhi: {
        url: string;
        reference_date: string;
        raw_charger_rows_in_delhi: number;
        deduplicated_stations: number;
        total_connectors: number;
        dc_connectors: number;
        ac_connectors: number;
        total_power_kw: number;
      };
      osm_delhi: {
        reference_date: string;
        mapped_stations: number;
      };
      context_layers: {
        power_nodes_total: number;
        substations: number;
        transformers: number;
        plants: number;
        demand_attractors: number;
        major_road_ways_raw: number;
        major_road_polylines_rendered: number;
      };
    };
  };
  rto_summary: DelhiRtoRecord[];
  districts_summary: DelhiDistrictSummary[];
  stations: {
    switch_delhi: DelhiStationRecord[];
    bee: DelhiStationRecord[];
    osm: DelhiStationRecord[];
  };
  grid_cells_2km: DelhiGridCell[];
  overlays: {
    power_nodes: DelhiPowerNode[];
    demand_attractors: DelhiDemandAttractor[];
  };
}

export interface FeatureImportanceItem {
  feature: string;
  importance: number;
}

export interface SpatialDemandRegressorInfo {
  model_type: string;
  r2_score: number;
  cv_r2_mean: number;
  cv_r2_std: number;
  mae: number;
  rmse: number;
  feature_importances: FeatureImportanceItem[];
  sample_size: number;
}

export interface BassDiffusionProjection {
  year: number;
  national_cumulative_evs: number;
  national_p10_low: number;
  national_p90_high: number;
  delhi_projected_fleet: number;
  is_forecast: boolean;
}

export interface BassDiffusionInfo {
  model_name: string;
  parameters: {
    p_innovation_coefficient: number;
    q_imitation_coefficient: number;
    M_market_potential_millions: number;
    r2_fit: number;
  };
  projections: BassDiffusionProjection[];
}

export interface OptimalSitedCandidate {
  cell_id: string;
  district: string;
  lat: number;
  lon: number;
  ai_demand_score: number;
  dist_to_existing_km: number;
  substation_dist_m: number;
  grid_feasibility_score: number;
  electrical_tier: string;
  max_hosting_kw: number;
  utility_score: number;
  worldpop: number;
  poi_count: number;
  transit_count: number;
  rank: number;
  recommended_ac_connectors: number;
  recommended_dc_fast_nozzles: number;
  recommended_swap_dockets: number;
  total_installed_load_kw: number;
}

export interface ConstrainedOptimizationInfo {
  k_stations_target: number;
  min_spacing_km: number;
  solver: string;
  total_optimal_sites: number;
  optimal_sites: OptimalSitedCandidate[];
}

export interface AiOptimizationBundle {
  metadata: {
    title: string;
    version: string;
    generated_at: string;
    competition: string;
  };
  spatial_demand_regressor: SpatialDemandRegressorInfo;
  bass_diffusion_forecasting: BassDiffusionInfo;
  constrained_siting_optimization: ConstrainedOptimizationInfo;
}

export interface AppDatasets {
  national: NationalOverviewBundle;
  indiaGeoJson: FeatureCollection;
  delhi: DelhiPilotBundle;
  delhiDistrictsGeoJson: FeatureCollection;
  delhiRoadsGeoJson: FeatureCollection;
  aiOptimization?: AiOptimizationBundle | null;
}

export function validateNationalBundle(data: unknown): NationalOverviewBundle {
  if (!data || typeof data !== 'object') {
    throw new Error('Invalid national_overview.json payload: expected object');
  }
  const obj = data as NationalOverviewBundle;
  if (!Array.isArray(obj.states) || obj.states.length !== 36) {
    throw new Error(`Schema validation failed: expected 36 states, got ${obj.states?.length}`);
  }
  return obj;
}

export function validateDelhiBundle(data: unknown): DelhiPilotBundle {
  if (!data || typeof data !== 'object') {
    throw new Error('Invalid delhi_pilot.json payload: expected object');
  }
  const obj = data as DelhiPilotBundle;
  if (!Array.isArray(obj.districts_summary) || obj.districts_summary.length === 0) {
    throw new Error('Schema validation failed: missing Delhi districts_summary');
  }
  if (!obj.stations || !Array.isArray(obj.stations.switch_delhi) || !Array.isArray(obj.stations.bee)) {
    throw new Error('Schema validation failed: missing Delhi stations arrays');
  }
  return obj;
}
