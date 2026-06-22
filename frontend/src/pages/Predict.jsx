import { useState } from 'react';
import { Heart, Zap } from 'lucide-react';
import PatientForm from '../components/PatientForm';
import ResultCard from '../components/ResultCard';
import { predictRisk } from '../api/client';

export default function PredictPage() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (formData) => {
    setLoading(true);
    setError(null);
    try {
      const data = await predictRisk(formData);
      setResult(data);
      // Scroll to result on mobile
      setTimeout(() => {
        document.getElementById('result-section')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 100);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Prediction failed. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Hero */}
      <div className="text-center mb-10 animate-fade-in">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-semibold text-teal-400 border border-teal-500/30 bg-teal-500/10 mb-4">
          <Zap size={12} />
          AI-Powered Heart Risk Assessment
        </div>
        <h1 className="text-4xl md:text-5xl font-black font-display text-white mb-3">
          Digital Twin of the{' '}
          <span className="text-gradient">Heart</span>
        </h1>
        <p className="text-slate-400 text-lg max-w-2xl mx-auto">
          Enter patient vitals to generate a comprehensive cardiovascular risk score powered by three
          independent ML models: <span className="text-slate-300">Cardio</span>, <span className="text-slate-300">Framingham</span>, and <span className="text-slate-300">UCI Heart</span>.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
        {/* Form Panel */}
        <div className="glass-card p-6 animate-slide-up">
          <div className="flex items-center gap-2 mb-6">
            <div className="w-8 h-8 rounded-lg bg-teal-500/20 flex items-center justify-center">
              <Heart size={16} className="text-teal-400 animate-heartbeat" />
            </div>
            <div>
              <h2 className="font-display font-bold text-white">Patient Profile</h2>
              <p className="text-xs text-slate-400">Enter clinical parameters</p>
            </div>
          </div>
          <PatientForm onSubmit={handleSubmit} loading={loading} />
        </div>

        {/* Result Panel */}
        <div id="result-section" className="animate-slide-up animate-delay-100">
          {error && (
            <div className="glass-card p-5 border border-red-500/30 bg-red-500/5 text-sm text-red-400 mb-4">
              <strong>Error:</strong> {error}
            </div>
          )}
          {!result && !error && !loading && (
            <div className="glass-card p-12 flex flex-col items-center justify-center text-center space-y-4 min-h-80">
              <div className="w-16 h-16 rounded-full bg-teal-500/10 flex items-center justify-center">
                <Heart size={32} className="text-teal-500/50" />
              </div>
              <div>
                <h3 className="font-display font-semibold text-slate-300 mb-1">Awaiting Input</h3>
                <p className="text-sm text-slate-500">Fill in the patient form and click Predict to see the heart risk assessment.</p>
              </div>
            </div>
          )}
          {loading && (
            <div className="glass-card p-12 flex flex-col items-center justify-center text-center space-y-4 min-h-80">
              <div className="w-16 h-16 rounded-full bg-teal-500/10 flex items-center justify-center">
                <Heart size={32} className="text-teal-400 animate-heartbeat" />
              </div>
              <div>
                <h3 className="font-display font-semibold text-white mb-1">Analyzing…</h3>
                <p className="text-sm text-slate-400">Running ensemble prediction across 3 models</p>
              </div>
              <div className="flex gap-1">
                {[0, 1, 2].map(i => (
                  <div key={i} className="w-2 h-2 rounded-full bg-teal-400 animate-bounce" style={{ animationDelay: `${i * 0.15}s` }} />
                ))}
              </div>
            </div>
          )}
          {result && <ResultCard result={result} />}
        </div>
      </div>
    </div>
  );
}
