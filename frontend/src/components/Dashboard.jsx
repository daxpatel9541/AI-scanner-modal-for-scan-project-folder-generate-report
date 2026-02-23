import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Shield, Upload, History, AlertTriangle, CheckCircle, BarChart3, ChevronRight, Zap } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import UploadModal from './UploadModal';
import ScanDetailModal from './ScanDetailModal';

const Dashboard = () => {
    const [history, setHistory] = useState([]);
    const [isUploadOpen, setIsUploadOpen] = useState(false);
    const [selectedScan, setSelectedScan] = useState(null);
    const [isDetailOpen, setIsDetailOpen] = useState(false);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchHistory();
    }, []);

    const fetchHistory = async () => {
        try {
            const response = await axios.get('http://localhost:8000/api/history/');
            setHistory(response.data);
        } catch (error) {
            console.error("Error fetching history:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleScanClick = (scan) => {
        setSelectedScan(scan);
        setIsDetailOpen(true);
    };

    const stats = [
        { label: 'Total Scans', value: history.length, icon: BarChart3, color: 'text-blue-400' },
        { label: 'Critical Issues', value: history.reduce((acc, scan) => acc + scan.total_issues, 0), icon: AlertTriangle, color: 'text-red-400' },
        { label: 'Avg Risk Score', value: history.length ? (history.reduce((acc, scan) => acc + scan.risk_score, 0) / history.length).toFixed(1) : 0, icon: Zap, color: 'text-yellow-400' },
        { label: 'Security Health', value: '94%', icon: CheckCircle, color: 'text-green-400' },
    ];

    return (
        <div className="min-h-screen w-full p-4 md:p-8 text-slate-200">
            {/* Header */}
            <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-6 mb-12">
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="flex items-center gap-3"
                >
                    <div className="p-3 bg-blue-500/20 rounded-2xl border border-blue-500/30">
                        <Shield className="w-8 h-8 text-blue-400" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold gradient-text">AI SecureScan</h1>
                        <p className="text-slate-400 text-sm">Enterprise Code Security Scanner</p>
                    </div>
                </motion.div>

                <motion.button
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setIsUploadOpen(true)}
                    className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-500 rounded-xl font-semibold shadow-lg shadow-blue-900/20 transition-all"
                >
                    <Upload className="w-5 h-5" />
                    New Security Scan
                </motion.button>
            </div>

            {/* Stats Grid */}
            <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
                {stats.map((stat, idx) => (
                    <motion.div
                        key={stat.label}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.1 }}
                        className="glass-card p-6 rounded-3xl"
                    >
                        <div className="flex items-center justify-between mb-4">
                            <stat.icon className={`w-6 h-6 ${stat.color}`} />
                            <div className="text-xs font-medium text-slate-500 uppercase tracking-wider">Live</div>
                        </div>
                        <div className="text-3xl font-bold mb-1">{stat.value}</div>
                        <div className="text-slate-400 text-sm">{stat.label}</div>
                    </motion.div>
                ))}
            </div>

            {/* Scan History */}
            <div className="max-w-7xl mx-auto">
                <div className="flex items-center justify-between mb-6 px-2">
                    <h2 className="text-xl font-bold flex items-center gap-2">
                        <History className="w-5 h-5 text-blue-400" />
                        Recent Security Audits
                    </h2>
                    <button className="text-sm text-blue-400 hover:text-blue-300 font-medium">View All</button>
                </div>

                <div className="grid gap-4">
                    <AnimatePresence>
                        {loading ? (
                            <div className="text-center py-12 text-slate-500">Loading audit history...</div>
                        ) : history.length === 0 ? (
                            <div className="glass-card p-12 rounded-3xl text-center">
                                <div className="inline-flex p-4 bg-slate-800/50 rounded-full mb-4">
                                    <Shield className="w-8 h-8 text-slate-600" />
                                </div>
                                <h3 className="text-xl font-semibold mb-2 text-slate-300">No scans found</h3>
                                <p className="text-slate-500 mb-6">Start your first security audit to see results here.</p>
                                <button
                                    onClick={() => setIsUploadOpen(true)}
                                    className="text-blue-400 hover:text-blue-300 font-semibold"
                                >
                                    Run initial scan &rarr;
                                </button>
                            </div>
                        ) : (
                            history.map((scan, idx) => (
                                <motion.div
                                    key={scan.id}
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: idx * 0.05 }}
                                    onClick={() => handleScanClick(scan)}
                                    className="glass-card p-5 rounded-2xl flex items-center justify-between group hover:border-blue-500/30 transition-all cursor-pointer"
                                >
                                    <div className="flex items-center gap-4">
                                        <div className={`p-3 rounded-xl ${scan.risk_score > 50 ? 'bg-red-500/10 text-red-500' :
                                            scan.risk_score > 20 ? 'bg-yellow-500/10 text-yellow-500' :
                                                'bg-green-500/10 text-green-500'
                                            }`}>
                                            {scan.risk_score > 50 ? <AlertTriangle /> : <CheckCircle />}
                                        </div>
                                        <div>
                                            <h4 className="font-semibold text-slate-200">Scan #{scan.id} • {scan.project_name || 'Analysis'}</h4>
                                            <p className="text-sm text-slate-500">{new Date(scan.created_at).toLocaleDateString()} • Grade: <span className="text-blue-400 font-bold">{scan.security_grade}</span></p>
                                        </div>
                                    </div>

                                    <div className="flex flex-col items-end gap-1">
                                        <div className="flex items-center gap-4">
                                            <div className="text-right">
                                                <div className="text-sm font-bold text-slate-300">{scan.total_issues} Issues</div>
                                                <div className="text-xs text-slate-500">Risk: {scan.risk_percentage?.toFixed(1)}%</div>
                                            </div>
                                            <ChevronRight className="w-5 h-5 text-slate-600 group-hover:text-blue-400 group-hover:translate-x-1 transition-all" />
                                        </div>
                                    </div>
                                </motion.div>
                            ))
                        )}
                    </AnimatePresence>
                </div>
            </div>

            {/* Modals */}
            <UploadModal
                isOpen={isUploadOpen}
                onClose={() => setIsUploadOpen(false)}
                onSuccess={(data) => {
                    setIsUploadOpen(false);
                    // Show details of the volatile scan immediately
                    setSelectedScan(data);
                    setIsDetailOpen(true);
                }}
            />

            <ScanDetailModal
                isOpen={isDetailOpen}
                onClose={() => setIsDetailOpen(false)}
                scan={selectedScan}
            />
        </div>
    );
};

export default Dashboard;
