import React, { useState } from 'react';
import { Save, Bell, Shield, Smartphone, HardDrive, MessageSquare } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000';

const Configuration = () => {
    const [config, setConfig] = useState({
        telegram_token: '',
        telegram_chat_id: '',
        gdrive_folder: '',
        whatsapp_key: '',
        whatsapp_phone: '',
        username: '',
        api_key: '',
        phone_numbers: ''
    });
    const [status, setStatus] = useState({ type: '', message: '' });
    const [isSaving, setIsSaving] = useState(false);

    const handleChange = (e) => {
        setConfig({ ...config, [e.target.name]: e.target.value });
    };

    const handleSave = async (e) => {
        e.preventDefault();
        setIsSaving(true);
        setStatus({ type: '', message: '' });

        try {
            const res = await fetch(`${API_BASE_URL}/config`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(config)
            });
            const data = await res.json();
            if (res.ok) {
                setStatus({ type: 'success', message: data.message || 'Configuration saved successfully!' });
            } else {
                setStatus({ type: 'error', message: 'Failed to save configuration.' });
            }
        } catch (err) {
            console.error(err);
            setStatus({ type: 'error', message: 'Network error occurred.' });
        } finally {
            setIsSaving(false);
        }
    };

    return (
        <div className="flex flex-col h-full gap-6 overflow-y-auto pr-2">
            <div>
                <h2 className="text-3xl font-bold flex items-center gap-3">
                    <Shield className="w-8 h-8 text-blue-500" /> System Configuration
                </h2>
                <p className="text-slate-400 mt-1">Manage alert endpoints and authentication</p>
            </div>

            <form onSubmit={handleSave} className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Core Auth */}
                <div className="glass-panel p-6 space-y-4 shadow-[0_0_15px_rgba(59,130,246,0.05)] border-t-2 border-t-blue-500/50">
                    <h3 className="text-lg font-semibold flex items-center gap-2 mb-4">
                        <Shield className="w-5 h-5 text-blue-400" /> Core Authentication
                    </h3>
                    <div>
                        <label className="block text-sm font-medium text-slate-400 mb-1">Username</label>
                        <input
                            type="text" name="username" value={config.username} onChange={handleChange}
                            className="w-full bg-slate-950/50 border border-slate-700/50 rounded-lg px-4 py-2.5 outline-none focus:border-blue-500 transition-colors"
                            placeholder="Admin"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-slate-400 mb-1">Alert API Key</label>
                        <input
                            type="password" name="api_key" value={config.api_key} onChange={handleChange}
                            className="w-full bg-slate-950/50 border border-slate-700/50 rounded-lg px-4 py-2.5 outline-none focus:border-blue-500 transition-colors"
                            placeholder="••••••••••••••••"
                        />
                    </div>
                </div>

                {/* Telegram */}
                <div className="glass-panel p-6 space-y-4 shadow-[0_0_15px_rgba(56,189,248,0.05)] border-t-2 border-t-sky-500/50">
                    <h3 className="text-lg font-semibold flex items-center gap-2 mb-4">
                        <MessageSquare className="w-5 h-5 text-sky-400" /> Telegram Integration
                    </h3>
                    <div>
                        <label className="block text-sm font-medium text-slate-400 mb-1">Bot Token</label>
                        <input
                            type="text" name="telegram_token" value={config.telegram_token} onChange={handleChange}
                            className="w-full bg-slate-950/50 border border-slate-700/50 rounded-lg px-4 py-2.5 outline-none focus:border-sky-500 transition-colors"
                            placeholder="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-slate-400 mb-1">Chat ID</label>
                        <input
                            type="text" name="telegram_chat_id" value={config.telegram_chat_id} onChange={handleChange}
                            className="w-full bg-slate-950/50 border border-slate-700/50 rounded-lg px-4 py-2.5 outline-none focus:border-sky-500 transition-colors"
                            placeholder="-1001234567890"
                        />
                    </div>
                </div>

                {/* WhatsApp & SMS */}
                <div className="glass-panel p-6 space-y-4 shadow-[0_0_15px_rgba(34,197,94,0.05)] border-t-2 border-t-emerald-500/50">
                    <h3 className="text-lg font-semibold flex items-center gap-2 mb-4">
                        <Smartphone className="w-5 h-5 text-emerald-400" /> WhatsApp & External SMS
                    </h3>
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-slate-400 mb-1">CallMeBot API Key</label>
                            <input
                                type="text" name="whatsapp_key" value={config.whatsapp_key} onChange={handleChange}
                                className="w-full bg-slate-950/50 border border-slate-700/50 rounded-lg px-4 py-2.5 outline-none focus:border-emerald-500 transition-colors"
                                placeholder="Required for WA"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-400 mb-1">WhatsApp Phone</label>
                            <input
                                type="text" name="whatsapp_phone" value={config.whatsapp_phone} onChange={handleChange}
                                className="w-full bg-slate-950/50 border border-slate-700/50 rounded-lg px-4 py-2.5 outline-none focus:border-emerald-500 transition-colors"
                                placeholder="+1234567890"
                            />
                        </div>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-slate-400 mb-1">SMS Phone Numbers (comma separated)</label>
                        <input
                            type="text" name="phone_numbers" value={config.phone_numbers} onChange={handleChange}
                            className="w-full bg-slate-950/50 border border-slate-700/50 rounded-lg px-4 py-2.5 outline-none focus:border-emerald-500 transition-colors"
                            placeholder="+1234567890, +0987654321"
                        />
                    </div>
                </div>

                {/* Cloud Storage */}
                <div className="glass-panel p-6 space-y-4 shadow-[0_0_15px_rgba(245,158,11,0.05)] border-t-2 border-t-amber-500/50">
                    <h3 className="text-lg font-semibold flex items-center gap-2 mb-4">
                        <HardDrive className="w-5 h-5 text-amber-400" /> Cloud Storage
                    </h3>
                    <div className="p-4 bg-amber-500/10 border border-amber-500/20 rounded-xl mb-4 text-sm text-amber-200/80">
                        For Google Drive JSON, please place `gdrive_service.json` in the `/config` folder in the backend directory manually.
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-slate-400 mb-1">Google Drive Folder ID (optional)</label>
                        <input
                            type="text" name="gdrive_folder" value={config.gdrive_folder} onChange={handleChange}
                            className="w-full bg-slate-950/50 border border-slate-700/50 rounded-lg px-4 py-2.5 outline-none focus:border-amber-500 transition-colors"
                            placeholder="1A2B3C4D5E6F7G8H9I0J"
                        />
                    </div>
                </div>

                {/* Global Save */}
                <div className="md:col-span-2 glass-panel p-6 flex flex-col sm:flex-row items-center justify-between gap-4">
                    <div className="flex-1">
                        {status.message && (
                            <div className={`px-4 py-3 rounded-xl flex items-center gap-3 ${status.type === 'error' ? 'bg-red-500/10 text-red-400 border border-red-500/20' : 'bg-green-500/10 text-green-400 border border-green-500/20'}`}>
                                {status.type === 'error' ? <AlertTriangle className="w-5 h-5 shrink-0" /> : <CheckCircle className="w-5 h-5 shrink-0" />}
                                <span className="font-medium">{status.message}</span>
                            </div>
                        )}
                    </div>
                    <button
                        type="submit"
                        disabled={isSaving}
                        className={`px-8 py-3 rounded-xl font-bold flex items-center gap-2 transition-all shadow-lg min-w-[200px] justify-center ${isSaving ? 'bg-slate-700 text-slate-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-500 text-white hover:shadow-blue-500/25'}`}
                    >
                        {isSaving ? 'Saving...' : <><Save className="w-5 h-5" /> Save Configuration</>}
                    </button>
                </div>
            </form>
        </div>
    );
};

export default Configuration;
