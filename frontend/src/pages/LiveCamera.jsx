import React, { useState, useEffect, useRef } from 'react';
import { Play, Square, AlertCircle, Video, Camera, Settings } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000';

const LiveCamera = () => {
    const [cameras, setCameras] = useState(['0 - Camera 0']);
    const [settings, setSettings] = useState({
        camera_index: 0,
        resolution: '320x240',
        confidence: 0.4,
        enable_alerts: true,
        cooldown: 10
    });
    const [isStreaming, setIsStreaming] = useState(false);
    const [status, setStatus] = useState('🔴 Stopped');
    const imgRef = useRef(null);

    useEffect(() => {
        fetch(`${API_BASE_URL}/cameras`)
            .then(res => res.json())
            .then(data => setCameras(data.cameras || ['0 - Camera 0']))
            .catch(err => console.error("Failed to fetch cameras:", err));

        fetch(`${API_BASE_URL}/status`)
            .then(res => res.json())
            .then(data => {
                setIsStreaming(data.status === 'active');
                setStatus(data.status === 'active' ? '🟢 Running' : '🔴 Stopped');
            })
            .catch(err => console.error(err));
    }, []);

    const handleStart = async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/start_stream`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(settings)
            });
            if (res.ok) {
                setIsStreaming(true);
                setStatus('🟢 Running');
                // Force image reload
                if (imgRef.current) {
                    imgRef.current.src = `${API_BASE_URL}/video_feed?t=${new Date().getTime()}`;
                }
            }
        } catch (err) {
            console.error(err);
            setStatus('🔴 Error');
        }
    };

    const handleStop = async () => {
        try {
            await fetch(`${API_BASE_URL}/stop_stream`, { method: 'POST' });
            setIsStreaming(false);
            setStatus('🔴 Stopped');
            if (imgRef.current) {
                imgRef.current.src = '';
            }
        } catch (err) {
            console.error(err);
        }
    };

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        let finalValue = type === 'checkbox' ? checked : value;
        if (name === 'camera_index') finalValue = parseInt(value, 10);
        if (name === 'confidence') finalValue = parseFloat(value);
        if (name === 'cooldown') finalValue = parseInt(value, 10);

        setSettings(prev => ({ ...prev, [name]: finalValue }));
    };

    return (
        <div className="flex flex-col h-full gap-8">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-4xl font-bold tracking-tight bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">Live Camera</h2>
                    <p className="text-slate-400 mt-2 font-medium">Real-time object and motion detection</p>
                </div>
                <div className={`px-5 py-2.5 rounded-full border flex items-center gap-3 shadow-lg ${isStreaming ? 'bg-green-500/10 border-green-500/30 text-green-400 shadow-green-500/10' : 'bg-rose-500/10 border-rose-500/30 text-rose-400 shadow-rose-500/10'}`}>
                    <div className={`relative flex h-3 w-3`}>
                        <div className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${isStreaming ? 'bg-green-400' : 'bg-rose-400'}`}></div>
                        <div className={`relative inline-flex rounded-full h-3 w-3 ${isStreaming ? 'bg-green-500' : 'bg-rose-500'}`}></div>
                    </div>
                    <span className="font-semibold tracking-wide">{status}</span>
                </div>
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 flex-1 min-h-0">
                <div className="xl:col-span-2 glass-panel flex flex-col overflow-hidden relative group p-1">
                    <div className="absolute inset-0 flex items-center justify-center bg-[#0B0F19]/80 z-[-1]">
                        <span className="text-slate-500 font-medium tracking-widest uppercase">Camera Offline</span>
                    </div>

                    <div className="relative w-full h-full rounded-xl overflow-hidden bg-black/40 border border-white/[0.05]">
                        {isStreaming ? (
                            <img
                                ref={imgRef}
                                src={`${API_BASE_URL}/video_feed`}
                                className="w-full h-full object-contain"
                                alt="Live feed"
                            />
                        ) : (
                            <div className="flex-1 flex flex-col items-center justify-center h-full gap-4 text-slate-600">
                                <Video className="w-20 h-20 opacity-50" strokeWidth={1.5} />
                                <p className="font-medium tracking-wide">Awaiting Feed</p>
                            </div>
                        )}

                        <div className="absolute bottom-4 inset-x-4 flex justify-between items-center opacity-0 group-hover:opacity-100 transition-opacity bg-black/60 backdrop-blur-md p-4 rounded-xl border border-white/10 shadow-2xl">
                            <span className="text-sm font-semibold tracking-wide text-white flex items-center gap-2">
                                <Camera className="w-4 h-4 text-cyan-400" />
                                {cameras.find(c => parseInt(c) === settings.camera_index)}
                            </span>
                            <span className="text-sm font-medium text-slate-300 bg-white/10 px-3 py-1 rounded-lg">
                                {settings.resolution}
                            </span>
                        </div>
                    </div>
                </div>

                <div className="glass-panel p-8 overflow-y-auto flex flex-col gap-8 relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-fuchsia-500/10 blur-[50px] rounded-full pointer-events-none"></div>

                    <div>
                        <h3 className="text-xl font-bold mb-6 flex items-center gap-2 pb-4 border-b border-white/[0.05]">
                            <Settings className="w-5 h-5 text-fuchsia-400" />
                            Stream Controls
                        </h3>

                        <div className="space-y-6">
                            <div>
                                <label className="block text-sm font-semibold text-slate-300 mb-2 tracking-wide">Select Camera</label>
                                <select
                                    name="camera_index"
                                    value={settings.camera_index}
                                    onChange={handleChange}
                                    className="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 outline-none focus:border-fuchsia-500 focus:ring-1 focus:ring-fuchsia-500 transition-all text-slate-200"
                                    disabled={isStreaming}
                                >
                                    {cameras.map((cam, idx) => (
                                        <option key={idx} value={parseInt(cam, 10)} className="bg-slate-900">{cam}</option>
                                    ))}
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-semibold text-slate-300 mb-2 tracking-wide">Resolution</label>
                                <select
                                    name="resolution"
                                    value={settings.resolution}
                                    onChange={handleChange}
                                    className="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all text-slate-200"
                                    disabled={isStreaming}
                                >
                                    <option value="320x240" className="bg-slate-900">320x240 (Fast)</option>
                                    <option value="640x480" className="bg-slate-900">640x480 (Balanced)</option>
                                    <option value="1280x720" className="bg-slate-900">1280x720 (High Quality)</option>
                                </select>
                            </div>

                            <div className="bg-white/[0.02] p-4 rounded-xl border border-white/[0.05]">
                                <div className="flex justify-between items-center mb-3">
                                    <label className="block text-sm font-semibold text-slate-300 tracking-wide">AI Confidence Match</label>
                                    <span className="text-sm font-bold bg-purple-500/20 text-purple-300 px-2 py-1 rounded-md">{(settings.confidence * 100).toFixed(0)}%</span>
                                </div>
                                <input
                                    type="range"
                                    name="confidence"
                                    min="0.1" max="0.9" step="0.05"
                                    value={settings.confidence}
                                    onChange={handleChange}
                                    className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-500"
                                />
                            </div>

                            <div className="pt-4 border-t border-white/[0.05]">
                                <label className="flex items-center justify-between cursor-pointer group p-3 rounded-xl hover:bg-white/5 transition-colors">
                                    <span className="font-semibold text-slate-300 flex items-center gap-3 tracking-wide">
                                        <div className={`p-2 rounded-lg ${settings.enable_alerts ? 'bg-amber-500/20 text-amber-400' : 'bg-slate-800 text-slate-500'} transition-colors`}>
                                            <AlertCircle className="w-4 h-4" />
                                        </div>
                                        Security Alerts
                                    </span>
                                    <div className="relative">
                                        <input
                                            type="checkbox"
                                            name="enable_alerts"
                                            checked={settings.enable_alerts}
                                            onChange={handleChange}
                                            className="sr-only peer"
                                        />
                                        <div className="w-12 h-6 bg-slate-700/50 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-amber-500 shadow-inner border border-white/5"></div>
                                    </div>
                                </label>
                            </div>

                            {settings.enable_alerts && (
                                <div className="animate-in slide-in-from-top-2 fade-in duration-300 pl-14">
                                    <label className="block text-xs font-semibold text-slate-400 mb-2 tracking-wide uppercase">Alert Cooldown (Seconds)</label>
                                    <input
                                        type="number"
                                        name="cooldown"
                                        value={settings.cooldown}
                                        onChange={handleChange}
                                        className="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-2 outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500 transition-all text-slate-200 font-mono text-sm"
                                    />
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="mt-auto pt-6">
                        {!isStreaming ? (
                            <button
                                onClick={handleStart}
                                className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-400 hover:to-blue-400 text-white py-4 rounded-xl font-bold tracking-wide transition-all shadow-[0_0_20px_rgba(6,182,212,0.3)] hover:shadow-[0_0_25px_rgba(6,182,212,0.5)] transform hover:-translate-y-0.5"
                            >
                                <Play className="w-5 h-5 fill-current" /> INITIALIZE STREAM
                            </button>
                        ) : (
                            <button
                                onClick={handleStop}
                                className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-rose-500 to-red-600 hover:from-rose-400 hover:to-red-500 text-white py-4 rounded-xl font-bold tracking-wide transition-all shadow-[0_0_20px_rgba(244,63,94,0.3)] hover:shadow-[0_0_25px_rgba(244,63,94,0.5)] transform hover:-translate-y-0.5"
                            >
                                <Square className="w-5 h-5 fill-current" /> TERMINATE STREAM
                            </button>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LiveCamera;
