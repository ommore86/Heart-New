import { BrowserRouter, Routes, Route, NavLink, useLocation } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { Heart, Activity, FlaskConical, Wifi, WifiOff } from 'lucide-react';
import PredictPage from './pages/Predict';
import SimulatePage from './pages/Simulate';
import { checkHealth } from './api/client';

function NavItem({ to, icon: Icon, label }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all duration-200 ${
          isActive
            ? 'bg-teal-500/20 text-teal-400 border border-teal-500/30'
            : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
        }`
      }
    >
      <Icon size={16} />
      {label}
    </NavLink>
  );
}

function StatusDot({ online }) {
  return (
    <div className={`flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full border ${
      online === null
        ? 'text-slate-500 border-slate-700'
        : online
          ? 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10'
          : 'text-red-400 border-red-500/30 bg-red-500/10'
    }`}>
      {online === null ? (
        <span className="w-1.5 h-1.5 rounded-full bg-slate-500 animate-pulse" />
      ) : online ? (
        <Wifi size={11} />
      ) : (
        <WifiOff size={11} />
      )}
      {online === null ? 'Checking…' : online ? 'API Online' : 'API Offline'}
    </div>
  );
}

function Layout({ children }) {
  const [apiOnline, setApiOnline] = useState(null);

  useEffect(() => {
    const check = async () => {
      try {
        await checkHealth();
        setApiOnline(true);
      } catch {
        setApiOnline(false);
      }
    };
    check();
    const interval = setInterval(check, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen mesh-bg">
      {/* Navbar */}
      <nav className="sticky top-0 z-50 border-b border-white/[0.06] backdrop-blur-md"
        style={{ background: 'rgba(6, 8, 24, 0.85)' }}>
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center gap-6">
          {/* Logo */}
          <div className="flex items-center gap-2.5 mr-2">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-red-500 to-red-700 flex items-center justify-center shadow-glow-red">
              <Heart size={18} className="text-white animate-heartbeat" />
            </div>
            <div className="hidden sm:block">
              <div className="font-display font-black text-white text-sm leading-none">Digital Twin</div>
              <div className="text-[10px] text-teal-400 font-semibold tracking-wide">of the Heart</div>
            </div>
          </div>

          {/* Nav items */}
          <div className="flex items-center gap-1">
            <NavItem to="/" icon={Activity} label="Predict" />
            <NavItem to="/simulate" icon={FlaskConical} label="Simulate" />
          </div>

          {/* Spacer + API status */}
          <div className="ml-auto">
            <StatusDot online={apiOnline} />
          </div>
        </div>
      </nav>

      {/* Main content */}
      <main className="relative z-10 py-4">
        {children}
      </main>

      {/* Footer */}
      <footer className="border-t border-white/[0.05] mt-12 py-6">
        <div className="max-w-7xl mx-auto px-4 text-center text-xs text-slate-600">
          Digital Twin of the Heart — IEEE VESIT Research Project • For educational use only
        </div>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<PredictPage />} />
          <Route path="/simulate" element={<SimulatePage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
