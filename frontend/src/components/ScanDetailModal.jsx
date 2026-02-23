import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, AlertTriangle, CheckCircle, FileText, Download, Shield, ExternalLink, Zap } from 'lucide-react';

const ScanDetailModal = ({ isOpen, onClose, scan }) => {
    if (!scan) return null;

    const generateReport = () => {
        // Simulation of report generation
        alert("Generating professional security report for Scan #" + scan.id + "...");
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 20 }}
                        className="glass-card w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col rounded-3xl"
                    >
                        {/* Header */}
                        <div className="p-6 border-b border-slate-800 flex items-center justify-between bg-slate-900/50">
                            <div className="flex items-center gap-3">
                                <div className={`p-2 rounded-lg ${scan.risk_score > 50 ? 'bg-red-500/10 text-red-500' : 'bg-green-500/10 text-green-500'}`}>
                                    <Shield className="w-6 h-6" />
                                </div>
                                <div>
                                    <h2 className="text-xl font-bold">Scan Report #{scan.id}</h2>
                                    <p className="text-sm text-slate-500">{new Date(scan.created_at).toLocaleDateString()} • {scan.project_name || 'Project Analysis'}</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-2">
                                <button
                                    onClick={generateReport}
                                    className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-sm font-semibold transition-all shadow-lg shadow-blue-900/20"
                                >
                                    <Download className="w-4 h-4" />
                                    Generate Report
                                </button>
                                <button
                                    onClick={onClose}
                                    className="p-2 hover:bg-slate-800 rounded-lg transition-colors text-slate-400"
                                >
                                    <X className="w-6 h-6" />
                                </button>
                            </div>
                        </div>

                        {/* Content */}
                        <div className="flex-1 overflow-y-auto p-6 space-y-8">
                            {/* Summary Stats */}
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div className="p-4 bg-slate-800/30 rounded-2xl border border-slate-700/30">
                                    <p className="text-slate-500 text-xs uppercase tracking-wider mb-1">Risk Score</p>
                                    <p className={`text-2xl font-bold ${scan.risk_score > 50 ? 'text-red-400' : 'text-green-400'}`}>{scan.risk_score}/100</p>
                                </div>
                                <div className="p-4 bg-slate-800/30 rounded-2xl border border-slate-700/30">
                                    <p className="text-slate-500 text-xs uppercase tracking-wider mb-1">Total Issues</p>
                                    <p className="text-2xl font-bold text-slate-200">{scan.total_issues}</p>
                                </div>
                                <div className="p-4 bg-slate-800/30 rounded-2xl border border-slate-700/30">
                                    <p className="text-slate-500 text-xs uppercase tracking-wider mb-1">Scan Status</p>
                                    <div className="flex items-center gap-2 text-green-400 font-bold uppercase text-sm">
                                        <CheckCircle className="w-4 h-4" />
                                        Completed
                                    </div>
                                </div>
                            </div>

                            {/* Vulnerability List */}
                            <div>
                                <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                                    <AlertTriangle className="w-5 h-5 text-yellow-500" />
                                    Vulnerability Details
                                </h3>
                                <div className="space-y-4">
                                    {scan.vulnerabilities?.map((vuln, idx) => (
                                        <motion.div
                                            key={vuln.id}
                                            initial={{ opacity: 0, x: -10 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            transition={{ delay: idx * 0.1 }}
                                            className="p-5 bg-slate-900/50 rounded-2xl border border-slate-800 group hover:border-blue-500/20 transition-all"
                                        >
                                            <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                                                <div className="space-y-2">
                                                    <div className="flex items-center gap-2">
                                                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-tighter ${vuln.severity === 'HIGH' || vuln.severity === 'CRITICAL' ? 'bg-red-500/20 text-red-500' :
                                                            vuln.severity === 'MEDIUM' ? 'bg-yellow-500/20 text-yellow-500' : 'bg-blue-500/20 text-blue-500'
                                                            }`}>
                                                            {vuln.severity}
                                                        </span>
                                                        <h5 className="font-bold text-slate-200 text-sm md:text-base">{vuln.vulnerability_type}</h5>
                                                    </div>
                                                    <div className="flex items-center gap-4 text-xs text-slate-500">
                                                        <span className="flex items-center gap-1">
                                                            <FileText className="w-3 h-3" />
                                                            {vuln.file_name}
                                                        </span>
                                                        <span>Line: {vuln.line_number}</span>
                                                    </div>
                                                    <div className="mt-3 p-4 bg-blue-500/5 rounded-xl border border-blue-500/10 italic text-sm text-slate-400 line-leading-loose">
                                                        <Zap className="w-3 h-3 inline mr-2 text-blue-400" />
                                                        {vuln.explanation}
                                                    </div>
                                                </div>
                                                <button className="text-xs text-blue-400 hover:text-blue-300 font-semibold flex items-center gap-1 h-fit whitespace-nowrap">
                                                    View Code <ExternalLink className="w-3 h-3" />
                                                </button>
                                            </div>
                                        </motion.div>
                                    ))}
                                    {(!scan.vulnerabilities || scan.vulnerabilities.length === 0) && (
                                        <div className="text-center py-8 text-slate-500">No specific vulnerabilities to display.</div>
                                    )}
                                </div>
                            </div>
                        </div>

                        {/* Footer */}
                        <div className="p-6 bg-slate-900/80 border-t border-slate-800 text-center">
                            <p className="text-xs text-slate-500 italic">
                                AI SecureScan utilizes advanced contextual reasoning to provide fix suggestions. Always verify suggestions against your security policies.
                            </p>
                        </div>
                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
};

export default ScanDetailModal;
