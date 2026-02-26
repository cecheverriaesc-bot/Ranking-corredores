import React, { useState, useMemo, useEffect } from 'react';
import {
    Shield, Target, Zap, Users, Map, Brain, AlertTriangle,
    ArrowRight, ChevronLeft, TrendingUp, Activity, Search, MessageSquare, Award,
    Trophy, BarChart3
} from 'lucide-react';
import { TEAMS, MONTHLY_DATA } from '../constants';
import { CorredorData, BrokerGoalData } from '../types';

interface SquadLaboratoryProps {
    onBack: () => void;
    rankingData: CorredorData[];
    monthlyGoal: number;
}

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
}

const SquadLaboratory: React.FC<SquadLaboratoryProps> = ({
    onBack,
    rankingData,
    monthlyGoal,
    selectedMonth: parentSelectedMonth,
    onMonthChange
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

                // Fetch intelligence (existing)
                const intelligenceResponse = await fetch('/api/v2_intelligence');
                if (!intelligenceResponse.ok) throw new Error('Failed to fetch intelligence data');
                const intelligenceData = await intelligenceResponse.json();

                // Fetch capacity (new)
                const capacityResponse = await fetch('/api/v3_capacity');
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

            {/* Encabezado */}
            <header className="flex justify-between items-center mb-10 border-b border-indigo-500/20 pb-6">
                <div className="flex items-center gap-4">
                    <button
                        onClick={onBack}
                        className="p-2 rounded-xl bg-slate-800/50 hover:bg-indigo-500/20 text-slate-400 hover:text-white transition-all"
                    >
                        <ChevronLeft size={20} />
                    </button>
                    <div>
                        <h1 className="text-2xl font-black text-white uppercase tracking-widest flex items-center gap-3">
                            <Brain className="text-indigo-400" />
                            Laboratorio Estratégico
                        </h1>
                        <div className="flex items-center gap-4 mt-2">
                            <p className="text-xs font-bold text-indigo-500/80 uppercase tracking-widest">Misión 110% • Meta Estratégica</p>
                            <MonthSelector selected={selectedMonth} onChange={setSelectedMonth} />
                        </div>
                    </div>
                </div>
                <div className="flex items-center gap-6">
                    <div className="text-right">
                        <p className="text-[10px] font-bold text-slate-500 uppercase">Contratos</p>
                        <p className="text-xl font-black text-white">{stats.totalContracts}</p>
                    </div>
                    <div className="text-right">
                        <p className="text-[10px] font-bold text-slate-500 uppercase">Proyección Final</p>
                        <p className="text-xl font-black text-blue-400">{stats.projection}</p>
                    </div>
                    <div className="text-right pl-4 border-l border-slate-800">
                        <p className="text-[10px] font-bold text-slate-500 uppercase">Target 110%</p>
                        <p className="text-xl font-black text-emerald-400">{(stats.targetCheck).toFixed(0)}</p>
                    </div>
                </div>
            </header>

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

                        {/* Score Methodology Legend - REDISEÑADO PREMIUM */}
                        <div className="mb-8 p-6 bg-gradient-to-br from-slate-950 to-slate-900 border border-slate-700/50 rounded-3xl shadow-inner">
                            <div className="flex items-center gap-4 mb-8">
                                <div className="p-3 bg-amber-500/20 rounded-2xl border border-amber-500/30">
                                    <BarChart3 className="text-amber-400 w-6 h-6" />
                                </div>
                                <div>
                                    <h4 className="text-lg font-black text-white uppercase tracking-wider">
                                        Arquitectura del Scoring <span className="text-amber-400 ml-2">(75/100 PTS)</span>
                                    </h4>
                                    <p className="text-xs text-slate-500 font-medium">
                                        Fase 1: Enfoque en Gestión Comercial y Conversión
                                    </p>
                                </div>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                {/* Pilar 1: Engagement */}
                                <div className="p-5 bg-slate-800/20 rounded-2xl border border-emerald-500/10 hover:border-emerald-500/30 transition-all">
                                    <div className="flex justify-between items-start mb-4">
                                        <div className="flex items-center gap-2">
                                            <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></div>
                                            <span className="text-emerald-400 font-black uppercase text-xs tracking-wider">Engagement & Gestión</span>
                                        </div>
                                        <span className="text-xl font-black text-white">35 Pts</span>
                                    </div>
                                    <div className="w-full h-1 bg-slate-800 rounded-full mb-4 overflow-hidden">
                                        <div className="h-full bg-emerald-500" style={{ width: '46%' }}></div>
                                    </div>
                                    <ul className="grid grid-cols-2 gap-x-4 gap-y-2 text-[11px] text-slate-400">
                                        <li className="flex items-center gap-1.5 font-medium">• Visitas Realizadas <span className="text-[10px] text-emerald-500/70">(10)</span></li>
                                        <li className="flex items-center gap-1.5 font-medium">• No Cancela Visitas <span className="text-[10px] text-emerald-500/70">(8)</span></li>
                                        <li className="flex items-center gap-1.5 font-medium">• Respuesta &lt;24h <span className="text-[10px] text-emerald-500/70">(5)</span></li>
                                        <li className="flex items-center gap-1.5 font-medium">• Gestión Activa <span className="text-[10px] text-emerald-500/70">(7)</span></li>
                                        <li className="flex items-center gap-1.5 font-medium col-span-2">• No Descarta Leads <span className="text-[10px] text-emerald-500/70">(5)</span></li>
                                    </ul>
                                </div>

                                {/* Pilar 2: Rendimiento */}
                                <div className="p-5 bg-slate-800/20 rounded-2xl border border-blue-500/10 hover:border-blue-500/30 transition-all">
                                    <div className="flex justify-between items-start mb-4">
                                        <div className="flex items-center gap-2">
                                            <div className="w-2.5 h-2.5 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.5)]"></div>
                                            <span className="text-blue-400 font-black uppercase text-xs tracking-wider">Rendimiento & Conversión</span>
                                        </div>
                                        <span className="text-xl font-black text-white">40 Pts</span>
                                    </div>
                                    <div className="w-full h-1 bg-slate-800 rounded-full mb-4 overflow-hidden">
                                        <div className="h-full bg-blue-500" style={{ width: '53%' }}></div>
                                    </div>
                                    <ul className="grid grid-cols-1 gap-2 text-[11px] text-slate-400">
                                        <li className="flex items-center gap-1.5 font-medium">• Prospecto → Reserva <span className="text-[10px] text-blue-500/70">(15)</span></li>
                                        <li className="flex items-center gap-1.5 font-medium">• Reservas Absolutas <span className="text-[10px] text-blue-500/70">(10)</span></li>
                                        <li className="flex items-center gap-1.5 font-medium">• Leads/Visita Eficiencia <span className="text-[10px] text-blue-500/70">(10)</span></li>
                                        <li className="flex items-center gap-1.5 font-medium">• Lead → Contrato <span className="text-[10px] text-blue-500/70">(5)</span></li>
                                    </ul>
                                </div>
                            </div>

                            <div className="mt-6 flex flex-col items-center gap-2">
                                <div className="flex items-center gap-2 text-[10px] text-slate-500 font-medium">
                                    <Activity size={12} className="text-indigo-500" />
                                    <span>Pilar 3: <span className="text-slate-300">Eficiencia Operativa (25%)</span> — Próximamente: Resolución de Tickets</span>
                                </div>
                                <p className="text-[9px] text-slate-600 italic">
                                    * Hover sobre el score de cada corredor para ver el desglose detallado
                                </p>
                            </div>
                        </div>

                        <div className="overflow-x-auto">
                            <table className="w-full text-left border-collapse">
                                <thead>
                                    <tr className="text-[10px] font-black text-slate-500 uppercase tracking-wider border-b border-slate-800">
                                        <th className="py-4">Corredor</th>
                                        <th className="py-4 text-center">Reservas</th>
                                        <th className="py-4 text-center text-emerald-400">Contratos</th>
                                        <th className="py-4 text-center">Conv. %</th>
                                        <th className="py-4 text-center text-amber-400">Score</th>
                                        <th className="py-4 text-center">Capacidad</th>
                                        <th className="py-4 text-center text-indigo-400">Leads Diarios</th>
                                        <th className="py-4 text-center text-pink-400">Meta Personal</th>
                                        <th className="py-4 text-center">Acción Sugerida</th>
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
                                                <td className="py-4 text-center relative group">
                                                    <div className="flex flex-col items-center gap-1">
                                                        <span className={`px-2 py-1 rounded-lg text-xs font-black cursor-help ${(broker.score || 0) >= 0.25 ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' :
                                                            (broker.score || 0) >= 0.15 ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30' :
                                                                'bg-red-500/20 text-red-400 border border-red-500/30'
                                                            }`}>
                                                            {((broker.score || 0) * 100).toFixed(0)}
                                                        </span>
                                                    </div>
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

                                                <td className="py-4 text-center">
                                                    <span className={`px-3 py-1 rounded-full font-bold text-xs ${broker.leadsNeeded > 20 ? 'bg-red-500/20 text-red-400' : 'bg-blue-500/20 text-blue-400'}`}>
                                                        +{broker.leadsNeeded}
                                                    </span>
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
                                                    <span className={`text-[10px] font-bold uppercase ${broker.action === "Coaching Urgente" ? 'text-red-400' :
                                                        broker.action === "Meta Cumplida" ? 'text-slate-500' : 'text-emerald-400'
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
