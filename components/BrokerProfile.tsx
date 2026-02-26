import React, { useState, useEffect } from 'react';
import {
    ArrowLeft, Target, TrendingUp, TrendingDown, ChevronRight,
    AlertTriangle, Award, BarChart3, Zap, Activity, Shield,
    Calendar, Users, Star, Phone, Clock, CheckCircle2, XCircle,
    Flame, ArrowRight
} from 'lucide-react';

// ============================================================
// INTERFACES
// ============================================================

interface BrokerIntelligence {
    name: string;
    region_type: 'RM' | 'REGIONES';
    comunas: string[];
    leads: number;
    reservas: number;
    meta_personal: number;
    faltante: number;
    conversion: string;
    leadsNeeded: number;
    action: string;
    score: number;
    percentile: number;
    score_engagement: number;
    score_rendimiento: number;
    score_eficiencia: number;
    visitas_realizadas: number;
    visitas_canceladas: number;
    no_contesto: number;
    telefono?: string;
    breakdown_engagement: Record<string, number>;
    breakdown_rendimiento: Record<string, number>;
    breakdown_eficiencia: Record<string, number>;
}

interface BrokerProfileProps {
    broker: BrokerIntelligence;
    onBack: () => void;
    selectedMonth?: string;
}

// ============================================================
// HELPERS
// ============================================================

function getScoreCategory(score: number): { label: string; color: string; border: string; bg: string } {
    if (score >= 80) return { label: 'ELITE', color: 'text-emerald-400', border: 'border-emerald-400/40', bg: 'bg-emerald-500/20' };
    if (score >= 65) return { label: 'ALTO RENDIMIENTO', color: 'text-blue-400', border: 'border-blue-400/40', bg: 'bg-blue-500/20' };
    if (score >= 50) return { label: 'ESTABLE', color: 'text-yellow-400', border: 'border-yellow-400/40', bg: 'bg-yellow-500/20' };
    return { label: 'EN DESARROLLO', color: 'text-orange-400', border: 'border-orange-400/40', bg: 'bg-orange-500/20' };
}

function getInitials(name: string): string {
    return name.split(' ').slice(0, 2).map(n => n[0]).join('').toUpperCase();
}

// Estimate commission: 30% of avg rental fee (~$580K CLP) * reservas
function estimateCommission(reservas: number): string {
    const avgCanon = 580000;
    const commission = Math.round(reservas * avgCanon * 0.30);
    if (commission >= 1000000) return `$${(commission / 1000000).toFixed(1)}M`;
    return `$${(commission / 1000).toFixed(0)}K`;
}

// Estimate canon-based commission CLP per reserva
const AVG_CANON_CLP = 580000;
const COMMISSION_RATE = 0.30;

interface ActivityWeek {
    week: string;    // e.g. "2026-W05"
    date: string;    // e.g. "2026-01-27"
    agenda: number;
    visitadas: number;
    canceladas: number;
    leads: number;
    reservas: number;
}

const DAYS = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo'] as const;
const DAY_LABELS = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];


// ============================================================
// SUB-COMPONENTS
// ============================================================

const ProgressBar: React.FC<{ value: number; max: number; color?: string }> = ({ value, max, color = 'bg-blue-500' }) => {
    const pct = Math.min(100, Math.round((value / Math.max(max, 1)) * 100));
    return (
        <div className="h-2 bg-slate-800 rounded-full overflow-hidden border border-slate-700">
            <div
                className={`h-full ${color} rounded-full transition-all duration-700`}
                style={{ width: `${pct}%` }}
            />
        </div>
    );
};

const KpiCard: React.FC<{
    icon: React.ReactNode;
    label: string;
    value: string;
    delta?: string;
    positive?: boolean;
    borderColor?: string;
}> = ({ icon, label, value, delta, positive = true, borderColor = 'border-slate-700' }) => (
    <div className={`bg-[#1e2433] border ${borderColor} rounded-2xl p-5 hover:border-opacity-70 transition-all group`}>
        <div className="flex justify-between items-start mb-4">
            <div className="p-2.5 rounded-xl bg-slate-800 group-hover:scale-110 transition-transform">
                {icon}
            </div>
            {delta && (
                <div className={`flex items-center gap-1 text-[10px] font-black px-2 py-0.5 rounded-full border ${positive
                    ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                    : 'bg-red-500/10 text-red-400 border-red-500/20'}`}>
                    {positive ? <TrendingUp size={10} /> : <TrendingDown size={10} />}
                    {delta}
                </div>
            )}
        </div>
        <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">{label}</p>
        <p className="text-3xl font-black text-white mt-1">{value}</p>
    </div>
);

// Heatmap Cell color utility
function heatmapCellClass(val: number, max: number): string {
    if (val === 0) return 'bg-slate-900 border-slate-800 text-slate-700';
    const r = val / max;
    if (r < 0.2) return 'bg-blue-600/15 border-blue-600/15 text-blue-400/50';
    if (r < 0.4) return 'bg-blue-600/30 border-blue-600/25 text-blue-300/70';
    if (r < 0.6) return 'bg-blue-600/50 border-blue-600/40 text-white/80';
    if (r < 0.8) return 'bg-blue-600/70 border-blue-600/60 text-white font-black';
    return 'bg-blue-600 border-blue-500 text-white font-black shadow-[0_0_12px_rgba(39,102,236,0.5)]';
}

// ============================================================
// MAIN COMPONENT
// ============================================================

const BrokerProfile: React.FC<BrokerProfileProps> = ({ broker, onBack, selectedMonth }) => {
    const [heatmapView, setHeatmapView] = useState<'reservas' | 'agenda' | 'leads'>('agenda');
    const [heatmapData, setHeatmapData] = useState<ActivityWeek[]>([]);
    const [heatmapLoading, setHeatmapLoading] = useState(true);
    const [heatmapError, setHeatmapError] = useState<string | null>(null);
    const category = getScoreCategory(broker.score);
    const initials = getInitials(broker.name);

    // Fetch real heatmap data from v6_broker_activity
    useEffect(() => {
        const fetchActivity = async () => {
            setHeatmapLoading(true);
            setHeatmapError(null);
            try {
                const encodedName = encodeURIComponent(broker.name);
                const res = await fetch(`/api/v6_broker_activity?broker_name=${encodedName}&weeks_back=16`);
                if (!res.ok) throw new Error(`Error ${res.status}`);
                const json = await res.json();
                setHeatmapData(json.weeks || []);
            } catch (err) {
                setHeatmapError('Sin datos de actividad histórica aún');
            } finally {
                setHeatmapLoading(false);
            }
        };
        fetchActivity();
    }, [broker.name]);

    // Meta de reservas personal (desde broker.meta_personal)
    const metaReservas = broker.meta_personal > 0 ? broker.meta_personal : 7;
    const reservasCumplidas = broker.reservas;
    const pctMeta = Math.min(100, Math.round((reservasCumplidas / metaReservas) * 100));
    const diasRestantes = 12; // Simplified – in production: calculate from selectedMonth
    const ritmoActual = parseFloat((reservasCumplidas / Math.max(1, 28 - diasRestantes)).toFixed(2));
    const ritmoNec = parseFloat(((metaReservas - reservasCumplidas) / Math.max(1, diasRestantes)).toFixed(2));
    const atRisk = reservasCumplidas < metaReservas && ritmoActual < ritmoNec;

    // Commission
    const commisionActual = Math.round(reservasCumplidas * AVG_CANON_CLP * COMMISSION_RATE);
    const commisionFmt = commisionActual >= 1000000
        ? `$${(commisionActual / 1000000).toFixed(1)}M`
        : `$${(commisionActual / 1000).toFixed(0)}K`;

    // Derived heatmap values from API data
    const getWeekValue = (week: ActivityWeek) =>
        heatmapView === 'reservas' ? week.reservas
            : heatmapView === 'agenda' ? week.agenda
                : week.leads;

    const heatmapMax = Math.max(...heatmapData.map(getWeekValue), 1);

    // Chunk weeks into rows of 8 (max 2 months visible at once)
    const COLS = 8;
    const heatmapRows: ActivityWeek[][] = [];
    for (let i = 0; i < heatmapData.length; i += COLS) {
        heatmapRows.push(heatmapData.slice(i, i + COLS));
    }

    // Phone WhatsApp link
    const phoneHref = broker.telefono
        ? `https://wa.me/${broker.telefono.replace(/\D/g, '')}`
        : null;

    return (
        <div className="min-h-screen bg-[#101622] text-slate-200 pb-20">

            {/* ---- GLOW BG ---- */}
            <div aria-hidden className="fixed inset-0 pointer-events-none overflow-hidden">
                <div className="absolute top-[-15%] left-[-10%] w-[600px] h-[600px] bg-blue-600/8 rounded-full blur-[140px]" />
                <div className="absolute top-[30%] right-[-10%] w-[400px] h-[400px] bg-emerald-500/6 rounded-full blur-[120px]" />
            </div>

            {/* ---- STICKY HEADER ---- */}
            <header className="relative z-10 bg-[#1e2433]/80 backdrop-blur-md border-b border-slate-800 sticky top-0">
                <div className="max-w-6xl mx-auto px-4 sm:px-6 py-3 flex items-center gap-3">
                    <button
                        onClick={onBack}
                        className="flex items-center gap-2 px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-bold text-slate-400 hover:text-white transition-all"
                    >
                        <ArrowLeft size={14} />
                        Laboratorio
                    </button>
                    <ChevronRight size={14} className="text-slate-600" />
                    <span className="text-xs font-bold text-white uppercase tracking-widest">{broker.name}</span>
                    <div className="ml-auto flex items-center gap-2">
                        <span className={`text-[10px] font-black uppercase tracking-widest px-3 py-1 rounded-full border ${category.bg} ${category.color} ${category.border}`}>
                            {category.label}
                        </span>
                        <span className="text-[10px] font-black text-slate-500 bg-slate-800 border border-slate-700 px-2 py-1 rounded-full uppercase">
                            #{Math.round(100 - broker.percentile + 1)}° LUGAR
                        </span>
                    </div>
                </div>
            </header>

            <main className="max-w-6xl mx-auto px-4 sm:px-6 py-8 space-y-8 relative z-10">

                {/* ============================================================ */}
                {/* HERO CARD */}
                {/* ============================================================ */}
                <section className="bg-[#1e2433] rounded-3xl border border-slate-800 overflow-hidden shadow-2xl">
                    <div className="bg-gradient-to-r from-blue-600/20 via-transparent to-emerald-500/10 p-8">
                        <div className="flex flex-col md:flex-row items-start md:items-center gap-6">

                            {/* Avatar */}
                            <div className="relative flex-shrink-0">
                                <div className="w-20 h-20 rounded-full bg-gradient-to-br from-blue-600 to-emerald-500 flex items-center justify-center text-2xl font-black text-white shadow-2xl border-4 border-[#1e2433]">
                                    {initials}
                                </div>
                                <div className="absolute -bottom-1 -right-1 bg-emerald-500 w-6 h-6 rounded-full flex items-center justify-center border-2 border-[#1e2433]">
                                    <CheckCircle2 size={12} className="text-white fill-white" />
                                </div>
                            </div>

                            <div className="flex-1">
                                <div className="flex flex-wrap items-start justify-between gap-4">
                                    <div>
                                        <h1 className="text-3xl font-black text-white tracking-tight">{broker.name}</h1>
                                        <p className="text-sm text-slate-400 font-semibold mt-1">
                                            Corredor {broker.region_type} · {broker.comunas.slice(0, 3).join(', ')}
                                            {broker.comunas.length > 3 ? ` +${broker.comunas.length - 3}` : ''}
                                        </p>
                                        <div className="flex flex-wrap items-center gap-2 mt-3">
                                            <span className={`inline-flex items-center gap-1.5 ${category.bg} ${category.color} border ${category.border} px-3 py-1 rounded-full text-xs font-black uppercase`}>
                                                <Award size={12} /> {category.label}
                                            </span>
                                            <span className="inline-flex items-center gap-1.5 bg-amber-500/10 text-amber-400 border border-amber-500/30 px-3 py-1 rounded-full text-xs font-bold uppercase">
                                                <Star size={12} /> Percentil {broker.percentile.toFixed(1)}°
                                            </span>
                                            {phoneHref && (
                                                <a href={phoneHref} target="_blank" rel="noreferrer"
                                                    className="inline-flex items-center gap-1.5 bg-green-500/10 text-green-400 border border-green-500/30 px-3 py-1 rounded-full text-xs font-bold hover:bg-green-500/20 transition-colors">
                                                    <Phone size={12} /> WhatsApp
                                                </a>
                                            )}
                                        </div>
                                    </div>

                                    {/* Score */}
                                    <div className="text-right">
                                        <div className="text-7xl font-black text-white tracking-tighter leading-none"
                                            style={{ textShadow: '0 0 40px rgba(39,102,236,0.5)' }}>
                                            {broker.score.toFixed(1)}
                                        </div>
                                        <p className="text-[10px] text-slate-500 uppercase font-bold tracking-widest mt-1">Score Total</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Score Breakdown Bar */}
                    <div className="px-8 py-4 border-t border-slate-800 grid grid-cols-3 gap-6">
                        {[
                            { label: 'Engagement', value: broker.score_engagement, max: 35, color: 'bg-gradient-to-r from-indigo-600 to-indigo-400', textColor: 'text-indigo-400' },
                            { label: 'Rendimiento', value: broker.score_rendimiento, max: 40, color: 'bg-gradient-to-r from-blue-600 to-blue-400', textColor: 'text-blue-400' },
                            { label: 'Eficiencia', value: broker.score_eficiencia, max: 25, color: 'bg-gradient-to-r from-emerald-600 to-emerald-400', textColor: 'text-emerald-400' },
                        ].map(({ label, value, max, color, textColor }) => (
                            <div key={label}>
                                <div className="flex justify-between text-xs font-bold uppercase tracking-widest mb-1.5">
                                    <span className={textColor}>{label}</span>
                                    <span className="text-white">{value.toFixed(1)} / {max}</span>
                                </div>
                                <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                                    <div
                                        className={`h-full ${color} rounded-full transition-all duration-700`}
                                        style={{ width: `${Math.min(100, (value / max) * 100)}%` }}
                                    />
                                </div>
                            </div>
                        ))}
                    </div>
                </section>

                {/* ============================================================ */}
                {/* META PERSONAL TRACKER */}
                {/* ============================================================ */}
                <section className={`bg-[#1e2433] rounded-3xl border shadow-2xl overflow-hidden ${atRisk ? 'border-amber-500/30' : 'border-emerald-500/30'}`}>

                    {/* Alert strip */}
                    {atRisk ? (
                        <div className="bg-amber-500/10 border-b border-amber-500/30 px-6 py-3 flex items-center gap-3">
                            <AlertTriangle size={16} className="text-amber-400 flex-shrink-0" />
                            <p className="text-xs font-bold text-amber-300">
                                Riesgo de incumplimiento — Faltan <strong>{metaReservas - reservasCumplidas} reservas</strong> en {diasRestantes} días.
                                Al ritmo actual proyecta {Math.round(ritmoActual * (28 - diasRestantes) + reservasCumplidas)} reservas.
                            </p>
                        </div>
                    ) : (
                        <div className="bg-emerald-500/10 border-b border-emerald-500/30 px-6 py-3 flex items-center gap-3">
                            <CheckCircle2 size={16} className="text-emerald-400 flex-shrink-0" />
                            <p className="text-xs font-bold text-emerald-300">
                                En camino — Al ritmo actual proyecta <strong>{Math.min(Math.round(ritmoActual * 28), metaReservas + 2)} reservas</strong> al cierre de mes.
                            </p>
                        </div>
                    )}

                    <div className="p-8">
                        <div className="flex items-center gap-3 mb-6">
                            <div className={`p-3 rounded-2xl border ${atRisk ? 'bg-amber-500/20 border-amber-500/30' : 'bg-emerald-500/20 border-emerald-500/30'}`}>
                                <Target size={24} className={atRisk ? 'text-amber-400' : 'text-emerald-400'} />
                            </div>
                            <div>
                                <h2 className="text-lg font-black text-white uppercase tracking-widest">Meta Personal · Reservas</h2>
                                <p className="text-xs text-slate-500 font-semibold mt-0.5">
                                    Objetivo mensual comprometido · {selectedMonth || 'Mes actual'}
                                </p>
                            </div>
                            <div className="ml-auto text-right">
                                <div className="text-3xl font-black text-white">
                                    {metaReservas} <span className="text-lg text-slate-400 font-bold">reservas</span>
                                </div>
                                <p className="text-[10px] text-slate-500 uppercase font-bold tracking-widest">Objetivo del mes</p>
                            </div>
                        </div>

                        {/* Progress */}
                        <div className="mb-6">
                            <div className="flex justify-between items-end mb-2">
                                <div>
                                    <span className="text-4xl font-black text-white">{reservasCumplidas}</span>
                                    <span className="text-slate-500 text-lg font-bold ml-2">/ {metaReservas} reservas</span>
                                </div>
                                <div className="text-right">
                                    <span className="text-3xl font-black text-blue-400">{pctMeta}%</span>
                                    <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Cumplido</p>
                                </div>
                            </div>
                            <div className="h-5 bg-slate-900 rounded-full overflow-hidden border border-slate-800 relative">
                                <div
                                    className="h-full bg-gradient-to-r from-blue-600 via-blue-400 to-blue-500/80 rounded-full transition-all duration-700"
                                    style={{ width: `${pctMeta}%` }}
                                />
                            </div>
                            <div className="flex justify-between text-[10px] font-bold text-slate-700 uppercase tracking-widest mt-1.5">
                                <span>0</span>
                                <span>{diasRestantes} días restantes</span>
                                <span>{metaReservas} reservas</span>
                            </div>
                        </div>

                        {/* Rhythm + commission cards */}
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                            <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-2xl p-5 flex items-center gap-4">
                                <div className="p-3 bg-emerald-500/20 rounded-xl"><TrendingUp size={22} className="text-emerald-400" /></div>
                                <div>
                                    <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Ritmo Actual</p>
                                    <p className="text-2xl font-black text-emerald-400">{ritmoActual}<span className="text-sm font-bold text-slate-400"> res/día</span></p>
                                    <p className="text-[10px] text-slate-500 font-semibold mt-0.5">Últimos 7 días hábiles</p>
                                </div>
                            </div>
                            <div className={`border rounded-2xl p-5 flex items-center gap-4 ${atRisk ? 'bg-amber-500/10 border-amber-500/30' : 'bg-blue-600/10 border-blue-600/30'}`}>
                                <div className={`p-3 rounded-xl ${atRisk ? 'bg-amber-500/20' : 'bg-blue-600/20'}`}>
                                    <Target size={22} className={atRisk ? 'text-amber-400' : 'text-blue-400'} />
                                </div>
                                <div>
                                    <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Ritmo Necesario</p>
                                    <p className={`text-2xl font-black ${atRisk ? 'text-amber-400' : 'text-blue-400'}`}>
                                        {ritmoNec.toFixed(2)}<span className="text-sm font-bold text-slate-400"> res/día</span>
                                    </p>
                                    {atRisk && (
                                        <p className="text-[10px] text-red-400 font-bold mt-0.5">
                                            ↑ +{(ritmoNec - ritmoActual).toFixed(2)} sobre ritmo actual
                                        </p>
                                    )}
                                </div>
                            </div>
                            <div className="bg-blue-600/10 border border-blue-600/30 rounded-2xl p-5 flex items-center gap-4">
                                <div className="p-3 bg-blue-600/20 rounded-xl">
                                    <Star size={22} className="text-blue-400" />
                                </div>
                                <div>
                                    <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Comisión Est.</p>
                                    <p className="text-2xl font-black text-blue-400">
                                        {commisionFmt}<span className="text-sm font-bold text-slate-400"> CLP</span>
                                    </p>
                                    <p className="text-[10px] text-slate-500 font-semibold mt-0.5">30% cañón · {reservasCumplidas} reservas</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>

                {/* ============================================================ */}
                {/* KPI CARDS */}
                {/* ============================================================ */}
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                    <KpiCard
                        icon={<Activity size={18} className="text-blue-400" />}
                        label="Leads del mes"
                        value={String(broker.leads)}
                        delta={`${broker.leads} gestionados`}
                        positive={broker.leads > 10}
                        borderColor="hover:border-blue-500/50 border-slate-700"
                    />
                    <KpiCard
                        icon={<CheckCircle2 size={18} className="text-emerald-400" />}
                        label="Visitas realizadas"
                        value={String(broker.visitas_realizadas)}
                        delta={`${broker.visitas_canceladas} canceladas`}
                        positive={broker.visitas_canceladas < broker.visitas_realizadas * 0.3}
                        borderColor="hover:border-emerald-500/50 border-slate-700"
                    />
                    <KpiCard
                        icon={<Zap size={18} className="text-yellow-400" />}
                        label="Conversión"
                        value={broker.conversion}
                        delta={`${broker.leads} leads`}
                        positive={parseFloat(broker.conversion) > 30}
                        borderColor="hover:border-yellow-500/50 border-slate-700"
                    />
                    <KpiCard
                        icon={<Shield size={18} className="text-purple-400" />}
                        label="Score Engagement"
                        value={broker.score_engagement.toFixed(1)}
                        delta={`/ 35 pts`}
                        positive={broker.score_engagement > 25}
                        borderColor="hover:border-purple-500/50 border-slate-700"
                    />
                </div>

                {/* ============================================================ */}
                {/* SCORE BREAKDOWN + COMUNAS */}
                {/* ============================================================ */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                    {/* Score Breakdown detail */}
                    <div className="bg-[#1e2433] rounded-3xl border border-slate-800 p-8 shadow-xl">
                        <h2 className="text-lg font-black text-white uppercase tracking-widest flex items-center gap-2 mb-6">
                            <BarChart3 size={18} className="text-amber-400" />
                            Composición del Score
                        </h2>
                        <div className="space-y-6">
                            {/* Engagement */}
                            <div>
                                <div className="flex justify-between mb-1.5">
                                    <span className="text-xs font-black uppercase text-indigo-400 tracking-widest">Engagement (35%)</span>
                                    <span className="text-sm font-black text-white">{broker.score_engagement.toFixed(1)} pts</span>
                                </div>
                                <ProgressBar value={broker.score_engagement} max={35} color="bg-gradient-to-r from-indigo-600 to-indigo-400" />
                                <div className="grid grid-cols-2 gap-2 mt-3">
                                    {Object.entries(broker.breakdown_engagement).slice(0, 4).map(([k, v]) => (
                                        <div key={k} className="bg-slate-900 rounded-xl px-3 py-2 border border-slate-800">
                                            <p className="text-[9px] text-slate-600 uppercase font-bold truncate">{k.replace(/_/g, ' ')}</p>
                                            <p className="text-sm font-black text-indigo-400">{typeof v === 'number' ? v.toFixed(1) : v}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                            {/* Rendimiento */}
                            <div>
                                <div className="flex justify-between mb-1.5">
                                    <span className="text-xs font-black uppercase text-blue-400 tracking-widest">Rendimiento (40%)</span>
                                    <span className="text-sm font-black text-white">{broker.score_rendimiento.toFixed(1)} pts</span>
                                </div>
                                <ProgressBar value={broker.score_rendimiento} max={40} color="bg-gradient-to-r from-blue-600 to-blue-400" />
                            </div>
                            {/* Eficiencia */}
                            <div>
                                <div className="flex justify-between mb-1.5">
                                    <span className="text-xs font-black uppercase text-emerald-400 tracking-widest">Eficiencia (25%)</span>
                                    <span className="text-sm font-black text-white">{broker.score_eficiencia.toFixed(1)} pts</span>
                                </div>
                                <ProgressBar value={broker.score_eficiencia} max={25} color="bg-gradient-to-r from-emerald-600 to-emerald-400" />
                            </div>
                        </div>
                    </div>

                    {/* Action & Comunas */}
                    <div className="space-y-4">
                        {/* Action card */}
                        <div className="bg-[#1e2433] rounded-3xl border border-blue-600/30 p-6 shadow-xl">
                            <h2 className="text-sm font-black text-white uppercase tracking-widest flex items-center gap-2 mb-4">
                                <Flame size={16} className="text-orange-400" />
                                Acción Sugerida
                            </h2>
                            <p className="text-sm text-slate-300 font-semibold leading-relaxed">{broker.action}</p>
                            <div className="flex items-center gap-3 mt-4">
                                <div className="bg-blue-600/20 border border-blue-600/30 rounded-xl px-3 py-2 text-xs font-bold text-blue-400">
                                    Leads necesarios: <strong>{broker.leadsNeeded}</strong>
                                </div>
                                <div className="bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-xs font-bold text-slate-400">
                                    Faltante: <strong className="text-white">{broker.faltante}</strong>
                                </div>
                            </div>
                        </div>

                        {/* Comunas */}
                        <div className="bg-[#1e2433] rounded-3xl border border-slate-800 p-6 shadow-xl">
                            <h2 className="text-sm font-black text-white uppercase tracking-widest flex items-center gap-2 mb-4">
                                <Users size={16} className="text-pink-400" />
                                Zona de Operación
                            </h2>
                            <div className="flex flex-wrap gap-2">
                                {broker.comunas.map(c => (
                                    <span key={c} className="bg-slate-800 border border-slate-700 text-slate-300 px-3 py-1 rounded-xl text-xs font-bold">
                                        {c}
                                    </span>
                                ))}
                            </div>
                            <div className="mt-3 flex items-center gap-2">
                                <span className={`text-[10px] uppercase font-black px-2 py-1 rounded-lg ${broker.region_type === 'RM' ? 'bg-blue-600/20 text-blue-400' : 'bg-purple-600/20 text-purple-400'}`}>
                                    {broker.region_type}
                                </span>
                                <span className="text-[10px] text-slate-600 font-bold">{broker.comunas.length} comunas activas</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* ============================================================ */}
                {/* HEATMAP */}
                {/* ============================================================ */}
                <section className="bg-[#1e2433] rounded-3xl border border-slate-800 p-8 shadow-xl">
                    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
                        <div>
                            <h2 className="text-lg font-black text-white uppercase tracking-widest flex items-center gap-2">
                                <Activity size={18} className="text-pink-400" />
                                Activity Heatmap
                            </h2>
                            <p className="text-xs text-slate-500 font-semibold mt-1">
                                Datos reales · últimas 16 semanas
                            </p>
                        </div>
                        <div className="flex gap-2">
                            {(['agenda', 'reservas', 'leads'] as const).map(v => (
                                <button
                                    key={v}
                                    onClick={() => setHeatmapView(v)}
                                    className={`px-4 py-2 rounded-xl text-xs font-black uppercase tracking-widest border transition-all ${heatmapView === v
                                        ? 'bg-blue-600/30 border-blue-500/80 text-white'
                                        : 'bg-slate-800 border-slate-700 text-slate-400 hover:text-white'}`}
                                >
                                    {v}
                                </button>
                            ))}
                        </div>
                    </div>

                    {heatmapLoading ? (
                        <div className="flex items-center justify-center h-24 text-slate-500 text-xs font-bold uppercase tracking-widest">
                            <Clock size={14} className="mr-2 animate-spin" /> Cargando actividad real...
                        </div>
                    ) : heatmapError || heatmapData.length === 0 ? (
                        <div className="flex items-center justify-center h-24 text-slate-600 text-xs font-bold uppercase tracking-widest gap-2">
                            <XCircle size={14} />
                            {heatmapError || 'Sin actividad en las últimas 16 semanas'}
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {heatmapRows.map((row, rowIdx) => (
                                <div key={rowIdx} className="flex gap-2">
                                    {row.map((week) => {
                                        const val = getWeekValue(week);
                                        const shortDate = week.date.slice(5); // MM-DD
                                        return (
                                            <div
                                                key={week.week}
                                                title={`${week.week} (${week.date})\nAgenda: ${week.agenda} | Leads: ${week.leads} | Reservas: ${week.reservas}`}
                                                className={`flex-1 h-14 rounded-xl border flex flex-col items-center justify-center text-xs transition-all duration-200 ${heatmapCellClass(val, heatmapMax)}`}
                                            >
                                                <span className="text-[9px] font-bold opacity-60">{shortDate}</span>
                                                <span className="text-base font-black">{val > 0 ? val : '–'}</span>
                                            </div>
                                        );
                                    })}
                                </div>
                            ))}

                            {/* Legend */}
                            <div className="flex items-center gap-3 mt-4 text-[10px]">
                                <span className="text-slate-500 font-bold uppercase">Intensidad:</span>
                                {[15, 30, 50, 70, 100].map(p => (
                                    <div key={p} className="w-5 h-5 rounded-lg" style={{ background: `rgba(39,102,236,${p / 100})`, border: `1px solid rgba(39,102,236,${p / 80})` }} />
                                ))}
                                <span className="text-slate-600 font-bold">Bajo → Alto</span>
                                <span className="ml-auto text-slate-600 font-bold">
                                    {heatmapData.length} semanas · {heatmapData[0]?.date} → {heatmapData[heatmapData.length - 1]?.date}
                                </span>
                            </div>
                        </div>
                    )}
                </section>

                {/* ============================================================ */}
                {/* NEXT STEPS */}
                {/* ============================================================ */}
                <section>
                    <h2 className="text-lg font-black text-white uppercase tracking-widest flex items-center gap-2 mb-6">
                        <Flame size={18} className="text-indigo-400" />
                        Próximos Pasos Sugeridos
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {[
                            {
                                icon: <Star size={22} className="text-blue-400" />,
                                bg: 'bg-blue-600/20',
                                border: 'border-blue-600/30',
                                hover: 'hover:border-blue-500/60',
                                glow: 'bg-blue-500/10',
                                btnColor: 'text-blue-400',
                                title: 'Sesión de Coaching',
                                desc: `Revisar estrategia de cierre y fórmula de seguimiento en etapa prospecto → reserva. Foco en eficiencia de visitas.`,
                                cta: 'Agendar sesión'
                            },
                            {
                                icon: <Award size={22} className="text-emerald-400" />,
                                bg: 'bg-emerald-500/20',
                                border: 'border-emerald-500/30',
                                hover: 'hover:border-emerald-400/60',
                                glow: 'bg-emerald-500/10',
                                btnColor: 'text-emerald-400',
                                title: broker.score >= 80 ? 'Reconocimiento Elite' : 'Siguiente Nivel',
                                desc: broker.score >= 80
                                    ? `${broker.name} alcanzó percentil ${broker.percentile.toFixed(1)}°. Compartir logro en reunión para reforzar cultura de alto rendimiento.`
                                    : `${broker.name} está a ${(80 - broker.score).toFixed(1)} puntos de alcanzar el nivel ELITE. Definir acciones concretas para lograrlo.`,
                                cta: 'Publicar logro'
                            },
                            {
                                icon: <Activity size={22} className="text-purple-400" />,
                                bg: 'bg-purple-500/20',
                                border: 'border-purple-500/30',
                                hover: 'hover:border-purple-400/60',
                                glow: 'bg-purple-500/10',
                                btnColor: 'text-purple-400',
                                title: 'Optimización de Pipeline',
                                desc: `${broker.leadsNeeded > 0 ? `Necesita ${broker.leadsNeeded} leads adicionales para cumplir meta.` : 'En camino a su meta.'} Revisar velocidad de contacto y priorizar prospectos calientes de esta semana.`,
                                cta: 'Ver pipeline'
                            }
                        ].map(({ icon, bg, border, hover, glow, btnColor, title, desc, cta }) => (
                            <div key={title} className={`bg-[#1e2433] ${border} ${hover} border rounded-2xl p-6 transition-all group relative overflow-hidden`}>
                                <div className={`absolute top-0 right-0 w-20 h-20 ${glow} rounded-full blur-2xl pointer-events-none`} />
                                <div className="relative z-10">
                                    <div className={`p-3 ${bg} rounded-xl w-fit mb-4 ${border} group-hover:scale-110 transition-transform border`}>
                                        {icon}
                                    </div>
                                    <h3 className="text-base font-black text-white mb-2">{title}</h3>
                                    <p className="text-xs text-slate-400 font-semibold mb-4 leading-relaxed">{desc}</p>
                                    <button className={`flex items-center gap-1.5 ${btnColor} text-xs font-black uppercase tracking-widest hover:gap-3 transition-all`}>
                                        {cta} <ArrowRight size={12} />
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </section>

            </main>
        </div>
    );
};

export default BrokerProfile;
