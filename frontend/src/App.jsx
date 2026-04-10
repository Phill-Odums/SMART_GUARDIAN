import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import LiveCamera from './pages/LiveCamera';
import ImageAnalysis from './pages/ImageAnalysis';
import SingleCapture from './pages/SingleCapture';
import Configuration from './pages/Configuration';
import About from './pages/About';
import { Menu, X } from 'lucide-react';

function App() {
  const [activeTab, setActiveTab] = useState('live');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const renderContent = () => {
    switch (activeTab) {
      case 'live': return <LiveCamera />;
      case 'analysis': return <ImageAnalysis />;
      case 'single': return <SingleCapture />;
      case 'config': return <Configuration />;
      case 'about': return <About />;
      default: return <LiveCamera />;
    }
  };

  return (
    <div className="flex h-screen w-full bg-[#0B0F19] text-slate-200 overflow-hidden relative selection:bg-fuchsia-500/30">
      {/* Vibrant Animated Background Orbs */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-purple-600/20 mix-blend-screen filter blur-[100px] animate-blob pointer-events-none" />
      <div className="absolute top-[20%] right-[-10%] w-[40%] h-[40%] rounded-full bg-cyan-600/20 mix-blend-screen filter blur-[100px] animate-blob animation-delay-2000 pointer-events-none" />
      <div className="absolute bottom-[-20%] left-[20%] w-[40%] h-[40%] rounded-full bg-fuchsia-600/20 mix-blend-screen filter blur-[100px] animate-blob animation-delay-4000 pointer-events-none" />

      {/* Desktop Sidebar */}
      <div className="z-10">
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      </div>

      {/* Mobile Header / Menu Toggle */}
      <div className="md:hidden absolute top-0 left-0 right-0 h-16 bg-[#0B0F19]/80 backdrop-blur-md border-b border-white/[0.05] flex items-center justify-between px-4 z-50">
        <span className="font-bold text-xl tracking-tight bg-gradient-to-r from-cyan-400 via-fuchsia-500 to-purple-500 bg-clip-text text-transparent">SMART GUARDAN</span>
        <button onClick={() => setMobileMenuOpen(!mobileMenuOpen)} className="p-2 rounded-lg bg-white/5 text-slate-200 hover:bg-white/10 transition">
          {mobileMenuOpen ? <X /> : <Menu />}
        </button>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden absolute inset-0 z-40 bg-[#0B0F19]/95 backdrop-blur-xl flex flex-col pt-24 px-6 space-y-4">
          {['live', 'analysis', 'single', 'config', 'about'].map(id => (
            <button
              key={id}
              onClick={() => { setActiveTab(id); setMobileMenuOpen(false); }}
              className={`w-full text-left px-6 py-4 rounded-xl capitalize tracking-wide transition-all ${activeTab === id ? 'bg-gradient-to-r from-fuchsia-600 to-purple-600 text-white font-semibold shadow-lg shadow-fuchsia-500/20' : 'bg-white/5 text-slate-300 hover:bg-white/10'}`}
            >
              {id.replace('-', ' ')}
            </button>
          ))}
        </div>
      )}

      {/* Main Content Area */}
      <main className="flex-1 overflow-hidden pt-20 md:pt-6 md:p-6 md:pr-4 z-10 relative">
        <div className="h-full w-full animate-in fade-in duration-500">
          {renderContent()}
        </div>
      </main>
    </div>
  );
}

export default App;
