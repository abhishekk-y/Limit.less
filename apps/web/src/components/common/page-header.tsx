import React from 'react';
import { DemoBadge } from './demo-badge';

interface PageHeaderProps {
  title: string;
  description?: string;
  isDemo?: boolean;
  action?: React.ReactNode;
}

export function PageHeader({ title, description, isDemo, action }: PageHeaderProps) {
  return (
    <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center pb-6 mb-6 border-b border-slate-200">
      <div className="space-y-1">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">{title}</h1>
          {isDemo && <DemoBadge />}
        </div>
        {description && <p className="text-sm text-slate-500">{description}</p>}
      </div>
      {action && <div className="mt-4 sm:mt-0">{action}</div>}
    </div>
  );
}
