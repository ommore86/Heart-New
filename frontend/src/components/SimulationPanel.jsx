import { useState } from 'react';
import { ArrowRight, TrendingDown, Cigarette, Dumbbell, Activity, Droplets, Scale, Zap } from 'lucide-react';
import RiskGauge from './RiskGauge';

const RISK_CONFIG = {
  Low:      { color: '#10b981', bg: 'bg-emerald-500/10', border: 'border-emerald-500/25', badgeClass: 'risk-badge-low' },
  Moderate: { color: '#f59e0b', bg: 'bg-amber-500/10',   border: 'border-amber-500/25',   badgeClass: 'risk-badge-moderate' },
  High:     { color: '#ef4444', bg: 'bg-red-500/10',      border: 'border-red-500/25',      badgeClass: 'risk-badge-high' },
};

function ScenarioSlider({ label, icon: Icon, field, value, onChange, min, max, step = 1, unit }) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="flex items-center gap-2 text-sm text-slate-300">
          <Icon size={14} className="text-slate-400" /> {label}
        </label>
        <span className={`text-sm font-bold font-display ${value < 0 ? 'text-teal-400' : value > 0 ? 'text-red-400' : 'text-slate-400'}`}>
          {value > 0 ? '+' : ''}{value}{unit}
        </span>
      </div>
      <input type="range" min={min} max={max} step={step} value={value}
        onChange={e => onChange(field, parseFloat(e.target.value))}
        className="w-full"
      />
      <div className="flex justify-between text-xs text-slate-600">
        <span>{min}{unit}</span>
        <span>0{unit}</span>
        <span>+{max}{unit}</span>
      </div>
    </div>
  );
}

function ComparePane({ label, result, side }) {
  if (!result) return (
    <div className={`glass-card p-6 flex items-center justify-center text-slate-500 text-sm min-h-64 ${side === 'before' ? 'opacity-70' : ''}`}>
      {side === 'before' ? 'Run a prediction first' : 'Configure scenario →'}
    </div>
  );

  const cfg = RISK_CONFIG[result.RiskCategory] || RISK_CONFIG.Moderate;
  return (
    <div className={`glass-card p-5 border ${cfg.border} space-y-3`}>
      <div className="flex items-center justify-between">
        <span className={`text-xs font-bold uppercase tracking-widest ${side === 'before' ? 'text-slate-400' : 'text-teal-400'}`}>
          {label}
        </span>
        <span className={cfg.badgeClass}>{result.RiskCategory}</span>
      </div>
      <div className="flex justify-center">
        <RiskGauge score={result.HeartRiskScore} size={220} />
      </div>
      <div className="grid grid-cols-2 gap-2 text-center">
        <div className="stat-tile">
          <span className="label">Risk Score</span>
          <span className="value" style={{ color: cfg.color }}>{result.HeartRiskScore.toFixed(1)}</span>
        </div>
        <div className="stat-tile">
          <span className="label">Probability</span>
          <span className="value" style={{ color: cfg.color }}>{(result.DiseaseProbability * 100).toFixed(1)}%</span>
        </div>
      </div>
    </div>
  );
}

export default function SimulationPanel({ basePatient, beforeResult, onSimulate, simResult, loading }) {
  const [scenario, setScenario] = useState({
    systolic_bp_delta: 0,
    diastolic_bp_delta: 0,
    cholesterol_delta: 0,
    glucose_delta: 0,
    stop_smoking: false,
    start_exercise: false,
    bmi_delta: 0,
    weight_delta: 0,
  });

  const handleScenarioChange = (field, value) => {
    setScenario(prev => ({ ...prev, [field]: value }));
  };

  const handleToggle = (field) => {
    setScenario(prev => ({ ...prev, [field]: !prev[field] }));
  };

  const handleSimulate = () => {
    if (!basePatient) return;
    onSimulate(basePatient, scenario);
  };

  const hasChanges = scenario.systolic_bp_delta !== 0 || scenario.diastolic_bp_delta !== 0 ||
    scenario.cholesterol_delta !== 0 || scenario.glucose_delta !== 0 ||
    scenario.stop_smoking || scenario.start_exercise || scenario.bmi_delta !== 0;

  return (
    <div className="space-y-6">
      {/* Scenario Configuration */}
      <div className="glass-card p-6 space-y-5">
        <div>
          <h3 className="font-display font-bold text-white text-lg mb-1">Configure Scenario</h3>
          <p className="text-sm text-slate-400">Adjust lifestyle and clinical parameters to see how risk changes.</p>
        </div>

        {/* BP changes */}
        <div>
          <p className="section-heading">Blood Pressure</p>
          <div className="space-y-4">
            <ScenarioSlider label="Systolic BP change" icon={Activity} field="systolic_bp_delta"
              value={scenario.systolic_bp_delta} onChange={handleScenarioChange}
              min={-60} max={60} unit=" mmHg" />
            <ScenarioSlider label="Diastolic BP change" icon={Activity} field="diastolic_bp_delta"
              value={scenario.diastolic_bp_delta} onChange={handleScenarioChange}
              min={-40} max={40} unit=" mmHg" />
          </div>
        </div>

        {/* Lab changes */}
        <div>
          <p className="section-heading">Lab Values</p>
          <div className="space-y-4">
            <ScenarioSlider label="Cholesterol change" icon={Droplets} field="cholesterol_delta"
              value={scenario.cholesterol_delta} onChange={handleScenarioChange}
              min={-100} max={100} unit=" mg/dL" />
            <ScenarioSlider label="Glucose change" icon={Zap} field="glucose_delta"
              value={scenario.glucose_delta} onChange={handleScenarioChange}
              min={-100} max={100} unit=" mg/dL" />
            <ScenarioSlider label="BMI change" icon={Scale} field="bmi_delta"
              value={scenario.bmi_delta} onChange={handleScenarioChange}
              min={-10} max={10} step={0.5} unit="" />
          </div>
        </div>

        {/* Lifestyle toggles */}
        <div>
          <p className="section-heading">Lifestyle Changes</p>
          <div className="space-y-3">
            {[
              { field: 'stop_smoking', label: 'Stop Smoking', icon: Cigarette },
              { field: 'start_exercise', label: 'Start Regular Exercise', icon: Dumbbell },
            ].map(({ field, label, icon: Icon }) => (
              <div key={field} className="flex items-center justify-between p-4 rounded-xl border border-white/[0.06] bg-white/[0.03]">
                <label className="flex items-center gap-2 text-sm font-medium text-slate-300">
                  <Icon size={15} className="text-slate-400" /> {label}
                </label>
                <button type="button" onClick={() => handleToggle(field)}
                  className={`relative inline-flex h-7 w-14 items-center rounded-full transition-all duration-300 ${scenario[field] ? 'bg-teal-500' : 'bg-slate-700'}`}>
                  <span className={`inline-block h-5 w-5 transform rounded-full bg-white shadow-lg transition-transform duration-300 ${scenario[field] ? 'translate-x-8' : 'translate-x-1'}`} />
                </button>
                <span className={`text-xs font-semibold w-6 ${scenario[field] ? 'text-teal-400' : 'text-slate-500'}`}>
                  {scenario[field] ? 'ON' : 'OFF'}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Applied changes */}
        {hasChanges && (
          <div className="bg-teal-500/10 border border-teal-500/25 rounded-xl p-3 space-y-1">
            <p className="text-xs font-semibold text-teal-400 mb-2">Changes to apply:</p>
            {scenario.systolic_bp_delta !== 0 && <p className="text-xs text-slate-300">• Systolic BP: {scenario.systolic_bp_delta > 0 ? '+' : ''}{scenario.systolic_bp_delta} mmHg</p>}
            {scenario.diastolic_bp_delta !== 0 && <p className="text-xs text-slate-300">• Diastolic BP: {scenario.diastolic_bp_delta > 0 ? '+' : ''}{scenario.diastolic_bp_delta} mmHg</p>}
            {scenario.cholesterol_delta !== 0 && <p className="text-xs text-slate-300">• Cholesterol: {scenario.cholesterol_delta > 0 ? '+' : ''}{scenario.cholesterol_delta} mg/dL</p>}
            {scenario.glucose_delta !== 0 && <p className="text-xs text-slate-300">• Glucose: {scenario.glucose_delta > 0 ? '+' : ''}{scenario.glucose_delta} mg/dL</p>}
            {scenario.bmi_delta !== 0 && <p className="text-xs text-slate-300">• BMI: {scenario.bmi_delta > 0 ? '+' : ''}{scenario.bmi_delta}</p>}
            {scenario.stop_smoking && <p className="text-xs text-slate-300">• Stop smoking ✓</p>}
            {scenario.start_exercise && <p className="text-xs text-slate-300">• Start exercising ✓</p>}
          </div>
        )}

        <button
          type="button"
          disabled={loading || !basePatient}
          onClick={handleSimulate}
          className="btn-primary w-full justify-center py-3.5"
        >
          {loading ? (
            <>
              <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
              </svg>
              Simulating…
            </>
          ) : (
            <>
              <TrendingDown size={16} />
              Run Digital Twin Simulation
            </>
          )}
        </button>
        {!basePatient && (
          <p className="text-xs text-center text-slate-500">Run a prediction first, then simulate scenarios.</p>
        )}
      </div>

      {/* Comparison panels */}
      <div>
        <h3 className="font-display font-bold text-white text-lg mb-4">Before vs. After</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-start">
          <ComparePane label="BEFORE" result={beforeResult} side="before" />
          <div className="hidden md:flex items-center justify-center">
            <div className="flex flex-col items-center gap-2">
              <ArrowRight size={24} className="text-teal-500" />
              {simResult && (
                <div className={`text-center px-3 py-1 rounded-full text-sm font-bold ${
                  simResult.improvement_percent > 0
                    ? 'bg-emerald-500/20 text-emerald-400'
                    : 'bg-red-500/20 text-red-400'
                }`}>
                  {simResult.improvement_percent > 0 ? '↓' : '↑'} {Math.abs(simResult.improvement_percent).toFixed(1)}%
                </div>
              )}
            </div>
          </div>
          <ComparePane label="AFTER SCENARIO" result={simResult?.after} side="after" />
        </div>
      </div>

      {/* Improvement summary */}
      {simResult && (
        <div className={`glass-card p-5 border space-y-4 animate-slide-up ${
          simResult.improvement_percent > 0 ? 'border-emerald-500/20 bg-emerald-500/5' : 'border-red-500/20 bg-red-500/5'
        }`}>
          <div className="flex items-center justify-between">
            <h4 className="font-display font-bold text-white">Simulation Summary</h4>
            <div className={`text-3xl font-black font-display ${simResult.improvement_percent > 0 ? 'text-emerald-400' : 'text-red-400'}`}>
              {simResult.improvement_percent > 0 ? '-' : '+'}{Math.abs(simResult.improvement_percent).toFixed(1)}%
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3 text-center">
            <div className="stat-tile">
              <span className="label">Before Score</span>
              <span className="value text-slate-300">{simResult.before.HeartRiskScore.toFixed(1)}</span>
            </div>
            <div className="stat-tile">
              <span className="label">After Score</span>
              <span className="value" style={{ color: simResult.improvement_percent > 0 ? '#10b981' : '#ef4444' }}>
                {simResult.after.HeartRiskScore.toFixed(1)}
              </span>
            </div>
            <div className="stat-tile">
              <span className="label">Risk Change</span>
              <span className="value" style={{ color: simResult.risk_delta > 0 ? '#10b981' : '#ef4444' }}>
                {simResult.risk_delta > 0 ? '-' : '+'}{Math.abs(simResult.risk_delta).toFixed(1)}
              </span>
            </div>
          </div>

          {simResult.scenario_applied?.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-teal-400 mb-2">Applied interventions:</p>
              <ul className="space-y-1">
                {simResult.scenario_applied.map((s, i) => (
                  <li key={i} className="text-sm text-slate-300 flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-teal-400 flex-shrink-0" />
                    {s}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
