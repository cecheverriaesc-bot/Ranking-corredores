import React, { useState, useMemo, useEffect } from 'react';
import {
    Shield, Target, Zap, Users, Map, Brain, AlertTriangle,
    ArrowRight, ChevronLeft, TrendingUp, Activity, Search, MessageSquare, Award,
    Trophy, BarChart3
} from 'lucide-react';
import { TEAMS, MONTHLY_DATA } from '../constants';
import { CorredorData, BrokerGoalData } from '../types';



// --- Month Selector Component (Timeline Style) ---
const MONTH_NAMES: Record<string, string> = {
    '01': 'Ene',
    '02': 'Feb',
    '03': 'Mar',
    '04': 'Abr',
    '05': 'May',
    '06': 'Jun',
    '07': 'Jul',
    '08': 'Ago',
    '09': 'Sep',
    '10': 'Oct',
    '11': 'Nov',
    '12': 'Dic'
};

const MonthSelector = ({ selected, onChange }: { selected: string; onChange: (m: string) => void }) => {
    const availableMonths = Object.keys(MONTHLY_DATA).sort();
    const currentYear = availableMonths.some(m => m.startsWith('2026')) ? '2026' : availableMonths[0]?.split('-')[0] || '2026';
    const allMonths = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'];
    const lastAvailableMonth = availableMonths.length > 0 ? availableMonths[availableMonths.length - 1] : null;
    const lastAvailableMonthNum = lastAvailableMonth ? parseInt(lastAvailableMonth.split('-')[1], 10) : 0;
    const isTotalYear = selected === 'total-year';

    return (
        <div className="flex items-center gap-3">
            <div className="flex flex-col items-center">
                <span className="text-2xl font-black text-white tracking-tight">2026</span>
            </div>

            <div className="flex items-center gap-1 bg-slate-800/30 px-4 py-3 rounded-2xl border border-slate-700/50">
                {allMonths.map((monthNum, index) => {
                    const monthKey = `${currentYear}-${monthNum}`;
                    const monthName = MONTH_NAMES[monthNum];
                    const hasData = MONTHLY_DATA[monthKey];
                    const isSelected = selected === monthKey;
                    const isTotalYear = selected === 'total-year';
                    const monthIndex = parseInt(monthNum, 10);
                    const isCompleted = hasData || (lastAvailableMonthNum > 0 && monthIndex <= lastAvailableMonthNum);
                    const isFuture = !hasData && monthIndex > lastAvailableMonthNum;

                    return (
                        <React.Fragment key={monthKey}>
                            <button
                                onClick={() => onChange(monthKey)}
                                disabled={isFuture}
                                className={`relative flex items-center justify-center w-9 h-9 rounded-xl text-xs font-black uppercase transition-all duration-300 ${isSelected
                                    ? 'bg-gradient-to-br from-blue-500 to-blue-600 text-white shadow-lg shadow-blue-500/30 scale-110'
                                    : isCompleted
                                        ? 'bg-slate-700 text-slate-300 hover:bg-slate-600 hover:text-white hover:scale-105'
                                        : 'bg-slate-800/50 text-slate-600 cursor-not-allowed'
                                    }`}
                                title={monthName}
                            >
                                {monthName}
                                {hasData && !isSelected && (
                                    <span className="absolute -bottom-0.5 w-1 h-1 bg-emerald-400 rounded-full"></span>
                                )}
                                {isSelected && (
                                    <span className="absolute -bottom-0.5 w-1 h-1 bg-white rounded-full animate-pulse"></span>
                                )}
                            </button>

                            {index < allMonths.length - 1 && (
                                <div className={`w-1 h-0.5 transition-colors duration-300 ${isCompleted && allMonths[index + 1] && (
                                    MONTHLY_DATA[`${currentYear}-${allMonths[index + 1]}`] ||
                                    parseInt(allMonths[index + 1], 10) <= lastAvailableMonthNum
                                )
                                    ? 'bg-slate-600'
                                    : 'bg-slate-800'
                                    }`}></div>
                            )}
                        </React.Fragment>
                    );
                })}
            </div>

            <button
                onClick={() => onChange('total-year')}
                className={`flex flex-col items-center gap-1 px-4 py-2 rounded-xl border transition-all duration-300 ${isTotalYear
                    ? 'bg-gradient-to-br from-emerald-500 to-emerald-600 border-emerald-400/50 text-white shadow-lg shadow-emerald-500/30'
                    : 'bg-slate-800/50 border-slate-700 text-slate-400 hover:bg-slate-700 hover:text-white'
                    }`}
            >
                <Trophy size={16} className={isTotalYear ? 'fill-white' : ''} />
                <span className="text-[9px] font-black uppercase tracking-tight">Total</span>
            </button>
        </div>
    );
};

interface SquadLaboratoryProps {
    onBack: () => void;
    rankingData: CorredorData[];
    monthlyGoal: number;
    selectedMonth?: string;
    onMonthChange?: (month: string) => void;
    onSetGoal?: (broker: any) => void; // Added onSetGoal to props
}

const SquadLaboratory: React.FC<SquadLaboratoryProps> = ({
    onBack,
    rankingData,
    monthlyGoal,
    selectedMonth: parentSelectedMonth,
    onMonthChange,
    onSetGoal // Destructured onSetGoal
}) => {
    // Month Selection State - use parent value if provided, otherwise local
    const [localSelectedMonth, setLocalSelectedMonth] = useState<string>('2026-02');
    const selectedMonth = parentSelectedMonth !== undefined ? parentSelectedMonth : localSelectedMonth;
    const setSelectedMonth = onMonthChange || setLocalSelectedMonth;

    // State for API data
    const [intelligenceData, setIntelligenceData] = useState<any>(null);
    const [capacityData, setCapacityData] = useState<any>(null);
    const [brokerGoals, setBrokerGoals] = useState<Record<string, BrokerGoalData>>({});
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Fetch intelligence, capacity and goals data
    useEffect(() => {
        const fetchAllData = async () => {
            try {
                setIsLoading(true);

                // Construir query params para el mes seleccionado
                const queryParams = new URLSearchParams();
                const capacityParams = new URLSearchParams();

                if (selectedMonth === 'total-year') {
                    queryParams.append('year', '2026');
                    queryParams.append('month', 'all');
                    capacityParams.append('year', '2026');
                    capacityParams.append('month', 'all');
                } else if (selectedMonth) {
                    const [year, month] = selectedMonth.split('-');
                    if (year && month) {
                        queryParams.append('year', year);
                        queryParams.append('month', parseInt(month, 10).toString());
                        capacityParams.append('year', year);
                        capacityParams.append('month', parseInt(month, 10).toString());
                    }
                }

                // Fetch intelligence (existing)
                const intelligenceResponse = await fetch(`/api/v2_intelligence?${queryParams.toString()}`);
                if (!intelligenceResponse.ok) throw new Error('Failed to fetch intelligence data');
                const intelligenceData = await intelligenceResponse.json();

                // Fetch capacity (new)
                const capacityQueryStr = capacityParams.toString();
                const capacityUrl = `/api/v3_capacity${capacityQueryStr ? `?${capacityQueryStr}` : ''}`;
                const capacityResponse = await fetch(capacityUrl);
                if (!capacityResponse.ok) throw new Error('Failed to fetch capacity data');
                const capacityData = await capacityResponse.json();

                // Fetch broker goals - use selected month
                const goalsMonth = selectedMonth === 'total-year' ? new Date().toISOString().slice(0, 7) : selectedMonth;
                const goalsResponse = await fetch(`/api/v4_goals?month=${goalsMonth}-01`);
                if (goalsResponse.ok) {
                    const goalsData = await goalsResponse.json();
                    if (Array.isArray(goalsData)) {
                        const goalsMap: Record<string, BrokerGoalData> = {};
                        goalsData.forEach((goal: BrokerGoalData) => {
                            goalsMap[goal.broker_name] = goal;
                        });
                        setBrokerGoals(goalsMap);
                    }
                }

                setIntelligenceData(intelligenceData);
                setCapacityData(capacityData);
                setError(null);
            } catch (err) {
                console.error('Error fetching data:', err);
                setError('Error cargando datos de inteligencia');
            } finally {
                setIsLoading(false);
            }
        };

        fetchAllData();
    }, [selectedMonth]);

    // Extract data from API response
    const brokers = intelligenceData?.brokers || [];
    const coverage = intelligenceData?.coverage || [];
    const efficiencyAlerts = intelligenceData?.efficiency_alerts || {
        leadsSinGestion: 0,
        unidadesSinVisitas: 0
    };

    const squadMembers = useMemo(() => {
        return rankingData.filter(r => r.coord === 'carlos.echeverria@assetplan.cl');
    }, [rankingData]);

    // Detección de Mes Cerrado
    const isClosedMonth = useMemo(() => {
        if (!selectedMonth || selectedMonth === 'total-year') return false;
        const [year, month] = selectedMonth.split('-').map(Number);
        const today = new Date();
        const currentYear = today.getFullYear();
        const currentMonth = today.getMonth() + 1;

        if (year < currentYear) return true;
        if (year === currentYear && month < currentMonth) return true;
        return false;
    }, [selectedMonth]);

    const stats = useMemo(() => {
        const totalReservas = squadMembers.reduce((acc, curr) => acc + (curr.val || 0), 0);
        const totalContracts = squadMembers.reduce((acc, curr) => acc + (curr.contracts || 0), 0);
        const targetCheck = monthlyGoal * 1.10; // Meta 110% (Generalmente 2066 para Feb)

        // Proyección real basada en ritmo diario de RESERVAS
        const today = new Date();
        const currentMonth = today.getMonth();
        const currentYear = today.getFullYear();
        const currentDay = today.getDate();
        const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate(); // Get actual days in month
        const daysRemaining = Math.max(0, daysInMonth - currentDay);

        // Ritmo de reservas
        const reservaDailyRate = currentDay > 0 ? totalReservas / currentDay : 0;
        const reservaProjection = totalReservas + (reservaDailyRate * daysRemaining);

        return {
            totalReservas,
            totalContracts,
            targetCheck,
            projection: Math.round(reservaProjection)
        };
    }, [squadMembers, monthlyGoal]);

    // Count limit adjustments needed (with safe check)
    const limitAdjustmentsNeeded = capacityData?.brokers?.filter((b: any) =>
        b.limit_recommendation?.action === 'increase'
    ).length || 0;

    const coverageAlerts = coverage.filter((d: any) => d.stock > 20 && d.activeBrokers < 2);

    // Early return for loading state
    if (isLoading) {
        return (
            <div className="min-h-screen bg-[#0f172a] text-slate-200 font-sans">
                <div className="fixed inset-0 z-[100] bg-[#0f172a] flex flex-col items-center justify-center">
                    <div className="w-16 h-16 border-4 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin mb-4"></div>
                    <p className="text-indigo-400 font-black uppercase tracking-widest text-xs animate-pulse">Cargando Inteligencia...</p>
                </div>
            </div>
        );
    }

    // Early return for error state
    if (error) {
        return (
            <div className="min-h-screen bg-[#0f172a] text-slate-200 font-sans">
                <div className="fixed inset-0 z-[100] bg-[#0f172a] flex flex-col items-center justify-center p-6">
                    <div className="max-w-md bg-red-500/10 border border-red-500/30 rounded-xl p-6 text-center">
                        <AlertTriangle className="w-12 h-12 text-red-400 mx-auto mb-4" />
                        <h3 className="text-xl font-bold text-red-400 mb-2">Error de Conexión</h3>
                        <p className="text-slate-400 mb-4">{error}</p>
                        <p className="text-slate-500 text-xs mb-6">Las APIs de inteligencia no están respondiendo correctamente. Esto puede ser un problema temporal de conexión a la base de datos.</p>
                        <button
                            onClick={onBack}
                            className="px-6 py-3 bg-slate-700 hover:bg-slate-600 rounded-xl text-white font-bold transition-colors uppercase tracking-widest text-xs"
                        >
                            Volver al Dashboard
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-[#0f172a] text-slate-200 font-sans p-6 pb-20 animate-in fade-in duration-500">

            {/* Encabezado - REDISEÑO PREMIUM */}
            <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-12 border-b border-white/5 pb-10">
                <div className="flex items-center gap-6">
                    <button
                        onClick={onBack}
                        className="p-3 rounded-2xl bg-slate-800/40 hover:bg-slate-700/60 text-slate-400 hover:text-white transition-all border border-slate-700/50 group"
                    >
                        <ChevronLeft size={24} className="group-hover:-translate-x-1 transition-transform" />
                    </button>
                    <div>
                        <div className="flex items-center gap-3 mb-2">
                            <div className="p-2 bg-indigo-500/20 rounded-lg">
                                <Brain size={24} className="text-indigo-400" />
                            </div>
                            <h1 className="text-3xl font-black text-white uppercase tracking-tighter">
                                Squad <span className="text-indigo-500">Laboratory</span>
                            </h1>
                        </div>
                        <div className="flex items-center gap-4">
                            <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 text-[10px] font-black uppercase tracking-widest">
                                <Target size={12} /> Misión 110%
                            </span>
                            <MonthSelector selected={selectedMonth} onChange={setSelectedMonth} />
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-4 w-full md:w-auto overflow-x-auto pb-2 md:pb-0">
                    <div className="flex-1 min-w-[140px] px-6 py-4 bg-slate-900/50 rounded-2xl border border-white/5 backdrop-blur-xl">
                        <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Contratos</p>
                        <div className="flex items-end gap-2 text-2xl font-black text-white">
                            {stats.totalContracts}
                            <Award size={18} className="text-emerald-500 mb-1" />
                        </div>
                    </div>
                    {!isClosedMonth && (
                        <div className="flex-1 min-w-[140px] px-6 py-4 bg-slate-900/50 rounded-2xl border border-white/5 backdrop-blur-xl">
                            <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Proyección</p>
                            <div className="flex items-end gap-2 text-2xl font-black text-blue-400">
                                {stats.projection}
                                <TrendingUp size={18} className="text-blue-500 mb-1" />
                            </div>
                        </div>
                    )}
                    <div className="flex-1 min-w-[140px] px-6 py-4 bg-emerald-500/5 rounded-2xl border border-emerald-500/10 backdrop-blur-xl">
                        <p className="text-[10px] font-black text-emerald-500/60 uppercase tracking-widest mb-1">Target</p>
                        <div className="flex items-end gap-2 text-2xl font-black text-emerald-400">
                            {(stats.targetCheck).toFixed(0)}
                            <Trophy size={18} className="text-emerald-500 mb-1" />
                        </div>
                    </div>
                </div>
            </header>

            {/* Banner de Mes Cerrado - SQUAD VERSION */}
            {isClosedMonth && (
                <section className="mb-10 animate-in slide-in-from-top duration-500">
                    <div className="relative overflow-hidden rounded-[2.5rem] bg-gradient-to-br from-slate-950 to-slate-900 border border-amber-500/20 p-8 shadow-2xl">
                        <div className="absolute top-0 right-0 w-80 h-80 bg-amber-500/5 rounded-full blur-[100px] pointer-events-none"></div>
                        <div className="relative flex flex-col md:flex-row items-center justify-between gap-8">
                            <div className="flex items-center gap-6">
                                <div className="p-4 bg-amber-500/10 rounded-3xl border border-amber-500/20 shadow-[0_0_20px_rgba(245,158,11,0.1)]">
                                    <Award className="w-10 h-10 text-amber-400" />
                                </div>
                                <div>
                                    <h2 className="text-3xl font-black text-white uppercase tracking-tighter mb-1">Cierre de Operación</h2>
                                    <p className="text-slate-400 text-sm font-bold uppercase tracking-widest">Snapshot Definitivo • {selectedMonth}</p>
                                </div>
                            </div>

                            <div className="flex items-center gap-12 bg-white/5 px-8 py-4 rounded-3xl border border-white/10 backdrop-blur-md">
                                <div className="text-center">
                                    <p className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-2">Meta Squad</p>
                                    <p className="text-2xl font-black text-white">{monthlyGoal}</p>
                                </div>
                                <div className="h-10 w-px bg-white/10"></div>
                                <div className="text-center">
                                    <p className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-2">Check Final</p>
                                    <p className={`text-2xl font-black ${(stats.totalContracts / monthlyGoal) >= 1 ? 'text-emerald-400' : 'text-amber-400'}`}>
                                        {((stats.totalContracts / monthlyGoal) * 100).toFixed(1)}%
                                    </p>
                                </div>
                                <div className="h-10 w-px bg-white/10"></div>
                                <div className="text-center">
                                    <p className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] mb-2">Resultado</p>
                                    <span className={`px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest ${(stats.totalContracts / monthlyGoal) >= 1 ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'}`}>
                                        {(stats.totalContracts / monthlyGoal) >= 1 ? 'Objetivo Logrado' : 'Incompleto'}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>
            )}

            {/* Grilla Principal */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">

                {/* Columna Izquierda: Inteligencia & Stock */}
                <div className="lg:col-span-8 space-y-8">

                    {/* Matriz de Coaching */}
                    <section className="bg-slate-900/50 rounded-3xl p-8 border border-slate-800 shadow-2xl relative overflow-hidden">
                        <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/5 rounded-full blur-3xl pointer-events-none"></div>
                        <h3 className="text-lg font-bold text-white uppercase tracking-widest mb-6 flex items-center gap-2">
                            <Zap size={18} className="text-yellow-400" /> Análisis de Rendimiento Operativo
                        </h3>

                        {/* Score Methodology - REDISEÑO PREMIUM 3 PILARES */}
                        <div className="mb-12 p-8 bg-gradient-to-br from-slate-950 to-slate-900 border border-white/5 rounded-[2.5rem] shadow-2xl relative overflow-hidden group">
                            <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/5 rounded-full blur-[100px] -translate-y-1/2 translate-x-1/2 group-hover:bg-indigo-500/10 transition-colors"></div>

                            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-10 relative z-10">
                                <div className="flex items-center gap-6">
                                    <div className="p-4 bg-amber-500/10 rounded-3xl border border-amber-500/20 shadow-[0_0_20px_rgba(245,158,11,0.05)]">
                                        <Award className="text-amber-400 w-8 h-8" />
                                    </div>
                                    <div>
                                        <h4 className="text-2xl font-black text-white uppercase tracking-tighter">
                                            Arquitectura <span className="text-amber-400">Scoring V3</span>
                                        </h4>
                                        <p className="text-[10px] text-slate-500 font-bold uppercase tracking-[0.2em]">
                                            Fase 3: Engagement + Rendimiento + Eficiencia
                                        </p>
                                    </div>
                                </div>
                                <div className="flex items-center gap-3 px-6 py-3 bg-white/5 rounded-2xl border border-white/10 backdrop-blur-md">
                                    <span className="text-3xl font-black text-white tracking-tighter">100</span>
                                    <span className="text-[10px] font-black text-slate-500 uppercase">Puntos<br />Máximos</span>
                                </div>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative z-10">
                                {/* Pilar 1: Engagement */}
                                <div className="p-6 bg-slate-800/20 rounded-3xl border border-emerald-500/5 hover:border-emerald-500/30 transition-all group/pilar">
                                    <div className="flex justify-between items-start mb-4">
                                        <div className="flex items-center gap-2">
                                            <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.4)]"></div>
                                            <span className="text-emerald-400 font-black uppercase text-[10px] tracking-widest">Engagement</span>
                                        </div>
                                        <span className="text-xl font-black text-white">30%</span>
                                    </div>
                                    <div className="w-full h-1.5 bg-slate-800 rounded-full mb-6 overflow-hidden">
                                        <div className="h-full bg-gradient-to-r from-emerald-600 to-emerald-400" style={{ width: '30%' }}></div>
                                    </div>
                                    <div className="space-y-3">
                                        <div className="flex items-center justify-between text-[10px] text-slate-400 font-bold uppercase tracking-wider">
                                            <span>Visitas / No Cancela</span>
                                            <span className="text-emerald-500/70">12 Pts</span>
                                        </div>
                                        <div className="flex items-center justify-between text-[10px] text-slate-400 font-bold uppercase tracking-wider">
                                            <span>Gestión Leads</span>
                                            <span className="text-emerald-500/70">12 Pts</span>
                                        </div>
                                        <div className="flex items-center justify-between text-[10px] text-slate-400 font-bold uppercase tracking-wider">
                                            <span>Respuesta 24h</span>
                                            <span className="text-emerald-500/70">6 Pts</span>
                                        </div>
                                    </div>
                                </div>

                                {/* Pilar 2: Rendimiento */}
                                <div className="p-6 bg-slate-800/20 rounded-3xl border border-blue-500/5 hover:border-blue-500/30 transition-all group/pilar">
                                    <div className="flex justify-between items-start mb-4">
                                        <div className="flex items-center gap-2">
                                            <div className="w-2.5 h-2.5 rounded-full bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.4)]"></div>
                                            <span className="text-blue-400 font-black uppercase text-[10px] tracking-widest">Rendimiento</span>
                                        </div>
                                        <span className="text-xl font-black text-white">55%</span>
                                    </div>
                                    <div className="w-full h-1.5 bg-slate-800 rounded-full mb-6 overflow-hidden">
                                        <div className="h-full bg-gradient-to-r from-blue-600 to-blue-400" style={{ width: '55%' }}></div>
                                    </div>
                                    <div className="space-y-3">
                                        <div className="flex items-center justify-between text-[10px] text-slate-400 font-bold uppercase tracking-wider">
                                            <span>Conv. Lead/Contrato</span>
                                            <span className="text-blue-500/70">27.5 Pts</span>
                                        </div>
                                        <div className="flex items-center justify-between text-[10px] text-slate-400 font-bold uppercase tracking-wider">
                                            <span>Contratos Absolutos</span>
                                            <span className="text-blue-500/70">13.75 Pts</span>
                                        </div>
                                        <div className="flex items-center justify-between text-[10px] text-slate-400 font-bold uppercase tracking-wider">
                                            <span>Eficiencia Prospección</span>
                                            <span className="text-blue-500/70">13.75 Pts</span>
                                        </div>
                                    </div>
                                </div>

                                {/* Pilar 3: Eficiencia */}
                                <div className="p-6 bg-slate-800/20 rounded-3xl border border-purple-500/5 hover:border-purple-500/30 transition-all group/pilar">
                                    <div className="flex justify-between items-start mb-4">
                                        <div className="flex items-center gap-2">
                                            <div className="w-2.5 h-2.5 rounded-full bg-purple-500 shadow-[0_0_10px_rgba(168,85,247,0.4)]"></div>
                                            <span className="text-purple-400 font-black uppercase text-[10px] tracking-widest">Eficiencia</span>
                                        </div>
                                        <span className="text-xl font-black text-white">15%</span>
                                    </div>
                                    <div className="w-full h-1.5 bg-slate-800 rounded-full mb-6 overflow-hidden">
                                        <div className="h-full bg-gradient-to-r from-purple-600 to-purple-400" style={{ width: '15%' }}></div>
                                    </div>
                                    <div className="space-y-3">
                                        <div className="flex items-center justify-between text-[10px] text-slate-400 font-bold uppercase tracking-wider">
                                            <span>Velocidad de Cierre</span>
                                            <span className="text-purple-500/70">5 Pts</span>
                                        </div>
                                        <div className="flex items-center justify-between text-[10px] text-slate-400 font-bold uppercase tracking-wider">
                                            <span>Resolución Tickets</span>
                                            <span className="text-purple-500/70">5 Pts</span>
                                        </div>
                                        <div className="flex items-center justify-between text-[10px] text-slate-400 font-bold uppercase tracking-wider">
                                            <span>Calidad de Datos</span>
                                            <span className="text-purple-500/70">5 Pts</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="overflow-x-auto">
                            <table className="w-full text-left border-collapse">
                                <thead>
                                    <tr className="text-[10px] font-black text-slate-500 uppercase tracking-[0.2em] border-b border-white/5">
                                        <th className="py-6 px-4">Corredor</th>
                                        <th className="py-6 text-center">Reservas</th>
                                        <th className="py-6 text-center text-emerald-400">Contratos</th>
                                        <th className="py-6 text-center">Eficiencia</th>
                                        <th className="py-6 text-center text-amber-400">Score</th>
                                        <th className="py-6 text-center">Capacidad</th>
                                        <th className="py-6 text-center text-indigo-400">Leads</th>
                                        <th className="py-6 text-center text-pink-400">Meta</th>
                                        <th className="py-6 text-center">Acción Sugerida</th>
                                    </tr>
                                </thead>
                                <tbody className="text-sm">
                                    {brokers.map((broker: any) => {
                                        // Find matching broker in rankingData to get contracts and real-time values
                                        const realBroker = rankingData.find(r =>
                                            r.name.toLowerCase().replace(/\s+/g, '') === broker.name.toLowerCase().replace(/\s+/g, '') ||
                                            r.name.toLowerCase().includes(broker.name.toLowerCase().split(' ')[0])
                                        );
                                        const realContracts = realBroker?.contracts || 0;
                                        const realReservas = realBroker?.val || 0;

                                        // Get broker goal and commitment
                                        const brokerGoal = brokerGoals[broker.name];
                                        const personalGoal = brokerGoal?.personal_goal || 0;
                                        const commitmentComment = brokerGoal?.commitment_comment;

                                        // Find capacity data for this broker
                                        const capacityInfo = capacityData?.brokers.find((c: any) =>
                                            c.corredor.toLowerCase().includes(broker.name.toLowerCase().split(' ')[0])
                                        );

                                        return (
                                            <tr key={broker.name} className="border-b border-slate-800/50 hover:bg-white/5 transition-colors group">
                                                <td className="py-4 font-bold text-slate-300">
                                                    {broker.name}
                                                </td>
                                                <td className="py-4 text-center font-bold text-slate-400">{realReservas}</td>
                                                <td className="py-4 text-center font-black text-emerald-400">{realContracts}</td>
                                                <td className="py-4 text-center font-mono text-slate-400">
                                                    {parseFloat(broker.conversion || '0').toFixed(1)}%
                                                </td>

                                                {/* Score Column */}
                                                <td className="py-4 text-center">
                                                    <span className={`px-3 py-1.5 rounded-lg text-sm font-black ${broker.score >= 70 ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 shadow-[0_0_15px_rgba(16,185,129,0.1)]' :
                                                        broker.score >= 40 ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30' :
                                                            'bg-red-500/20 text-red-400 border border-red-500/30'
                                                        }`}>
                                                        {broker.score?.toFixed(0) || '0'}
                                                    </span>
                                                </td>

                                                {/* Capacity Column */}
                                                <td className="py-4 text-center">
                                                    {capacityInfo ? (
                                                        <span className={`px-2 py-1 rounded-full text-[10px] font-bold ${capacityInfo.capacity_status === 'critical' ? 'bg-red-500/20 text-red-400' :
                                                            capacityInfo.capacity_status === 'warning' ? 'bg-yellow-500/20 text-yellow-400' :
                                                                'bg-emerald-500/20 text-emerald-400'
                                                            }`}>
                                                            {Math.round(capacityInfo.capacity_pct || 0)}%
                                                        </span>
                                                    ) : '-'}
                                                </td>

                                                {/* Meta Reservas Column */}
                                                <td className="py-4 text-center">
                                                    <div className="flex flex-col items-center">
                                                        <span className="text-[9px] text-slate-500 font-bold uppercase mb-0.5">Meta Reservas</span>
                                                        {broker.meta_personal ? ( // Changed personalMeta to meta_personal
                                                            <span className="text-sm font-black text-white">{broker.meta_personal}</span> // Changed personalMeta to meta_personal
                                                        ) : (
                                                            <button
                                                                onClick={() => onSetGoal && onSetGoal(broker)} // Updated onClick to use onSetGoal
                                                                className="text-[9px] bg-slate-800 hover:bg-slate-700 text-slate-400 px-2 py-0.5 rounded-lg border border-slate-700 transition-colors uppercase font-black"
                                                            >
                                                                Definir
                                                            </button>
                                                        )}
                                                    </div>
                                                </td>

                                                <td className="py-4 text-center">
                                                    {isClosedMonth ? (
                                                        <span className="text-[10px] text-slate-600 font-bold uppercase">Consolidado</span>
                                                    ) : (
                                                        <span className={`px-3 py-1 rounded-full font-bold text-xs ${broker.leadsNeeded > 20 ? 'bg-red-500/20 text-red-400' : 'bg-blue-500/20 text-blue-400'}`}>
                                                            +{broker.leadsNeeded}
                                                        </span>
                                                    )}
                                                </td>

                                                {/* Meta Personal Column */}
                                                <td className="py-4 text-center">
                                                    {personalGoal > 0 ? (
                                                        <div className="flex flex-col items-center gap-1">
                                                            <span className="text-sm font-black text-pink-400">{personalGoal}</span>
                                                            {commitmentComment && (
                                                                <div className="relative group/tooltip">
                                                                    <MessageSquare size={14} className="text-slate-500 cursor-help" />
                                                                    <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-[9px] text-slate-300 whitespace-nowrap opacity-0 invisible group-hover/tooltip:opacity-100 group-hover/tooltip:visible transition-all z-50 max-w-xs shadow-xl">
                                                                        <div className="font-bold text-pink-400 mb-1">Compromiso:</div>
                                                                        {commitmentComment}
                                                                    </div>
                                                                </div>
                                                            )}
                                                        </div>
                                                    ) : (
                                                        <span className="text-[10px] text-slate-600 font-bold">Sin meta</span>
                                                    )}
                                                </td>

                                                <td className="py-4 text-center">
                                                    <span className={`text-[10px] font-black uppercase px-2.5 py-1 rounded-full border ${broker.action === "Meta Cumplida" ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                                                        broker.action === "Coaching Urgente" ? 'bg-red-500/10 text-red-400 border-red-500/20 animate-pulse' :
                                                            'bg-blue-500/10 text-blue-400 border-blue-500/20'
                                                        }`}>
                                                        {broker.action}
                                                    </span>
                                                </td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>
                    </section>
                </div>

                {/* Columna Derecha: Geo & Alertas */}
                <div className="lg:col-span-4 space-y-8">

                    {/* Radar de Cobertura */}
                    <section className="bg-slate-900/50 rounded-3xl p-6 border border-slate-800 shadow-2xl">
                        <h3 className="text-sm font-bold text-white uppercase tracking-widest mb-6 flex items-center gap-2">
                            <Map size={16} className="text-blue-400" /> Cobertura vs Stock
                        </h3>

                        <div className="space-y-4">
                            {coverage.map((zone: any) => (
                                <div key={zone.comuna} className="group">
                                    <div className="flex justify-between items-end mb-1">
                                        <span className="text-xs font-bold text-slate-400 group-hover:text-white transition-colors">{zone.comuna}</span>
                                        <div className="text-xs">
                                            <span className="text-white font-black">{zone.stock} Unds</span>
                                            <span className="text-slate-600 mx-2">|</span>
                                            <span className={`${zone.activeBrokers < 2 ? 'text-red-400' : 'text-emerald-400'} font-bold`}>
                                                {zone.activeBrokers} Activos
                                            </span>
                                        </div>
                                    </div>
                                    <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden flex">
                                        <div className="h-full bg-blue-500" style={{ width: `${Math.min(zone.stock, 100)}%` }}></div>
                                    </div>
                                    {zone.alert === 'critical' && (
                                        <div className="mt-2 p-2 bg-red-500/10 border border-red-500/30 rounded-lg flex items-center gap-2">
                                            <AlertTriangle size={12} className="text-red-500" />
                                            <p className="text-[10px] text-red-400 font-bold uppercase">Zona Desatendida</p>
                                        </div>
                                    )}
                                    {zone.alert === 'warning' && (
                                        <div className="mt-2 p-2 bg-yellow-500/10 border border-yellow-500/30 rounded-lg flex items-center gap-2">
                                            <AlertTriangle size={12} className="text-yellow-500" />
                                            <p className="text-[10px] text-yellow-400 font-bold uppercase">Alta Demanda</p>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </section>

                    {/* Estadísticas de Eficiencia */}
                    <section className="bg-gradient-to-br from-indigo-900/20 to-slate-900 rounded-3xl p-6 border border-indigo-500/30 shadow-2xl">
                        <h3 className="text-sm font-bold text-white uppercase tracking-widest mb-6 flex items-center gap-2">
                            <Activity size={16} className="text-indigo-400" /> Eficiencia Leads
                        </h3>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="p-4 bg-slate-950/50 rounded-2xl border border-slate-800 text-center">
                                <p className="text-2xl font-black text-white">{efficiencyAlerts.leadsSinGestion}</p>
                                <p className="text-[10px] text-slate-500 font-bold uppercase mt-1">Leads sin Gestión <br /> ({"> 24h"})</p>
                            </div>
                            <div className="p-4 bg-slate-950/50 rounded-2xl border border-slate-800 text-center">
                                <p className="text-2xl font-black text-white">{efficiencyAlerts.unidadesSinVisitas}</p>
                                <p className="text-[10px] text-slate-500 font-bold uppercase mt-1">Unidades <br /> sin Visitas (15d)</p>
                            </div>
                        </div>
                    </section>

                </div>
            </div>
        </div>
    );
};

export default SquadLaboratory;
