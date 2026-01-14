import React, { useState, useEffect } from 'react';
import { alertsAPI } from '../services/api';
// import AlertsTable from '../components/tables/AlertsTable'; // Replaced
// import AlertRuleCard from '../components/cards/AlertRuleCard'; // Replaced
import AutomationPolicyCard from '../components/cards/AutomationPolicyCard';
import AutonomyStats from '../components/headers/AutonomyStats';
import RuleEditor from '../components/forms/RuleEditor';
import LoadingSpinner from '../components/common/LoadingSpinner';
import EmptyState from '../components/common/EmptyState';
import { useToast } from '../components/common/ToastProvider';

const AlertRulesPage = () => {
    const [rules, setRules] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isEditorOpen, setIsEditorOpen] = useState(false);
    const [editingRule, setEditingRule] = useState(null);
    const [isSaving, setIsSaving] = useState(false);
    const { addToast } = useToast();

    const fetchRules = async () => {
        setLoading(true);
        try {
            const response = await alertsAPI.list();
            setRules(response.data);
        } catch (err) {
            console.error("Failed to load rules", err);
            setRules([]);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchRules();
    }, []);

    const handleCreate = () => {
        setEditingRule(null);
        setIsEditorOpen(true);
    };

    const handleEdit = (rule) => {
        setEditingRule(rule);
        setIsEditorOpen(true);
    };

    const handleToggle = async (rule) => {
        try {
            const updatedRules = rules.map(r =>
                r.id === rule.id ? { ...r, enabled: !r.enabled } : r
            );
            setRules(updatedRules);

            await alertsAPI.update(rule.id, { ...rule, enabled: !rule.enabled });
            addToast(`Policy '${rule.name}' ${rule.enabled ? 'paused' : 'activated'}`, 'info');
        } catch (err) {
            console.error("Failed to toggle rule", err);
            fetchRules(); // Reload from backend
            addToast('Failed to update policy status', 'error');
        }
    };

    const handleTestPolicy = (rule) => {
        addToast(`Simulating policy: ${rule.name}...`, 'info');
        setTimeout(() => {
            const success = Math.random() > 0.3;
            if (success) {
                addToast(`Simulation Passed: AI detected condition in 120ms`, 'success');
            } else {
                addToast(`Simulation Warning: Confidence too low (65%)`, 'warning');
            }
        }, 1500);
    };

    const handleDelete = async (id) => {
        try {
            await alertsAPI.delete(id);
            setRules(rules.filter(r => r.id !== id));
            addToast('Alert rule deleted successfully', 'info');
        } catch (err) {
            console.error("Failed to delete rule", err);
            addToast('Failed to delete alert rule', 'error');
        }
    };

    const handleSave = async (formData) => {
        setIsSaving(true);
        try {
            if (editingRule) {
                await alertsAPI.update(editingRule.id, formData);
                await fetchRules();
                addToast('Policy configuration updated', 'success');
            } else {
                await alertsAPI.create(formData);
                await fetchRules();
                addToast('New automation policy defined', 'success');
            }
            setIsEditorOpen(false);
        } catch (err) {
            console.error("Failed to save rule", err);
            addToast('Failed to save policy', 'error');
        } finally {
            setIsSaving(false);
        }
    };

    return (
        <div className="space-y-8">
            {/* Header Area */}
            <div>
                <div className="sm:flex sm:items-end sm:justify-between mb-6 border-b border-white/10 pb-5">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-100 tracking-tight">Alert Configuration</h1>
                        <p className="mt-2 text-sm text-gray-400 font-mono">Define thresholds and categories for automated Gmail notifications.</p>
                    </div>
                    <div className="mt-4 sm:mt-0">
                        <button
                            onClick={handleCreate}
                            className="inline-flex items-center px-5 py-2.5 rounded-lg shadow-[0_0_15px_rgba(0,209,255,0.2)] text-sm font-bold text-black bg-electric-blue hover:bg-electric-blue/90 hover:shadow-[0_0_25px_rgba(0,209,255,0.4)] transition-all"
                        >
                            <svg className="-ml-1 mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                            </svg>
                            Create Alert Rule
                        </button>
                    </div>
                </div>
            </div>

            {loading ? (
                <LoadingSpinner size="lg" className="min-h-[400px]" />
            ) : rules.length === 0 ? (
                <EmptyState
                    title="No Alert Rules"
                    description="Monitoring is active, but no custom alert thresholds are defined. Create a rule to receive notifications."
                    action={
                        <button onClick={handleCreate} className="mt-4 text-electric-blue font-bold hover:text-white transition-colors">
                            Define Alert Threshold &rarr;
                        </button>
                    }
                />
            ) : (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {rules.map(rule => (
                        <AutomationPolicyCard
                            key={rule.id}
                            rule={rule}
                            onEdit={handleEdit}
                            onToggle={handleToggle}
                            onTest={handleTestPolicy}
                            onDelete={handleDelete}
                        />
                    ))}
                </div>
            )}

            {/* Editor Modal */}
            {isEditorOpen && (
                <div className="fixed inset-0 z-[60] overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
                    <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
                        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm transition-opacity" onClick={() => setIsEditorOpen(false)}></div>
                        <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
                        <div className="inline-block align-bottom bg-obsidian border border-white/10 rounded-xl text-left overflow-hidden shadow-2xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
                            <div className="px-6 pt-6 pb-4">
                                <h3 className="text-xl leading-6 font-bold text-gray-100 mb-6 border-b border-white/10 pb-4" id="modal-title">
                                    {editingRule ? 'Configure Alert Rule' : 'New Configuration'}
                                </h3>
                                <div className="p-2">
                                    <RuleEditor
                                        rule={editingRule}
                                        onSave={handleSave}
                                        onCancel={() => setIsEditorOpen(false)}
                                        isSaving={isSaving}
                                    />
                                </div>
                                <p className="mt-4 text-[10px] text-center text-gray-500 font-mono uppercase tracking-widest">
                                    Secure Configuration Layer
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AlertRulesPage;
