import { Activity, Building2, ChevronDown, Globe2, Info, LayoutDashboard, Menu, Moon, Play, Shield, Sun, UserRound, X } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import fallback from './data/fallback.json'
import { I18nProvider, Language, useI18n } from './i18n'
import { getPockets, getSummary, Pocket, Summary } from './lib/api'
import { Admin } from './pages/Admin'
import { Assurance } from './pages/Assurance'
import { Dashboard } from './pages/Dashboard'
import { Landing } from './pages/Landing'
import { Methodology } from './pages/Methodology'
import { Optimizer } from './pages/Optimizer'
import { PocketDetail } from './pages/PocketDetail'
import { Resident } from './pages/Resident'
import { Simulator } from './pages/Simulator'

type Page = 'home' | 'dashboard' | 'pocket' | 'simulator' | 'optimizer' | 'assurance' | 'resident' | 'admin' | 'methodology'

function AppContent() {
  const { language, setLanguage, t } = useI18n()
  const [page, setPage] = useState<Page>('home')
  const [pockets, setPockets] = useState<Pocket[]>([])
  const [summary, setSummary] = useState<Summary>(fallback.summary)
  const [selectedId, setSelectedId] = useState('NS-0766')
  const [dark, setDark] = useState(false)
  const [menu, setMenu] = useState(false)
  const [demo, setDemo] = useState(false)
  const [demoStep, setDemoStep] = useState(0)

  useEffect(() => { getPockets().then(data => setPockets(data.items)); getSummary().then(setSummary) }, [])
  useEffect(() => { document.documentElement.dataset.theme = dark ? 'dark' : 'light' }, [dark])
  useEffect(() => {
    if (!demo) return
    const pages: Page[] = ['dashboard', 'pocket', 'simulator', 'resident']
    const timer = window.setInterval(() => {
      setDemoStep(old => {
        const next = (old + 1) % pages.length
        setPage(pages[next])
        if (pages[next] === 'pocket') setSelectedId('NS-0766')
        return next
      })
    }, 4200)
    setPage(pages[0])
    return () => window.clearInterval(timer)
  }, [demo])

  const open = (next: string) => { setPage(next as Page); setMenu(false); if (next === 'pocket') setSelectedId('NS-0766') }
  const active = (key: Page) => page === key ? 'active' : ''
  const navigation: { key: Page; label: string; icon: React.ReactNode }[] = [
    { key: 'dashboard', label: t('dashboard'), icon: <LayoutDashboard size={16} /> },
    { key: 'simulator', label: t('simulator'), icon: <Activity size={16} /> },
    { key: 'optimizer', label: t('optimizer'), icon: <Building2 size={16} /> },
    { key: 'assurance', label: t('assurance'), icon: <Shield size={16} /> },
  ]
  const currentTitle = useMemo(() => ({
    home: t('missionControl'), dashboard: t('priorityMap'), pocket: t('pocketDetail'), simulator: t('simulator'), optimizer: t('optimizer'), assurance: t('assurance'), resident: t('resident'), admin: t('officerView'), methodology: t('methodology'),
  }[page]), [page, t])

  return <div className="app-shell">
    <header className="topbar">
      <button className="brand" onClick={() => open('home')}><span className="brand-mark"><span /><span /><span /></span><span><b>{t('brand')}</b><small>{t('tagline')}</small></span></button>
      <nav className="desktop-nav">{navigation.map(item => <button key={item.key} className={active(item.key)} onClick={() => open(item.key)}>{item.icon}{item.label}</button>)}</nav>
      <div className="top-actions">
        <button className="demo-button" onClick={() => setDemo(old => !old)}><Play size={13} fill="currentColor" /> {demo ? t('demoStep', { step: demoStep + 1 }) : t('demoMode')}</button>
        <div className="lang-select"><Globe2 size={15} /><select value={language} onChange={e => setLanguage(e.target.value as Language)} aria-label={t('language')}><option value="en">EN</option><option value="hi">हिन्दी</option><option value="mr">मराठी</option></select><ChevronDown size={13} /></div>
        <button className="theme-button" aria-label={t('toggleDark')} onClick={() => setDark(old => !old)}>{dark ? <Sun size={17} /> : <Moon size={17} />}</button>
        <button className="menu-button" aria-label={t('openMenu')} onClick={() => setMenu(old => !old)}>{menu ? <X /> : <Menu />}</button>
      </div>
    </header>
    {menu && <div className="mobile-menu">{navigation.map(item => <button key={item.key} onClick={() => open(item.key)}>{item.icon}{item.label}</button>)}<button onClick={() => open('resident')}><UserRound size={16} />{t('resident')}</button><button onClick={() => open('admin')}><Shield size={16} />{t('admin')}</button><button onClick={() => open('methodology')}><Info size={16} />{t('methodology')}</button></div>}
    <div className="body-layout">
      <aside className="sidebar"><div className="side-label">{t('workspace')}</div><button className={active('home')} onClick={() => open('home')}><Activity size={17} />{t('overview')}</button>{navigation.map(item => <button key={item.key} className={active(item.key)} onClick={() => open(item.key)}>{item.icon}{item.label}</button>)}<div className="side-separator" /><div className="side-label">{t('peopleTrust')}</div><button className={active('resident')} onClick={() => open('resident')}><UserRound size={17} />{t('resident')}</button><button className={active('admin')} onClick={() => open('admin')}><Shield size={17} />{t('admin')}</button><button className={active('methodology')} onClick={() => open('methodology')}><Info size={17} />{t('methodology')}</button><div className="sidebar-bottom"><div className="network-status"><span className="live-dot" /><div><b>{t('demoDataLayer')}</b><small>{t('seededOfflineReady')}</small></div></div><div className="side-policy"><small>{t('alignedTo')}</small><b>PMAY-U · SRA · SBM-U</b></div></div></aside>
      <main className="main-content"><div className="breadcrumb"><span>{t('brand')}</span><b>/</b><span>{currentTitle}</span>{page !== 'home' && <span className="crumb-demo">{t('syntheticDemo')}</span>}</div>{page === 'home' && <Landing summary={summary} onOpen={open} />}{page === 'dashboard' && <Dashboard pockets={pockets} summary={summary} onSelect={id => { setSelectedId(id); open('pocket') }} />}{page === 'pocket' && <PocketDetail id={selectedId} onBack={() => open('dashboard')} />}{page === 'simulator' && <Simulator />}{page === 'optimizer' && <Optimizer pockets={pockets} />}{page === 'assurance' && <Assurance pockets={pockets} onSelect={id => { setSelectedId(id); open('pocket') }} />}{page === 'resident' && <Resident />}{page === 'admin' && <Admin />}{page === 'methodology' && <Methodology />}</main>
    </div>
    <footer className="site-footer"><span>{t('footerCopyright')}</span><span><Info size={13} /> {t('footerNotice')}</span><span>{t('footerRegion')}</span></footer>
  </div>
}

export default function App() { return <I18nProvider><AppContent /></I18nProvider> }
