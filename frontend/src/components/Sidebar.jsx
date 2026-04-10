import React from 'react';
import { Camera, Image as ImageIcon, Settings, Info, Video } from 'lucide-react';

const Sidebar = ({ activeTab, setActiveTab }) => {
    const tabs = [
        { id: 'live', label: 'Live Camera', icon: <Video className="w-5 h-5" /> },
        { id: 'analysis', label: 'Image Analysis', icon: <ImageIcon className="w-5 h-5" /> },
        { id: 'single', label: 'Single Capture', icon: <Camera className="w-5 h-5" /> },
        { id: 'config', label: 'Configuration', icon: <Settings className="w-5 h-5" /> },
        { id: 'about', label: 'About', icon: <Info className="w-5 h-5" /> }
    ];

    return (
        <div className="w-64 glass-panel m-4 flex flex-col hidden md:flex relative overflow-hidden group">
            <div className="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-cyan-400 via-purple-500 to-fuchsia-500 opacity-50 group-hover:opacity-100 transition-opacity"></div>
            <div className="p-6 border-b border-white/[0.05]">
                <h1 className="text-2xl font-bold tracking-tight bg-gradient-to-r from-cyan-300 via-purple-400 to-fuchsia-400 bg-clip-text text-transparent">
                    SAFE GUARD
                </h1>
                <p className="text-xs font-medium text-slate-400 mt-1 uppercase tracking-widest">Security Core</p>
            </div>
            <nav className="flex-1 p-4 space-y-2 relative z-10">
                {tabs.map((tab) => {
                    const isActive = activeTab === tab.id;
                    return (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-300 ${isActive
                                ? 'bg-gradient-to-r from-purple-500/20 to-fuchsia-500/20 text-white shadow-[inset_0_1px_1px_rgba(255,255,255,0.1)] border border-fuchsia-500/30'
                                : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
                                }`}
                        >
                            <div className={`${isActive ? 'text-fuchsia-400 drop-shadow-[0_0_8px_rgba(217,70,239,0.5)]' : ''}`}>
                                {tab.icon}
                            </div>
                            <span className={`font-medium tracking-wide ${isActive ? 'font-semibold' : ''}`}>{tab.label}</span>
                        </button>
                    )
                })}
            </nav>
            <div className="p-4 border-t border-white/[0.05] bg-black/10">
                <div className="flex items-center space-x-3 text-sm text-slate-400 font-medium bg-white/5 px-4 py-3 rounded-xl border border-white/5">
                    <div className="relative flex h-3 w-3">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-3 w-3 bg-cyan-500 shadow-[0_0_8px_rgba(6,182,212,0.8)]"></span>
                    </div>
                    <span>System Online</span>
                </div>
            </div>
        </div>
    );
};

export default Sidebar;
