import React, { useState, useMemo, useEffect } from 'react';
import {
    Shield, Target, Zap, Users, Map, Brain, AlertTriangle,
    ArrowRight, ChevronLeft, TrendingUp, Activity, Search, MessageSquare, Award,
    Filter, Trophy, Medal, Star, TrendingDown, Minus, BarChart3, PieChart
} from 'lucide-react';
import { TEAMS, MONTHLY_DATA } from '../constants';
import { CorredorData, BrokerGoalData } from '../types';

interface SquadLaboratoryProps {
    onBack: () => void;
    rankingData: CorredorData[];
    monthlyGoal: number;
    userEmail: string | null;
    selectedMonth?: string;
    onMonthChange?: (month: string) => void;
}

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
    telefono?: string;  // Teléfono para WhatsApp
    breakdown_engagement: Record<string, number>;
    breakdown_rendimiento: Record<string, number>;
    breakdown_eficiencia: Record<string, number>;
}

interface IntelligenceData {
    brokers: BrokerIntelligence[];
    brokers_rm: BrokerIntelligence[];
    brokers_regiones: BrokerIntelligence[];
    leader?: BrokerIntelligence;
    squad_summary: {
        meta_equipo: number;
        contratos_actuales: number;
        faltante_equipo: number;
        dias_restantes: number;
        total_brokers_rm: number;
        total_brokers_regiones: number;
        scoring_version: string;
        scoring_methodology?: {
            engagement_weight: number;
            rendimiento_weight: number;
            total_possible: number;
            normalization: string;
        };
    };
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

const StrategicLab: React.FC<SquadLaboratoryProps> = ({
    onBack,
    rankingData,
    monthlyGoal,
    userEmail,
    selectedMonth: parentSelectedMonth,
    onMonthChange
}) => {
    // Month Selection State - use parent value if provided, otherwise local
    const [localSelectedMonth, setLocalSelectedMonth] = useState<string>('2026-02');
    const selectedMonth = parentSelectedMonth !== undefined ? parentSelectedMonth : localSelectedMonth;
    const setSelectedMonth = onMonthChange || setLocalSelectedMonth;

    // State for API data
    const [intelligenceData, setIntelligenceData] = useState<IntelligenceData | null>(null);
    const [capacityData, setCapacityData] = useState<any>(null);
    const [brokerGoals, setBrokerGoals] = useState<Record<string, BrokerGoalData>>({});
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Filter states
    const [regionFilter, setRegionFilter] = useState<'ALL' | 'RM' | 'REGIONES'>('ALL');
    const [searchTerm, setSearchTerm] = useState('');
    const [minScore, setMinScore] = useState(0);
    const [showPillarColumns, setShowPillarColumns] = useState(false);

    // Access control - solo Carlos puede acceder
    const isCarlos = userEmail === 'carlos.echeverria@assetplan.cl';

    // Fetch intelligence, capacity and goals data
    useEffect(() => {
        // Verificar acceso
        if (!isCarlos) {
            setError('Acceso denegado. Esta vista es exclusiva para Carlos Echeverria.');
            return;
        }

        const fetchAllData = async () => {
            try {
                setIsLoading(true);

                // Fetch intelligence v5 con filtro de región
                const intelligenceResponse = await fetch(`/api/v5_intelligence?region=${regionFilter}`);
                if (!intelligenceResponse.ok) throw new Error('Failed to fetch intelligence data');
                const intelligenceData = await intelligenceResponse.json();

                // Fetch capacity
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
    }, [regionFilter, isCarlos, selectedMonth]);

    // Extract data from API response
    const brokers = intelligenceData?.brokers || [];
    const coverage = intelligenceData ? [] : []; // Placeholder para coverage
    const efficiencyAlerts = intelligenceData ? {
        leadsSinGestion: 0,
        unidadesSinVisitas: 0
    } : { leadsSinGestion: 0, unidadesSinVisitas: 0 };

    // Filtered brokers based on search and score
    const filteredBrokers = useMemo(() => {
        return brokers.filter((broker: BrokerIntelligence) => {
            const matchesSearch = broker.name.toLowerCase().includes(searchTerm.toLowerCase());
            const matchesScore = broker.score >= minScore;
            return matchesSearch && matchesScore;
        });
    }, [brokers, searchTerm, minScore]);

    // Stats calculation
    const stats = useMemo(() => {
        const totalReservas = filteredBrokers.reduce((acc, curr) => acc + (curr.reservas || 0), 0);
        const totalContracts = rankingData.reduce((acc, curr) => acc + (curr.contracts || 0), 0);
        const targetCheck = monthlyGoal * 1.10;

        const today = new Date();
        const currentMonth = today.getMonth();
        const currentYear = today.getFullYear();
        const currentDay = today.getDate();
        const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
        const daysRemaining = Math.max(0, daysInMonth - currentDay);

        const reservaDailyRate = currentDay > 0 ? totalReservas / currentDay : 0;
        const reservaProjection = totalReservas + (reservaDailyRate * daysRemaining);

        return {
            totalReservas,
            totalContracts,
            targetCheck,
            projection: Math.round(reservaProjection)
        };
    }, [filteredBrokers, rankingData, monthlyGoal]);

    // Get score color
    const getScoreColor = (score: number) => {
        const maxScore = intelligenceData?.squad_summary?.scoring_methodology?.total_possible || 100;
        const percentage = (score / maxScore) * 100;

        if (percentage >= 70) return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
        if (percentage >= 40) return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
        return 'bg-red-500/20 text-red-400 border-red-500/30';
    };

    // Get region badge
    const getRegionBadge = (regionType: string) => {
        if (regionType === 'RM') {
            return (
                <span className="px-2 py-0.5 rounded-md bg-blue-500/20 text-blue-400 border border-blue-500/30 text-[9px] font-black uppercase">
                    RM
                </span>
            );
        }
        return (
            <span className="px-2 py-0.5 rounded-md bg-orange-500/20 text-orange-400 border border-orange-500/30 text-[9px] font-black uppercase">
                Regiones
            </span>
        );
    };

    // Get action badge
    const getActionBadge = (action: string) => {
        if (action.includes('Meta Cumplida')) {
            return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
        }
        if (action.includes('Coaching')) {
            return 'bg-red-500/20 text-red-400 border-red-500/30';
        }
        if (action.includes('leads/día')) {
            return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
        }
        return 'bg-slate-500/20 text-slate-400 border-slate-500/30';
    };

    // Render access denied
    if (!isCarlos) {
        return (
            <div className="min-h-screen bg-[#0f172a] text-slate-200 font-sans p-6 flex items-center justify-center">
                <div className="max-w-md bg-red-500/10 border border-red-500/30 rounded-2xl p-8 text-center">
                    <AlertTriangle className="w-16 h-16 text-red-400 mx-auto mb-4" />
                    <h2 className="text-2xl font-black text-red-400 mb-2">Acceso Denegado</h2>
                    <p className="text-slate-400 mb-6">Esta vista es exclusiva para Carlos Echeverria.</p>
                    <button
                        onClick={onBack}
                        className="px-6 py-3 bg-slate-800 hover:bg-slate-700 rounded-xl text-white font-bold transition-all"
                    >
                        Volver al Dashboard
                    </button>
                </div>
            </div>
        );
    }

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
            <header className="flex justify-between items-center mb-6 border-b border-indigo-500/20 pb-6">
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
                            Laboratorio Estratégico v5
                        </h1>
                        <div className="flex items-center gap-4 mt-2">
                            <p className="text-xs font-bold text-indigo-500/80 uppercase tracking-widest">Scoring Estadístico Robusto</p>
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
                        <p className="text-[10px] font-bold text-slate-500 uppercase">Proyección</p>
                        <p className="text-xl font-black text-blue-400">{stats.projection}</p>
                    </div>
                    <div className="text-right pl-4 border-l border-slate-800">
                        <p className="text-[10px] font-bold text-slate-500 uppercase">Target 110%</p>
                        <p className="text-xl font-black text-emerald-400">{(stats.targetCheck).toFixed(0)}</p>
                    </div>
                </div>
            </header>

            {/* Barra de Progreso Global del Squad */}
            {intelligenceData?.squad_summary && (
                <section className="mb-8 bg-gradient-to-r from-slate-900/80 to-slate-800/50 rounded-2xl p-5 border border-slate-700/50">
                    <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                            <Target className="w-5 h-5 text-indigo-400" />
                            <span className="text-sm font-black text-white uppercase tracking-wide">
                                Progreso del Squad
                            </span>
                        </div>
                        <div className="text-right">
                            <span className={`text-lg font-black ${(intelligenceData.squad_summary.contratos_actuales / intelligenceData.squad_summary.meta_equipo * 100) >= 80
                                ? 'text-emerald-400'
                                : (intelligenceData.squad_summary.contratos_actuales / intelligenceData.squad_summary.meta_equipo * 100) >= 50
                                    ? 'text-amber-400'
                                    : 'text-red-400'
                                }`}>
                                ðŸŽ¯ {intelligenceData.squad_summary.contratos_actuales} / {intelligenceData.squad_summary.meta_equipo} ({((intelligenceData.squad_summary.contratos_actuales / intelligenceData.squad_summary.meta_equipo) * 100).toFixed(1)}%)
                            </span>
                        </div>
                    </div>
                    <div className="relative h-4 bg-slate-950 rounded-full overflow-hidden border border-slate-800">
                        <div
                            className={`absolute left-0 top-0 h-full rounded-full transition-all duration-500 ${(intelligenceData.squad_summary.contratos_actuales / intelligenceData.squad_summary.meta_equipo * 100) >= 80
                                ? 'bg-gradient-to-r from-emerald-600 to-emerald-400'
                                : (intelligenceData.squad_summary.contratos_actuales / intelligenceData.squad_summary.meta_equipo * 100) >= 50
                                    ? 'bg-gradient-to-r from-amber-600 to-amber-400'
                                    : 'bg-gradient-to-r from-red-600 to-red-400'
                                }`}
                            style={{ width: `${Math.min(100, (intelligenceData.squad_summary.contratos_actuales / intelligenceData.squad_summary.meta_equipo) * 100)}%` }}
                        />
                    </div>
                    <div className="flex justify-between mt-2 text-[9px] font-bold text-slate-500 uppercase tracking-wider">
                        <span>Inicio mes</span>
                        <span className={
                            (intelligenceData.squad_summary.contratos_actuales / intelligenceData.squad_summary.meta_equipo * 100) >= 80
                                ? 'text-emerald-500/70'
                                : (intelligenceData.squad_summary.contratos_actuales / intelligenceData.squad_summary.meta_equipo * 100) >= 50
                                    ? 'text-amber-500/70'
                                    : 'text-red-500/70'
                        }>
                            {intelligenceData.squad_summary.dias_restantes} días restantes
                        </span>
                        <span>Meta: {intelligenceData.squad_summary.meta_equipo}</span>
                    </div>
                </section>
            )}

            {/* Líder de Performance Total */}
            {intelligenceData?.leader && (
                <section className="mb-10 bg-gradient-to-r from-amber-900/20 to-yellow-900/20 rounded-3xl p-8 border-2 border-amber-500/40 shadow-2xl relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-96 h-96 bg-amber-500/10 rounded-full blur-3xl pointer-events-none"></div>
                    <div className="relative z-10">
                        <div className="flex items-center gap-2 mb-4">
                            <Trophy className="w-6 h-6 text-amber-400" />
                            <h2 className="text-lg font-black text-amber-400 uppercase tracking-widest">
                                ðŸ† Líder de Performance Total
                            </h2>
                        </div>
                        <div className="flex items-center gap-6">
                            <div className="w-20 h-20 rounded-full bg-amber-500/20 border-4 border-amber-400 flex items-center justify-center text-3xl font-black text-amber-400">
                                {intelligenceData.leader.name.charAt(0)}
                            </div>
                            <div>
                                <h3 className="text-3xl font-black text-white mb-1">
                                    {intelligenceData.leader.name}
                                </h3>
                                <div className="flex items-center gap-3 mb-2">
                                    {getRegionBadge(intelligenceData.leader.region_type)}
                                    <span className="text-slate-400 text-sm">
                                        {intelligenceData.leader.comunas?.slice(0, 3).join(', ')}
                                    </span>
                                </div>
                                <div className="flex items-center gap-6 text-sm">
                                    <div className="flex items-center gap-2">
                                        <Star className="w-4 h-4 text-amber-400" />
                                        <span className="text-amber-400 font-black">
                                            Score: {intelligenceData.leader.score.toFixed(1)}
                                        </span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <TrendingUp className="w-4 h-4 text-emerald-400" />
                                        <span className="text-emerald-400 font-black">
                                            {intelligenceData.leader.reservas} reservas
                                        </span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <Award className="w-4 h-4 text-blue-400" />
                                        <span className="text-blue-400 font-black">
                                            Percentil: {intelligenceData.leader.percentile}Â°
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>
            )}

            {/* Filtros y Controles */}
            <div className="mb-8 flex flex-wrap gap-4 items-center">
                <div className="flex items-center gap-2 bg-slate-900/50 rounded-xl p-1 border border-slate-800">
                    <button
                        onClick={() => setRegionFilter('ALL')}
                        className={`px-4 py-2 rounded-lg text-xs font-bold transition-all ${regionFilter === 'ALL'
                            ? 'bg-indigo-500 text-white'
                            : 'text-slate-400 hover:text-white'
                            }`}
                    >
                        Todos
                    </button>
                    <button
                        onClick={() => setRegionFilter('RM')}
                        className={`px-4 py-2 rounded-lg text-xs font-bold transition-all flex items-center gap-2 ${regionFilter === 'RM'
                            ? 'bg-blue-500 text-white'
                            : 'text-slate-400 hover:text-white'
                            }`}
                    >
                        <Map size={14} />
                        RM
                    </button>
                    <button
                        onClick={() => setRegionFilter('REGIONES')}
                        className={`px-4 py-2 rounded-lg text-xs font-bold transition-all flex items-center gap-2 ${regionFilter === 'REGIONES'
                            ? 'bg-orange-500 text-white'
                            : 'text-slate-400 hover:text-white'
                            }`}
                    >
                        <Map size={14} />
                        Regiones
                    </button>
                </div>

                <div className="flex-1 min-w-[200px]">
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
                        <input
                            type="text"
                            placeholder="Buscar corredor..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full pl-10 pr-4 py-2 bg-slate-900/50 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
                        />
                    </div>
                </div>

                <div className="flex items-center gap-3 bg-slate-900/50 rounded-xl px-4 py-2 border border-slate-800">
                    <Filter size={16} className="text-slate-500" />
                    <span className="text-xs font-bold text-slate-400">Score mín:</span>
                    <input
                        type="range"
                        min="0"
                        max="100"
                        value={minScore}
                        onChange={(e) => setMinScore(Number(e.target.value))}
                        className="w-24 accent-indigo-500"
                    />
                    <span className="text-xs font-black text-indigo-400 w-8">{minScore}</span>
                </div>

                <button
                    onClick={() => setShowPillarColumns(!showPillarColumns)}
                    className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 border ${showPillarColumns
                        ? 'bg-purple-500/20 text-purple-400 border-purple-500/50'
                        : 'bg-slate-800 text-slate-400 border-slate-700 hover:border-slate-600'
                        }`}
                >
                    <Target size={14} />
                    {showPillarColumns ? 'Ocultar Pilares' : 'Ver Pilares'}
                </button>
            </div>

            {/* Grilla Principal */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">

                {/* Columna Izquierda: Matriz de Scoring */}
                <div className="lg:col-span-9 space-y-8">

                    {/* Matriz de Coaching */}
                    <section className="bg-slate-900/50 rounded-3xl p-8 border border-slate-800 shadow-2xl relative overflow-hidden">
                        <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/5 rounded-full blur-3xl pointer-events-none"></div>
                        <h3 className="text-lg font-bold text-white uppercase tracking-widest mb-6 flex items-center gap-2">
                            <Zap size={18} className="text-yellow-400" /> Matriz de Asignación Inteligente
                        </h3>

                        {/* Score Methodology Legend */}
                        <div className="mb-6 p-5 bg-gradient-to-br from-amber-950/30 to-slate-950/50 border border-amber-500/30 rounded-2xl">
                            <div className="flex items-start gap-3 mb-4">
                                <div className="p-2 bg-amber-500/10 rounded-lg">
                                    <span className="text-2xl">ðŸ“Š</span>
                                </div>
                                <div className="flex-1">
                                    <h4 className="text-xs font-black text-amber-400 uppercase tracking-wider mb-1">
                                        Composición del Score ({intelligenceData?.squad_summary?.scoring_methodology?.total_possible || 100}/100)
                                    </h4>
                                    <p className="text-[9px] text-slate-500 italic">
                                        Scoring estadístico robusto con 3 pilares fundamentales
                                    </p>
                                </div>
                            </div>

                            <div className="grid grid-cols-3 gap-3 text-[9px]">
                                {/* Pilar 1 */}
                                <div className="p-3 bg-slate-950/50 rounded-xl border border-emerald-500/20">
                                    <div className="flex items-center gap-2 mb-2">
                                        <div className="w-3 h-3 bg-emerald-500 rounded-full"></div>
                                        <span className="text-emerald-400 font-black">
                                            {intelligenceData?.squad_summary?.scoring_methodology?.pilar_1_engagement?.weight || 35}% Engagement
                                        </span>
                                    </div>
                                    <div className="space-y-0.5 text-slate-400 pl-5">
                                        <div>• Visitas realizadas</div>
                                        <div>• No cancela visitas</div>
                                        <div>• No descarta leads</div>
                                        <div>• No descarta prospectos</div>
                                        <div>• Acción &lt;24h</div>
                                    </div>
                                </div>

                                {/* Pilar 2 */}
                                <div className="p-3 bg-slate-950/50 rounded-xl border border-blue-500/20">
                                    <div className="flex items-center gap-2 mb-2">
                                        <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                                        <span className="text-blue-400 font-black">
                                            {intelligenceData?.squad_summary?.scoring_methodology?.pilar_2_rendimiento?.weight || 40}% Rendimiento
                                        </span>
                                    </div>
                                    <div className="space-y-0.5 text-slate-400 pl-5">
                                        <div>• Conv. Prospectoâ†’Contrato</div>
                                        <div>• Conv. Leadâ†’Contrato</div>
                                        <div>• Contratos absolutos</div>
                                        <div>• Leads/Visita</div>
                                    </div>
                                </div>

                                {/* Pilar 3 */}
                                <div className="p-3 bg-slate-950/50 rounded-xl border border-purple-500/20">
                                    <div className="flex items-center gap-2 mb-2">
                                        <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
                                        <span className="text-purple-400 font-black">
                                            {intelligenceData?.squad_summary?.scoring_methodology?.pilar_3_eficiencia?.weight || 25}% Eficiencia
                                        </span>
                                    </div>
                                    <div className="space-y-0.5 text-slate-400 pl-5">
                                        <div>• Sin demora procesos</div>
                                        <div>• Tiempo resolución</div>
                                        <div>• Tickets severidad</div>
                                    </div>
                                </div>
                            </div>

                            <div className="mt-3 p-2 bg-slate-800/30 rounded-lg border border-slate-700/30">
                                <p className="text-[8px] text-slate-600 text-center">
                                    <span className="text-yellow-500 font-bold">Nota:</span> Normalización Z-Score robusta con IQR truncation para evitar outliers
                                </p>
                            </div>
                        </div>

                        {/* Tabla de Corredores */}
                        <div className="overflow-x-auto">
                            <table className="w-full text-left border-collapse">
                                <thead>
                                    <tr className="text-[10px] font-black text-slate-500 uppercase tracking-wider border-b border-slate-800">
                                        <th className="py-4">Pos</th>
                                        <th className="py-4">Corredor</th>
                                        <th className="py-4 text-center">Región</th>
                                        <th className="py-4 text-center">Reservas</th>
                                        <th className="py-4 text-center text-emerald-400">Contratos</th>
                                        <th className="py-4 text-center">Conv. %</th>
                                        {showPillarColumns && (
                                            <>
                                                <th className="py-4 text-center text-emerald-400 border-l border-slate-700">
                                                    <div className="flex items-center justify-center gap-1">
                                                        <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
                                                        Engagement
                                                    </div>
                                                </th>
                                                <th className="py-4 text-center text-blue-400">
                                                    <div className="flex items-center justify-center gap-1">
                                                        <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                                                        Rendimiento
                                                    </div>
                                                </th>
                                                <th className="py-4 text-center text-purple-400 border-r border-slate-700">
                                                    <div className="flex items-center justify-center gap-1">
                                                        <div className="w-2 h-2 rounded-full bg-purple-500"></div>
                                                        Eficiencia
                                                    </div>
                                                </th>
                                            </>
                                        )}
                                        <th className="py-4 text-center text-amber-400">Score</th>
                                        <th className="py-4 text-center text-indigo-400">Percentil</th>
                                        <th className="py-4 text-center">Meta</th>
                                        <th className="py-4 text-center">Acción</th>
                                        <th className="py-4 text-center text-emerald-400">WhatsApp</th>
                                    </tr>
                                </thead>
                                <tbody className="text-sm">
                                    {filteredBrokers.map((broker: BrokerIntelligence, index: number) => {
                                        // Get broker goal and commitment
                                        const brokerGoal = brokerGoals[broker.name];
                                        const personalGoal = brokerGoal?.personal_goal || broker.meta_personal;
                                        const commitmentComment = brokerGoal?.commitment_comment;

                                        // Find capacity data for this broker
                                        const capacityInfo = capacityData?.brokers?.find((c: any) =>
                                            c.corredor.toLowerCase().includes(broker.name.toLowerCase().split(' ')[0])
                                        );

                                        return (
                                            <tr key={broker.name} className="border-b border-slate-800/50 hover:bg-white/5 transition-colors group">
                                                <td className="py-4">
                                                    <div className="flex items-center gap-2">
                                                        {index === 0 && <Trophy size={16} className="text-amber-400" />}
                                                        {index === 1 && <Medal size={16} className="text-slate-400" />}
                                                        {index === 2 && <Star size={16} className="text-orange-400" />}
                                                        <span className={`font-black ${index < 3 ? 'text-white' : 'text-slate-500'}`}>
                                                            #{index + 1}
                                                        </span>
                                                    </div>
                                                </td>
                                                <td className="py-4 font-bold text-slate-300">
                                                    {broker.name}
                                                </td>
                                                <td className="py-4 text-center">
                                                    {getRegionBadge(broker.region_type)}
                                                </td>
                                                <td className="py-4 text-center font-bold text-slate-400">{broker.reservas}</td>
                                                <td className="py-4 text-center font-black text-emerald-400">{broker.reservas}</td>
                                                <td className="py-4 text-center font-mono text-slate-400">
                                                    {parseFloat(broker.conversion || '0').toFixed(1)}%
                                                </td>

                                                {showPillarColumns && (
                                                    <>
                                                        {/* Engagement Score */}
                                                        <td className="py-4 text-center border-l border-slate-700">
                                                            <span className="text-xs font-black text-emerald-400">
                                                                {broker.score_engagement.toFixed(1)}
                                                            </span>
                                                        </td>

                                                        {/* Rendimiento Score */}
                                                        <td className="py-4 text-center">
                                                            <span className="text-xs font-black text-blue-400">
                                                                {broker.score_rendimiento.toFixed(1)}
                                                            </span>
                                                        </td>

                                                        {/* Eficiencia Score */}
                                                        <td className="py-4 text-center border-r border-slate-700">
                                                            <span className="text-xs font-black text-purple-400">
                                                                {broker.score_eficiencia.toFixed(1)}
                                                            </span>
                                                        </td>
                                                    </>
                                                )}

                                                {/* Score Column */}
                                                <td className="py-4 text-center">
                                                    <span className={`px-3 py-1.5 rounded-lg text-sm font-black ${getScoreColor(broker.score)}`}>
                                                        {broker.score.toFixed(0)}
                                                    </span>
                                                </td>

                                                {/* Percentile Column */}
                                                <td className="py-4 text-center">
                                                    <div className="flex items-center justify-center gap-1">
                                                        <div className="w-16 h-2 bg-slate-800 rounded-full overflow-hidden">
                                                            <div
                                                                className="h-full bg-gradient-to-r from-indigo-500 to-purple-500"
                                                                style={{ width: `${broker.percentile}%` }}
                                                            ></div>
                                                        </div>
                                                        <span className="text-xs font-black text-indigo-400">
                                                            {broker.percentile.toFixed(0)}Â°
                                                        </span>
                                                    </div>
                                                </td>

                                                {/* Meta Personal Column */}
                                                <td className="py-4 text-center">
                                                    {personalGoal > 0 ? (
                                                        <div className="flex flex-col items-center gap-1">
                                                            <span className="text-sm font-black text-pink-400">{personalGoal}</span>
                                                            {broker.faltante > 0 && (
                                                                <span className="text-[9px] text-slate-500">
                                                                    -{broker.faltante}
                                                                </span>
                                                            )}
                                                        </div>
                                                    ) : (
                                                        <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded-lg bg-amber-500/20 text-amber-400 border border-amber-500/30 text-\[10px\] font-bold uppercase"><AlertTriangle size={12} /> Sin meta</span>
                                                    )}
                                                </td>

                                                <td className="py-4 text-center">
                                                    <span className={`text-[10px] font-bold uppercase px-2 py-1 rounded-md border ${getActionBadge(broker.action)}`}>
                                                        {broker.action}
                                                    </span>
                                                </td>

                                                {/* WhatsApp Column */}
                                                <td className="py-4 text-center">
                                                    {broker.telefono ? (
                                                        <a
                                                            href={`https://wa.me/56${broker.telefono.replace(/[^0-9]/g, '')}`}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-xs font-bold hover:bg-emerald-500/30 transition-colors"
                                                        >
                                                            <MessageSquare size={14} />
                                                            WhatsApp
                                                        </a>
                                                    ) : (
                                                        <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded-lg bg-slate-500/20 text-slate-400 border border-slate-500/30 text-[10px] font-bold uppercase">
                                                            <AlertTriangle size={12} />
                                                            Sin tel
                                                        </span>
                                                    )}
                                                </td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>

                        {filteredBrokers.length === 0 && (
                            <div className="text-center py-12">
                                <Search size={48} className="mx-auto text-slate-600 mb-4" />
                                <p className="text-slate-500 font-bold">No se encontraron corredores con los filtros actuales</p>
                            </div>
                        )}
                    </section>
                </div>

                {/* Columna Derecha: Resumen & Stats */}
                <div className="lg:col-span-3 space-y-6">

                    {/* Desglose de Pilares */}
                    <section className="bg-slate-900/50 rounded-3xl p-6 border border-slate-800 shadow-2xl">
                        <h3 className="text-sm font-bold text-white uppercase tracking-widest mb-6 flex items-center gap-2">
                            <Target size={16} className="text-amber-400" /> Pilares de Scoring
                        </h3>

                        <div className="space-y-4">
                            {/* Pilar 1: Engagement */}
                            <div className="p-4 bg-slate-800/50 rounded-xl border border-emerald-500/20">
                                <div className="flex items-center justify-between mb-2">
                                    <div className="flex items-center gap-2">
                                        <div className="w-3 h-3 rounded-full bg-emerald-500"></div>
                                        <span className="text-[10px] font-bold text-slate-400 uppercase">Engagement</span>
                                    </div>
                                    <span className="text-[10px] font-bold text-emerald-400">35%</span>
                                </div>
                                <div className="flex items-center justify-between">
                                    <span className="text-xs text-slate-500">Top: {intelligenceData?.brokers?.[0]?.score_engagement?.toFixed(1) || 0}</span>
                                    <span className="text-xs text-emerald-400 font-black">
                                        {(intelligenceData?.brokers?.reduce((max, b) => Math.max(max, b.score_engagement), 0) ?? 0).toFixed(1)}
                                    </span>
                                </div>
                            </div>

                            {/* Pilar 2: Rendimiento */}
                            <div className="p-4 bg-slate-800/50 rounded-xl border border-blue-500/20">
                                <div className="flex items-center justify-between mb-2">
                                    <div className="flex items-center gap-2">
                                        <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                                        <span className="text-[10px] font-bold text-slate-400 uppercase">Rendimiento</span>
                                    </div>
                                    <span className="text-[10px] font-bold text-blue-400">40%</span>
                                </div>
                                <div className="flex items-center justify-between">
                                    <span className="text-xs text-slate-500">Top: {intelligenceData?.brokers?.[0]?.score_rendimiento?.toFixed(1) || 0}</span>
                                    <span className="text-xs text-blue-400 font-black">
                                        {(intelligenceData?.brokers?.reduce((max, b) => Math.max(max, b.score_rendimiento), 0) ?? 0).toFixed(1)}
                                    </span>
                                </div>
                            </div>

                            {/* Pilar 3: Eficiencia */}
                            <div className="p-4 bg-slate-800/50 rounded-xl border border-purple-500/20">
                                <div className="flex items-center justify-between mb-2">
                                    <div className="flex items-center gap-2">
                                        <div className="w-3 h-3 rounded-full bg-purple-500"></div>
                                        <span className="text-[10px] font-bold text-slate-400 uppercase">Eficiencia</span>
                                    </div>
                                    <span className="text-[10px] font-bold text-purple-400">25%</span>
                                </div>
                                <div className="flex items-center justify-between">
                                    <span className="text-xs text-slate-500">Top: {intelligenceData?.brokers?.[0]?.score_eficiencia?.toFixed(1) || 0}</span>
                                    <span className="text-xs text-purple-400 font-black">
                                        {(intelligenceData?.brokers?.reduce((max, b) => Math.max(max, b.score_eficiencia), 0) ?? 0).toFixed(1)}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </section>

                    {/* Resumen del Equipo */}
                    <section className="bg-slate-900/50 rounded-3xl p-6 border border-slate-800 shadow-2xl">
                        <h3 className="text-sm font-bold text-white uppercase tracking-widest mb-6 flex items-center gap-2">
                            <BarChart3 size={16} className="text-indigo-400" /> Resumen del Squad
                        </h3>

                        <div className="space-y-4">
                            <div className="p-4 bg-slate-800/50 rounded-xl border border-slate-700">
                                <div className="flex items-center justify-between mb-2">
                                    <span className="text-[10px] font-bold text-slate-500 uppercase">Meta Equipo</span>
                                    <Target size={14} className="text-emerald-400" />
                                </div>
                                <p className="text-2xl font-black text-emerald-400">
                                    {intelligenceData?.squad_summary?.meta_equipo || 0}
                                </p>
                            </div>

                            <div className="p-4 bg-slate-800/50 rounded-xl border border-slate-700">
                                <div className="flex items-center justify-between mb-2">
                                    <span className="text-[10px] font-bold text-slate-500 uppercase">Contratos Actuales</span>
                                    <Award size={14} className="text-blue-400" />
                                </div>
                                <p className="text-2xl font-black text-blue-400">
                                    {intelligenceData?.squad_summary?.contratos_actuales || 0}
                                </p>
                            </div>

                            <div className="p-4 bg-slate-800/50 rounded-xl border border-slate-700">
                                <div className="flex items-center justify-between mb-2">
                                    <span className="text-[10px] font-bold text-slate-500 uppercase">Faltante</span>
                                    <TrendingDown size={14} className="text-orange-400" />
                                </div>
                                <p className="text-2xl font-black text-orange-400">
                                    {intelligenceData?.squad_summary?.faltante_equipo || 0}
                                </p>
                            </div>

                            <div className="p-4 bg-slate-800/50 rounded-xl border border-slate-700">
                                <div className="flex items-center justify-between mb-2">
                                    <span className="text-[10px] font-bold text-slate-500 uppercase">Días Restantes</span>
                                    <Activity size={14} className="text-purple-400" />
                                </div>
                                <p className="text-2xl font-black text-purple-400">
                                    {intelligenceData?.squad_summary?.dias_restantes || 0}
                                </p>
                            </div>
                        </div>
                    </section>

                    {/* Distribución por Región */}
                    <section className="bg-slate-900/50 rounded-3xl p-6 border border-slate-800 shadow-2xl">
                        <h3 className="text-sm font-bold text-white uppercase tracking-widest mb-6 flex items-center gap-2">
                            <PieChart size={16} className="text-blue-400" /> Distribución
                        </h3>

                        <div className="space-y-4">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                                    <span className="text-xs font-bold text-slate-400">RM</span>
                                </div>
                                <span className="text-lg font-black text-white">
                                    {intelligenceData?.squad_summary?.total_brokers_rm || 0}
                                </span>
                            </div>

                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <div className="w-3 h-3 rounded-full bg-orange-500"></div>
                                    <span className="text-xs font-bold text-slate-400">Regiones</span>
                                </div>
                                <span className="text-lg font-black text-white">
                                    {intelligenceData?.squad_summary?.total_brokers_regiones || 0}
                                </span>
                            </div>

                            <div className="pt-4 border-t border-slate-800">
                                <div className="text-center">
                                    <span className="text-[10px] font-bold text-slate-500 uppercase">Total Corredores</span>
                                    <p className="text-3xl font-black text-white mt-1">
                                        {(intelligenceData?.squad_summary?.total_brokers_rm || 0) +
                                            (intelligenceData?.squad_summary?.total_brokers_regiones || 0)}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </section>

                    {/* Alertas de Eficiencia */}
                    {efficiencyAlerts.leadsSinGestion > 0 || efficiencyAlerts.unidadesSinVisitas > 0 ? (
                        <section className="bg-red-500/10 rounded-3xl p-6 border border-red-500/30 shadow-2xl">
                            <h3 className="text-sm font-bold text-red-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                                <AlertTriangle size={16} /> Alertas
                            </h3>

                            <div className="space-y-3">
                                {efficiencyAlerts.leadsSinGestion > 0 && (
                                    <div className="p-3 bg-red-500/20 rounded-lg border border-red-500/30">
                                        <p className="text-[10px] font-bold text-red-400 uppercase mb-1">Leads sin Gestión</p>
                                        <p className="text-xl font-black text-white">{efficiencyAlerts.leadsSinGestion}</p>
                                    </div>
                                )}

                                {efficiencyAlerts.unidadesSinVisitas > 0 && (
                                    <div className="p-3 bg-red-500/20 rounded-lg border border-red-500/30">
                                        <p className="text-[10px] font-bold text-red-400 uppercase mb-1">Unidades sin Visitas</p>
                                        <p className="text-xl font-black text-white">{efficiencyAlerts.unidadesSinVisitas}</p>
                                    </div>
                                )}
                            </div>
                        </section>
                    ) : null}
                </div>
            </div>
        </div>
    );
};

export default StrategicLab;

