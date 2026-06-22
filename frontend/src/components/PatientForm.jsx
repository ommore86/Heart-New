import { useState } from 'react';
import { Activity, Heart, Cigarette, Dumbbell, Droplets, Zap, User, Scale } from 'lucide-react';

const DEFAULTS = {
  age: 45,
  gender: 1,
  systolic_bp: 120,
  diastolic_bp: 80,
  cholesterol: 200,
  glucose: 90,
  smoking: 0,
  physical_activity: 1,
  bmi: 25.0,
  heart_rate: 72,
  alcohol: 0,
};

function SliderField({ label, icon: Icon, name, value, onChange, min, max, step = 1, unit, color = 'teal' }) {
  const pct = ((value - min) / (max - min)) * 100;
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="flex items-center gap-2 text-sm font-medium text-slate-300">
          <Icon size={15} className={`text-${color}-400`} />
          {label}
        </label>
        <span className={`text-sm font-bold text-${color}-400 font-display`}>
          {value}{unit}
        </span>
      </div>
      <input
        type="range" name={name} min={min} max={max} step={step}
        value={value}
        onChange={e => onChange(name, parseFloat(e.target.value))}
        className="w-full"
        style={{
          background: `linear-gradient(to right, var(--tw-gradient-from, #14b8a6) ${pct}%, rgba(255,255,255,0.1) ${pct}%)`
        }}
      />
      <div className="flex justify-between text-xs text-slate-600">
        <span>{min}{unit}</span>
        <span>{max}{unit}</span>
      </div>
    </div>
  );
}

function ToggleField({ label, icon: Icon, name, value, onChange, onLabel = 'Yes', offLabel = 'No', onColor = 'crimson' }) {
  return (
    <div className="flex items-center justify-between p-4 rounded-xl border border-white/[0.06] bg-white/[0.03]">
      <label className="flex items-center gap-2 text-sm font-medium text-slate-300">
        <Icon size={15} className="text-slate-400" />
        {label}
      </label>
      <button
        type="button"
        onClick={() => onChange(name, value ? 0 : 1)}
        className={`relative inline-flex h-7 w-14 items-center rounded-full transition-all duration-300 focus:outline-none ${
          value ? (onColor === 'crimson' ? 'bg-red-500' : 'bg-teal-500') : 'bg-slate-700'
        }`}
      >
        <span className={`inline-block h-5 w-5 transform rounded-full bg-white shadow-lg transition-transform duration-300 ${value ? 'translate-x-8' : 'translate-x-1'}`} />
      </button>
      <span className={`text-xs font-semibold w-8 text-right ${value ? (onColor === 'crimson' ? 'text-red-400' : 'text-teal-400') : 'text-slate-500'}`}>
        {value ? onLabel : offLabel}
      </span>
    </div>
  );
}

export default function PatientForm({ onSubmit, loading }) {
  const [form, setForm] = useState(DEFAULTS);

  const handleChange = (name, value) => setForm(prev => ({ ...prev, [name]: value }));

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(form);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Demographics */}
      <div>
        <p className="section-heading">Demographics</p>
        <div className="grid grid-cols-1 gap-4">
          <SliderField label="Age" icon={User} name="age" value={form.age}
            onChange={handleChange} min={18} max={100} unit=" yrs" />
          <div className="flex items-center justify-between p-4 rounded-xl border border-white/[0.06] bg-white/[0.03]">
            <label className="flex items-center gap-2 text-sm font-medium text-slate-300">
              <User size={15} className="text-slate-400" /> Sex
            </label>
            <div className="flex gap-2">
              {[{ label: 'Male', value: 1 }, { label: 'Female', value: 0 }].map(opt => (
                <button key={opt.value} type="button"
                  onClick={() => handleChange('gender', opt.value)}
                  className={`px-4 py-1.5 rounded-lg text-sm font-semibold transition-all duration-200 ${
                    form.gender === opt.value
                      ? 'bg-teal-500 text-white shadow-glow-teal'
                      : 'bg-white/5 text-slate-400 hover:bg-white/10'
                  }`}>
                  {opt.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Blood Pressure */}
      <div>
        <p className="section-heading">Blood Pressure</p>
        <div className="space-y-4">
          <SliderField label="Systolic BP" icon={Activity} name="systolic_bp" value={form.systolic_bp}
            onChange={handleChange} min={80} max={220} unit=" mmHg"
            color={form.systolic_bp >= 140 ? 'red' : form.systolic_bp >= 120 ? 'amber' : 'teal'} />
          <SliderField label="Diastolic BP" icon={Activity} name="diastolic_bp" value={form.diastolic_bp}
            onChange={handleChange} min={40} max={140} unit=" mmHg"
            color={form.diastolic_bp >= 90 ? 'red' : form.diastolic_bp >= 80 ? 'amber' : 'teal'} />
        </div>
      </div>

      {/* Labs */}
      <div>
        <p className="section-heading">Lab Values</p>
        <div className="space-y-4">
          <SliderField label="Cholesterol" icon={Droplets} name="cholesterol" value={form.cholesterol}
            onChange={handleChange} min={100} max={400} unit=" mg/dL"
            color={form.cholesterol >= 240 ? 'red' : form.cholesterol >= 200 ? 'amber' : 'teal'} />
          <SliderField label="Glucose" icon={Zap} name="glucose" value={form.glucose}
            onChange={handleChange} min={60} max={300} unit=" mg/dL"
            color={form.glucose >= 126 ? 'red' : form.glucose >= 100 ? 'amber' : 'teal'} />
          <SliderField label="BMI" icon={Scale} name="bmi" value={form.bmi}
            onChange={handleChange} min={15} max={55} step={0.1} unit=""
            color={form.bmi >= 30 ? 'red' : form.bmi >= 25 ? 'amber' : 'teal'} />
          <SliderField label="Heart Rate" icon={Heart} name="heart_rate" value={form.heart_rate}
            onChange={handleChange} min={40} max={200} unit=" bpm" />
        </div>
      </div>

      {/* Lifestyle */}
      <div>
        <p className="section-heading">Lifestyle</p>
        <div className="space-y-3">
          <ToggleField label="Current Smoker" icon={Cigarette} name="smoking"
            value={form.smoking} onChange={handleChange} onLabel="Yes" offLabel="No" onColor="crimson" />
          <ToggleField label="Physically Active" icon={Dumbbell} name="physical_activity"
            value={form.physical_activity} onChange={handleChange} onLabel="Yes" offLabel="No" onColor="teal" />
          <ToggleField label="Alcohol Use" icon={Droplets} name="alcohol"
            value={form.alcohol} onChange={handleChange} onLabel="Yes" offLabel="No" onColor="crimson" />
        </div>
      </div>

      <button type="submit" disabled={loading} className="btn-primary w-full justify-center py-4 text-base">
        {loading ? (
          <>
            <svg className="animate-spin w-5 h-5" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
            </svg>
            Analyzing…
          </>
        ) : (
          <>
            <Heart size={18} className="animate-heartbeat" />
            Predict Heart Risk
          </>
        )}
      </button>
    </form>
  );
}

export { DEFAULTS };
