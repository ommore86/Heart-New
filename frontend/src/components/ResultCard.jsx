import { Heart, AlertTriangle, CheckCircle, Activity } from 'lucide-react';
import RiskGauge from './RiskGauge';
import ProbabilityChart from './ProbabilityChart';
import FeatureImportance from './FeatureImportance';

const RISK_CONFIG = {
  Low: {
    badgeClass: 'risk-badge-low',
    icon: CheckCircle,
    color: '#10b981',
    glowClass: 'shadow-glow-green',
    borderColor: 'border-emerald-500/20',
    bgColor: 'bg-emerald-500/5',
    message: 'Your heart health indicators are within normal range. Keep up the healthy lifestyle!',
  },
  Moderate: {
    badgeClass: 'risk-badge-moderate',
    icon: AlertTriangle,
    color: '#f59e0b',
    glowClass: 'shadow-glow-amber',
    borderColor: 'border-amber-500/20',
    bgColor: 'bg-amber-500/5',
    message: 'Some risk factors detected. Consider lifestyle modifications and consult your physician.',
  },
  High: {
    badgeClass: 'risk-badge-high',
    icon: AlertTriangle,
    color: '#ef4444',
    glowClass: 'shadow-glow-red',
    borderColor: 'border-red-500/20',
    bgColor: 'bg-red-500/5',
    message: 'Elevated cardiovascular risk detected. Please consult a cardiologist promptly.',
  },
};

export default function ResultCard({ result }) {
  if (!result) return null;

  const cfg = RISK_CONFIG[result.RiskCategory] || RISK_CONFIG.Moderate;
  const Icon = cfg.icon;

  return (
    <div className={`glass-card p-6 border ${cfg.borderColor} ${cfg.bgColor} animate-slide-up space-y-6`}>
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-lg font-display font-bold text-white mb-1">Risk Assessment</h2>
          <div className={cfg.badgeClass}>
            <Icon size={12} />
            {result.RiskCategory} Risk
          </div>
        </div>
        <div className="text-right">
          <div className="text-xs text-slate-400 mb-1">Disease Probability</div>
          <div className="text-2xl font-bold font-display" style={{ color: cfg.color }}>
            {(result.DiseaseProbability * 100).toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Gauge */}
      <div className="flex justify-center -my-2">
        <RiskGauge score={result.HeartRiskScore} size={260} />
      </div>

      {/* Advisory message */}
      <div className={`rounded-xl px-4 py-3 border ${cfg.borderColor} ${cfg.bgColor} flex gap-3 items-start`}>
        <Icon size={16} className="mt-0.5 flex-shrink-0" style={{ color: cfg.color }} />
        <p className="text-sm text-slate-300 leading-relaxed">{cfg.message}</p>
      </div>

      {/* Dataset probabilities */}
      <div className="glass-card p-4">
        <ProbabilityChart datasetProbabilities={result.DatasetProbabilities} />
      </div>

      {/* Feature importance */}
      {result.TopContributingFactors?.length > 0 && (
        <div className="glass-card p-4">
          <FeatureImportance contributions={result.TopContributingFactors} />
        </div>
      )}

      {/* Disclaimer */}
      <p className="text-xs text-slate-500 text-center leading-relaxed">
        ⚕️ This tool is for educational purposes only and does not constitute medical advice.
        Always consult a qualified healthcare professional.
      </p>
    </div>
  );
}
