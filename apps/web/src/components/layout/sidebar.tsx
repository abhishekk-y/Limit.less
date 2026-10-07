'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
}

const NAV_ITEMS = [
  { group: 'MY CAREER', items: [
    { label: 'Dashboard', href: '/dashboard' },
    { label: 'Talent Twin', href: '/talent-twin' },
    { label: 'Skill Passport', href: '/skill-passport' },
    { label: 'Career GPS', href: '/career-gps' },
    { label: 'Skill Galaxy', href: '/skill-galaxy' },
  ]},
  { group: 'OPPORTUNITIES', items: [
    { label: 'All Opportunities', href: '/opportunities' },
    { label: 'Application Tracker', href: '/application-tracker' },
    { label: 'Vault', href: '/vault' },
  ]},
  { group: 'GROW', items: [
    { label: 'Missions', href: '/missions' },
    { label: 'Copilot', href: '/copilot' },
    { label: 'DataInter', href: '/data-inter' },
  ]},
  { group: 'ORGANIZATION', items: [
    { label: 'Workforce Twin', href: '/org/workforce' },
    { label: 'Shock Simulator', href: '/org/shock-simulator' },
    { label: 'Team Composer', href: '/org/team-composer' },
    { label: 'Succession', href: '/org/succession' },
  ]},
  { group: 'INSTITUTION', items: [
    { label: 'Curriculum Twin', href: '/institution/curriculum' },
    { label: 'CDS Dashboard', href: '/institution/cds' },
    { label: 'Placement', href: '/institution/placement' },
    { label: 'Intervention', href: '/institution/intervention' },
  ]},
  { group: 'PLATFORM', items: [
    { label: 'Admin Console', href: '/admin' },
    { label: 'Experiment Center', href: '/admin/experiment-center' },
    { label: 'Billing', href: '/admin/billing' },
    { label: 'Data Lineage', href: '/admin/data-lineage' },
    { label: 'Fairness', href: '/admin/fairness' },
    { label: 'Settings', href: '/settings' },
  ]},
];

export function Sidebar({ isOpen, onToggle }: SidebarProps) {
  const pathname = usePathname();

  return (
    <>
      {isOpen && (
        <div className="fixed inset-0 bg-black/50 z-40 md:hidden" onClick={onToggle} aria-hidden="true" />
      )}

      <aside className={`
        fixed md:relative z-50 md:z-auto
        w-64 h-full bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700
        transform transition-transform duration-200 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0 md:w-0 md:border-0 md:overflow-hidden'}
        overflow-y-auto
      `}>
        {/* Logo */}
        <div className="p-5 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <Link href="/dashboard" className="flex items-center gap-2.5">
            <div className="w-8 h-8 bg-gradient-to-br from-violet-600 to-emerald-500 rounded-lg flex items-center justify-center text-white font-bold text-sm">SX</div>
            <span className="text-lg font-bold text-gray-900 dark:text-white">Limit.less</span>
          </Link>
          <button onClick={onToggle} className="md:hidden text-gray-400 hover:text-gray-600" aria-label="Close sidebar">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>

        {/* Navigation */}
        <nav className="p-3 space-y-5" aria-label="Main navigation">
          {NAV_ITEMS.map((group) => (
            <div key={group.group}>
              <h2 className="px-3 mb-1.5 text-[10px] font-bold tracking-widest text-gray-400 dark:text-gray-500 uppercase">
                {group.group}
              </h2>
              <div className="space-y-0.5">
                {group.items.map((item) => {
                  const isActive = pathname === item.href;
                  return (
                    <Link key={item.href} href={item.href}
                      className={`
                        flex items-center rounded-lg px-3 py-2 text-sm font-medium transition-colors
                        ${isActive
                          ? 'bg-violet-50 dark:bg-violet-500/10 text-violet-700 dark:text-violet-300'
                          : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white'
                        }
                      `}
                      aria-current={isActive ? 'page' : undefined}>
                      {item.label}
                    </Link>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>
      </aside>
    </>
  );
}

