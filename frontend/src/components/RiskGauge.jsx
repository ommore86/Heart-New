import { useEffect, useRef } from 'react';

/**
 * Animated SVG arc gauge for heart risk score (0–100).
 * Color: green (low) → amber (moderate) → red (high)
 */
export default function RiskGauge({ score = 0, size = 280 }) {
  const needleRef = useRef(null);
  const scoreTextRef = useRef(null);

  const cx = size / 2;
  const cy = size / 2 + 10;
  const radius = size * 0.38;
  const strokeWidth = size * 0.065;

  // Arc from -210° to 30° (240° sweep)
  const startAngle = -210;
  const endAngle = 30;
  const totalAngle = endAngle - startAngle; // 240

  function polarToCartesian(angle, r = radius) {
    const rad = (angle * Math.PI) / 180;
    return {
      x: cx + r * Math.cos(rad),
      y: cy + r * Math.sin(rad),
    };
  }

  function arcPath(start, end, r = radius) {
    const s = polarToCartesian(start, r);
    const e = polarToCartesian(end, r);
    const largeArc = end - start > 180 ? 1 : 0;
    return `M ${s.x} ${s.y} A ${r} ${r} 0 ${largeArc} 1 ${e.x} ${e.y}`;
  }

  // Needle angle: maps 0–100 score → startAngle to endAngle
  const needleAngle = startAngle + (score / 100) * totalAngle;
  const needleTip = polarToCartesian(needleAngle, radius * 0.78);
  const needleBase1 = polarToCartesian(needleAngle - 90, radius * 0.08);
  const needleBase2 = polarToCartesian(needleAngle + 90, radius * 0.08);

  // Color zones
  const lowEnd = startAngle + totalAngle * 0.4;   // 40% → 40 score
  const highStart = startAngle + totalAngle * 0.7; // 70% → 70 score

  // Dynamic color based on score
  const scoreColor = score >= 70 ? '#ef4444' : score >= 40 ? '#f59e0b' : '#10b981';
  const glowColor = score >= 70 ? 'rgba(239,68,68,0.4)' : score >= 40 ? 'rgba(245,158,11,0.4)' : 'rgba(16,185,129,0.4)';

  return (
    <div className="flex flex-col items-center">
      <svg
        width={size}
        height={size * 0.85}
        viewBox={`0 0 ${size} ${size * 0.85}`}
        style={{ filter: `drop-shadow(0 0 20px ${glowColor})` }}
      >
        <defs>
          <linearGradient id="arcGradLow" gradientUnits="userSpaceOnUse"
            x1={polarToCartesian(startAngle).x} y1={polarToCartesian(startAngle).y}
            x2={polarToCartesian(lowEnd).x} y2={polarToCartesian(lowEnd).y}>
            <stop offset="0%" stopColor="#10b981" />
            <stop offset="100%" stopColor="#34d399" />
          </linearGradient>
          <linearGradient id="arcGradMid" gradientUnits="userSpaceOnUse"
            x1={polarToCartesian(lowEnd).x} y1={polarToCartesian(lowEnd).y}
            x2={polarToCartesian(highStart).x} y2={polarToCartesian(highStart).y}>
            <stop offset="0%" stopColor="#f59e0b" />
            <stop offset="100%" stopColor="#fbbf24" />
          </linearGradient>
          <linearGradient id="arcGradHigh" gradientUnits="userSpaceOnUse"
            x1={polarToCartesian(highStart).x} y1={polarToCartesian(highStart).y}
            x2={polarToCartesian(endAngle).x} y2={polarToCartesian(endAngle).y}>
            <stop offset="0%" stopColor="#ef4444" />
            <stop offset="100%" stopColor="#ff6b6b" />
          </linearGradient>
          <filter id="needleGlow">
            <feGaussianBlur stdDeviation="2" result="blur" />
            <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
          </filter>
        </defs>

        {/* Background track */}
        <path
          d={arcPath(startAngle, endAngle)}
          fill="none"
          stroke="rgba(255,255,255,0.06)"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />

        {/* Color zones */}
        <path d={arcPath(startAngle, lowEnd)} fill="none" stroke="url(#arcGradLow)" strokeWidth={strokeWidth} strokeLinecap="round" />
        <path d={arcPath(lowEnd, highStart)} fill="none" stroke="url(#arcGradMid)" strokeWidth={strokeWidth} strokeLinecap="round" />
        <path d={arcPath(highStart, endAngle)} fill="none" stroke="url(#arcGradHigh)" strokeWidth={strokeWidth} strokeLinecap="round" />

        {/* Tick marks */}
        {[0, 20, 40, 60, 80, 100].map((val) => {
          const angle = startAngle + (val / 100) * totalAngle;
          const inner = polarToCartesian(angle, radius - strokeWidth / 2 - 4);
          const outer = polarToCartesian(angle, radius + strokeWidth / 2 + 4);
          return (
            <line key={val} x1={inner.x} y1={inner.y} x2={outer.x} y2={outer.y}
              stroke="rgba(255,255,255,0.3)" strokeWidth="1.5" strokeLinecap="round" />
          );
        })}

        {/* Needle */}
        <polygon
          ref={needleRef}
          points={`${needleTip.x},${needleTip.y} ${needleBase1.x},${needleBase1.y} ${needleBase2.x},${needleBase2.y}`}
          fill={scoreColor}
          filter="url(#needleGlow)"
          style={{ transition: 'all 1s cubic-bezier(0.34, 1.56, 0.64, 1)' }}
        />
        {/* Center hub */}
        <circle cx={cx} cy={cy} r={strokeWidth * 0.45} fill={scoreColor}
          style={{ filter: `drop-shadow(0 0 8px ${scoreColor})` }} />
        <circle cx={cx} cy={cy} r={strokeWidth * 0.22} fill="white" />

        {/* Score text */}
        <text x={cx} y={cy + radius * 0.55} textAnchor="middle"
          style={{ fontFamily: 'Outfit, sans-serif', fontSize: size * 0.16, fontWeight: 800, fill: scoreColor, filter: `drop-shadow(0 0 8px ${glowColor})` }}>
          {score.toFixed(1)}
        </text>
        <text x={cx} y={cy + radius * 0.78} textAnchor="middle"
          style={{ fontFamily: 'Inter, sans-serif', fontSize: size * 0.058, fontWeight: 500, fill: 'rgba(148,163,184,0.9)' }}>
          Heart Risk Score
        </text>

        {/* Zone labels */}
        {(() => {
          const lowMid = polarToCartesian(startAngle + totalAngle * 0.2, radius * 1.22);
          const midMid = polarToCartesian(startAngle + totalAngle * 0.55, radius * 1.22);
          const highMid = polarToCartesian(startAngle + totalAngle * 0.85, radius * 1.22);
          return (
            <>
              <text x={lowMid.x} y={lowMid.y} textAnchor="middle"
                style={{ fontFamily: 'Inter, sans-serif', fontSize: size * 0.046, fill: '#34d399', fontWeight: 600 }}>Low</text>
              <text x={midMid.x} y={midMid.y} textAnchor="middle"
                style={{ fontFamily: 'Inter, sans-serif', fontSize: size * 0.046, fill: '#fbbf24', fontWeight: 600 }}>Moderate</text>
              <text x={highMid.x} y={highMid.y} textAnchor="middle"
                style={{ fontFamily: 'Inter, sans-serif', fontSize: size * 0.046, fill: '#ff6b6b', fontWeight: 600 }}>High</text>
            </>
          );
        })()}
      </svg>
    </div>
  );
}
