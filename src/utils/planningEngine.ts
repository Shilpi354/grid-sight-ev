import type { DelhiDistrictSummary, DelhiGridCell, NationalStateRecord } from '../types/data';

export type CoverageNetworkBaseline =
  | 'ANY_OFFICIAL'
  | 'SWITCH_DELHI_CHARGING'
  | 'BEE_DELHI'
  | 'DC_FAST_ONLY'
  | 'BATTERY_SWAPPING';

export type GrowthScenarioId = 'LOW' | 'BASELINE' | 'HIGH';

export interface GrowthScenarioConfig {
  id: GrowthScenarioId;
  label: string;
  horizonYear: number;
  description: string;
  // Multipliers on active EV fleet from Oct 2026 baseline to 2030 (4-year compounding)
  multiplier2W: number;
  multiplier3W: number;
  multiplier4W: number;
  multiplierBus: number;
  multiplierGoods: number;
  // Share of daily vehicle energy demand met by public charging/swapping (vs home/depot charging)
  publicChargingShare2W: number;
  publicChargingShare3W: number;
  publicChargingShare4W: number;
  publicChargingShareBus: number;
  publicChargingShareGoods: number;
  // Share of 2W & 3W public energy demand served via Battery Swapping (vs plug-in AC/LEV DC)
  swapShareOfPublic2W3W: number;
  // Effective daily dispensing hours per connector/docket (accounting for queuing & peak hours)
  effectiveHoursPerDayAC: number;      // e.g., 5.5 hrs/day at average 3.5 kW = 19.25 kWh/day per AC connector
  effectiveHoursPerDayDC: number;      // e.g., 6.0 hrs/day at average 30 kW = 180 kWh/day per DC nozzle
  swapsPerDocketPerDay: number;        // e.g., 14 swaps/day per docket (~2.0 kWh/swap = 28 kWh/day)
}

export const DEFAULT_SCENARIOS: Record<GrowthScenarioId, GrowthScenarioConfig> = {
  LOW: {
    id: 'LOW',
    label: 'Conservative (Low Growth — 2030)',
    horizonYear: 2030,
    description:
      'Assumes ~14% CAGR across 2W/3W and ~16% CAGR for 4W/Commercial (1.68x–1.81x current Oct 2026 fleet by 2030), with higher reliance on residential overnight charging.',
    multiplier2W: 1.70,
    multiplier3W: 1.55,
    multiplier4W: 1.80,
    multiplierBus: 1.65,
    multiplierGoods: 1.75,
    publicChargingShare2W: 0.15,
    publicChargingShare3W: 0.45,
    publicChargingShare4W: 0.25,
    publicChargingShareBus: 0.15, // 85% charged at dedicated DTC/Cluster bus depots
    publicChargingShareGoods: 0.40,
    swapShareOfPublic2W3W: 0.28,
    effectiveHoursPerDayAC: 6.0,
    effectiveHoursPerDayDC: 6.5,
    swapsPerDocketPerDay: 14,
  },
  BASELINE: {
    id: 'BASELINE',
    label: 'Baseline Policy Trajectory (2030)',
    horizonYear: 2030,
    description:
      'Aligns with observed VAHAN 2023–2026 trajectory (~22% CAGR for 2W/4W, ~18% for 3W, ~25% for e-Buses/Goods), with moderate public opportunity charging and battery swapping.',
    multiplier2W: 2.20,
    multiplier3W: 1.90,
    multiplier4W: 2.35,
    multiplierBus: 2.40,
    multiplierGoods: 2.30,
    publicChargingShare2W: 0.20,
    publicChargingShare3W: 0.55,
    publicChargingShare4W: 0.32,
    publicChargingShareBus: 0.20,
    publicChargingShareGoods: 0.50,
    swapShareOfPublic2W3W: 0.35,
    effectiveHoursPerDayAC: 5.5,
    effectiveHoursPerDayDC: 6.0,
    swapsPerDocketPerDay: 12,
  },
  HIGH: {
    id: 'HIGH',
    label: 'High Accelerated Electrification (2030)',
    horizonYear: 2030,
    description:
      'Models rapid commercial fleet & ride-hailing electrification (~28–32% CAGR) with dense urban apartment dwellers relying heavily on public curb/hub charging.',
    multiplier2W: 2.85,
    multiplier3W: 2.35,
    multiplier4W: 3.10,
    multiplierBus: 3.00,
    multiplierGoods: 3.00,
    publicChargingShare2W: 0.28,
    publicChargingShare3W: 0.65,
    publicChargingShare4W: 0.42,
    publicChargingShareBus: 0.25,
    publicChargingShareGoods: 0.60,
    swapShareOfPublic2W3W: 0.40,
    effectiveHoursPerDayAC: 5.0,
    effectiveHoursPerDayDC: 5.5,
    swapsPerDocketPerDay: 11,
  },
};

/**
 * Documented vehicle energy consumption assumptions (Indian urban driving conditions):
 * - 2W: 32 km/day * 0.032 kWh/km = 1.024 kWh/day
 * - 3W (e-rickshaw / e-auto): 85 km/day * 0.075 kWh/km = 6.375 kWh/day
 * - 4W (LMV / e-cab / passenger car): 48 km/day * 0.145 kWh/km = 6.96 kWh/day
 * - E-Bus: 180 km/day * 1.15 kWh/km = 207.0 kWh/day
 * - E-Goods (L5N / LGV): 75 km/day * 0.18 kWh/km = 13.5 kWh/day
 */
export const DAILY_VEHICLE_KWH = {
  ev2W: 1.024,
  ev3W: 6.375,
  ev4W: 6.96,
  evBus: 207.0,
  evGoods: 13.5,
};

export interface EvaluatedGridCell extends DelhiGridCell {
  selectedDistanceKm: number;
  isCovered: boolean;
  isUnderservedPriority: boolean;
  priorityScore: number;
  recommendedAcConnectors: number;
  recommendedDcConnectors: number;
  recommendedStations: number;
}

export interface CoverageEvaluationSummary {
  totalCells: number;
  coveredCells: number;
  uncoveredCells: number;
  underservedPriorityCells: number;
  areaCoveredPct: number;
  populationCoveredPct: number;
  populationInUnderservedPriority: number;
  poisCoveredPct: number;
  evaluatedCells: EvaluatedGridCell[];
  topUnderservedCells: EvaluatedGridCell[];
}

export function getCellDistanceForBaseline(
  cell: DelhiGridCell,
  baseline: CoverageNetworkBaseline
): number {
  switch (baseline) {
    case 'ANY_OFFICIAL':
      return cell.dist_any_official_km;
    case 'SWITCH_DELHI_CHARGING':
      return cell.dist_switch_charging_km;
    case 'BEE_DELHI':
      return cell.dist_bee_station_km;
    case 'DC_FAST_ONLY':
      return cell.dist_dc_fast_km;
    case 'BATTERY_SWAPPING':
      return cell.dist_switch_swap_km;
  }
}

export function evaluateDelhiGridCoverage(
  cells: DelhiGridCell[],
  radiusKm: number,
  baseline: CoverageNetworkBaseline,
  minDemandScoreForPriority: number = 22,
  useAiDemandModel: boolean = true,
  useContinuousDecay: boolean = true
): CoverageEvaluationSummary {
  let coveredCells = 0;
  let underservedPriorityCells = 0;
  let totalPop = 0;
  let coveredPop = 0;
  let underservedPriorityPop = 0;
  let totalPois = 0;
  let coveredPois = 0;

  const evaluatedCells: EvaluatedGridCell[] = cells.map((cell) => {
    const distKm = getCellDistanceForBaseline(cell, baseline);
    const isCovered = distKm <= radiusKm;
    
    // Choose between AI Machine Learning Demand Score vs Heuristic
    const activeDemandScore = useAiDemandModel && cell.ai_demand_score !== undefined
      ? cell.ai_demand_score
      : cell.demand_score;

    const isUnderservedPriority = !isCovered && activeDemandScore >= minDemandScoreForPriority;

    totalPop += cell.worldpop_2025_est;
    totalPois += cell.poi_count;
    if (isCovered) {
      coveredCells += 1;
      coveredPop += cell.worldpop_2025_est;
      coveredPois += cell.poi_count;
    } else if (isUnderservedPriority) {
      underservedPriorityCells += 1;
      underservedPriorityPop += cell.worldpop_2025_est;
    }

    // Priority score calculation:
    // Option A: Continuous Sigmoid Distance Decay: S = D * (1 - 1 / (1 + (d/r)^4))
    // Option B: Step function heuristic with linear deficit factor
    let priorityScore = 0;
    if (useContinuousDecay) {
      const decayFactor = 1.0 - 1.0 / (1.0 + Math.pow(distKm / Math.max(0.1, radiusKm), 4));
      priorityScore = isCovered ? 0 : Number((activeDemandScore * decayFactor * 1.25).toFixed(1));
    } else {
      const distDeficitFactor = isCovered ? 0 : Math.min(2.0, (distKm - radiusKm) / Math.max(0.5, radiusKm));
      priorityScore = isCovered
        ? 0
        : Number((activeDemandScore * (0.65 + 0.35 * distDeficitFactor)).toFixed(1));
    }

    // Recommend station sizing for underserved priority cells based on physics-grounded energy demand
    const recAc = isUnderservedPriority ? Math.max(2, Math.round(activeDemandScore / 10)) : 0;
    const recDc = isUnderservedPriority ? Math.max(1, Math.round((activeDemandScore + cell.transit_hub_count * 5) / 20)) : 0;
    const recStations = isUnderservedPriority ? Math.max(1, Math.ceil((recAc + recDc) / 6)) : 0;

    return {
      ...cell,
      selectedDistanceKm: distKm,
      isCovered,
      isUnderservedPriority,
      priorityScore,
      recommendedAcConnectors: recAc,
      recommendedDcConnectors: recDc,
      recommendedStations: recStations,
    };
  });

  const topUnderservedCells = [...evaluatedCells]
    .filter((c) => c.isUnderservedPriority)
    .sort((a, b) => b.priorityScore - a.priorityScore);

  const totalCells = cells.length;
  return {
    totalCells,
    coveredCells,
    uncoveredCells: totalCells - coveredCells,
    underservedPriorityCells,
    areaCoveredPct: Number(((100 * coveredCells) / Math.max(1, totalCells)).toFixed(1)),
    populationCoveredPct: Number(((100 * coveredPop) / Math.max(1, totalPop)).toFixed(1)),
    populationInUnderservedPriority: underservedPriorityPop,
    poisCoveredPct: Number(((100 * coveredPois) / Math.max(1, totalPois)).toFixed(1)),
    evaluatedCells,
    topUnderservedCells,
  };
}

export interface FutureRequirementRow {
  geographyName: string;
  currentActiveEvs: number;
  projectedActiveEvs: number;
  dailyPublicPlugInKwh: number;
  dailyPublicSwapKwh: number;
  // Existing supply (explicitly separated by unit)
  existingStations: number;
  existingChargingPoints: number;
  existingAcConnectors: number;
  existingDcConnectors: number;
  existingSwapDockets: number;
  // Gross required supply in target horizon year
  requiredTotalAcConnectors: number;
  requiredTotalDcConnectors: number;
  requiredTotalConnectors: number;
  requiredTotalChargingPoints: number;
  requiredTotalStations: number;
  requiredTotalSwapDockets: number;
  // Net new additions needed
  netNewAcConnectors: number;
  netNewDcConnectors: number;
  netNewConnectors: number;
  netNewChargingPoints: number;
  netNewStations: number;
  netNewSwapDockets: number;
  addedInstalledPowerKw: number;
}

/**
 * Calculates transparent, assumption-driven future charger requirements for Delhi districts
 * or National states without inventing any universal fixed EV-to-charger ratio.
 */
export function computeDelhiDistrictFutureRequirements(
  districts: DelhiDistrictSummary[],
  scenario: GrowthScenarioConfig,
  supplyBaseline: 'SWITCH_DELHI' | 'BEE_DELHI',
  useRedistributedCommercialDemand: boolean = true
): FutureRequirementRow[] {
  // Average rated power per AC connector (4.2 kW blend of 3.3kW LEV AC and 7.4kW Type-2)
  // Average rated power per DC connector (30.0 kW blend of 15kW Bharat DC-001 and 30-60kW CCS2)
  const avgAcPowerKw = 4.2;
  const avgDcPowerKw = 30.0;
  const dailyCapPerAcConnectorKwh = avgAcPowerKw * scenario.effectiveHoursPerDayAC;
  const dailyCapPerDcConnectorKwh = avgDcPowerKw * scenario.effectiveHoursPerDayDC;
  const kwhPerBatterySwap = 2.1; // average 2W/3W swappable pack energy per swap
  const dailyCapPerSwapDocketKwh = scenario.swapsPerDocketPerDay * kwhPerBatterySwap;

  return districts.map((d) => {
    const base2W = useRedistributedCommercialDemand ? d.estimated_ev_2w : d.zonal_rto_2w;
    const base3W = useRedistributedCommercialDemand ? d.estimated_ev_3w : d.zonal_rto_3w;
    const base4W = useRedistributedCommercialDemand ? d.estimated_ev_4w : d.zonal_rto_4w;
    const baseBus = useRedistributedCommercialDemand ? d.estimated_ev_bus : d.zonal_rto_bus;
    const baseGoods = useRedistributedCommercialDemand ? d.estimated_ev_goods : d.zonal_rto_goods;
    const currentTotal = base2W + base3W + base4W + baseBus + baseGoods;

    const proj2W = Math.round(base2W * scenario.multiplier2W);
    const proj3W = Math.round(base3W * scenario.multiplier3W);
    const proj4W = Math.round(base4W * scenario.multiplier4W);
    const projBus = Math.round(baseBus * scenario.multiplierBus);
    const projGoods = Math.round(baseGoods * scenario.multiplierGoods);
    const projectedTotal = proj2W + proj3W + proj4W + projBus + projGoods;

    // Public daily energy demand (kWh/day)
    const pub2WKwh = proj2W * DAILY_VEHICLE_KWH.ev2W * scenario.publicChargingShare2W;
    const pub3WKwh = proj3W * DAILY_VEHICLE_KWH.ev3W * scenario.publicChargingShare3W;
    const pub4WKwh = proj4W * DAILY_VEHICLE_KWH.ev4W * scenario.publicChargingShare4W;
    const pubBusKwh = projBus * DAILY_VEHICLE_KWH.evBus * scenario.publicChargingShareBus;
    const pubGoodsKwh = projGoods * DAILY_VEHICLE_KWH.evGoods * scenario.publicChargingShareGoods;

    // Split 2W/3W public energy between Battery Swapping and Plug-in AC/LEV-DC
    const swapKwh = (pub2WKwh + pub3WKwh) * scenario.swapShareOfPublic2W3W;
    const plugIn2W3WKwh = (pub2WKwh + pub3WKwh) * (1 - scenario.swapShareOfPublic2W3W);

    // AC connectors serve 85% of 2W/3W plug-in + 35% of 4W public charging + 25% of Goods public charging
    const dailyAcDemandKwh = plugIn2W3WKwh * 0.85 + pub4WKwh * 0.35 + pubGoodsKwh * 0.25;
    // DC fast connectors serve 15% of 2W/3W plug-in (LEV DC) + 65% of 4W + 75% of Goods + 100% of public opportunity Bus charging
    const dailyDcDemandKwh = plugIn2W3WKwh * 0.15 + pub4WKwh * 0.65 + pubGoodsKwh * 0.75 + pubBusKwh;

    const reqAcConnectors = Math.ceil(dailyAcDemandKwh / Math.max(1, dailyCapPerAcConnectorKwh));
    const reqDcConnectors = Math.ceil(dailyDcDemandKwh / Math.max(1, dailyCapPerDcConnectorKwh));
    const reqTotalConnectors = reqAcConnectors + reqDcConnectors;
    // Distinguish Charging Points (EVSE units: typically 1 per AC charger, 1 EVSE per 1.4 DC dual-gun chargers)
    const reqChargingPoints = reqAcConnectors + Math.ceil(reqDcConnectors / 1.35);
    // Distinguish Physical Charging Stations (assuming average 4.5 charging points per multi-charger urban station)
    const reqStations = Math.ceil(reqChargingPoints / 4.5);
    const reqSwapDockets = Math.ceil(swapKwh / Math.max(1, dailyCapPerSwapDocketKwh));

    const existingStations =
      supplyBaseline === 'SWITCH_DELHI' ? d.switch_delhi_charging_stations : d.bee_stations;
    const existingChargingPoints =
      supplyBaseline === 'SWITCH_DELHI' ? d.switch_delhi_charging_points : d.bee_charger_rows;
    const existingAcConnectors =
      supplyBaseline === 'SWITCH_DELHI' ? d.switch_delhi_ac_points : d.bee_ac_connectors;
    const existingDcConnectors =
      supplyBaseline === 'SWITCH_DELHI' ? d.switch_delhi_dc_points : d.bee_dc_connectors;
    const existingSwapDockets = d.switch_delhi_swap_dockets;

    const netNewAc = Math.max(0, reqAcConnectors - existingAcConnectors);
    const netNewDc = Math.max(0, reqDcConnectors - existingDcConnectors);
    const netNewConnectors = netNewAc + netNewDc;
    const netNewPoints = Math.max(0, reqChargingPoints - existingChargingPoints);
    const netNewStations = Math.max(0, reqStations - existingStations);
    const netNewSwapDockets = Math.max(0, reqSwapDockets - existingSwapDockets);
    const addedKw = Math.round(netNewAc * avgAcPowerKw + netNewDc * avgDcPowerKw);

    return {
      geographyName: d.district,
      currentActiveEvs: currentTotal,
      projectedActiveEvs: projectedTotal,
      dailyPublicPlugInKwh: Math.round(dailyAcDemandKwh + dailyDcDemandKwh),
      dailyPublicSwapKwh: Math.round(swapKwh),
      existingStations,
      existingChargingPoints,
      existingAcConnectors,
      existingDcConnectors,
      existingSwapDockets,
      requiredTotalAcConnectors: reqAcConnectors,
      requiredTotalDcConnectors: reqDcConnectors,
      requiredTotalConnectors: reqTotalConnectors,
      requiredTotalChargingPoints: reqChargingPoints,
      requiredTotalStations: reqStations,
      requiredTotalSwapDockets: reqSwapDockets,
      netNewAcConnectors: netNewAc,
      netNewDcConnectors: netNewDc,
      netNewConnectors,
      netNewChargingPoints: netNewPoints,
      netNewStations,
      netNewSwapDockets,
      addedInstalledPowerKw: addedKw,
    };
  });
}

export function computeNationalStateFutureRequirements(
  states: NationalStateRecord[],
  scenario: GrowthScenarioConfig
): FutureRequirementRow[] {
  const avgAcPowerKw = 4.2;
  const avgDcPowerKw = 30.0;
  const dailyCapPerAcConnectorKwh = avgAcPowerKw * scenario.effectiveHoursPerDayAC;
  const dailyCapPerDcConnectorKwh = avgDcPowerKw * scenario.effectiveHoursPerDayDC;
  const dailyCapPerSwapDocketKwh = scenario.swapsPerDocketPerDay * 2.1;

  return states.map((s) => {
    const proj2W = Math.round(s.ev_2w * scenario.multiplier2W);
    const proj3W = Math.round(s.ev_3w * scenario.multiplier3W);
    const proj4W = Math.round(s.ev_4w_lmv_pv * scenario.multiplier4W);
    const projBus = Math.round(s.ev_bus * scenario.multiplierBus);
    const projGoods = Math.round(s.ev_goods * scenario.multiplierGoods);
    const projectedTotal = proj2W + proj3W + proj4W + projBus + projGoods;

    const pub2WKwh = proj2W * DAILY_VEHICLE_KWH.ev2W * scenario.publicChargingShare2W;
    const pub3WKwh = proj3W * DAILY_VEHICLE_KWH.ev3W * scenario.publicChargingShare3W;
    const pub4WKwh = proj4W * DAILY_VEHICLE_KWH.ev4W * scenario.publicChargingShare4W;
    const pubBusKwh = projBus * DAILY_VEHICLE_KWH.evBus * scenario.publicChargingShareBus;
    const pubGoodsKwh = projGoods * DAILY_VEHICLE_KWH.evGoods * scenario.publicChargingShareGoods;

    const swapKwh = (pub2WKwh + pub3WKwh) * scenario.swapShareOfPublic2W3W;
    const plugIn2W3WKwh = (pub2WKwh + pub3WKwh) * (1 - scenario.swapShareOfPublic2W3W);

    const dailyAcDemandKwh = plugIn2W3WKwh * 0.85 + pub4WKwh * 0.35 + pubGoodsKwh * 0.25;
    const dailyDcDemandKwh = plugIn2W3WKwh * 0.15 + pub4WKwh * 0.65 + pubGoodsKwh * 0.75 + pubBusKwh;

    const reqAcConnectors = Math.ceil(dailyAcDemandKwh / Math.max(1, dailyCapPerAcConnectorKwh));
    const reqDcConnectors = Math.ceil(dailyDcDemandKwh / Math.max(1, dailyCapPerDcConnectorKwh));
    const reqTotalConnectors = reqAcConnectors + reqDcConnectors;
    const reqChargingPoints = reqAcConnectors + Math.ceil(reqDcConnectors / 1.35);
    const reqStations = Math.ceil(reqChargingPoints / 3.5);
    const reqSwapDockets = Math.ceil(swapKwh / Math.max(1, dailyCapPerSwapDocketKwh));

    const netNewAc = Math.max(0, reqAcConnectors - s.bee_ac_connectors);
    const netNewDc = Math.max(0, reqDcConnectors - s.bee_dc_connectors);
    const netNewConnectors = netNewAc + netNewDc;
    const netNewPoints = Math.max(0, reqChargingPoints - s.bee_raw_charger_rows);
    const netNewStations = Math.max(0, reqStations - s.bee_unique_stations);
    const addedKw = Math.round(netNewAc * avgAcPowerKw + netNewDc * avgDcPowerKw);

    return {
      geographyName: s.state_name,
      currentActiveEvs: s.total_ev_active,
      projectedActiveEvs: projectedTotal,
      dailyPublicPlugInKwh: Math.round(dailyAcDemandKwh + dailyDcDemandKwh),
      dailyPublicSwapKwh: Math.round(swapKwh),
      existingStations: s.bee_unique_stations,
      existingChargingPoints: s.bee_raw_charger_rows,
      existingAcConnectors: s.bee_ac_connectors,
      existingDcConnectors: s.bee_dc_connectors,
      existingSwapDockets: 0,
      requiredTotalAcConnectors: reqAcConnectors,
      requiredTotalDcConnectors: reqDcConnectors,
      requiredTotalConnectors: reqTotalConnectors,
      requiredTotalChargingPoints: reqChargingPoints,
      requiredTotalStations: reqStations,
      requiredTotalSwapDockets: reqSwapDockets,
      netNewAcConnectors: netNewAc,
      netNewDcConnectors: netNewDc,
      netNewConnectors,
      netNewChargingPoints: netNewPoints,
      netNewStations,
      netNewSwapDockets: reqSwapDockets,
      addedInstalledPowerKw: addedKw,
    };
  });
}
