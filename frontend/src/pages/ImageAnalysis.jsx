import React, { useState } from 'react';
import { Upload, Image as ImageIcon, CheckCircle, AlertTriangle } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000';

const ImageAnalysis = () => {
    const [selectedFile, setSelectedFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [resultImg, setResultImg] = useState(null);
    const [summary, setSummary] = useState('');
    const [isAnalyzing, setIsAnalyzing] = useState(false);

    const [settings, setSettings] = useState({
        confidence: 0.4,
        device: 'cpu'
    });

    const handleFileChange = (e) => {
        if (e.target.files && e.target.files[0]) {
            const file = e.target.files[0];
            setSelectedFile(file);
            setPreview(URL.createObjectURL(file));
            setResultImg(null);
            setSummary('');
        }
    };

    const handleAnalyze = async () => {
        if (!selectedFile) return;

        setIsAnalyzing(true);
        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('conf', settings.confidence);
        formData.append('device', settings.device);

        try {
            const res = await fetch(`${API_BASE_URL}/analyze_image`, {
                method: 'POST',
                body: formData,
            });
            const data = await res.json();
            if (data.image) {
                setResultImg(data.image);
                setSummary(data.summary);
            } else {
                setSummary(data.error || "Analysis failed");
            }
        } catch (err) {
            console.error(err);
            setSummary("Network Error");
        } finally {
            setIsAnalyzing(false);
        }
    };

    return (
        <div className="flex flex-col h-full gap-8">
            <div className="flex justify-between items-end">
                <div>
                    <h2 className="text-4xl font-bold tracking-tight bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">Image Analysis</h2>
                    <p className="text-slate-400 mt-2 font-medium">Upload an image for AI detection</p>
                </div>
                {isAnalyzing && (
                    <div className="flex items-center gap-3 bg-purple-500/10 border border-purple-500/30 px-5 py-2.5 rounded-full shadow-[0_0_15px_rgba(168,85,247,0.2)]">
                        <div className="w-4 h-4 rounded-full border-2 border-purple-400 border-t-transparent animate-spin"></div>
                        <span className="text-purple-400 font-semibold tracking-wide">Processing...</span>
                    </div>
                )}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1 min-h-0">
                <div className="lg:col-span-2 flex flex-col gap-6">
                    <div className="grid grid-cols-2 gap-4 h-full relative">
                        <div className="glass-panel relative overflow-hidden group flex flex-col p-1">
                            <div className="border-b border-white/[0.05] p-4 bg-white/[0.02] font-semibold tracking-wide text-sm text-slate-300 flex justify-between items-center z-10">
                                <span className="flex items-center gap-2"><ImageIcon className="w-4 h-4 text-cyan-400" /> Original Input</span>
                                {selectedFile && <span className="text-cyan-400 truncate w-32 text-right bg-cyan-400/10 px-2 py-1 rounded-md">{selectedFile.name}</span>}
                            </div>
                            <div className="flex-1 relative bg-black/40 flex items-center justify-center p-4 rounded-b-xl">
                                {preview ? (
                                    <img src={preview} alt="Upload preview" className="max-w-full max-h-full object-contain drop-shadow-2xl rounded-lg border border-white/5" />
                                ) : (
                                    <div className="text-center flex flex-col items-center">
                                        <div className="p-4 bg-white/5 rounded-full mb-4">
                                            <ImageIcon className="w-10 h-10 text-slate-600" />
                                        </div>
                                        <p className="text-slate-500 text-sm font-medium tracking-wide">Select an image to analyze</p>
                                    </div>
                                )}

                                <div className="absolute inset-0 bg-[#0B0F19]/90 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-all duration-300 border-2 border-dashed border-cyan-500/50 m-4 rounded-xl backdrop-blur-md">
                                    <label className="cursor-pointer flex flex-col items-center transform transition-transform group-hover:scale-105">
                                        <div className="p-4 bg-cyan-500/20 rounded-full mb-3 shadow-[0_0_15px_rgba(6,182,212,0.4)] ring-1 ring-cyan-500/50">
                                            <Upload className="w-8 h-8 text-cyan-400" />
                                        </div>
                                        <span className="text-cyan-400 font-bold tracking-wide">Browse Files</span>
                                        <span className="text-xs text-slate-400 mt-1">Supports JPG, PNG</span>
                                        <input type="file" className="hidden" accept="image/*" onChange={handleFileChange} />
                                    </label>
                                </div>
                            </div>
                        </div>

                        <div className="glass-panel relative flex flex-col p-1 overflow-hidden">
                            <div className="absolute top-0 right-0 w-48 h-48 bg-purple-500/10 blur-[60px] rounded-full pointer-events-none"></div>
                            <div className="border-b border-white/[0.05] p-4 bg-white/[0.02] font-semibold tracking-wide text-sm text-slate-300 flex items-center gap-2 z-10">
                                <CheckCircle className="w-4 h-4 text-purple-400" /> AI Detection Result
                            </div>
                            <div className="flex-1 relative bg-black/40 flex items-center justify-center p-4 rounded-b-xl z-0">
                                {isAnalyzing ? (
                                    <div className="flex flex-col items-center">
                                        <div className="w-12 h-12 border-4 border-purple-500/30 border-t-purple-500 rounded-full animate-spin mb-4 shadow-[0_0_15px_rgba(168,85,247,0.5)]"></div>
                                        <span className="text-purple-400 font-bold tracking-widest uppercase text-sm animate-pulse">Running YOLO Inference</span>
                                    </div>
                                ) : resultImg ? (
                                    <img src={resultImg} alt="Analysis Result" className="max-w-full max-h-full object-contain drop-shadow-2xl rounded-lg border border-purple-500/20" />
                                ) : (
                                    <div className="text-center flex flex-col items-center">
                                        <div className="p-4 bg-white/5 rounded-full mb-4">
                                            <CheckCircle className="w-10 h-10 text-slate-600" />
                                        </div>
                                        <p className="text-slate-500 text-sm font-medium tracking-wide">Awaiting analysis</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>

                <div className="glass-panel p-8 flex flex-col gap-6 relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-32 h-32 bg-cyan-500/10 blur-[50px] rounded-full pointer-events-none"></div>
                    <div>
                        <h3 className="text-xl font-bold mb-6 flex items-center gap-2 pb-4 border-b border-white/[0.05]">
                            <AlertTriangle className="w-5 h-5 text-cyan-400" />
                            Inference Parameters
                        </h3>
                        <div className="space-y-6">
                            <div className="bg-white/[0.02] p-4 rounded-xl border border-white/[0.05]">
                                <div className="flex justify-between items-center mb-3">
                                    <label className="block text-sm font-semibold text-slate-300 tracking-wide">Confidence Threshold</label>
                                    <span className="text-sm font-bold bg-purple-500/20 text-purple-300 px-2 py-1 rounded-md">{(settings.confidence * 100).toFixed(0)}%</span>
                                </div>
                                <input
                                    type="range"
                                    min="0.1" max="0.9" step="0.05"
                                    value={settings.confidence}
                                    onChange={(e) => setSettings({ ...settings, confidence: parseFloat(e.target.value) })}
                                    className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-500"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-semibold text-slate-300 mb-2 tracking-wide">Processing Device</label>
                                <select
                                    value={settings.device}
                                    onChange={(e) => setSettings({ ...settings, device: e.target.value })}
                                    className="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all text-slate-200"
                                >
                                    <option value="cpu" className="bg-slate-900">CPU Optimized</option>
                                    <option value="0" className="bg-slate-900">GPU (CUDA 0)</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    <div className="flex-1 min-h-[150px] bg-black/40 rounded-xl p-5 border border-white/[0.05] flex flex-col shadow-inner">
                        <h4 className="text-sm font-bold tracking-wider text-slate-400 mb-3 flex items-center gap-2 uppercase">
                            {resultImg ? <CheckCircle className="w-4 h-4 text-green-400" /> : <AlertTriangle className="w-4 h-4 text-amber-500" />}
                            Detection Summary
                        </h4>
                        <div className="flex-1 overflow-y-auto text-sm text-slate-300 leading-relaxed font-mono">
                            {summary || "Upload an image and initialize analysis to retrieve telemetrics."}
                        </div>
                    </div>

                    <div className="pt-2">
                        <button
                            onClick={handleAnalyze}
                            disabled={!selectedFile || isAnalyzing}
                            className={`w-full py-4 rounded-xl font-bold tracking-wide transition-all shadow-lg flex justify-center items-center gap-2 transform ${!selectedFile || isAnalyzing ? 'bg-white/5 text-slate-500 cursor-not-allowed border border-white/5' : 'bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white shadow-[0_0_20px_rgba(6,182,212,0.3)] hover:shadow-[0_0_25px_rgba(6,182,212,0.5)] hover:-translate-y-0.5'}`}
                        >
                            {isAnalyzing ? (
                                <>Processing Request...</>
                            ) : (
                                <>INITIALIZE ANALYSIS</>
                            )}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ImageAnalysis;
