import React from 'react';

function Skeleton({ className = '' }: { className?: string }) {
  return <div className={`bg-gray-200 dark:bg-gray-700 rounded animate-pulse ${className}`} />;
}

export function LoadingState() {
  return (
    <div className="w-full space-y-4 p-4 page-enter">
      <div className="flex items-center space-x-4">
        <Skeleton className="h-12 w-12 rounded-full" />
        <div className="space-y-2">
          <Skeleton className="h-4 w-[250px]" />
          <Skeleton className="h-4 w-[200px]" />
        </div>
      </div>
      <Skeleton className="h-[200px] w-full rounded-xl" />
      <div className="grid grid-cols-3 gap-4">
        <Skeleton className="h-[120px] w-full rounded-xl" />
        <Skeleton className="h-[120px] w-full rounded-xl" />
        <Skeleton className="h-[120px] w-full rounded-xl" />
      </div>
    </div>
  );
}
