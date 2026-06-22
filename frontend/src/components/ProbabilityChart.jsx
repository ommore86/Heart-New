import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell, LabelList
} from 'recharts';

const DATASET_LABELS = {
  cardio: 'Cardio Dataset',
  framingham: 'Framingham Study',
  uci: 'UCI Heart Disease',
};

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const val = payload[0].value;
  return (
    <div className="glass-card px-4 py-2.5 text-sm">
      <p className="font-semibold text-white">{DATASET_LABELS[payload[0].payload.name] || payload[0].payload.name}</p>
      <p className="text-teal-400 font-bold">{(val * 100).toFixed(1)}% probability</p>
    </div>
  );
};

export default function ProbabilityChart({ datasetProbabilities }) {
  if (!datasetProbabilities) return null;

  const data = Object.entries(datasetProbabilities).map(([name, prob]) => ({
    name,
    label: DATASET_LABELS[name] || name,
    probability: parseFloat(prob.toFixed(4)),
    percentage: parseFloat((prob * 100).toFixed(1)),
  }));

  const getBarColor = (prob) => {
    if (prob >= 0.7) return '#ef4444';
    if (prob >= 0.4) return '#f59e0b';
    return '#10b981';
  };

  return (
    <div className="space-y-3">
      <p className="section-heading">Dataset Probabilities</p>
      <div style={{ height: 160 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{ left: 4, right: 40, top: 4, bottom: 4 }}>
            <CartesianGrid horizontal={false} strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
            <XAxis type="number" domain={[0, 1]} tick={{ fill: '#64748b', fontSize: 11 }}
              tickFormatter={v => `${(v * 100).toFixed(0)}%`} axisLine={false} tickLine={false} />
            <YAxis type="category" dataKey="label" tick={{ fill: '#94a3b8', fontSize: 12 }}
              width={130} axisLine={false} tickLine={false} />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
            <Bar dataKey="probability" radius={[0, 6, 6, 0]} maxBarSize={28}>
              <LabelList
                dataKey="percentage"
                position="right"
                formatter={v => `${v}%`}
                style={{ fill: '#cbd5e1', fontSize: 12, fontWeight: 600 }}
              />
              {data.map((entry, index) => (
                <Cell key={index} fill={getBarColor(entry.probability)}
                  fillOpacity={0.85}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
