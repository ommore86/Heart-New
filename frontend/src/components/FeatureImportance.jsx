import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, LabelList
} from 'recharts';

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="glass-card px-4 py-2.5 text-sm">
      <p className="font-semibold text-white">{d.displayValue || d.feature}</p>
      <p className={d.direction === 'positive' ? 'text-red-400' : 'text-emerald-400'}>
        {d.direction === 'positive' ? '↑ Increases risk' : '↓ Reduces risk'}
      </p>
      <p className="text-slate-300 font-bold">Impact: {(d.contribution * 100).toFixed(1)}%</p>
    </div>
  );
};

export default function FeatureImportance({ contributions }) {
  if (!contributions?.length) return null;

  const data = contributions.slice(0, 8).map(c => ({
    ...c,
    value: c.direction === 'positive' ? c.contribution : -c.contribution,
    displayValue: c.display_value || c.feature,
    absVal: c.contribution,
  }));

  const getColor = (item) => item.direction === 'positive' ? '#ef4444' : '#10b981';

  return (
    <div className="space-y-4">
      <p className="section-heading">Top Risk Factors (SHAP)</p>

      {/* Legend */}
      <div className="flex gap-4 text-xs text-slate-400">
        <span className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-sm bg-red-500 opacity-80" />
          Increases risk
        </span>
        <span className="flex items-center gap-1.5">
          <span className="w-3 h-3 rounded-sm bg-emerald-500 opacity-80" />
          Reduces risk
        </span>
      </div>

      {/* Bar chart */}
      <div style={{ height: Math.max(160, contributions.length * 36) }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{ left: 8, right: 40, top: 4, bottom: 4 }}>
            <XAxis type="number" tick={{ fill: '#64748b', fontSize: 11 }}
              tickFormatter={v => `${(Math.abs(v) * 100).toFixed(0)}%`}
              axisLine={false} tickLine={false} />
            <YAxis type="category" dataKey="displayValue" tick={{ fill: '#94a3b8', fontSize: 12 }}
              width={145} axisLine={false} tickLine={false} />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
            <Bar dataKey="absVal" radius={[0, 6, 6, 0]} maxBarSize={24}>
              <LabelList
                dataKey="absVal"
                position="right"
                formatter={v => `${(v * 100).toFixed(1)}%`}
                style={{ fill: '#cbd5e1', fontSize: 11, fontWeight: 600 }}
              />
              {data.map((entry, index) => (
                <Cell key={index} fill={getColor(entry)} fillOpacity={0.82} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Factor pills */}
      <div className="flex flex-wrap gap-2 pt-1">
        {data.map((f, i) => (
          <div key={i} className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border ${
            f.direction === 'positive'
              ? 'bg-red-500/10 text-red-400 border-red-500/25'
              : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/25'
          }`}>
            {f.direction === 'positive' ? <TrendingUp size={10} /> : <TrendingDown size={10} />}
            {f.displayValue}
          </div>
        ))}
      </div>
    </div>
  );
}
