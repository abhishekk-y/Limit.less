import React from 'react';

interface ConfidenceBadgeProps {
  level: 'high' | 'medium' | 'low' | 'High' | 'Medium' | 'Low';
}

export function ConfidenceBadge({ level }: ConfidenceBadgeProps) {
  const normalized = level.toLowerCase() as 'high' | 'medium' | 'low';
  const config = {
    high: { label: 'High Confidence', className: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' },
    medium: { label: 'Medium Confidence', className: 'bg-amber-500/10 text-amber-400 border-amber-500/20' },
    low: { label: 'Low Confidence', className: 'bg-red-500/10 text-red-400 border-red-500/20' },
  };
  const { label, className } = config[normalized];
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium border ${className}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${normalized === 'high' ? 'bg-emerald-400' : normalized === 'medium' ? 'bg-amber-400' : 'bg-red-400'}`} />
      {label}
    </span>
  );
}
