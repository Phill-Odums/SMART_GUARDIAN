import React from 'react';
import { Bot, Cpu, Link, Star, Activity, ShieldAlert } from 'lucide-react';

const About = () => {
    return (
        <div className="flex flex-col h-full gap-6 overflow-y-auto pr-2">
            <div>
                <h2 className="text-3xl font-bold tracking-tight">About SMARTGUARD</h2>
                <p className="text-slate-400 mt-1">High-performance AI Security Monitor</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                <div className="glass-panel p-8 space-y-6">
                    <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-500/20 mb-6">
                        <ShieldAlert className="w-8 h-8 text-white" />
                    </div>

                    <h3 className="text-2xl font-semibold mb-2">System Overview</h3>
                    <p className="text-slate-300 leading-relaxed text-lg">
                        This AI Security Monitor leverages real-time object detection across multiple camera feeds.
                        It integrates highly optimized motion detection to reduce processing overhead and minimize fake alerts.
                    </p>

                    <div className="pt-4 border-t border-slate-700/50">
                        <h4 className="font-medium text-slate-200 mb-3 flex items-center gap-2"><Star className="w-4 h-4 text-amber-400" /> Key Features</h4>
                        <ul className="space-y-3">
                            {[
                                'Real-time multi-camera monitoring via Fast MJPEG streaming',
                                'Motion detection heuristics targeting false positives',
                                'Configurable alerting via Telegram, WhatsApp, SMS & Drive',
                                'Sleek, responsive dark-mode Dashboard'
                            ].map((item, i) => (
                                <li key={i} className="flex items-start gap-3 text-slate-300">
                                    <div className="w-1.5 h-1.5 rounded-full bg-blue-500 mt-2 shrink-0" />
                                    <span>{item}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>

                <div className="glass-panel p-8 flex flex-col gap-6">
                    <h3 className="text-xl font-semibold mb-2">Technical Specifications</h3>

                    <div className="grid grid-cols-1 gap-4 flex-1">
                        <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-700/50 flex items-center gap-4">
                            <div className="w-12 h-12 rounded-lg bg-emerald-500/10 flex items-center justify-center shrink-0">
                                <Bot className="w-6 h-6 text-emerald-400" />
                            </div>
                            <div>
                                <h5 className="font-medium text-slate-200">AI Model</h5>
                                <p className="text-sm text-slate-400">YOLOv8n (Ultralytics)</p>
                            </div>
                        </div>

                        <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-700/50 flex items-center gap-4">
                            <div className="w-12 h-12 rounded-lg bg-orange-500/10 flex items-center justify-center shrink-0">
                                <Cpu className="w-6 h-6 text-orange-400" />
                            </div>
                            <div>
                                <h5 className="font-medium text-slate-200">Inference Core</h5>
                                <p className="text-sm text-slate-400">OpenCV / PyTorch Core</p>
                            </div>
                        </div>

                        <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-700/50 flex items-center gap-4">
                            <div className="w-12 h-12 rounded-lg bg-sky-500/10 flex items-center justify-center shrink-0">
                                <Activity className="w-6 h-6 text-sky-400" />
                            </div>
                            <div>
                                <h5 className="font-medium text-slate-200">Architecture</h5>
                                <p className="text-sm text-slate-400">FastAPI backend + React (Vite) Frontend</p>
                            </div>
                        </div>

                        <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-700/50 flex items-center gap-4">
                            <div className="w-12 h-12 rounded-lg bg-rose-500/10 flex items-center justify-center shrink-0">
                                <Link className="w-6 h-6 text-rose-400" />
                            </div>
                            <div>
                                <h5 className="font-medium text-slate-200">Communication</h5>
                                <p className="text-sm text-slate-400">HTTP REST & Server-Sent Events (MJPEG)</p>
                            </div>
                        </div>
                    </div>

                    <div className="mt-auto pt-6 border-t border-slate-700/50 text-center">
                        <p className="text-sm text-slate-500">SMARTGUARD Version 2.0.0</p>
                    </div>
                </div>

            </div>
        </div>
    );
};

export default About;
