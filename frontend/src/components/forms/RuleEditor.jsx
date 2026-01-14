import React, { useState, useEffect } from 'react';

const RuleEditor = ({ rule, onSave, onCancel, isSaving }) => {
    const [formData, setFormData] = useState({
        name: '',
        category: 'Database',
        threshold: 5,
        window_minutes: 15,
        severity: 'HIGH',
        enabled: true
    });

    useEffect(() => {
        if (rule) {
            setFormData({
                name: rule.name || '',
                category: rule.category || 'Database',
                threshold: rule.threshold || 5,
                window_minutes: rule.window_minutes || 15,
                severity: rule.severity || 'HIGH',
                enabled: rule.enabled !== undefined ? rule.enabled : true
            });
        }
    }, [rule]);

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        onSave({
            ...formData,
            threshold: parseInt(formData.threshold),
            window_minutes: parseInt(formData.window_minutes)
        });
    };

    const inputClasses = "mt-1 block w-full bg-black/60 border border-white/20 rounded-xl text-white font-medium py-3 px-4 focus:ring-2 focus:ring-electric-blue focus:border-transparent outline-none transition-all placeholder:text-gray-600";
    const labelClasses = "block text-[10px] font-black text-gray-400 uppercase tracking-widest ml-1 mb-1";

    return (
        <form onSubmit={handleSubmit} className="space-y-6">
            <div>
                <label className={labelClasses}>Descriptive Name</label>
                <input
                    type="text"
                    name="name"
                    required
                    className={inputClasses}
                    value={formData.name}
                    onChange={handleChange}
                    placeholder="e.g., PostgreSQL Latency Spike Warning"
                />
            </div>

            <div>
                <label className={labelClasses}>Trigger Category</label>
                <select
                    name="category"
                    className={inputClasses}
                    value={formData.category}
                    onChange={handleChange}
                >
                    <option value="Database">Database & Storage</option>
                    <option value="Network">Network & CDN</option>
                    <option value="Security">Security & IAM</option>
                    <option value="Compute">Compute & Clusters</option>
                    <option value="Application">Application Logic</option>
                    <option value="API">API Gateway</option>
                </select>
                <p className="mt-1.5 text-[10px] text-gray-500 italic">Emails will trigger when AI identifies logs matching this category.</p>
            </div>

            <div className="grid grid-cols-2 gap-4">
                <div>
                    <label className={labelClasses}>Error Count Threshold</label>
                    <input
                        type="number"
                        name="threshold"
                        required
                        min="1"
                        className={inputClasses}
                        value={formData.threshold}
                        onChange={handleChange}
                    />
                </div>
                <div>
                    <label className={labelClasses}>Time Window (min)</label>
                    <input
                        type="number"
                        name="window_minutes"
                        required
                        min="1"
                        className={inputClasses}
                        value={formData.window_minutes}
                        onChange={handleChange}
                    />
                </div>
            </div>

            <div>
                <label className={labelClasses}>Criticality Level</label>
                <div className="grid grid-cols-4 gap-2">
                    {['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'].map((s) => (
                        <button
                            key={s}
                            type="button"
                            onClick={() => setFormData({ ...formData, severity: s })}
                            className={`py-2 rounded-lg text-[10px] font-bold border transition-all ${formData.severity === s
                                    ? 'bg-electric-blue/20 border-electric-blue text-electric-blue'
                                    : 'bg-white/5 border-white/10 text-gray-500 hover:border-white/30'
                                }`}
                        >
                            {s}
                        </button>
                    ))}
                </div>
            </div>

            <div className="flex items-center gap-3 bg-white/5 p-4 rounded-xl border border-white/10">
                <input
                    id="enabled"
                    name="enabled"
                    type="checkbox"
                    className="h-5 w-5 bg-black border-white/20 rounded text-electric-blue focus:ring-electric-blue"
                    checked={formData.enabled}
                    onChange={handleChange}
                />
                <label htmlFor="enabled" className="text-sm font-bold text-gray-300 pointer-events-none">
                    Enable Continuous Monitoring
                </label>
            </div>

            <div className="flex justify-end gap-3 pt-6 border-t border-white/10">
                <button
                    type="button"
                    onClick={onCancel}
                    className="px-6 py-2.5 rounded-xl text-xs font-bold text-gray-400 hover:text-white hover:bg-white/5 transition-all"
                >
                    Discard Changes
                </button>
                <button
                    type="submit"
                    disabled={isSaving}
                    className="px-6 py-2.5 bg-electric-blue text-black rounded-xl text-xs font-black tracking-widest hover:bg-white hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-50"
                >
                    {isSaving ? 'SYNCING...' : 'SAVE CONFIGURATION'}
                </button>
            </div>
        </form>
    );
};

export default RuleEditor;
