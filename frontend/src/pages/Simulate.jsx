import { useState } from 'react';
import { FlaskConical, Heart } from 'lucide-react';
import PatientForm, { DEFAULTS } from '../components/PatientForm';
import SimulationPanel from '../components/SimulationPanel';
import { predictRisk, simulateRisk } from '../api/client';

export default function SimulatePage() {
  const [basePatient, setBasePatient] = useState(null);
  const [beforeResult, setBeforeResult] = useState(null);
  const [simResult, setSimResult] = useState(null);
  const [loadingBase, setLoadingBase] = useState(false);
  const [loadingSim, setLoadingSim] = useState(false);
  const [error, setError] = useState(null);

  const handleBasePredict = async (formData) => {
    setLoadingBase(true);
    setError(null);
    setSimResult(null);
    try {
      const data = await predictRisk(formData);
      setBasePatient(formData);
      setBeforeResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Prediction failed.');
    } finally {
      setLoadingBase(false);
    }
  };

  const handleSimulate = async (patient, scenario) => {
    setLoadingSim(true);
    setError(null);
    try {
      const data = await simulateRisk(patient, scenario);
      setSimResult(data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Simulation failed.');
    } finally {
      setLoadingSim(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Hero */}
      <div className="text-center mb-10 animate-fade-in">
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-semibold text-violet-400 border border-violet-500/30 bg-violet-500/10 mb-4">
          <FlaskConical size={12} />
          Digital Twin Simulation
        </div>
        <h1 className="text-4xl md:text-5xl font-black font-display text-white mb-3">
          What-If{' '}
          <span className="text-gradient">Scenarios</span>
        </h1>
        <p className="text-slate-400 text-lg max-w-2xl mx-auto">
          Create a virtual patient, then simulate lifestyle changes — stop smoking, reduce BP, lose weight —
          and see how each intervention changes your projected heart risk.
        </p>
      </div>

      {error && (
        <div className="glass-card p-4 border border-red-500/30 bg-red-500/5 text-sm text-red-400 mb-6 max-w-xl mx-auto">
          <strong>Error:</strong> {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-8 items-start">
        {/* Step 1: Base patient */}
        <div className="lg:col-span-2">
          <div className="glass-card p-6 animate-slide-up">
            <div className="flex items-center gap-3 mb-5">
              <div className="w-7 h-7 rounded-full bg-teal-500 flex items-center justify-center text-xs font-bold text-white">1</div>
              <div>
                <h2 className="font-display font-bold text-white">Create Digital Twin</h2>
                <p className="text-xs text-slate-400">Set the baseline patient</p>
              </div>
              {beforeResult && (
                <div className="ml-auto risk-badge-low text-xs">✓ Ready</div>
              )}
            </div>
            <PatientForm onSubmit={handleBasePredict} loading={loadingBase} />
          </div>
        </div>

        {/* Step 2: Simulation */}
        <div className="lg:col-span-3 animate-slide-up animate-delay-100">
          <div className="flex items-center gap-3 mb-5">
            <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold text-white ${basePatient ? 'bg-teal-500' : 'bg-slate-700 text-slate-400'}`}>2</div>
            <div>
              <h2 className="font-display font-bold text-white">Run Simulation</h2>
              <p className="text-xs text-slate-400">Apply what-if changes</p>
            </div>
          </div>
          <SimulationPanel
            basePatient={basePatient}
            beforeResult={beforeResult}
            onSimulate={handleSimulate}
            simResult={simResult}
            loading={loadingSim}
          />
        </div>
      </div>
    </div>
  );
}
