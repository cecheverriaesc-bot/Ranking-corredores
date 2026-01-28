import React, { useState, useMemo, useEffect, useCallback } from 'react';
import {
    Search, TrendingUp, TrendingDown, Users, Microscope, UserMinus, BatteryMedium, Zap,
    Flame, CalendarCheck, Medal, Crown, Droplet, GraduationCap, Flower2, Star, Target,
    Scale, Clock, Briefcase, Filter, ArrowRight, Calendar, RefreshCw
} from 'lucide-react';
import { HISTORY_2025, NAMES_WITH_AGENDA, TEAMS, MONTHLY_GOAL, DAILY_GOALS } from './constants';
import { SquadStats, DashboardStats, CorredorData, DailyStat } from './types';

const IconMap: Record<string, React.FC<any>> = {
    Flame, Droplet, GraduationCap, Flower2, Star
};

const App: React.FC = () => {
    const [searchTerm, setSearchTerm] = useState('');
    const [rankingData, setRankingData] = useState<CorredorData[]>([]);
    const [othersData, setOthersData] = useState<CorredorData[]>([]);
    const [dailyStatsData, setDailyStatsData] = useState<DailyStat[]>([]);
    const [lastUpdate, setLastUpdate] = useState('');
    const [isLoading, setIsLoading] = useState(true);
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [total2025YTD, setTotal2025YTD] = useState(0);

    const fetchData = useCallback(async (isSilent = false) => {
        if (!isSilent) setIsLoading(true);
        else setIsRefreshing(true);

        try {
            const response = await fetch('/api/v2_ranking');
            if (!response.ok) throw new Error('API Error');
            const data = await response.json();

            setRankingData(data.ranking);
            setOthersData(data.others);
            setDailyStatsData(data.daily_stats);
            setLastUpdate(data.last_update);
            setTotal2025YTD(data.total_2025_ytd || 0);
        } catch (error) {
            console.error("Error fetching data:", error);
            // Fallback would go here if needed
        } finally {
            setIsLoading(false);
            setIsRefreshing(false);
        }
    }, []);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    const daysRemaining = useMemo(() => {
        const today = new Date();
        const lastDayOfMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0);
        return Math.max(0, lastDayOfMonth.getDate() - today.getDate());
    }, []);

    const stats: DashboardStats = useMemo(() => {
        let totalActual = 0;
        let total2025Today = total2025YTD; // Use dynamic value from API
        let globalQualified = 0;
        const squadStats: Record<string, SquadStats> = {};

        Object.keys(TEAMS).forEach(id => {
            squadStats[id] = { cur: 0, past: 0, qual: 0, others: 0, totalMembers: 0, activeMembers: 0, totalLeads: 0, totalAgendas: 0 };
        });

        const historyMap = HISTORY_2025;
        // Total 2025 calculation removed from here as it's now fetched from API

        [...rankingData, ...othersData].forEach(item => {
            totalActual += item.val;
            const hist = historyMap[item.name]?.c || 0;
            const isExternal = othersData.some(e => e.name === item.name);
            const isFreelance = !isExternal;

            if (isFreelance && item.val >= 7) globalQualified++;

            if (squadStats[item.coord]) {
                squadStats[item.coord].cur += item.val;
                squadStats[item.coord].past += hist;
                if (isFreelance) {
                    squadStats[item.coord].totalMembers += 1;
                    if (item.val > 0) squadStats[item.coord].activeMembers += 1;
                    if (item.val >= 7) squadStats[item.coord].qual++;
                    squadStats[item.coord].totalLeads += (item.leads || 0);
                    squadStats[item.coord].totalAgendas += (item.agendas || 0);
                } else {
                    squadStats[item.coord].others += item.val;
                }
            }
        });

        const todayDay = new Date().getDate();
        let accMetaToToday = 0;
        let accRealToToday = 0;

        dailyStatsData.forEach(s => {
            const dayNum = parseInt(s.date.split('-')[2]);
            if (dayNum <= todayDay) accRealToToday += s.count;
        });

        for (let d = 1; d <= todayDay; d++) {
            accMetaToToday += DAILY_GOALS[d] || 0;
        }

        return {
            totalActual, total2025Today, globalQualified, squadStats,
            accMetaToToday, accRealToToday,
            diagnostics: { loss: [], lossVolume: 0, slowdown: [], slowdownVolume: 0, growth: [], growthVolume: 0 }
        };
    }, [rankingData, othersData, dailyStatsData]);

    const filteredData = useMemo(() => {
        return rankingData.filter(item =>
            !item.hidden && item.name.toLowerCase().includes(searchTerm.toLowerCase())
        );
    }, [searchTerm, rankingData]);

    const top3 = useMemo(() => {
        const sorted = [...rankingData]
            .filter(i => !i.hidden)
            .sort((a, b) => b.val - a.val);
        return [sorted[0], sorted[1], sorted[2]].filter(Boolean);
    }, [rankingData]);

    const getStatusBadge = (val: number) => {
        if (val >= 8) return <span className="bg-emerald-500/20 text-emerald-400 px-3 py-1 rounded-full font-bold text-[9px] uppercase border border-emerald-500/50">Clasificado</span>;
        if (val === 7) return <span className="bg-emerald-500 text-white px-3 py-1 rounded-full font-black text-[9px] uppercase shadow-[0_0_10px_rgba(16,185,129,0.5)]">Calificado</span>;
        if (val === 6) return <span className="bg-blue-500/20 text-blue-400 px-3 py-1 rounded-full font-bold text-[9px] uppercase border border-blue-500/50">Próximo</span>;
        if (val === 5) return <span className="bg-yellow-500/20 text-yellow-400 px-3 py-1 rounded-full font-bold text-[9px] uppercase border border-yellow-500/50">Límite</span>;
        if (val > 0) return <span className="bg-red-500/20 text-red-400 px-3 py-1 rounded-full font-bold text-[9px] uppercase border border-red-500/50">Riesgo</span>;
        return <span className="bg-slate-800 text-slate-500 px-3 py-1 rounded-full font-bold text-[9px] uppercase border border-slate-700">Sin prod.</span>;
    };

    const trendDiff = stats.totalActual - stats.total2025Today;
    const progressPercentage = Math.min((stats.totalActual / MONTHLY_GOAL) * 100, 100);

    return (
        <div className="min-h-screen bg-[#101622] text-slate-200 font-sans pb-20 selection:bg-assetplan-accent selection:text-white">
            {/* Loading Overlay */}
            {isLoading && (
                <div className="fixed inset-0 z-[100] bg-[#101622]/80 backdrop-blur-md flex flex-col items-center justify-center">
                    <div className="w-16 h-16 border-4 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin mb-4"></div>
                    <p className="text-indigo-400 font-black uppercase tracking-widest text-xs animate-pulse">Sincronizando Real-Time...</p>
                </div>
            )}

            {/* Header */}
            <header className="relative pt-10 pb-20 px-6 overflow-hidden">
                <div className="absolute top-[-20%] left-[-10%] w-[500px] h-[500px] bg-blue-600/20 rounded-full blur-[120px] pointer-events-none"></div>
                <div className="absolute top-[-20%] right-[-10%] w-[500px] h-[500px] bg-indigo-600/10 rounded-full blur-[120px] pointer-events-none"></div>

                <div className="container mx-auto relative z-10 flex flex-col lg:flex-row justify-between items-end gap-8 border-b border-[#324467] pb-10">
                    <div className="w-full lg:w-auto">
                        <div className="flex items-center gap-4 mb-6">
                            <img src="/logo_white.png" alt="Assetplan" className="h-36 w-auto opacity-90" />
                            <div className="h-10 w-px bg-[#324467]"></div>
                            <div>
                                <h2 className="text-white font-black uppercase text-sm tracking-widest leading-none">Home Operativo</h2>
                                <h3 className="text-blue-400 font-bold uppercase text-[10px] tracking-widest">Ranking Enero 2026</h3>
                            </div>
                        </div>

                        <div className="flex items-end gap-x-12 gap-y-6 flex-wrap">
                            <div>
                                <p className="text-[#64748b] text-[10px] font-bold uppercase tracking-widest mb-2">Producción Consolidada</p>
                                <div className="flex items-baseline gap-3">
                                    <span className="text-7xl font-black text-white tracking-tighter">{stats.totalActual}</span>
                                    <div className="text-right">
                                        <p className="text-sm font-bold text-blue-400">/ {MONTHLY_GOAL} Meta</p>
                                        <div className={`text-xs font-bold flex items-center gap-1 ${trendDiff >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                                            {trendDiff > 0 ? '+' : ''}{trendDiff} vs 2025
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="flex-1 min-w-[200px]">
                                <div className="flex justify-between text-[10px] uppercase font-bold text-blue-300 mb-2">
                                    <span>Progreso Mensual</span>
                                    <span>{progressPercentage.toFixed(1)}%</span>
                                </div>
                                <div className="h-2 w-full bg-[#1e293b] rounded-full overflow-hidden border border-[#324467]">
                                    <div
                                        className="h-full bg-gradient-to-r from-blue-600 to-emerald-400 relative"
                                        style={{ width: `${progressPercentage}%` }}
                                    >
                                        <div className="absolute inset-0 bg-white/30 animate-[shimmer_2s_infinite]"></div>
                                    </div>
                                </div>
                                <p className="text-[10px] text-slate-500 mt-2 font-medium flex items-center gap-1">
                                    <Clock size={10} /> Quedan {daysRemaining} días de gestión
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="flex flex-col items-end gap-3">
                        <span className="text-blue-200/50 text-[10px] font-bold uppercase tracking-widest italic transition-colors">Líder: Carlos Echeverría</span>
                        <div className="flex items-center gap-3">
                            <div className="flex items-center gap-3 text-slate-500 bg-[#1e293b]/50 px-4 py-2.5 rounded-2xl border border-[#324467]">
                                <Clock size={12} className="text-emerald-500/50" />
                                <p className="text-[10px] font-bold uppercase tracking-wider">
                                    <span className="text-slate-600 text-[8px]">Última Reserva Tomada:</span> <br />
                                    <span className="text-emerald-500/80 text-xs">{lastUpdate || '---'}</span>
                                </p>
                            </div>
                            <button
                                onClick={() => fetchData(true)}
                                disabled={isRefreshing}
                                className={`p-3.5 rounded-2xl border border-indigo-500/30 bg-indigo-500/10 text-indigo-400 hover:bg-indigo-500/20 hover:border-indigo-500/50 transition-all ${isRefreshing ? 'opacity-50 cursor-not-allowed shadow-none' : 'cursor-pointer active:scale-90 shadow-lg shadow-indigo-500/10 active:shadow-none'}`}
                                title="Refrescar datos en tiempo real (Base de Datos)"
                            >
                                <RefreshCw size={18} className={isRefreshing ? 'animate-spin' : ''} />
                            </button>
                        </div>
                    </div>
                </div>
            </header>

            <main className="container mx-auto px-4 -mt-6 relative z-20">
                {/* Real-time indicator for the table if needed */}
                <nav className="flex justify-center gap-4 mb-10 sticky top-6 z-50">
                    <div className="bg-[#1e293b]/80 backdrop-blur-md border border-[#324467] rounded-2xl p-2 shadow-2xl flex gap-2">
                        <a href="#ranking" className="px-6 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest text-slate-400 hover:text-white hover:bg-white/5 transition-all flex items-center gap-2">
                            <Medal size={14} className="text-yellow-500" /> Ranking
                        </a>
                        <div className="w-px h-6 bg-[#324467] self-center"></div>
                        <a href="#squads" className="px-6 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest text-slate-400 hover:text-white hover:bg-white/5 transition-all flex items-center gap-2">
                            <Users size={14} className="text-blue-500" /> Squads
                        </a>
                        <div className="w-px h-6 bg-[#324467] self-center"></div>
                        <a href="#grafico" className="px-6 py-2 rounded-xl text-[10px] font-black uppercase tracking-widest text-slate-400 hover:text-white hover:bg-white/5 transition-all flex items-center gap-2">
                            <TrendingUp size={14} className="text-indigo-500" /> Evolución
                        </a>
                    </div>
                </nav>

                {/* Podium Section */}
                <div id="ranking" className="scroll-mt-32">
                    {!searchTerm && top3.length >= 3 && (
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16 items-end max-w-5xl mx-auto">
                            <div className="order-2 md:order-1 relative group">
                                <div className="text-center mb-4"><span className="text-slate-400 font-bold text-xs uppercase tracking-widest">2° Lugar</span></div>
                                <div className="bg-[#1e293b] p-6 rounded-3xl border border-[#324467] text-center shadow-xl relative overflow-hidden group-hover:border-slate-400/50 transition-colors">
                                    <div className="absolute top-0 left-0 w-full h-1 bg-slate-400"></div>
                                    <h3 className="font-bold text-slate-200 truncate">{top3[1].name}</h3>
                                    <div className="mt-4 text-4xl font-black text-white">{top3[1].val}</div>
                                    <p className="text-[10px] text-slate-500 uppercase font-bold mt-1">Reservas</p>
                                </div>
                            </div>

                            <div className="order-1 md:order-2 scale-110 relative z-10 group">
                                <div className="absolute inset-0 bg-yellow-500/20 blur-[60px] rounded-full -z-10 opacity-50 group-hover:opacity-80 transition-opacity"></div>
                                <div className="flex justify-center mb-4"><Crown size={32} className="text-yellow-400 fill-yellow-400 animate-pulse" /></div>
                                <div className="bg-[#1e293b] p-8 rounded-3xl border border-yellow-500/50 text-center shadow-2xl relative overflow-hidden bg-gradient-to-b from-[#1e293b] to-[#162032]">
                                    <div className="absolute top-0 left-0 w-full h-1 bg-yellow-400"></div>
                                    <h3 className="text-lg font-black text-white truncate">{top3[0].name}</h3>
                                    {NAMES_WITH_AGENDA.includes(top3[0].name) && (
                                        <span className="inline-flex items-center gap-1 bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded text-[9px] font-bold uppercase mt-2 border border-blue-500/30">
                                            <Calendar size={10} /> Agenda Activa
                                        </span>
                                    )}
                                    <div className="mt-6 text-6xl font-black text-white tracking-tighter drop-shadow-[0_0_15px_rgba(250,204,21,0.3)]">{top3[0].val}</div>
                                    <p className="text-xs text-yellow-500 uppercase font-bold mt-2 tracking-widest">Reservas</p>
                                    <div className="mt-6 grid grid-cols-2 gap-2 border-t border-white/5 pt-4">
                                        <div>
                                            <p className="text-[10px] text-slate-500 uppercase">Leads</p>
                                            <p className="text-white font-bold">{top3[0].leads || 0}</p>
                                        </div>
                                        <div>
                                            <p className="text-[10px] text-slate-500 uppercase">Visitas</p>
                                            <p className="text-white font-bold">{top3[0].agendas || 0}</p>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="order-3 relative group">
                                <div className="text-center mb-4"><span className="text-orange-400/80 font-bold text-xs uppercase tracking-widest">3° Lugar</span></div>
                                <div className="bg-[#1e293b] p-6 rounded-3xl border border-[#324467] text-center shadow-xl relative overflow-hidden group-hover:border-orange-400/50 transition-colors">
                                    <div className="absolute top-0 left-0 w-full h-1 bg-orange-400"></div>
                                    <h3 className="font-bold text-slate-200 truncate">{top3[2].name}</h3>
                                    <div className="mt-4 text-4xl font-black text-white">{top3[2].val}</div>
                                    <p className="text-[10px] text-slate-500 uppercase font-bold mt-1">Reservas</p>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Table Section */}
                    <div className="bg-[#1e293b] rounded-3xl border border-[#324467] overflow-hidden shadow-2xl mb-12">
                        <div className="p-6 border-b border-[#324467] flex flex-col md:flex-row justify-between items-center gap-6">
                            <div className="relative w-full md:w-96">
                                <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
                                <input
                                    type="text"
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                    placeholder="Filtrar por nombre..."
                                    className="w-full bg-[#101622] text-slate-200 pl-12 pr-4 py-3 rounded-xl border border-[#324467] focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-all"
                                />
                            </div>
                            <div className="flex gap-4">
                                <div className="text-right">
                                    <p className="text-[10px] text-slate-500 font-bold uppercase">Corredores Activos</p>
                                    <p className="text-white font-bold text-lg">{rankingData.length}</p>
                                </div>
                                <div className="w-px h-10 bg-[#324467]"></div>
                                <div className="text-right">
                                    <p className="text-[10px] text-slate-500 font-bold uppercase">En Meta (7+)</p>
                                    <p className="text-emerald-400 font-bold text-lg">{stats.globalQualified}</p>
                                </div>
                            </div>
                        </div>
                        <div className="overflow-x-auto">
                            <table className="w-full text-left">
                                <thead className="bg-[#162032] text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                                    <tr>
                                        <th className="px-6 py-4 text-center w-16">#</th>
                                        <th className="px-6 py-4">Corredor</th>
                                        <th className="px-6 py-4 text-center text-blue-400">Leads</th>
                                        <th className="px-6 py-4 text-center text-purple-400">Agendas</th>
                                        <th className="px-6 py-4 text-center text-white bg-[#324467]/20 border-x border-[#324467]">Reservas</th>
                                        <th className="px-6 py-4 text-center">Vs 2025</th>
                                        <th className="px-6 py-4 text-center">Estado</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-[#324467] text-sm">
                                    {filteredData.map((item, index) => {
                                        const rank = index + 1;
                                        const history = HISTORY_2025[item.name];
                                        const diff = history ? item.val - history.c : item.val;
                                        const team = TEAMS[item.coord];
                                        const TeamIcon = team ? IconMap[team.icon as keyof typeof IconMap] : null;

                                        return (
                                            <tr key={item.name} className="group hover:bg-[#324467]/20 transition-colors">
                                                <td className="px-6 py-4 text-center font-mono text-slate-500 group-hover:text-white">{rank}</td>
                                                <td className="px-6 py-4">
                                                    <div className="flex items-center gap-3">
                                                        {TeamIcon && (
                                                            <div className={`p-1.5 rounded-lg bg-[#101622] border border-[#324467] ${team.color}`}>
                                                                <TeamIcon size={14} />
                                                            </div>
                                                        )}
                                                        <div>
                                                            <div className="font-bold text-slate-200 group-hover:text-white">{item.name}</div>
                                                            {NAMES_WITH_AGENDA.includes(item.name) && (
                                                                <div className="text-[9px] text-blue-400 flex items-center gap-1 mt-0.5 font-bold uppercase tracking-wide">
                                                                    <Calendar size={8} /> Agenda Activa
                                                                </div>
                                                            )}
                                                        </div>
                                                    </div>
                                                </td>
                                                <td className="px-6 py-4 text-center font-bold text-slate-300">{item.leads || 0}</td>
                                                <td className="px-6 py-4 text-center font-bold text-slate-300">{item.agendas || 0}</td>
                                                <td className="px-6 py-4 text-center bg-[#324467]/10 border-x border-[#324467] relative">
                                                    <span className="text-lg font-black text-white">{item.val}</span>
                                                    {item.fallen > 0 && <span className="absolute bottom-2 left-0 w-full text-[9px] font-bold text-red-400 opacity-60">-{item.fallen} caídas</span>}
                                                </td>
                                                <td className="px-6 py-4 text-center">
                                                    <div className={`inline-flex items-center gap-1 font-bold ${diff > 0 ? 'text-emerald-400' : diff < 0 ? 'text-red-400' : 'text-slate-500'}`}>
                                                        {diff > 0 ? '+' : ''}{diff}
                                                    </div>
                                                    {history && <div className="text-[9px] text-slate-500 mt-0.5">({history.t} en 2025)</div>}
                                                </td>
                                                <td className="px-6 py-4 text-center">{getStatusBadge(item.val)}</td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                {/* Squads Rendering */}
                <div id="squads" className="scroll-mt-32">
                    <h3 className="text-xl font-bold text-white uppercase tracking-widest mb-6 flex items-center gap-3">
                        <Users size={20} className="text-blue-500" />
                        Rendimiento por Squad
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
                        {Object.entries(stats.squadStats).map(([email, data]) => {
                            const team = TEAMS[email];
                            if (!team || (data.cur === 0 && data.totalMembers === 0 && !team.my)) return null;
                            const TeamIcon = IconMap[team.icon as keyof typeof IconMap];
                            return (
                                <div key={email} className={`bg-[#1e293b] rounded-2xl p-6 border border-[#324467] hover:border-blue-500/50 transition-colors ${team.my ? 'ring-1 ring-orange-500/50' : ''}`}>
                                    <div className="flex justify-between items-start mb-6">
                                        <div className={`p-3 rounded-xl bg-[#101622] border border-[#324467] ${team.color}`}>{TeamIcon && <TeamIcon size={20} />}</div>
                                        <div className="text-right">
                                            <p className="text-3xl font-black text-white">{data.cur}</p>
                                            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Reservas</p>
                                        </div>
                                    </div>
                                    <div className="space-y-3">
                                        <div className="flex justify-between items-center text-xs">
                                            <span className="text-slate-400 font-medium">Leads Asignados</span>
                                            <span className="text-white font-bold">{data.totalLeads}</span>
                                        </div>
                                        <div className="w-full bg-[#101622] rounded-full h-1.5 overflow-hidden">
                                            <div className="bg-slate-700 h-full rounded-full" style={{ width: `${Math.min((data.cur / (data.totalLeads || 1)) * 100 * 10, 100)}%` }}></div>
                                        </div>
                                        <div className="flex justify-between items-center text-xs pt-2 border-t border-[#324467]">
                                            <span className="text-slate-400 font-medium">Corredores Activos</span>
                                            <span className="text-emerald-400 font-bold">{data.activeMembers} <span className="text-slate-500">/ {data.totalMembers}</span></span>
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>

                <div id="grafico" className="scroll-mt-32">
                    <h3 className="text-xl font-bold text-white uppercase tracking-widest mb-6 flex items-center gap-3">
                        <TrendingUp size={20} className="text-indigo-500" />
                        Evolución Diaria de Reservas
                    </h3>
                    <div className="bg-[#1e293b] p-8 rounded-[2rem] border border-[#324467] mb-20 shadow-2xl">
                        {/* Goal KPI Header */}
                        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-10 pb-8 border-b border-[#324467]/50">
                            <div className="bg-[#101622] p-4 rounded-2xl border border-[#324467]">
                                <p className="text-[10px] text-slate-500 font-bold uppercase mb-1">Meta Acumulada a Hoy</p>
                                <p className="text-2xl font-black text-white">{stats.accMetaToToday.toFixed(0)}</p>
                            </div>
                            <div className="bg-[#101622] p-4 rounded-2xl border border-[#324467]">
                                <p className="text-[10px] text-slate-500 font-bold uppercase mb-1">Real Acumulado a Hoy</p>
                                <p className="text-2xl font-black text-blue-400">{stats.accRealToToday}</p>
                            </div>
                            <div className="bg-[#101622] p-4 rounded-2xl border border-[#324467]">
                                <p className="text-[10px] text-slate-500 font-bold uppercase mb-1">Brecha (Gap)</p>
                                <p className={`text-2xl font-black ${stats.accRealToToday >= stats.accMetaToToday ? 'text-emerald-400' : 'text-red-400'}`}>
                                    {stats.accRealToToday >= stats.accMetaToToday ? '+' : ''}{(stats.accRealToToday - stats.accMetaToToday).toFixed(0)}
                                </p>
                            </div>
                            <div className="bg-[#101622] p-4 rounded-2xl border border-[#324467]">
                                <p className="text-[10px] text-slate-500 font-bold uppercase mb-1">% Cumplimiento Mensual</p>
                                <p className="text-2xl font-black text-white">
                                    {((stats.accRealToToday / (stats.accMetaToToday || 1)) * 100).toFixed(1)}%
                                </p>
                            </div>
                        </div>

                        <div className="overflow-x-auto overflow-y-visible">
                            <div className="min-w-[900px] h-[400px] flex items-end gap-3 relative px-10 pb-10 pt-20">
                                {/* Bars Generation */}
                                {(() => {
                                    const daysMap = new Map<string, Record<string, number>>();
                                    const dates = Array.from({ length: 31 }, (_, i) => `2026-01-${(i + 1).toString().padStart(2, '0')}`);
                                    dailyStatsData.forEach(stat => {
                                        const key = stat.date;
                                        if (!daysMap.has(key)) daysMap.set(key, {});
                                        const entry = daysMap.get(key)!;
                                        entry[stat.coord] = (entry[stat.coord] || 0) + stat.count;
                                    });
                                    let maxVal = 0;
                                    dates.forEach(date => {
                                        const dayNum = parseInt(date.split('-')[2]);
                                        const total = Object.values(daysMap.get(date) || {}).reduce((a, b) => a + b, 0);
                                        const goal = DAILY_GOALS[dayNum] || 0;
                                        maxVal = Math.max(maxVal, total, goal);
                                    });
                                    if (maxVal === 0) maxVal = 10;
                                    return dates.map((date, index) => {
                                        const dayNum = index + 1;
                                        const dayData = daysMap.get(date) || {};
                                        const total = Object.values(dayData).reduce((a, b) => a + b, 0);
                                        const goal = DAILY_GOALS[dayNum] || 0;

                                        const heightPct = (total / maxVal) * 100;
                                        const goalPosPct = (goal / maxVal) * 100;

                                        return (
                                            <div key={date} className="h-full flex-1 flex flex-col justify-end group relative">
                                                {/* Total Label - Permanent */}
                                                {total > 0 && (
                                                    <div className="text-[10px] font-black text-blue-300 text-center mb-1 group-hover:text-white transition-colors">
                                                        {total}
                                                    </div>
                                                )}
                                                {/* Bar Container */}
                                                <div className="w-full flex flex-col-reverse rounded-t-lg overflow-hidden relative shadow-lg" style={{ height: `${heightPct}%` }}>
                                                    {Object.entries(dayData).map(([coord, count]) => {
                                                        const team = TEAMS[coord];
                                                        if (!team) return null;
                                                        const segmentHeight = (count / total) * 100;
                                                        const segmentColor = team.bg.replace('bg-', 'bg-').split(' ')[0].replace('-50', '-500');
                                                        return (
                                                            <div key={coord} style={{ height: `${segmentHeight}%` }} className={`${segmentColor} w-full border-t border-black/10`}></div>
                                                        );
                                                    })}
                                                </div>

                                                {/* Tooltip - Moved outside overflow-hidden bar container */}
                                                <div className="opacity-0 group-hover:opacity-100 absolute -top-28 left-1/2 -translate-x-1/2 bg-[#162032] text-white text-[10px] font-bold px-4 py-3 rounded-xl border border-[#324467] shadow-[0_0_30px_rgba(0,0,0,0.8)] z-[100] pointer-events-none transition-all scale-90 group-hover:scale-100 min-w-[160px]">
                                                    <p className="text-white text-[11px] border-b border-[#324467]/50 pb-2 mb-2 font-black tracking-widest uppercase">Enero {dayNum}</p>
                                                    <div className="space-y-2">
                                                        <div className="flex justify-between gap-4"><span className="text-slate-500">Reserva Real:</span> <span className="text-white text-sm font-black">{total}</span></div>
                                                        <div className="flex justify-between gap-4"><span className="text-slate-500">Meta Diaria:</span> <span className="text-blue-400 font-bold">{goal.toFixed(1)}</span></div>
                                                        <div className="flex justify-between gap-4 border-t border-[#324467]/50 pt-2 mt-1 font-black">
                                                            <span className="text-slate-500">Diferencia:</span>
                                                            <span className={total >= goal ? 'text-emerald-400' : 'text-red-400'}>
                                                                {total >= goal ? '+' : ''}{(total - goal).toFixed(1)}
                                                            </span>
                                                        </div>
                                                        <div className="flex justify-between gap-4">
                                                            <span className="text-slate-500">Logro:</span>
                                                            <span className={total >= goal ? 'text-emerald-400' : 'text-blue-300'}>
                                                                {((total / (goal || 1)) * 100).toFixed(1)}%
                                                            </span>
                                                        </div>
                                                    </div>
                                                    {/* Arrow */}
                                                    <div className="absolute -bottom-1.5 left-1/2 -translate-x-1/2 w-3 h-3 bg-[#162032] border-r border-b border-[#324467] rotate-45"></div>
                                                </div>
                                                {/* Goal Line */}
                                                <div
                                                    className="absolute left-0 right-0 h-px bg-white/40 border-t border-dashed border-white/20 z-10 pointer-events-none"
                                                    style={{ bottom: `calc(${goalPosPct}% + 1.5rem)` }}
                                                ></div>
                                                <div className="text-[10px] text-slate-500 font-black text-center mt-3 group-hover:text-white transition-colors">{index + 1}</div>
                                            </div>
                                        );
                                    });
                                })()}
                            </div>
                        </div>
                        {/* Legend */}
                        <div className="flex flex-wrap justify-center gap-6 mt-4 border-t border-[#324467] pt-4">
                            <div className="flex items-center gap-2 text-slate-400 font-bold uppercase text-[9px]">
                                <div className="w-6 h-px bg-white/40 border-t border-dashed border-white/20"></div>
                                <span>Meta Diaria (Histórico)</span>
                            </div>
                            {Object.values(TEAMS).map(team => (
                                <div key={team.name} className="flex items-center gap-2">
                                    <div className={`w-3 h-3 rounded-full ${team.bg.replace('bg-', 'bg-').split(' ')[0].replace('-50', '-500')}`}></div>
                                    <span className="text-[10px] text-slate-400 font-bold uppercase">{team.name}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div >
            </main >
        </div >
    );
};

export default App;