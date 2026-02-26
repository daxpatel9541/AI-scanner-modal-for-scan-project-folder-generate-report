import React, { useState, useCallback } from 'react';
import axios from 'axios';
import { X, Upload, FileCode, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const UploadModal = ({ isOpen, onClose, onSuccess }) => {
    const [file, setFile] = useState(null); // ZIP file or Array of files
    const [projectName, setProjectName] = useState('');
    const [status, setStatus] = useState('idle'); // idle, uploading, scansuccess, error
    const [errorMessage, setErrorMessage] = useState('');
    const [progress, setProgress] = useState(0);
    const [uploadMode, setUploadMode] = useState('file'); // 'file' or 'folder'

    const [ignoredCount, setIgnoredCount] = useState(0);
    const IGNORED_DIRS = [
        'node_modules', '.git', '.svn', '.hg', 'dist', 'build',
        'venv', '.venv', 'env', '.env', '__pycache__',
        '.vscode', '.idea', '.next', 'target', 'vendor',
        'assets', 'images', 'img', 'docs', 'documentation', 'logs',
        'tmp', 'temp', 'obj', 'bin', '.cache', 'bower_components', 'site-packages'
    ];

    const IGNORED_EXTENSIONS = [
        '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.webp', // Images
        '.mp4', '.mov', '.avi', '.wmv', '.flv', // Video
        '.mp3', '.wav', '.flac', '.m4a', // Audio
        '.pdf', '.docx', '.doc', '.xlsx', '.xls', '.pptx', '.ppt', // Documents
        '.zip', '.tar', '.gz', '.rar', '.7z', // Archives
        '.exe', '.dll', '.so', '.dylib', '.bin', // Binaries
        '.woff', '.woff2', '.ttf', '.eot', // Fonts
        '.map', '.log', '.tmp' // Metadata/Logs
    ];

    const handleFileChange = (e) => {
        const selectedFiles = e.target.files;
        if (selectedFiles && selectedFiles.length > 0) {
            if (uploadMode === 'file') {
                setFile(selectedFiles[0]);
                if (!projectName) setProjectName(selectedFiles[0].name.replace('.zip', ''));
                setIgnoredCount(0);
            } else {
                const fileArray = Array.from(selectedFiles);

                // Smart Ignore: Filter out dependency folders, metadata, and unimportant file types
                const filteredFiles = fileArray.filter(f => {
                    const pathParts = f.webkitRelativePath.split('/');
                    const fileName = f.name.toLowerCase();
                    // Don't check the root folder (pathParts[0]) against IGNORED_DIRS
                    // Only check subfolders (pathParts.slice(1))
                    const hasIgnoredDir = pathParts.slice(1).some(part => IGNORED_DIRS.includes(part));
                    const hasIgnoredExt = IGNORED_EXTENSIONS.some(ext => fileName.endsWith(ext));
                    return !hasIgnoredDir && !hasIgnoredExt;
                });

                setFile(filteredFiles);
                setIgnoredCount(fileArray.length - filteredFiles.length);

                // Extract folder name from webkitRelativePath
                const firstPath = selectedFiles[0].webkitRelativePath;
                if (firstPath && !projectName) {
                    setProjectName(firstPath.split('/')[0]);
                }
            }
        }
    };

    const [scanStep, setScanStep] = useState(0);

    const scanSteps = [
        "Initializing Security Engine...",
        "Extracting Codebase & Resolving Dependencies...",
        "Running Bandit Static Analysis (Python)...",
        "Running Semgrep Multi-language Patterns...",
        "Applying AI Contextual Reasoning Layer...",
        "Finalizing Risk Scorings & Analytics..."
    ];

    const handleUpload = async () => {
        if (!file) return;

        setStatus('uploading');
        setProgress(0);
        setScanStep(0);

        const formData = new FormData();
        formData.append('projectName', projectName);
        formData.append('mode', uploadMode);

        if (uploadMode === 'file') {
            formData.append('file', file);
        } else {
            // Folder mode: append each file with its relative path
            file.forEach((f) => {
                formData.append('files', f);
                formData.append('paths', f.webkitRelativePath);
            });
        }

        try {
            // Simulated initialization phases
            for (let i = 0; i < 3; i++) {
                setScanStep(i);
                setProgress(Math.round(((i + 1) / scanSteps.length) * 100));
                await new Promise(resolve => setTimeout(resolve, 600));
            }

            const response = await axios.post('http://localhost:8000/api/upload/', formData);

            // Finalizing phases
            for (let i = 3; i < scanSteps.length; i++) {
                setScanStep(i);
                setProgress(Math.round(((i + 1) / scanSteps.length) * 100));
                await new Promise(resolve => setTimeout(resolve, 800));
            }

            setStatus('scansuccess');
            setTimeout(() => {
                onSuccess(response.data);
                reset();
            }, 1000);
        } catch (error) {
            console.error("Upload error:", error);
            const msg = error.response?.data?.error || "There was an issue processing your project assets. Check system limits.";
            setErrorMessage(msg);
            setStatus('error');
        }
    };

    const reset = () => {
        setFile(null);
        setProjectName('');
        setStatus('idle');
        setErrorMessage('');
        setProgress(0);
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onClick={onClose}
                className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm"
            />

            <motion.div
                initial={{ opacity: 0, scale: 0.95, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                className="relative w-full max-w-lg glass-card rounded-3xl overflow-hidden shadow-2xl"
            >
                <div className="p-6 border-b border-white/5 flex items-center justify-between">
                    <h2 className="text-xl font-bold text-white">Advanced Security Scan</h2>
                    <button onClick={onClose} className="p-1 hover:bg-white/10 rounded-lg transition-all">
                        <X className="w-5 h-5 text-slate-400" />
                    </button>
                </div>

                <div className="p-8">
                    <AnimatePresence mode="wait">
                        {status === 'idle' && (
                            <motion.div
                                key="idle"
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -10 }}
                            >
                                {/* Mode Toggle */}
                                <div className="flex bg-slate-900/50 p-1 rounded-xl mb-6 border border-white/5">
                                    <button
                                        onClick={() => { setUploadMode('file'); setFile(null); }}
                                        className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all ${uploadMode === 'file' ? 'bg-blue-600 text-white shadow-lg' : 'text-slate-400 hover:text-white'}`}
                                    >
                                        ZIP File
                                    </button>
                                    <button
                                        onClick={() => { setUploadMode('folder'); setFile(null); }}
                                        className={`flex-1 py-2 rounded-lg text-sm font-medium transition-all ${uploadMode === 'folder' ? 'bg-blue-600 text-white shadow-lg' : 'text-slate-400 hover:text-white'}`}
                                    >
                                        Project Folder
                                    </button>
                                </div>

                                <div className="mb-6">
                                    <label className="block text-sm font-medium text-slate-400 mb-2">Project Name</label>
                                    <input
                                        type="text"
                                        value={projectName}
                                        onChange={(e) => setProjectName(e.target.value)}
                                        placeholder="e.g. Fintech API Core"
                                        className="w-full bg-slate-900/50 border border-white/10 rounded-xl px-4 py-3 focus:outline-none focus:border-blue-500 transition-all text-white"
                                    />
                                </div>

                                <div className="relative group border-2 border-dashed border-white/10 hover:border-blue-500/50 rounded-2xl p-10 text-center transition-all">
                                    {uploadMode === 'file' ? (
                                        <input
                                            type="file"
                                            accept=".zip"
                                            onChange={handleFileChange}
                                            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                        />
                                    ) : (
                                        <input
                                            type="file"
                                            webkitdirectory="true"
                                            directory="true"
                                            multiple
                                            onChange={handleFileChange}
                                            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                        />
                                    )}
                                    <div className="flex flex-col items-center pointer-events-none">
                                        <div className="p-4 bg-blue-500/10 rounded-2xl mb-4 group-hover:scale-110 transition-transform">
                                            <Upload className="w-8 h-8 text-blue-400" />
                                        </div>
                                        {file ? (
                                            <div className="flex flex-col items-center gap-1">
                                                <div className="flex items-center gap-2 text-blue-300 font-medium">
                                                    <FileCode className="w-4 h-4" />
                                                    {uploadMode === 'file' ? file.name : `${file.length} Files Selected`}
                                                </div>
                                                {ignoredCount > 0 && (
                                                    <span className="text-[10px] text-slate-500 bg-slate-800/50 px-2 py-0.5 rounded-full border border-white/5">
                                                        Smart Ignored {ignoredCount} dependency files
                                                    </span>
                                                )}
                                            </div>
                                        ) : (
                                            <>
                                                <h3 className="text-white font-semibold mb-1">
                                                    {uploadMode === 'file' ? 'Select ZIP File' : 'Select Project Folder'}
                                                </h3>
                                                <p className="text-slate-500 text-sm">
                                                    {uploadMode === 'file' ? 'Upload a single .ZIP file' : 'Analysis will be recursive'}
                                                </p>
                                            </>
                                        )}
                                    </div>
                                </div>

                                {file && file.length > 1000 && (
                                    <div className="mt-4 p-3 bg-blue-500/10 border border-blue-500/20 rounded-xl flex items-start gap-3">
                                        <AlertCircle className="w-5 h-5 text-blue-400 shrink-0 mt-0.5" />
                                        <p className="text-xs text-blue-300">
                                            <span className="font-bold">Enterprise Tip:</span> This is a large project. For faster scanning and better stability, we recommend uploading as a <span className="underline italic">single ZIP file</span>.
                                        </p>
                                    </div>
                                )}

                                <button
                                    disabled={!file || status === 'uploading'}
                                    onClick={handleUpload}
                                    className="w-full mt-8 py-4 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-800 disabled:text-slate-500 rounded-2xl font-bold text-lg shadow-lg transition-all"
                                >
                                    {status === 'uploading' ? 'Analyzing...' : 'Start Deep Analysis'}
                                </button>
                            </motion.div>
                        )}

                        {status === 'uploading' && (
                            <motion.div
                                key="uploading"
                                className="flex flex-col items-center py-12"
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                            >
                                <div className="relative w-32 h-32 mb-8">
                                    <svg className="w-full h-full transform -rotate-90">
                                        <circle
                                            cx="64"
                                            cy="64"
                                            r="58"
                                            stroke="currentColor"
                                            strokeWidth="8"
                                            fill="transparent"
                                            className="text-slate-800"
                                        />
                                        <motion.circle
                                            cx="64"
                                            cy="64"
                                            r="58"
                                            stroke="currentColor"
                                            strokeWidth="8"
                                            fill="transparent"
                                            strokeDasharray="364.4"
                                            initial={{ strokeDashoffset: 364.4 }}
                                            animate={{ strokeDashoffset: 364.4 - (progress / 100) * 364.4 }}
                                            className="text-blue-500"
                                        />
                                    </svg>
                                    <div className="absolute inset-0 flex items-center justify-center">
                                        <span className="text-2xl font-bold text-white">{progress}%</span>
                                    </div>
                                </div>
                                <h3 className="text-xl font-bold text-white mb-2">{scanSteps[scanStep]}</h3>
                                <p className="text-slate-400">Deep scanning mode: {progress}% Complete</p>
                            </motion.div>
                        )}

                        {status === 'scansuccess' && (
                            <motion.div
                                key="success"
                                initial={{ opacity: 0, scale: 0.9 }}
                                animate={{ opacity: 1, scale: 1 }}
                                className="flex flex-col items-center py-12"
                            >
                                <div className="p-4 bg-green-500/20 rounded-full mb-6">
                                    <CheckCircle2 className="w-16 h-16 text-green-400" />
                                </div>
                                <h3 className="text-2xl font-bold text-white mb-2">Scan Completed!</h3>
                                <p className="text-slate-400">Generating security report and risk metrics...</p>
                            </motion.div>
                        )}

                        {status === 'error' && (
                            <motion.div
                                key="error"
                                className="flex flex-col items-center py-12"
                            >
                                <div className="p-4 bg-red-500/20 rounded-full mb-6">
                                    <AlertCircle className="w-16 h-16 text-red-400" />
                                </div>
                                <h3 className="text-xl font-bold text-white mb-2">Scanning Failed</h3>
                                <p className="text-slate-400 mb-2 px-4 text-center">{errorMessage}</p>
                                <p className="text-xs text-slate-500 mb-6 max-w-xs text-center italic">Tip: Large projects are often more stable when uploaded as a single ZIP file.</p>
                                <button onClick={reset} className="text-blue-400 hover:text-blue-300 font-bold underline">Try Again</button>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>
            </motion.div>
        </div>
    );
};

export default UploadModal;
