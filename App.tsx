import React, { useState, useMemo } from 'react';
import {
    Search,
    TrendingUp,
    TrendingDown,
    Users,
    Microscope,
    UserMinus,
    BatteryMedium,
    Zap,
    Flame,
    CalendarCheck,
    Medal,
    Crown,
    Droplet,
    GraduationCap,
    Flower2,
    Star,
    Target,
    Scale,
    Clock,
    Briefcase,
    Filter,
    ArrowRight,
    Calendar
} from 'lucide-react';
import { CURRENT_RANKING_2026, HISTORY_2025, NAMES_WITH_AGENDA, TEAMS, MONTHLY_GOAL, OTHER_BROKERS_2026, LAST_UPDATE, DAILY_STATS } from './constants';
import { SquadStats, DiagnosticItem, DashboardStats, CorredorData, DailyStat } from './types';

// Map string icon names to components
const IconMap: Record<string, React.FC<any>> = {
    Flame, Droplet, GraduationCap, Flower2, Star
};

const App: React.FC = () => {
    const [searchTerm, setSearchTerm] = useState('');

    // Calculate days remaining in the current month
    const daysRemaining = useMemo(() => {
        const today = new Date();
        const lastDayOfMonth = new Date(today.getFullYear(), today.getMonth() + 1, 0);
        return Math.max(0, lastDayOfMonth.getDate() - today.getDate());
    }, []);

    // Main Logic Calculation
    const stats: DashboardStats = useMemo(() => {
        let totalActual = 0;
        let total2025Today = 0;
        let globalQualified = 0;
        const squadStats: Record<string, SquadStats> = {};

        // Initialize squads
        Object.keys(TEAMS).forEach(id => {
            squadStats[id] = { cur: 0, past: 0, qual: 0, others: 0, totalMembers: 0, activeMembers: 0, totalLeads: 0, totalAgendas: 0 };
        });

        // Maps for quick lookup
        const currentMap = new Map<string, CorredorData>();
        [...CURRENT_RANKING_2026, ...OTHER_BROKERS_2026].forEach(i => currentMap.set(i.name, i));
        const historyMap = HISTORY_2025;

        // 0. Pre-calculate Total 2025 (Partial) independently to include churned brokers
        Object.values(historyMap).forEach(h => {
            total2025Today += h.c;
        });

        // 1. Calculate Aggregates (Totals & Squads)
        [...CURRENT_RANKING_2026, ...OTHER_BROKERS_2026].forEach(item => {
            totalActual += item.val;
            const hist = historyMap[item.name]?.c || 0;

            const isExternal = OTHER_BROKERS_2026.some(e => e.name === item.name);
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

        return {
            totalActual,
            total2025Today,
            globalQualified,
            squadStats,
            diagnostics: {
                loss: [], lossVolume: 0, slowdown: [], slowdownVolume: 0, growth: [], growthVolume: 0
            }
        };
    }, []);

    const filteredData = useMemo(() => {
        return CURRENT_RANKING_2026.filter(item =>
            !item.hidden && item.name.toLowerCase().includes(searchTerm.toLowerCase())
        );
    }, [searchTerm]);

    const top3 = useMemo(() => {
        const sorted = [...CURRENT_RANKING_2026]
            .filter(i => !i.hidden)
            .sort((a, b) => b.val - a.val);
        return [sorted[0], sorted[1], sorted[2]].filter(Boolean);
    }, []);

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

                    <div className="flex flex-col items-end gap-1">
                        <span className="text-blue-200/50 text-[10px] font-bold uppercase tracking-widest italic group-hover:text-blue-200 transition-colors">Líder: Carlos Echeverría</span>
                        <div className="flex items-center gap-2 text-slate-500">
                            <Clock size={12} className="text-emerald-500/50" />
                            <p className="text-[10px] font-bold uppercase tracking-wider">
                                <span className="text-slate-600">Última reserva:</span> <span className="text-emerald-500/80">{LAST_UPDATE}</span>
                            </p>
                        </div>
                    </div>
                </div>
            </header>

            <main className="container mx-auto px-4 -mt-6 relative z-20">
                {/* Podium Section */}
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
                                <p className="text-white font-bold text-lg">{CURRENT_RANKING_2026.length}</p>
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

                {/* Squads Rendering */}
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

                {/* Stacking Chart */}
                <h3 className="text-xl font-bold text-white uppercase tracking-widest mb-6 flex items-center gap-3">
                    <TrendingUp size={20} className="text-indigo-500" />
                    Evolución Diaria de Reservas
                </h3>
                <div className="bg-[#1e293b] p-8 rounded-[2rem] border border-[#324467] mb-20 shadow-2xl overflow-x-auto min-h-[400px]">
                    <div className="min-w-[900px] h-[300px] flex items-end gap-3 relative px-10 pb-10">
                        {/* Bars Generation */}
                        {(() => {
                            const daysMap = new Map<string, Record<string, number>>();
                            const dates = Array.from({ length: 31 }, (_, i) => `2026-01-${(i + 1).toString().padStart(2, '0')}`);
                            DAILY_STATS.forEach(stat => {
                                const key = stat.date;
                                if (!daysMap.has(key)) daysMap.set(key, {});
                                const entry = daysMap.get(key)!;
                                entry[stat.coord] = (entry[stat.coord] || 0) + stat.count;
                            });
                            let maxVal = 0;
                            dates.forEach(date => {
                                const total = Object.values(daysMap.get(date) || {}).reduce((a, b) => a + b, 0);
                                if (total > maxVal) maxVal = total;
                            });
                            if (maxVal === 0) maxVal = 10;
                            return dates.map((date, index) => {
                                const dayData = daysMap.get(date) || {};
                                const total = Object.values(dayData).reduce((a, b) => a + b, 0);
                                const heightPct = (total / maxVal) * 100;
                                return (
                                    <div key={date} className="h-full flex-1 flex flex-col justify-end group relative">
                                        {/* Total Label - Permanent */}
                                        {total > 0 && (
                                            <div className="text-[10px] font-black text-blue-300 text-center mb-1 group-hover:text-white transition-colors">
                                                {total}
                                            </div>
                                        )}
                                        <div className="w-full flex flex-col-reverse rounded-t-lg overflow-hidden relative shadow-lg" style={{ height: `${heightPct}%` }}>
                                            {Object.entries(dayData).map(([coord, count]) => {
                                                const team = TEAMS[coord];
                                                if (!team) return null;
                                                const segmentHeight = (count / total) * 100;
                                                const segmentColor = team.bg.replace('bg-', 'bg-').split(' ')[0].replace('-50', '-500');
                                                return (
                                                    <div key={coord} style={{ height: `${segmentHeight}%` }} className={`${segmentColor} w-full border-t border-black/10`} title={`${team.name}: ${count}`}></div>
                                                );
                                            })}
                                            <div className="opacity-0 group-hover:opacity-100 absolute -top-12 left-1/2 -translate-x-1/2 bg-[#101622] text-white text-[10px] font-bold px-3 py-2 rounded-xl border border-white/10 shadow-2xl z-50 pointer-events-none transition-all scale-90 group-hover:scale-100">
                                                <p className="text-white text-xs">{total} Reservas</p>
                                                <p className="text-slate-500 font-normal">{date}</p>
                                            </div>
                                        </div>
                                        <div className="text-[10px] text-slate-500 font-black text-center mt-3 group-hover:text-white transition-colors">{index + 1}</div>
                                    </div>
                                );
                            });
                        })()}
                    </div>
                </div>
            </main>
        </div>
    );
};

export default App;