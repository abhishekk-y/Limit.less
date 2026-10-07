'use client';

import React from 'react';

interface TopBarProps {
  onMenuToggle: () => void;
  onWhyToggle: () => void;
}

export function TopBar({ onMenuToggle, onWhyToggle }: TopBarProps) {
  return (
    <header className="h-14 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 flex items-center justify-between px-4 md:px-6 shrink-0">
      <div className="flex items-center gap-4">
        <button onClick={onMenuToggle} className="md:hidden text-gray-500 hover:text-gray-700 dark:text-gray-400" aria-label="Toggle menu">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16"/></svg>
        </button>

        <div className="hidden md:flex items-center gap-6 text-sm">
          <div className="flex items-center gap-1.5">
            <span className="text-gray-500">Readiness</span>
            <span className="font-bold text-violet-600">62%</span>
          </div>
          <div className="w-px h-4 bg-gray-200 dark:bg-gray-700" />
          <div className="flex items-center gap-1.5">
            <span className="text-gray-500">Skills</span>
            <span className="font-bold text-emerald-600">8</span>
          </div>
          <div className="w-px h-4 bg-gray-200 dark:bg-gray-700" />
          <div className="flex items-center gap-1.5">
            <span className="text-gray-500">Matches</span>
            <span className="font-bold text-amber-600">23</span>
          </div>
          <div className="w-px h-4 bg-gray-200 dark:bg-gray-700" />
          <div className="flex items-center gap-1.5">
            <span className="text-gray-500">Deadlines</span>
            <span className="font-bold text-red-600">3</span>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button onClick={onWhyToggle} className="hidden lg:flex items-center gap-1 text-sm text-gray-500 hover:text-violet-600 font-medium transition-colors" aria-label="Toggle Why panel">
          Why?
        </button>
        <button className="relative p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors" aria-label="Notifications">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/></svg>
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full" />
        </button>
        <div className="w-8 h-8 bg-violet-600 rounded-full flex items-center justify-center text-white text-sm font-semibold" aria-label="User avatar">
          A
        </div>
      </div>
    </header>
  );
}
