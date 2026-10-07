import React from 'react';
import { Button } from '@/components/ui/button';
import { Inbox } from 'lucide-react';

interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
}

export function EmptyState({ icon, title, description, actionLabel, onAction }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center min-h-[300px] border border-dashed rounded-lg bg-slate-50 border-slate-200">
      <div className="bg-white p-4 rounded-full shadow-sm mb-4 text-slate-400">
        {icon || <Inbox size={32} />}
      </div>
      <h3 className="text-lg font-semibold text-slate-800 mb-2">{title}</h3>
      <p className="text-slate-500 max-w-sm mb-6 text-sm">{description}</p>
      {actionLabel && onAction && (
        <Button onClick={onAction} variant="default" className="bg-blue-800 hover:bg-blue-900">
          {actionLabel}
        </Button>
      )}
    </div>
  );
}
