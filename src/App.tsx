import React, { useEffect, useState } from 'react';
import type { FeatureCollection } from 'geojson';
import {
  AlertCircle,
  BatteryCharging,
  BrainCircuit,
  Compass,
  FileCheck2,
  Globe2,
  Loader2,
  MapPin,
  RefreshCw,
} from 'lucide-react';
import {
  AiOptimizationBundle,
  AppDatasets,
  validateDelhiBundle,
  validateNationalBundle,
} from './types/data';
import { NationalOverviewView } from './components/NationalOverviewView';
import { DelhiPilotView } from './components/DelhiPilotView';
import { CoveragePlanningView } from './components/CoveragePlanningView';
import { DataAuditView } from './components/DataAuditView';
import { AiStudioView } from './components/AiStudioView';

type ActiveTab = 'DELHI_PILOT' | 'PLANNING' | 'AI_STUDIO' | 'DATA_AUDIT' | 'NATIONAL';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<ActiveTab>('DELHI_PILOT');
  const [datasets, setDatasets] = useState<AppDatasets | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadAllData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [natRes, indGeoRes, dlRes, dlDistGeoRes, dlRoadGeoRes, aiRes] = await Promise.all([
        fetch('/data/national_overview.json'),
        fetch('/data/india_states.geojson'),
        fetch('/data/delhi_pilot.json'),
        fetch('/data/delhi_districts.geojson'),
        fetch('/data/delhi_major_roads.geojson'),
        fetch('/data/ai_optimization_results.json').catch(() => null),
      ]);

      if (!natRes.ok || !indGeoRes.ok || !dlRes.ok || !dlDistGeoRes.ok || !dlRoadGeoRes.ok) {
        throw new Error('Failed to fetch one or more processed datasets from /data/*.json');
      }

      const [natJson, indGeoJson, dlJson, dlDistGeoJson, dlRoadGeoJson] = await Promise.all([
        natRes.json(),
        indGeoRes.json(),
        dlRes.json(),
        dlDistGeoRes.json(),
        dlRoadGeoRes.json(),
      ]);

      let aiJson: AiOptimizationBundle | null = null;
      if (aiRes && aiRes.ok) {
        try {
          aiJson = (await aiRes.json()) as AiOptimizationBundle;
        } catch {
          aiJson = null;
        }
      }

      const validatedNational = validateNationalBundle(natJson);
      const validatedDelhi = validateDelhiBundle(dlJson);

      setDatasets({
        national: validatedNational,
        indiaGeoJson: indGeoJson as FeatureCollection,
        delhi: validatedDelhi,
        delhiDistrictsGeoJson: dlDistGeoJson as FeatureCollection,
        delhiRoadsGeoJson: dlRoadGeoJson as FeatureCollection,
        aiOptimization: aiJson,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown data loading error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadAllData();
  }, []);

  return (
    <div className="app-shell">
      {/* Top Navigation Header */}
      <header className="app-header">
        <div className="brand-block">
          <div className="brand-icon">
            <BatteryCharging size={16} />
          </div>
          <div className="brand-title-row">
            <h1 className="brand-wordmark">GridSight EV</h1>
            <span className="brand-subtitle">Geospatial Infrastructure Intelligence</span>
          </div>
        </div>

        <nav className="main-nav" aria-label="Main Navigation">
          <button
            className={`nav-tab ${activeTab === 'DELHI_PILOT' ? 'nav-tab-active' : ''}`}
            onClick={() => setActiveTab('DELHI_PILOT')}
          >
            Delhi Map
          </button>
          <button
            className={`nav-tab ${activeTab === 'PLANNING' ? 'nav-tab-active' : ''}`}
            onClick={() => setActiveTab('PLANNING')}
          >
            Coverage Planning
          </button>
          <button
            className={`nav-tab ${activeTab === 'AI_STUDIO' ? 'nav-tab-active' : ''}`}
            onClick={() => setActiveTab('AI_STUDIO')}
            title="Explore Explainable Machine Learning Models & Siting Optimization"
            style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}
          >
            <BrainCircuit size={14} style={{ color: '#0d9488' }} />
            <span>AI &amp; Optimization</span>
          </button>
          <button
            className={`nav-tab ${activeTab === 'DATA_AUDIT' ? 'nav-tab-active' : ''}`}
            onClick={() => setActiveTab('DATA_AUDIT')}
          >
            Data &amp; Methodology
          </button>
          <button
            className={`nav-tab nav-tab-secondary ${activeTab === 'NATIONAL' ? 'nav-tab-active' : ''}`}
            onClick={() => setActiveTab('NATIONAL')}
            title="Explore 36 States/UTs National EV & Charger Overview"
          >
            National Overview
          </button>
        </nav>
      </header>

      {/* Main Content Area */}
      <main className="app-main">
        {loading && (
          <div className="state-box">
            <Loader2 size={32} className="spin icon-teal" />
            <h3>Loading Verified National &amp; Delhi Pilot Datasets...</h3>
            <p className="text-muted">
              Validating VAHAN (10.69M EVs), BEE (39,641 charger rows), Switch Delhi (876 stations), and
              spatial boundary layers...
            </p>
          </div>
        )}

        {error && (
          <div className="state-box error-box">
            <AlertCircle size={32} className="icon-rose" />
            <h3>Dataset Loading / Validation Error</h3>
            <p>{error}</p>
            <button className="btn-primary-sm" onClick={() => void loadAllData()}>
              <RefreshCw size={14} /> Retry Loading Datasets
            </button>
          </div>
        )}

        {!loading && !error && datasets && (
          <>
            {activeTab === 'NATIONAL' && (
              <NationalOverviewView
                bundle={datasets.national}
                indiaGeoJson={datasets.indiaGeoJson}
                onSelectDelhiPilot={() => setActiveTab('DELHI_PILOT')}
              />
            )}

            {activeTab === 'DELHI_PILOT' && (
              <DelhiPilotView
                bundle={datasets.delhi}
                districtsGeoJson={datasets.delhiDistrictsGeoJson}
                roadsGeoJson={datasets.delhiRoadsGeoJson}
                aiBundle={datasets.aiOptimization}
                onOpenPlanningView={() => setActiveTab('PLANNING')}
              />
            )}

            {activeTab === 'PLANNING' && (
              <CoveragePlanningView
                delhiBundle={datasets.delhi}
                delhiDistrictsGeoJson={datasets.delhiDistrictsGeoJson}
                nationalBundle={datasets.national}
                aiBundle={datasets.aiOptimization}
              />
            )}

            {activeTab === 'AI_STUDIO' && (
              <AiStudioView
                aiBundle={datasets.aiOptimization}
                onNavigateToPlanning={() => setActiveTab('PLANNING')}
              />
            )}

            {activeTab === 'DATA_AUDIT' && (
              <DataAuditView
                nationalBundle={datasets.national}
                delhiBundle={datasets.delhi}
              />
            )}
          </>
        )}
      </main>

      {/* Footer Attribution */}
      <footer className="app-footer">
        <div>
          <strong>Data Sources &amp; Attribution:</strong> MoRTH VAHAN4 (19 Oct 2026) • BEE EVPCS Registry (26
          Oct 2025) • PIB MHI/MoPNG PRID 2246042 &amp; 2246045 (01 Mar 2026) • GNCTD Switch Delhi Portal (19 Oct
          2026) • NITI Aayog IEMI 2025 • WorldPop 1km (CC BY 4.0) • DataMeet Boundaries (CC BY 4.0) •
          OpenStreetMap Contributors (ODbL 1.0).
        </div>
        <div className="mono">
          Physics-Informed Spatial AI (PIML) Suite • Zero Synthetic Data Used • Strict Source Separation
        </div>
      </footer>
    </div>
  );
};
