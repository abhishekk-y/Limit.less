import React from 'react';
import { Button } from '@/components/ui/button';
import { AlertTriangle } from 'lucide-react';

interface ErrorStateProps {
  title?: string;
  message: string;
  onRetry?: () => void;
}

export function ErrorState({ title = "Something went wrong", message, onRetry }: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center min-h-[300px] rounded-lg bg-red-50 border border-red-100">
      <div className="bg-white p-3 rounded-full mb-4 text-red-500 shadow-sm">
        <AlertTriangle size={28} />
      </div>
      <h3 className="text-lg font-semibold text-red-800 mb-2">{title}</h3>
      <p className="text-red-600 max-w-sm mb-6 text-sm">{message}</p>
      {onRetry && (
        <Button onClick={onRetry} variant="outline" className="border-red-200 text-red-700 hover:bg-red-100">
          Try Again
        </Button>
      )}
    </div>
  );
}
