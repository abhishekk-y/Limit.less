import React from 'react';

interface ScoreRingProps {
  score: number; // 0-100
  size?: number;
  strokeWidth?: number;
  label?: string;
}

export function ScoreRing({ score, size = 120, strokeWidth = 8, label }: ScoreRingProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (score / 100) * circumference;
  
  let colorClass = 'text-red-500';
  if (score >= 70) colorClass = 'text-emerald-500';
  else if (score >= 40) colorClass = 'text-amber-500';

  return (
    <div className="relative inline-flex items-center justify-center flex-col" style={{ width: size, height: size }}>
      <svg className="transform -rotate-90 w-full h-full">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="currentColor"
          strokeWidth={strokeWidth}
          fill="transparent"
          className="text-slate-100"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="currentColor"
          strokeWidth={strokeWidth}
          fill="transparent"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className={`transition-all duration-1000 ease-in-out ${colorClass}`}
          strokeLinecap="round"
        />
      </svg>
      <div className="absolute flex flex-col items-center justify-center text-center">
        <span className="text-2xl font-bold text-slate-800">{score}</span>
        {label && <span className="text-xs text-slate-500">{label}</span>}
      </div>
    </div>
  );
}
