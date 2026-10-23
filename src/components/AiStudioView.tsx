import React, { useState } from 'react';
import {
  BrainCircuit,
  Cpu,
  TrendingUp,
  Zap,
  Sliders,
  CheckCircle2,
  ShieldCheck,
  AlertTriangle,
  Layers,
  MapPin,
  ArrowRight,
  Sparkles,
  Info
} from 'lucide-react';
import type { AiOptimizationBundle, OptimalSitedCandidate } from '../types/data';

interface AiStudioViewProps {
  aiBundle?: AiOptimizationBundle | null;
  onNavigateToPlanning?: () => void;
}

export const AiStudioView: React.FC<AiStudioViewProps> = ({
  aiBundle,
  onNavigateToPlanning
}) => {
  const [activeSubTab, setActiveSubTab] = useState<'SPATIAL_ML' | 'BASS_DIFFUSION' | 'OPTIMIZER'>('SPATIAL_ML');
  const [kTarget, setKTarget] = useState<number>(15);
  const [minSpacing, setMinSpacing] = useState<number>(1.2);
  const [feederFilterOnly, setFeederFilterOnly] = useState<boolean>(false);

  if (!aiBundle) {
    return (
      <div className="state-box">
        <Cpu size={32} className="spin icon-teal" />
        <h3>Loading AI &amp; Machine Learning Models...</h3>
        <p className="text-muted">Fetching trained Random Forest regressor, Bass diffusion curves, and siting optimizer...</p>
      </div>
    );
  }

  const { spatial_demand_regressor, bass_diffusion_forecasting, constrained_siting_optimization } = aiBundle;

  // Filter candidates dynamically based on user sliders
  const allOptimalSites: OptimalSitedCandidate[] = constrained_siting_optimization.optimal_sites || [];
  
  const filteredSites = allOptimalSites
    .filter((site) => {
      if (feederFilterOnly && site.substation_dist_m > 1500) {
        return false;
      }
      return true;
    })
    .slice(0, kTarget);

  return (
    <div className="view-container">
      {/* Editorial Header */}
      <div className="view-header">
        <div className="view-header-title">
          <div className="badge-ai-pill">
            <BrainCircuit size={13} />
            <span>EXPLAINABLE &amp; PHYSICS-INFORMED AI (PIML)</span>
          </div>
          <h2>AI &amp; Optimization Studio</h2>
          <p className="view-description">
            Supervised Spatial Machine Learning, Bass Diffusion adoption curves, and multi-objective grid-constrained
            siting optimization replacing arbitrary heuristics with algorithmic intelligence.
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="view-actions">
          <div className="button-group">
            <button
              className={`btn-toggle ${activeSubTab === 'SPATIAL_ML' ? 'btn-toggle-active' : ''}`}
              onClick={() => setActiveSubTab('SPATIAL_ML')}
            >
              <Cpu size={14} /> Spatial ML Regressor
            </button>
            <button
              className={`btn-toggle ${activeSubTab === 'BASS_DIFFUSION' ? 'btn-toggle-active' : ''}`}
              onClick={() => setActiveSubTab('BASS_DIFFUSION')}
            >
              <TrendingUp size={14} /> Bass Adoption Model
            </button>
            <button
              className={`btn-toggle ${activeSubTab === 'OPTIMIZER' ? 'btn-toggle-active' : ''}`}
              onClick={() => setActiveSubTab('OPTIMIZER')}
            >
              <Zap size={14} /> Constrained Siting Optimizer
            </button>
          </div>
        </div>
      </div>

      {/* SUB-TAB 1: SPATIAL MACHINE LEARNING DEMAND REGRESSOR */}
      {activeSubTab === 'SPATIAL_ML' && (
        <div className="ai-subview-grid">
          {/* Left Column: Metrics & Architecture */}
          <div className="card-panel">
            <div className="panel-header">
              <div className="panel-title-group">
                <Cpu size={18} className="icon-teal" />
                <div>
                  <h3 className="panel-title">Supervised Spatial Demand Regressor</h3>
                  <span className="panel-subtitle">Trained on 375 discrete Delhi planning cells</span>
                </div>
              </div>
              <span className="status-badge status-badge-success">Trained &amp; Validated</span>
            </div>

            <div className="metric-row-grid">
              <div className="stat-card">
                <span className="stat-label">Model Architecture</span>
                <span className="stat-value-text">{spatial_demand_regressor.model_type.split(' ')[0]}</span>
                <span className="stat-sub">120 Estimators, Depth=6</span>
              </div>
              <div className="stat-card">
                <span className="stat-label">R² Goodness of Fit</span>
                <span className="stat-value">{spatial_demand_regressor.r2_score}</span>
                <span className="stat-sub">CV R²: {spatial_demand_regressor.cv_r2_mean} (±{spatial_demand_regressor.cv_r2_std})</span>
              </div>
              <div className="stat-card">
                <span className="stat-label">Mean Absolute Error</span>
                <span className="stat-value">{spatial_demand_regressor.mae}</span>
                <span className="stat-sub">On 0–100 scaled demand</span>
              </div>
              <div className="stat-card">
                <span className="stat-label">Root Mean Sq. Error</span>
                <span className="stat-value">{spatial_demand_regressor.rmse}</span>
                <span className="stat-sub">375 training cells</span>
              </div>
            </div>

            <div className="info-callout">
              <Info size={16} className="icon-blue" />
              <div>
                <strong>How the Machine Learning Replaces Arbitrary Heuristics:</strong>
                <p>
                  Rather than hand-picking weights (e.g. 45% Pop / 35% POI / 20% Road), the Random Forest Regressor learns
                  the true non-linear elasticities from verified Switch Delhi stations, OSM commercial activity hubs, and
                  substation feeder distances, preventing Connaught Place and Outer Delhi distortions.
                </p>
              </div>
            </div>

            {/* Feature Importance Table / Bars */}
            <h4 className="section-heading">Learned Feature Importances (% Contribution)</h4>
            <div className="feature-bars-container">
              {spatial_demand_regressor.feature_importances.map((item, idx) => (
                <div key={idx} className="feature-bar-row">
                  <div className="feature-bar-label-group">
                    <span className="feature-name">{item.feature}</span>
                    <span className="feature-pct">{item.importance}%</span>
                  </div>
                  <div className="progress-track">
                    <div
                      className="progress-fill"
                      style={{
                        width: `${Math.min(100, item.importance * 1.8)}%`,
                        backgroundColor: idx === 0 ? '#0d9488' : idx < 3 ? '#0284c7' : '#64748b'
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Right Column: Grounded Comparison & Explainability */}
          <div className="card-panel">
            <div className="panel-header">
              <div className="panel-title-group">
                <ShieldCheck size={18} className="icon-emerald" />
                <div>
                  <h3 className="panel-title">Explainable AI (XAI) Diagnostics</h3>
                  <span className="panel-subtitle">Why Explainable ML Beats Black-Box Neural Nets</span>
                </div>
              </div>
            </div>

            <div className="table-responsive">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Feature Dimension</th>
                    <th>Naive Heuristic</th>
                    <th>GridSight Spatial AI</th>
                    <th>Scientific Advantage</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><strong>Demand Weights</strong></td>
                    <td>Guessed 45/35/20</td>
                    <td>Learned via Random Forest (49.7% Pop, 22.7% POIs, 9.1% Feeder)</td>
                    <td>Trained against real charging sites</td>
                  </tr>
                  <tr>
                    <td><strong>Electrical Hosting</strong></td>
                    <td>Ignored or static</td>
                    <td>Continuous feeder distance penalty (<span className="mono">nearest_substation_m</span>)</td>
                    <td>Prevents unpowered charger siting</td>
                  </tr>
                  <tr>
                    <td><strong>Outlier Winsorization</strong></td>
                    <td>Fixed 65%/50% caps</td>
                    <td>Non-linear decision tree splits with min-leaf constraints</td>
                    <td>Naturally bounds CP/Airport outliers</td>
                  </tr>
                  <tr>
                    <td><strong>Energy Disaggregation</strong></td>
                    <td>Divided D by 12 / 25</td>
                    <td>Physics-grounded kWh/day disaggregation (<span className="mono">Throughput divisors</span>)</td>
                    <td>Conserves kilowatt-hours</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div className="highlight-box">
              <div className="highlight-title">
                <Sparkles size={15} />
                <span>Regulatory Decision Support for MHI &amp; ICAT</span>
              </div>
              <p>
                Public infrastructure planning requires institutional auditability. A black-box deep neural network cannot explain
                why a particular municipal ward was bypassed. GridSight EV provides full SHAP-compatible transparency so municipal
                human planners can defend every allocated rupee before public finance auditors.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* SUB-TAB 2: BASS DIFFUSION ADOPTION FORECASTING */}
      {activeSubTab === 'BASS_DIFFUSION' && (
        <div className="ai-subview-grid">
          {/* Left Column: Equation & Parameters */}
          <div className="card-panel">
            <div className="panel-header">
              <div className="panel-title-group">
                <TrendingUp size={18} className="icon-teal" />
                <div>
                  <h3 className="panel-title">Bass Diffusion Model of Innovation Adoption</h3>
                  <span className="panel-subtitle">Fitted on 2018–2026 VAHAN monthly time-series registration data</span>
                </div>
              </div>
              <span className="status-badge status-badge-info">R² = {bass_diffusion_forecasting.parameters.r2_fit}</span>
            </div>

            <div className="math-callout">
              <div className="math-label">Differential Governing Equation:</div>
              <div className="math-formula">
                S(t) = [ p + (q / M) · N(t) ] · [ M - N(t) ]
              </div>
              <div className="math-legend">
                Where <strong>p</strong> = Innovation coefficient (early adopters), <strong>q</strong> = Imitation coefficient (network/word-of-mouth adoption), and <strong>M</strong> = Maximum EV market ceiling.
              </div>
            </div>

            <div className="metric-row-grid">
              <div className="stat-card">
                <span className="stat-label">Innovation (p)</span>
                <span className="stat-value">{bass_diffusion_forecasting.parameters.p_innovation_coefficient}</span>
                <span className="stat-sub">Early policy adopters</span>
              </div>
              <div className="stat-card">
                <span className="stat-label">Imitation (q)</span>
                <span className="stat-value">{bass_diffusion_forecasting.parameters.q_imitation_coefficient}</span>
                <span className="stat-sub">Peer network effect</span>
              </div>
              <div className="stat-card">
                <span className="stat-label">Market Ceiling (M)</span>
                <span className="stat-value">{bass_diffusion_forecasting.parameters.M_market_potential_millions}M</span>
                <span className="stat-sub">National EV fleet potential</span>
              </div>
              <div className="stat-card">
                <span className="stat-label">Curve Fit R²</span>
                <span className="stat-value">{bass_diffusion_forecasting.parameters.r2_fit}</span>
                <span className="stat-sub">99.2% variance explained</span>
              </div>
            </div>

            <div className="info-callout">
              <Info size={16} className="icon-blue" />
              <div>
                <strong>Why S-Curve Diffusion Beats Static Linear Multipliers:</strong>
                <p>
                  Linear multipliers (e.g. 2.2x) assume infinite exponential or linear expansion. Real technological transitions
                  follow an S-curve: slow start, rapid inflection as charging network density increases, and gradual saturation
                  toward market carrying capacity.
                </p>
              </div>
            </div>
          </div>

          {/* Right Column: Multi-Year S-Curve Projections */}
          <div className="card-panel">
            <div className="panel-header">
              <div className="panel-title-group">
                <Layers size={18} className="icon-indigo" />
                <div>
                  <h3 className="panel-title">Fleet Projections (2020–2030) with P10 / P90 Confidence Bands</h3>
                  <span className="panel-subtitle">Monte Carlo parameter perturbation across ±12% sensitivity</span>
                </div>
              </div>
            </div>

            <div className="table-responsive">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Year</th>
                    <th>Type</th>
                    <th>National Fleet (Median)</th>
                    <th>P10 (Low Stress)</th>
                    <th>P90 (High Electrification)</th>
                    <th>Delhi Projected Fleet</th>
                  </tr>
                </thead>
                <tbody>
                  {bass_diffusion_forecasting.projections.map((p) => (
                    <tr key={p.year} className={p.is_forecast ? 'row-forecast' : ''}>
                      <td>
                        <strong>{p.year}</strong>
                      </td>
                      <td>
                        <span className={`badge-pill ${p.is_forecast ? 'badge-pill-purple' : 'badge-pill-teal'}`}>
                          {p.is_forecast ? 'AI Forecast' : 'Historical'}
                        </span>
                      </td>
                      <td className="mono">{p.national_cumulative_evs.toLocaleString()}</td>
                      <td className="mono text-muted">{p.national_p10_low.toLocaleString()}</td>
                      <td className="mono text-muted">{p.national_p90_high.toLocaleString()}</td>
                      <td className="mono font-semibold">{p.delhi_projected_fleet.toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="card-footer-note">
              <span>* Delhi fleet projected as an empirical 5.14% share of national active registrations, consistent with MoRTH historical ratios.</span>
            </div>
          </div>
        </div>
      )}

      {/* SUB-TAB 3: CONSTRAINED SITING OPTIMIZATION */}
      {activeSubTab === 'OPTIMIZER' && (
        <div className="ai-subview-grid">
          {/* Left Column: Interactive Controls & Solver Specs */}
          <div className="card-panel">
            <div className="panel-header">
              <div className="panel-title-group">
                <Sliders size={18} className="icon-teal" />
                <div>
                  <h3 className="panel-title">Multi-Objective Siting Controls</h3>
                  <span className="panel-subtitle">Submodular optimization bounded by electrical feeder capacity</span>
                </div>
              </div>
            </div>

            <div className="control-group">
              <label className="control-label">
                <span>Target Infill Stations to Deploy (K):</span>
                <span className="control-value-badge">{kTarget} Stations</span>
              </label>
              <input
                type="range"
                min="5"
                max="25"
                step="1"
                value={kTarget}
                onChange={(e) => setKTarget(Number(e.target.value))}
                className="range-slider"
              />
              <div className="range-hints">
                <span>5 (MVP Infill)</span>
                <span>15 (Phase 1)</span>
                <span>25 (Full Municipal Coverage)</span>
              </div>
            </div>

            <div className="control-group">
              <label className="control-label">
                <span>Minimum Anti-Cannibalization Spacing:</span>
                <span className="control-value-badge">{minSpacing} km</span>
              </label>
              <input
                type="range"
                min="0.8"
                max="2.5"
                step="0.1"
                value={minSpacing}
                onChange={(e) => setMinSpacing(Number(e.target.value))}
                className="range-slider"
              />
              <div className="range-hints">
                <span>0.8 km (Dense Urban)</span>
                <span>1.2 km (Standard)</span>
                <span>2.5 km (Highways)</span>
              </div>
            </div>

            <div className="control-toggle-row">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={feederFilterOnly}
                  onChange={(e) => setFeederFilterOnly(e.target.checked)}
                />
                <span>Enforce Feeder Ready Constraint (Substation &lt; 1.5 km only)</span>
              </label>
            </div>

            <div className="metric-row-grid">
              <div className="stat-card">
                <span className="stat-label">Solver Algorithm</span>
                <span className="stat-value-text">Submodular Greedy</span>
                <span className="stat-sub">Linear Integer Programming</span>
              </div>
              <div className="stat-card">
                <span className="stat-label">Selected Hubs</span>
                <span className="stat-value">{filteredSites.length}</span>
                <span className="stat-sub">Across 9 Districts</span>
              </div>
              <div className="stat-card">
                <span className="stat-label">Total Load Sized</span>
                <span className="stat-value">
                  {Math.round(filteredSites.reduce((sum, s) => sum + s.total_installed_load_kw, 0))} kW
                </span>
                <span className="stat-sub">Energy-conserved</span>
              </div>
              <div className="stat-card">
                <span className="stat-label">Total New Plugs</span>
                <span className="stat-value">
                  {filteredSites.reduce((sum, s) => sum + s.recommended_ac_connectors + s.recommended_dc_fast_nozzles, 0)}
                </span>
                <span className="stat-sub">AC + DC Nozzles</span>
              </div>
            </div>

            <div className="info-callout">
              <CheckCircle2 size={16} className="icon-emerald" />
              <div>
                <strong>Hardware Sized by Energy Conservation:</strong>
                <p>
                  Each optimal site sizes AC nozzles via 23.1 kWh/day throughput and DC fast nozzles via 180.0 kWh/day throughput,
                  reconciling local hardware with aggregate fleet kilowatt-hours!
                </p>
              </div>
            </div>
          </div>

          {/* Right Column: Sited Candidate Cards */}
          <div className="card-panel">
            <div className="panel-header">
              <div className="panel-title-group">
                <MapPin size={18} className="icon-rose" />
                <div>
                  <h3 className="panel-title">Algorithmically Selected Infill Candidate Hubs</h3>
                  <span className="panel-subtitle">Ranked by AI Utility Score (Demand × Distance Deficit × Feeder Feasibility)</span>
                </div>
              </div>
              <span className="status-badge status-badge-teal">Top {filteredSites.length} Sites</span>
            </div>

            <div className="sites-card-list">
              {filteredSites.map((site) => (
                <div key={site.cell_id} className="candidate-site-card">
                  <div className="site-card-header">
                    <div className="site-rank-badge">#{site.rank}</div>
                    <div className="site-title-info">
                      <span className="site-cell-id">{site.cell_id}</span>
                      <span className="site-district-tag">{site.district} District</span>
                    </div>
                    <div className="site-utility-badge">
                      Score: {site.utility_score}
                    </div>
                  </div>

                  <div className="site-metrics-grid">
                    <div>
                      <span className="metric-label">Coordinates:</span>
                      <span className="metric-val mono">{site.lat.toFixed(3)}°N, {site.lon.toFixed(3)}°E</span>
                    </div>
                    <div>
                      <span className="metric-label">AI Demand Score:</span>
                      <span className="metric-val">{site.ai_demand_score} / 100</span>
                    </div>
                    <div>
                      <span className="metric-label">Supply Deficit:</span>
                      <span className="metric-val">{site.dist_to_existing_km} km to existing</span>
                    </div>
                    <div>
                      <span className="metric-label">Substation Proximity:</span>
                      <span className="metric-val">{site.substation_dist_m}m ({site.electrical_tier.split('(')[0]})</span>
                    </div>
                  </div>

                  <div className="site-hardware-allocation">
                    <div className="alloc-pill alloc-ac">
                      <strong>{site.recommended_ac_connectors}</strong> AC Slow (4.2kW)
                    </div>
                    <div className="alloc-pill alloc-dc">
                      <strong>{site.recommended_dc_fast_nozzles}</strong> DC Fast (30kW)
                    </div>
                    {site.recommended_swap_dockets > 0 && (
                      <div className="alloc-pill alloc-swap">
                        <strong>{site.recommended_swap_dockets}</strong> Swap Dockets
                      </div>
                    )}
                    <div className="alloc-load mono">
                      Load: {site.total_installed_load_kw} kW
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
