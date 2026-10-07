import React from 'react';

export function DemoBadge() {
  return (
    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-violet-500/10 text-violet-400 border border-violet-500/20 tracking-wide">
      <span className="w-1.5 h-1.5 rounded-full bg-violet-400 animate-pulse" />
      DEMO
    </span>
  );
}
