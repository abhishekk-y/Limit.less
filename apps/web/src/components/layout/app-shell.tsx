'use client';

import { useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { Activity, ArrowUpRight, Bell, Briefcase, ChevronDown, ChevronLeft, ChevronRight, Compass, Fingerprint, FolderLock, GraduationCap, LayoutDashboard, LogOut, Menu, Route, Search, Settings, ShieldCheck, Users, X, FileText, ListChecks, Sparkles, type LucideIcon } from 'lucide-react';
import { useAuthContext } from '@/providers/auth-provider';
import api from '@/lib/api';

type NavItem = { href: string; label: string; icon: LucideIcon; description: string };
type NavGroup = { id: string; label: string; items: NavItem[] };
const overview: NavItem = { href: '/dashboard', label: 'Overview', icon: LayoutDashboard, description: 'Your progress and next steps' };
const careerGroups: NavGroup[] = [
  { id: 'identity', label: 'My profile', items: [
    { href: '/talent-twin', label: 'Talent Twin', icon: Fingerprint, description: 'Skills, evidence and trust scores' },
    { href: '/skill-passport', label: 'Skill Passport', icon: GraduationCap, description: 'Share your progress with consent' },
    { href: '/resume-builder', label: 'Résumé Studio', icon: FileText, description: 'Build and preview your résumé' },
    { href: '/vault', label: 'Document Vault', icon: FolderLock, description: 'Upload and manage your résumé' },
  ] },
  { id: 'growth', label: 'Learn & grow', items: [
    { href: '/career-gps', label: 'Career GPS', icon: Route, description: 'Plan a route toward your next role' },
    { href: '/missions', label: 'Skill Missions', icon: Compass, description: 'Build projects and add evidence' },
    { href: '/assessments', label: 'Assessments', icon: GraduationCap, description: 'Check your technical foundations' },
    { href: '/focus-planner', label: 'Focus Planner', icon: ListChecks, description: 'Plan daily actions and check project evidence' },
    { href: '/sas-research', label: 'SAS Data Lab', icon: Activity, description: 'Hackathon dataset analysis and evidence workflow' },
  ] },
  { id: 'opportunities', label: 'Find your next role', items: [
    { href: '/opportunities', label: 'Opportunities', icon: Briefcase, description: 'Search and compare demo opportunities' },
    { href: '/live-jobs', label: 'Live Jobs', icon: Briefcase, description: 'Import real employer listings and internships' },
    { href: '/profile-match', label: 'My matches', icon: Sparkles, description: 'Rank roles from your résumé and interests' },
    { href: '/apply-queue', label: 'Apply Queue', icon: ShieldCheck, description: 'Batch preparation and employer handoff' },
    { href: '/social-studio', label: 'Social Studio', icon: Users, description: 'Plan LinkedIn posts, comments and profile updates' },
    { href: '/application-tracker', label: 'Applications', icon: ShieldCheck, description: 'Review, approve and track applications' },
  ] },
];
const personal: NavGroup = { id: 'workspace', label: 'Workspace', items: [
  { href: '/notifications', label: 'Notifications', icon: Bell, description: 'Read updates from your workspace' },
  { href: '/settings', label: 'Settings & privacy', icon: Settings, description: 'Profile, data export and privacy controls' },
] };
const preferenceKey = 'skillsetu.navigation.v1';

export function AppShell({ children }: { children: React.ReactNode }) {
  const { user, isLoading, logout } = useAuthContext();
  const router = useRouter();
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const [compact, setCompact] = useState(false);
  const [autoCollapse, setAutoCollapse] = useState(true);
  const [hovered, setHovered] = useState(false);
  const [focusWithin, setFocusWithin] = useState(false);
  const rail = autoCollapse ? !(hovered || focusWithin) : compact;
  const [closedGroups, setClosedGroups] = useState<string[]>([]);
  const [preferencesLoaded, setPreferencesLoaded] = useState(false);
  const [offline, setOffline] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const [search, setSearch] = useState('');
  const sidebar = useRef<HTMLElement>(null);
  const menuButton = useRef<HTMLButtonElement>(null);
  const searchButton = useRef<HTMLButtonElement>(null);
  const dialog = useRef<HTMLDivElement>(null);
  const notifications = useQuery<{ is_read: boolean }[]>({ queryKey: ['/notifications'], queryFn: async () => (await api.get('/notifications')).data, enabled: !!user, refetchInterval: 60000 });
  const unread = notifications.data?.filter(n => !n.is_read).length || 0;
  const groups = [...careerGroups];
  if (user?.tenant_type === 'organization') groups.push({ id: 'organization', label: 'Organization', items: [{ href: '/org/workforce', label: 'Workforce', icon: Users, description: 'Import people, inspect coverage and build teams' }] });
  if (user?.tenant_type === 'institution') groups.push({ id: 'institution', label: 'Institution', items: [{ href: '/institution/curriculum', label: 'Curriculum', icon: GraduationCap, description: 'Compare your curriculum with role requirements' }] });
  if (user?.role === 'superadmin') groups.push({ id: 'platform', label: 'Platform control', items: [{ href: '/admin', label: 'Superadmin observatory', icon: Activity, description: 'Pipeline health, workers and data boundaries' }] });
  groups.push(personal);
  const items = [overview, ...groups.flatMap(group => group.items)];
  const active = items.find(item => pathname === item.href || pathname.startsWith(`${item.href}/`));
  const currentGroup = groups.find(group => group.items.some(item => item.href === active?.href));
  const results = items.filter(item => `${item.label} ${item.description}`.toLowerCase().includes(search.toLowerCase().trim()));

  useEffect(() => { if (!isLoading && !user) router.replace('/login'); }, [isLoading, user, router]);
  useEffect(() => {
    try {
      const saved = JSON.parse(localStorage.getItem(preferenceKey) || '{}');
      setCompact(saved.compact === true);
      // Auto-collapse is now the default sidebar behavior; no separate toggle is shown.
      setAutoCollapse(true);
      if (Array.isArray(saved.closedGroups)) setClosedGroups(saved.closedGroups.filter((id: unknown) => typeof id === 'string'));
    } catch { /* Navigation works even when browser storage is unavailable. */ }
    setPreferencesLoaded(true);
  }, []);
  useEffect(() => {
    if (preferencesLoaded) try { localStorage.setItem(preferenceKey, JSON.stringify({ compact, closedGroups, autoCollapse })); } catch { /* Optional preference storage. */ }
  }, [compact, closedGroups, autoCollapse, preferencesLoaded]);
  useEffect(() => {
    const update = () => setOffline(!navigator.onLine);
    update(); window.addEventListener('online', update); window.addEventListener('offline', update);
    return () => { window.removeEventListener('online', update); window.removeEventListener('offline', update); };
  }, []);
  useEffect(() => { setOpen(false); setSearchOpen(false); setSearch(''); }, [pathname]);
  useEffect(() => {
    const key = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') { event.preventDefault(); setSearchOpen(value => !value); setOpen(false); }
      if (event.key === 'Escape') {
        if (searchOpen) { setSearchOpen(false); searchButton.current?.focus(); }
        else if (open) { setOpen(false); menuButton.current?.focus(); }
      }
    };
    window.addEventListener('keydown', key);
    return () => window.removeEventListener('keydown', key);
  }, [open, searchOpen]);
  useEffect(() => {
    const media = window.matchMedia('(min-width: 1024px)');
    const update = () => { if (sidebar.current) sidebar.current.inert = !media.matches && !open; };
    update(); media.addEventListener('change', update);
    return () => media.removeEventListener('change', update);
  }, [open, isLoading]);
  useEffect(() => {
    if (!open && !searchOpen) return;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    const container = searchOpen ? dialog.current : sidebar.current;
    const elements = () => Array.from(container?.querySelectorAll<HTMLElement>('a[href],button:not([disabled]),input') || []).filter(element => element.getClientRects().length > 0);
    (searchOpen ? container?.querySelector<HTMLInputElement>('input') : elements()[0])?.focus();
    const trap = (event: KeyboardEvent) => {
      if (event.key !== 'Tab') return;
      const available = elements(); const first = available[0]; const last = available[available.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus(); }
      if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
    };
    window.addEventListener('keydown', trap);
    return () => { document.body.style.overflow = previousOverflow; window.removeEventListener('keydown', trap); };
  }, [open, searchOpen]);

  if (isLoading || !user) return <div role="status" className="min-h-screen flex items-center justify-center text-slate-500">Opening your workspace…</div>;
  const prototype = (pathname.startsWith('/admin') && pathname !== '/admin') || ['/skill-galaxy', '/copilot', '/org/shock-simulator', '/org/team-composer', '/org/succession', '/institution/cds', '/institution/placement', '/institution/intervention'].includes(pathname);
  const toggleGroup = (id: string) => setClosedGroups(current => current.includes(id) ? current.filter(value => value !== id) : [...current, id]);
  const closeMobile = () => { setOpen(false); menuButton.current?.focus(); };
  function navLink(item: NavItem) {
    const selected = active?.href === item.href;
    return <Link key={item.href} href={item.href} title={rail ? item.label : undefined} aria-label={item.label} aria-current={selected ? 'page' : undefined} className={`sidebar-nav-link relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition-colors ${rail ? 'lg:justify-center' : ''} ${selected ? 'bg-violet-100 text-violet-800 font-semibold' : 'text-slate-600 hover:bg-slate-100 hover:text-slate-950'}`}>
      <item.icon size={19} strokeWidth={1.7} className="sidebar-nav-icon shrink-0"/>
      <span aria-hidden={rail} className="sidebar-nav-label min-w-0 flex-1">{item.label}</span>
      {item.href === '/notifications' && unread > 0 && <span aria-label={`${unread} unread`} className={`rounded-full bg-violet-600 text-white text-[10px] min-w-5 text-center px-1 ${rail ? 'lg:absolute lg:right-0 lg:top-0' : ''}`}>{unread > 99 ? '99+' : unread}</span>}
      {selected && <span className={`w-1.5 h-1.5 rounded-full bg-violet-500 ${rail ? 'lg:hidden' : ''}`} aria-hidden="true"/>}
    </Link>;
  }
  return <div className="min-h-screen bg-[#f7f8fa] text-slate-900">
    <a className="sr-only focus:not-sr-only focus:fixed focus:top-2 focus:left-2 focus:z-[100] bg-white p-3" href="#main-content">Skip to main content</a>
    {open && <button className="fixed inset-0 z-40 bg-slate-950/40 backdrop-blur-sm lg:hidden" tabIndex={-1} aria-label="Close navigation overlay" onClick={closeMobile}/>}
    <aside ref={sidebar} data-collapsed={rail} data-auto-collapse={autoCollapse} onMouseEnter={() => setHovered(true)} onMouseLeave={() => setHovered(false)} onFocusCapture={event => { if (event.target.matches(':focus-visible')) setFocusWithin(true); }} onBlurCapture={event => { if (!event.currentTarget.contains(event.relatedTarget as Node)) setFocusWithin(false); }} id="workspace-navigation" aria-label="Workspace sidebar" className={`workspace-sidebar fixed inset-y-0 left-0 z-50 flex w-72 flex-col border-r border-slate-200 bg-white transition-[width,transform,background-color,color] duration-300 ease-in-out lg:translate-x-0 ${rail ? 'lg:w-20' : 'lg:w-64'} ${open ? 'translate-x-0' : '-translate-x-full'}`}>
      <div className={`h-20 shrink-0 flex items-center gap-2 ${rail ? 'px-5' : 'px-6'}`}>
        <Link href="/dashboard" aria-label="Limit.less home" className="sidebar-brand text-2xl font-bold tracking-tighter"><span aria-hidden={rail} className="sidebar-brand-full">Limit<span className="text-violet-600">.less</span></span><span aria-hidden={!rail} className="sidebar-brand-mark">L<span className="text-slate-900">.</span></span></Link>
        <button onClick={closeMobile} className="ml-auto p-2 lg:hidden" aria-label="Close navigation"><X size={20}/></button>
      </div>
      <div className={`sidebar-workspace mx-3 mb-4 rounded-xl border border-slate-200 bg-slate-50 p-3 flex items-center gap-3 ${rail ? 'lg:justify-center' : ''}`} title={`${user.tenant_type} workspace`}>
        <span className="h-8 w-8 shrink-0 rounded-lg bg-white border border-slate-200 grid place-items-center text-violet-600"><Users size={17}/></span>
        <div aria-hidden={rail} className="sidebar-workspace-copy min-w-0"><p className="text-xs font-semibold capitalize">{user.tenant_type} workspace</p><p className="text-[11px] text-slate-500 mt-0.5">Make your next move</p></div>
      </div>
      <nav className="flex-1 overflow-y-auto px-3 pb-3" aria-label="Main navigation">
        {navLink(overview)}
        {groups.map(group => {
          const expanded = rail || !closedGroups.includes(group.id);
          return <div key={group.id} className="mt-4">
            <button onClick={() => toggleGroup(group.id)} aria-hidden={rail} tabIndex={rail ? -1 : 0} onFocus={event => { if (rail) event.currentTarget.blur(); }} aria-expanded={expanded} aria-controls={`nav-group-${group.id}`} className="sidebar-category mb-1 flex w-full items-center justify-between px-3 py-2 text-[10px] font-bold uppercase tracking-[.12em] text-slate-400 hover:text-slate-700">
              {group.label}<ChevronDown size={13} className={`transition-transform ${expanded ? '' : '-rotate-90'}`}/>
            </button>
            {rail && <div className="hidden lg:block border-t border-slate-100 mb-3 mx-2"/>}
            <div id={`nav-group-${group.id}`} aria-hidden={!expanded} inert={!expanded} data-expanded={expanded} className="sidebar-group-clip"><div className="sidebar-group-items space-y-1">{group.items.map(navLink)}</div></div>
          </div>;
        })}
      </nav>
      <div className="sidebar-footer shrink-0 border-t border-slate-200 p-3">
        <button onClick={() => { if (autoCollapse) { setAutoCollapse(false); setCompact(true); } else setCompact(!compact); }} aria-label={rail ? 'Expand sidebar' : 'Collapse sidebar'} aria-expanded={!rail} aria-controls="workspace-navigation" className={`sidebar-collapse-control group hidden lg:flex w-full items-center gap-3 rounded-lg px-3 py-2 text-xs ${rail ? 'justify-center' : ''}`} title={rail ? 'Expand sidebar' : 'Collapse sidebar'}>{rail ? <ChevronRight size={18} className="sidebar-collapse-arrow sidebar-arrow-forward"/> : <><ChevronLeft size={18} className="sidebar-collapse-arrow sidebar-arrow-back"/><span>Collapse sidebar</span></>}</button>
        <div className={`flex items-center gap-3 pt-3 px-2 ${rail ? 'lg:flex-col' : ''}`}>
          <Link href="/settings" title="Your profile" aria-label="Your profile" className="w-9 h-9 shrink-0 bg-violet-100 text-violet-700 rounded-full grid place-items-center font-semibold">{user.name[0]}</Link>
          <div className={`min-w-0 flex-1 ${rail ? 'lg:hidden' : ''}`}><p className="text-xs font-semibold truncate">{user.name}</p><p className="text-[10px] text-slate-400 mt-0.5">Personal workspace</p></div>
          <button onClick={logout} aria-label="Sign out" title="Sign out" className="p-2 rounded-lg text-slate-400 hover:bg-slate-100 hover:text-slate-900"><LogOut size={17}/></button>
        </div>
      </div>
    </aside>
    <div className={`transition-[margin] duration-200 ${rail ? 'lg:ml-20' : 'lg:ml-64'}`}>
      <header className="h-16 sticky top-0 z-30 border-b border-slate-200 bg-white/95 backdrop-blur flex items-center justify-between gap-3 px-5 md:px-9">
        <div className="flex gap-3 items-center min-w-0"><button ref={menuButton} className="lg:hidden p-1" aria-label="Open navigation" aria-expanded={open} aria-controls="workspace-navigation" onClick={() => setOpen(true)}><Menu size={22}/></button><span className="text-xs text-slate-400 hidden md:inline">{currentGroup?.label || 'Workspace'}</span><ChevronRight size={13} className="text-slate-300 hidden md:inline"/><span className="text-sm font-medium truncate">{active?.label || 'Workspace'}</span></div>
        <div className="flex gap-2 sm:gap-4 items-center shrink-0">
          <button ref={searchButton} onClick={() => setSearchOpen(true)} aria-label="Search workspace" aria-haspopup="dialog" className="flex items-center gap-2 text-slate-400 hover:text-violet-700 p-2 sm:border sm:border-slate-200 sm:rounded-lg"><Search size={17}/><span className="text-xs hidden xl:inline">Find a tool…</span><kbd className="hidden sm:inline text-[10px] rounded bg-slate-100 px-1">Ctrl K</kbd></button>
          <span className="hidden sm:inline text-[10px] font-semibold tracking-wider uppercase rounded-full bg-violet-50 text-violet-700 px-3 py-1.5">{pathname === '/live-jobs' || pathname === '/apply-queue' ? 'Employer sources' : 'Career workspace'}</span>
          <Link href="/notifications" aria-label={unread ? `View notifications, ${unread} unread` : 'View notifications'} className="relative p-2 text-slate-500"><Bell size={18}/>{unread > 0 && <span className="absolute right-1 top-1 h-2 w-2 rounded-full bg-violet-600 ring-2 ring-white"/>}</Link>
        </div>
      </header>
      {offline && <div role="status" className="bg-amber-50 text-amber-900 text-sm p-3 text-center">You’re offline. Saved changes require the local API to be running.</div>}
      <main id="main-content" tabIndex={-1} className="p-5 md:p-9 xl:p-12">
        {prototype && <div role="note" className="mb-6 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-950"><strong>Design prototype.</strong> This screen contains illustrative data and unfinished controls. Its results are not calculated from your workspace. Use the main navigation for the connected features.</div>}
        {children}
      </main>
      <footer className="px-8 py-6 text-xs text-slate-400 border-t border-slate-200 flex justify-between gap-4"><span>Limit.less · Built on evidence.</span><Link href="/settings" className="hover:text-slate-600">Privacy & your data</Link></footer>
    </div>
    {searchOpen && <div className="fixed inset-0 z-[70] bg-slate-950/40 backdrop-blur-sm flex justify-center items-start pt-[12vh] px-4" onMouseDown={event => { if (event.target === event.currentTarget) { setSearchOpen(false); searchButton.current?.focus(); } }}>
      <div ref={dialog} role="dialog" aria-modal="true" aria-labelledby="workspace-search-title" className="w-full max-w-xl overflow-hidden rounded-2xl bg-white shadow-2xl border border-slate-200">
        <div className="p-5 border-b border-slate-100"><div className="flex items-center justify-between mb-4"><h2 id="workspace-search-title" className="text-sm font-semibold">Where would you like to go?</h2><button onClick={() => { setSearchOpen(false); searchButton.current?.focus(); }} aria-label="Close search" className="text-slate-400 p-1"><X size={18}/></button></div><div className="flex items-center gap-3"><Search size={20} className="text-violet-500"/><input aria-label="Find a workspace tool" placeholder="Search tools, skills, privacy…" value={search} onChange={event => setSearch(event.target.value)} className="w-full text-sm py-2 outline-none"/></div></div>
        <div className="max-h-[50vh] overflow-y-auto p-2">{results.length ? results.map(item => <Link key={item.href} href={item.href} onClick={() => setSearchOpen(false)} className="flex items-center gap-4 rounded-xl p-3 hover:bg-violet-50 focus:bg-violet-50"><span className="rounded-lg bg-slate-50 p-2 text-violet-600"><item.icon size={18}/></span><div className="flex-1"><p className="text-sm font-medium">{item.label}</p><p className="text-xs text-slate-500 mt-1">{item.description}</p></div><ArrowUpRight size={15} className="text-slate-400"/></Link>) : <p role="status" className="text-sm text-slate-500 p-8 text-center">No tools found. Try “missions”, “résumé” or “privacy”.</p>}</div>
        <div className="border-t border-slate-100 px-5 py-3 text-[11px] text-slate-400">Search your workspace tools · Tab to select · Enter to open · Esc to close</div>
      </div>
    </div>}
  </div>;
}



