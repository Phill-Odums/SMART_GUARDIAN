import React, { useState, useEffect } from 'react';
import { Camera, Aperture } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000';

const SingleCapture = () => {
    const [cameras, setCameras] = useState(['0 - Camera 0']);
    const [settings, setSettings] = useState({
        camera_index: 0,
        confidence: 0.25,
    });
    const [resultImg, setResultImg] = useState(null);
    const [summary, setSummary] = useState('');
    const [isCapturing, setIsCapturing] = useState(false);

    useEffect(() => {
        fetch(`${API_BASE_URL}/cameras`)
            .then(res => res.json())
            .then(data => setCameras(data.cameras || ['0 - Camera 0']))
            .catch(err => console.error(err));
    }, []);

    const handleCapture = async () => {
        setIsCapturing(true);
        setResultImg(null);
        setSummary('Initializing camera...');

        try {
            const res = await fetch(`${API_BASE_URL}/single_capture`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    camera_index: settings.camera_index,
                    resolution: '640x480',
                    confidence: settings.confidence,
                    enable_alerts: false,
                    cooldown: 0
                })
            });
            const data = await res.json();
            if (data.image) {
                setResultImg(data.image);
                setSummary(data.summary);
            } else {
                setSummary(data.error || "Capture failed");
            }
        } catch (err) {
            console.error(err);
            setSummary("Network Error");
        } finally {
            setIsCapturing(false);
        }
    };

    return (
        <div className="flex flex-col h-full gap-6">
            <div>
                <h2 className="text-3xl font-bold">Single Capture</h2>
                <p className="text-slate-400 mt-1">Capture and analyze a single frame from any camera</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1 min-h-0">
                <div className="lg:col-span-2 glass-panel flex flex-col relative overflow-hidden bg-slate-950">
                    {isCapturing ? (
                        <div className="absolute inset-0 flex flex-col items-center justify-center bg-slate-900/80 z-10 backdrop-blur-sm">
                            <Aperture className="w-16 h-16 text-blue-500 animate-[spin_3s_linear_infinite] mb-4" />
                            <span className="text-xl font-medium text-blue-400 animate-pulse">Capturing Frame...</span>
                            <span className="text-sm text-slate-400 mt-2">Warming up sensor & analyzing</span>
                        </div>
                    ) : null}

                    <div className="flex-1 flex items-center justify-center p-4">
                        {resultImg ? (
                            <img src={resultImg} alt="Capture Result" className="max-w-full max-h-full object-contain rounded shadow-2xl ring-1 ring-white/10" />
                        ) : (
                            <div className="text-center opacity-50">
                                <Camera className="w-20 h-20 text-slate-700 mx-auto mb-4" />
                                <p className="text-lg font-medium text-slate-500">Ready for capture</p>
                            </div>
                        )}
                    </div>
                </div>

                <div className="glass-panel p-6 flex flex-col gap-6" style={{ height: 'max-content' }}>
                    <div>
                        <h3 className="text-xl font-semibold mb-4 border-b border-slate-700/50 pb-2">Capture Settings</h3>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-slate-400 mb-1">Target Camera</label>
                                <select
                                    value={settings.camera_index}
                                    onChange={(e) => setSettings({ ...settings, camera_index: parseInt(e.target.value) })}
                                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2.5 outline-none focus:border-blue-500 transition-colors"
                                    disabled={isCapturing}
                                >
                                    {cameras.map((cam, idx) => (
                                        <option key={idx} value={parseInt(cam, 10)}>{cam}</option>
                                    ))}
                                </select>
                            </div>

                            <div>
                                <div className="flex justify-between mb-1">
                                    <label className="block text-sm font-medium text-slate-400">AI Confidence</label>
                                    <span className="text-sm text-blue-400">{settings.confidence.toFixed(2)}</span>
                                </div>
                                <input
                                    type="range"
                                    min="0.1" max="0.9" step="0.05"
                                    value={settings.confidence}
                                    onChange={(e) => setSettings({ ...settings, confidence: parseFloat(e.target.value) })}
                                    className="w-full accent-blue-500"
                                    disabled={isCapturing}
                                />
                            </div>
                        </div>
                    </div>

                    <div className="bg-slate-900 rounded-xl p-4 border border-slate-800 min-h-[120px]">
                        <h4 className="text-sm font-medium text-slate-400 mb-2">Detection Summary</h4>
                        <div className="text-sm font-mono text-slate-300 whitespace-pre-line">
                            {summary || "No data."}
                        </div>
                    </div>

                    <button
                        onClick={handleCapture}
                        disabled={isCapturing}
                        className={`w-full py-4 rounded-xl font-bold flex justify-center items-center gap-2 transition-all shadow-lg ${isCapturing ? 'bg-slate-800 text-slate-500' : 'bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-white hover:shadow-emerald-500/25'}`}
                    >
                        <Camera className="w-5 h-5" /> Capture & Analyze
                    </button>
                </div>
            </div>
        </div>
    );
};

export default SingleCapture;
