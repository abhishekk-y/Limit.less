import React from 'react';
import { ConfidenceBadge } from './confidence-badge';

interface LineageCardProps {
  source: string;
  period: string;
  recordsProcessed: number;
  formula: string;
  confidence: 'high' | 'medium' | 'low';
  limitations: string[];
}

export function LineageCard({ source, period, recordsProcessed, formula, confidence, limitations }: LineageCardProps) {
  return (
    <div className="glass-card p-4">
      <div className="flex justify-between items-center mb-3">
        <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wide flex items-center gap-1.5">
          Data Lineage
        </h4>
        <ConfidenceBadge level={confidence} />
      </div>
      <div className="border-t border-gray-100 dark:border-gray-700/50 pt-3">
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-xs text-gray-600 dark:text-gray-400">
          <div>
            <span className="font-medium text-gray-700 dark:text-gray-300 block mb-0.5">Source</span>
            {source}
          </div>
          <div>
            <span className="font-medium text-gray-700 dark:text-gray-300 block mb-0.5">Period</span>
            {period}
          </div>
          <div>
            <span className="font-medium text-gray-700 dark:text-gray-300 block mb-0.5">Records</span>
            {recordsProcessed.toLocaleString()}
          </div>
          <div className="col-span-2 md:col-span-3">
            <span className="font-medium text-gray-700 dark:text-gray-300 block mb-0.5">Formula</span>
            <code className="bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded text-[11px] font-mono">{formula}</code>
          </div>
          {limitations.length > 0 && (
            <div className="col-span-2 md:col-span-3">
              <span className="font-medium text-gray-700 dark:text-gray-300 block mb-0.5">Limitations</span>
              <ul className="list-disc pl-4 space-y-0.5">
                {limitations.map((limitation, i) => (
                  <li key={i}>{limitation}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
