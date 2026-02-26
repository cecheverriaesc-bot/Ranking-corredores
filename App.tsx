
import React, { useState, useMemo, useEffect } from 'react';
import {
    Search, TrendingUp, Users, Microscope, Calendar, Medal, Crown, Droplet,
    GraduationCap, Flower2, Star, Target, Clock, RefreshCw, Brain, Shield,
    UserMinus, BatteryMedium, Zap, Flame, LayoutDashboard, FlaskConical,
    ChevronDown, ChevronUp, AlertCircle, ArrowRight, Filter, Trophy,
    ChevronRight, ArrowUpRight, ArrowDownRight, CheckCircle2, Edit3, MessageSquare,
    Lock, LogOut
} from 'lucide-react';
import { ComposedChart, AreaChart, Area, Line, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { SpeedInsights } from '@vercel/speed-insights/react';
import { MONTHLY_DATA, TEAMS, HISTORY_2025, NAMES_WITH_AGENDA, LAST_DB_UPDATE } from './constants';

import { SquadStats, DashboardStats, CorredorData, DailyStat, MonthData, BrokerGoalData } from './types';
import SquadLaboratory from './components/SquadLaboratory';
import StrategicLab from './components/StrategicLab';
import GoalSettingModal from './components/GoalSettingModal';
import Login from './components/Login';
import BrokerProfile from './components/BrokerProfile';
import { useAppStore, useAuth, useSelectedMonth, useView, useFilteredBrokers, useTopBrokers } from './stores/useAppStore';

const IconMap: Record<string, React.FC<any>> = {
    Flame, Droplet, GraduationCap, Flower2, Star
};

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
    // Get available months from MONTHLY_DATA
    const availableMonths = Object.keys(MONTHLY_DATA).sort();

    // Current year (default to 2026 or first available)
    const currentYear = availableMonths.some(m => m.startsWith('2026')) ? '2026' : availableMonths[0]?.split('-')[0] || '2026';

    // All 12 months for the year
    const allMonths = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'];

    // Find the last available month to determine which are "completed"
    const lastAvailableMonth = availableMonths.length > 0 ? availableMonths[availableMonths.length - 1] : null;
    const lastAvailableMonthNum = lastAvailableMonth ? parseInt(lastAvailableMonth.split('-')[1], 10) : 0;
    const isTotalYear = selected === 'total-year';

    return (
        <div className="flex items-center gap-3">
            {/* Year Label */}
            <div className="flex flex-col items-center">
                <span className="text-2xl font-black text-white tracking-tight">2026</span>
            </div>

            {/* Timeline Container */}
            <div className="flex items-center gap-1 bg-slate-800/30 px-4 py-3 rounded-2xl border border-slate-700/50">
                {allMonths.map((monthNum, index) => {
                    const monthKey = `${currentYear}-${monthNum}`;
                    const monthName = MONTH_NAMES[monthNum];
                    const hasData = MONTHLY_DATA[monthKey];
                    const isSelected = selected === monthKey;
                    const isTotalYear = selected === 'total-year';

                    // Check if this month is "completed" (has data or is before last available)
                    const monthIndex = parseInt(monthNum, 10);
                    const isCompleted = hasData || (lastAvailableMonthNum > 0 && monthIndex <= lastAvailableMonthNum);
                    const isFuture = !hasData && monthIndex > lastAvailableMonthNum;

                    return (
                        <React.Fragment key={monthKey}>
                            {/* Month Button */}
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
                                {/* Data indicator dot */}
                                {hasData && !isSelected && (
                                    <span className="absolute -bottom-0.5 w-1 h-1 bg-emerald-400 rounded-full"></span>
                                )}
                                {isSelected && (
                                    <span className="absolute -bottom-0.5 w-1 h-1 bg-white rounded-full animate-pulse"></span>
                                )}
                            </button>

                            {/* Connector Line */}
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

            {/* Total Año Button */}
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

const App: React.FC = () => {
    // --- Authentication State ---
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [userEmail, setUserEmail] = useState<string | null>(null);

    // --- State Management ---
    const [view, setView] = useState<'dashboard' | 'laboratory' | 'strategic_lab' | 'broker_profile'>('dashboard');
    const [selectedBrokerProfile, setSelectedBrokerProfile] = useState<any | null>(null);
    const [selectedMonth, setSelectedMonth] = useState<string>('2026-02'); // Default to current month
    const [searchTerm, setSearchTerm] = useState('');
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [selectedSquad, setSelectedSquad] = useState<string>('all'); // 'all' o email del coordinador

    // Lab Access State
    const [showSecretPrompt, setShowSecretPrompt] = useState(false);
    const [secretCodeInput, setSecretCodeInput] = useState('');
    const [verifiedLabAccess, setVerifiedLabAccess] = useState(false);

    // View Mode State for Chart
    const [viewMode, setViewMode] = useState<'daily' | 'cumulative'>('daily');

    // Goal Setting State
    const [showGoalModal, setShowGoalModal] = useState(false);
    const [selectedBrokerForGoal, setSelectedBrokerForGoal] = useState<CorredorData | null>(null);
    const [brokerGoals, setBrokerGoals] = useState<Record<string, BrokerGoalData>>({});

    // --- Data Derivation ---
    const currentMonthData: MonthData = useMemo(() => {
        if (selectedMonth === 'total-year') {
            // Aggregate all months data
            const months = Object.keys(MONTHLY_DATA);
            if (months.length === 0) return MONTHLY_DATA['2026-02'] || { goal: 0, ranking: [], others: [] };

            // Combine all ranking data from all months
            const aggregatedRanking: Record<string, CorredorData> = {};
            let totalGoal = 0;
            let totalReservationGoal = 0;
            let totalContractGoal = 0;
            let total2025Ytd = 0;

            months.forEach(monthKey => {
                const monthData = MONTHLY_DATA[monthKey];
                totalGoal += monthData.goal || 0;
                totalReservationGoal += monthData.reservation_goal || 0;
                totalContractGoal += monthData.contract_goal || 0;
                total2025Ytd += monthData.total_2025_ytd || 0;

                // Aggregate ranking data
                monthData.ranking?.forEach((broker: CorredorData) => {
                    if (!aggregatedRanking[broker.name]) {
                        aggregatedRanking[broker.name] = { ...broker };
                    } else {
                        aggregatedRanking[broker.name].val += broker.val;
                        aggregatedRanking[broker.name].fallen += broker.fallen;
                        aggregatedRanking[broker.name].leads += broker.leads || 0;
                        aggregatedRanking[broker.name].agendas += broker.agendas || 0;
                        aggregatedRanking[broker.name].contracts += broker.contracts || 0;
                        // For personalMeta, use the max or sum? Let's use sum for yearly
                        aggregatedRanking[broker.name].personalMeta = (aggregatedRanking[broker.name].personalMeta || 0) + (broker.personalMeta || 0);
                    }
                });

                // Aggregate others data
                monthData.others?.forEach((broker: CorredorData) => {
                    if (!aggregatedRanking[broker.name]) {
                        aggregatedRanking[broker.name] = { ...broker };
                    } else {
                        aggregatedRanking[broker.name].val += broker.val;
                        aggregatedRanking[broker.name].fallen += broker.fallen;
                        aggregatedRanking[broker.name].leads += broker.leads || 0;
                        aggregatedRanking[broker.name].agendas += broker.agendas || 0;
                        aggregatedRanking[broker.name].contracts += broker.contracts || 0;
                    }
                });
            });

            const combinedRanking = Object.values(aggregatedRanking);

            // Get the last month data for reference to determine others
            const lastMonthKey = months[months.length - 1];
            const lastMonthData = MONTHLY_DATA[lastMonthKey];
            const othersNames = new Set(lastMonthData.others?.map(o => o.name) || []);

            return {
                goal: totalGoal,
                reservation_goal: totalReservationGoal,
                contract_goal: totalContractGoal,
                total_2025_ytd: total2025Ytd,
                ranking: combinedRanking.filter(b => !othersNames.has(b.name)),
                others: combinedRanking.filter(b => othersNames.has(b.name)),
                daily_stats: [],
                daily_goals: {}
            };
        }

        return MONTHLY_DATA[selectedMonth] || MONTHLY_DATA['2026-02'];
    }, [selectedMonth]);

    const processedDailyStats = useMemo(() => {
        const statsMap: Record<string, any> = {};

        // Fill dates (all days of month?) or just present data?
        // Assuming DAILY_STATS contains data for the days we have.
        const rawDaily = currentMonthData.daily_stats || [];

        rawDaily.forEach((item: DailyStat) => {
            const dateKey = item.date;
            if (!statsMap[dateKey]) {
                // Try to get goal for this day
                // date format YYYY-MM-DD. daily_goals keys are numbers (day of month)
                const dayNum = parseInt(dateKey.split('-')[2], 10);
                const dayGoal = currentMonthData.daily_goals?.[dayNum] || 0;

                statsMap[dateKey] = { date: dateKey, goal: dayGoal };
            }
            // Store count by squad email
            statsMap[dateKey][item.coord] = (statsMap[dateKey][item.coord] || 0) + item.count;
        });

        // Convert to array and Sort
        const sorted = Object.values(statsMap).sort((a: any, b: any) => a.date.localeCompare(b.date));

        // Add Cumulative Data
        let runningReal = 0;
        let runningGoal = 0;

        return sorted.map((day: any) => {
            // Sum all squad keys for total daily count (excluding date/goal keys)
            const dailyTotal = Object.keys(day).reduce((sum, key) => {
                if (key !== 'date' && key !== 'goal') return sum + (day[key] as number);
                return sum;
            }, 0);

            runningReal += dailyTotal;
            runningGoal += day.goal;

            return { ...day, accReal: runningReal, accGoal: runningGoal };
        });
    }, [currentMonthData]);


    const {
        goal: MONTHLY_GOAL,
        ranking: CURRENT_RANKING,
        others: OTHER_BROKERS,
        daily_stats: DAILY_STATS,
        daily_goals: DAILY_GOALS,
        total_2025_ytd: total2025Today
    } = currentMonthData;

    // Combine Ranking + Others for full calculations, but define "Main Ranking" separately if needed
    // Usually dashboard shows everything or separates "Others". 
    // Let's assume for stats we use everything, but for the table we might filter if needed.
    // However, the original code had separate "ranking" and "others".
    // Let's combine them for the main list unless "Others" were hidden.
    // In original App.tsx: `[...rankingData, ...othersData].forEach(...)` for stats.
    const ALL_BROKERS = useMemo(() => [...CURRENT_RANKING, ...OTHER_BROKERS], [CURRENT_RANKING, OTHER_BROKERS]);

    // --- Statistics Calculation ---
    const stats: DashboardStats = useMemo(() => {
        let totalActual = 0; // Reservas
        let totalContracts = 0; // Contratos Reales BI
        let globalQualified = 0;
        let brokersWithGoal = 0;
        let brokersMeetingGoal = 0;
        const squadStats: Record<string, SquadStats> = {};

        // Initialize Squad Stats
        Object.keys(TEAMS).forEach(id => {
            squadStats[id] = { cur: 0, contracts: 0, past: 0, qual: 0, others: 0, totalMembers: 0, activeMembers: 0, totalLeads: 0, totalAgendas: 0 };
        });

        const historyMap = currentMonthData.history || {};

        ALL_BROKERS.forEach(item => {
            totalActual += item.val;
            totalContracts += (item.contracts || 0);
            const hist = historyMap[item.name]?.c || 0;

            if (item.personalMeta && item.personalMeta > 0) {
                brokersWithGoal++;
                if (item.val >= item.personalMeta) brokersMeetingGoal++;
            }

            const isExternal = OTHER_BROKERS.some(e => e.name === item.name);
            const isFreelance = !isExternal;

            if (isFreelance && item.val >= 7) globalQualified++;

            if (squadStats[item.coord]) {
                squadStats[item.coord].cur += item.val; // Total reservations
                squadStats[item.coord].contracts += (item.contracts || 0); // Total contracts
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

        // Daily Progress
        const isTotalYear = selectedMonth === 'total-year';
        const daysInMonth = isTotalYear ? 365 : (selectedMonth === '2026-02' || selectedMonth === '2025-02') ? 28 : 31;
        const now = new Date();

        // For Total Year view, use sum of all monthly goals
        let accMetaToToday = 0;
        let accRealToToday = 0;
        let accMetaContractsToToday = 0;
        let accRealContractsToToday = 0;

        if (isTotalYear) {
            // For yearly view, use total goals from all months
            accMetaToToday = currentMonthData.goal || 0;
            accMetaContractsToToday = currentMonthData.contract_goal || 0;
            accRealToToday = totalActual;
            accRealContractsToToday = totalContracts;
        } else {
            // Precision logic for calculationDay (Sync with LAST_DB_UPDATE)
            let calculationDay = daysInMonth;
            const [updateDateStr, updateTimeStr] = LAST_DB_UPDATE.split(' ');
            const [d, m, y_update] = updateDateStr.split('/').map(Number);
            const [hh] = updateTimeStr.split(':').map(Number);

            const selectedDate = new Date(`${selectedMonth}-01T00:00:00`);
            const dataMonthStart = new Date(y_update, m - 1, 1);

            if (selectedDate.getTime() === dataMonthStart.getTime()) {
                // Margin of grace: if update < 8 AM, count only up to previous day
                calculationDay = hh < 8 ? Math.max(1, d - 1) : d;
            } else if (selectedDate > dataMonthStart) {
                calculationDay = 1; // Future
            }

            // Sum cumulative goals up to today
            const monthlyGoals = currentMonthData.daily_goals || {};
            for (let i = 1; i <= calculationDay; i++) {
                accMetaToToday += (monthlyGoals[i] || 0);
                // Approximation for contracts meta to today
                accMetaContractsToToday += ((currentMonthData.contract_goal || 0) / daysInMonth);
            }
            accRealToToday = totalActual;
            accRealContractsToToday = totalContracts;
        }

        return {
            totalActual,
            totalContracts,
            total2025Today,
            globalQualified: 0, // Not calculated in new logic, defaulting to 0
            squadStats,
            accMetaToToday,
            accRealToToday,
            accMetaContractsToToday,
            accRealContractsToToday,
            teamHealth: {
                total: brokersWithGoal,
                meeting: brokersMeetingGoal,
                pct: brokersWithGoal > 0 ? (brokersMeetingGoal / brokersWithGoal) * 100 : 0
            },
            diagnostics: { loss: [], lossVolume: 0, slowdown: [], slowdownVolume: 0, growth: [], growthVolume: 0 }
        };
    }, [ALL_BROKERS, currentMonthData, selectedMonth]);

    // --- UI Helpers ---
    const daysRemaining = useMemo(() => {
        const now = new Date();

        // For Total Year view, calculate days remaining in the year
        if (selectedMonth === 'total-year') {
            const yearEnd = new Date(now.getFullYear(), 11, 31);
            const diff = yearEnd.getTime() - now.getTime();
            return Math.max(0, Math.ceil(diff / (1000 * 60 * 60 * 24)));
        }

        const selectedDate = new Date(`${selectedMonth}-01T00:00:00`);
        const currentMonthStart = new Date(now.getFullYear(), now.getMonth(), 1);

        if (selectedDate < currentMonthStart) return 0; // Past month
        if (selectedDate > currentMonthStart) { // Future
            const daysInMonth = selectedMonth === '2026-02' ? 28 : 31;
            return daysInMonth;
        }

        // Current Month
        const daysInMonth = selectedMonth === '2026-02' ? 28 : 31;
        return Math.max(0, daysInMonth - now.getDate());
    }, [selectedMonth]);

    const filteredData = useMemo(() => {
        // Only show CURRENT_RANKING (Internals) in main table, exclude OTHER_BROKERS (Externals)
        let data = CURRENT_RANKING.filter(item =>
            !item.hidden && item.name.toLowerCase().includes(searchTerm.toLowerCase())
        );

        // Filter by squad if selected
        if (selectedSquad !== 'all') {
            data = data.filter(item => item.coord === selectedSquad);
        }

        return data;
    }, [searchTerm, CURRENT_RANKING, selectedSquad]);

    const top3 = useMemo(() => {
        const sorted = [...filteredData] // Use filteredData (Internals only) for Podium
            .sort((a, b) => b.val - a.val);
        return [sorted[0], sorted[1], sorted[2]].filter(Boolean);
    }, [filteredData]);

    const getStatusBadge = (val: number) => {
        if (val >= 8) return <span className="bg-emerald-500/20 text-emerald-400 px-3 py-1 rounded-full font-bold text-xs uppercase border border-emerald-500/50 shadow-[0_0_10px_rgba(16,185,129,0.2)]">Clasificado</span>;
        if (val === 7) return <span className="bg-emerald-500 text-white px-3 py-1 rounded-full font-black text-xs uppercase shadow-[0_0_15px_rgba(16,185,129,0.6)] animate-pulse">Calificado</span>;
        if (val === 6) return <span className="bg-blue-500/20 text-blue-400 px-3 py-1 rounded-full font-bold text-xs uppercase border border-blue-500/50">Próximo</span>;
        if (val === 5) return <span className="bg-yellow-500/20 text-yellow-400 px-3 py-1 rounded-full font-bold text-xs uppercase border border-yellow-500/50">Límite</span>;
        if (val > 0) return <span className="bg-red-500/20 text-red-400 px-3 py-1 rounded-full font-bold text-xs uppercase border border-red-500/50">Riesgo</span>;
        return <span className="bg-slate-800 text-slate-500 px-3 py-1 rounded-full font-bold text-xs uppercase border border-slate-700">Sin prod.</span>;
    };

    const trendDiff = stats.totalActual - stats.total2025Today;
    const resGoal = currentMonthData.reservation_goal || 2174;
    const progressPercentage = Math.min((stats.totalActual / resGoal) * 100, 100);

    // --- PROJECTION LOGIC (Data Driven) ---
    const contractGoal = currentMonthData.contract_goal || 2066;
    const safeAccMetaContracts = stats.accMetaContractsToToday || 1;
    const contractPace = stats.totalContracts / safeAccMetaContracts;
    const projectedContracts = Math.round(contractPace * contractGoal);

    // Progress for UI
    const contractProgressProyected = Math.min((projectedContracts / contractGoal) * 100, 100);
    const contractProgressReal = Math.min((stats.totalContracts / contractGoal) * 100, 100);

    // ============================================
    // GOAL MANAGEMENT FUNCTIONS
    // ============================================

    // Load broker goals when month changes
    React.useEffect(() => {
        const loadBrokerGoals = async () => {
            try {
                const response = await fetch(`/api/v4_goals?month=${selectedMonth}-01`);
                const data = await response.json();

                if (Array.isArray(data)) {
                    const goalsMap: Record<string, BrokerGoalData> = {};
                    data.forEach((goal: BrokerGoalData) => {
                        goalsMap[goal.broker_name] = goal;
                    });
                    setBrokerGoals(goalsMap);
                }
            } catch (error) {
                console.error('Error loading broker goals:', error);
            }
        };

        loadBrokerGoals();
    }, [selectedMonth]);

    const handleOpenGoalModal = (broker: CorredorData) => {
        // Verificar si ya tiene meta configurada
        const existingGoal = brokerGoals[broker.name];
        setSelectedBrokerForGoal({
            ...broker,
            // Guardar el email del coordinador en el broker para validación
            coord: broker.coord // El coord ya tiene el email
        });
        setShowGoalModal(true);
    };

    const handleSaveGoal = (goalData: BrokerGoalData) => {
        setBrokerGoals(prev => ({
            ...prev,
            [goalData.broker_name]: goalData
        }));
    };

    // ============================================
    // AUTHENTICATION FUNCTIONS
    // ============================================

    const handleLogin = (email: string, token: string, user: any) => {
        setUserEmail(email);
        setIsAuthenticated(true);
        // Guardar información adicional del usuario si es necesario
        if (user) {
            // Se puede extender para guardar role, squad, etc.
        }
    };

    const handleLogout = () => {
        // Limpiar token
        localStorage.removeItem('auth_token');
        setIsAuthenticated(false);
        setUserEmail(null);
        setView('dashboard');
        setVerifiedLabAccess(false);
    };

    // Verificar autenticación al cargar
    useEffect(() => {
        const verifyAuth = async () => {
            const token = localStorage.getItem('auth_token');
            if (token) {
                try {
                    const response = await fetch('/api/auth/verify', {
                        headers: {
                            'Authorization': `Bearer ${token}`,
                        },
                    });
                    const data = await response.json();
                    if (!data.valid) {
                        localStorage.removeItem('auth_token');
                        setIsAuthenticated(false);
                        setUserEmail(null);
                    }
                } catch {
                    localStorage.removeItem('auth_token');
                    setIsAuthenticated(false);
                    setUserEmail(null);
                }
            }
        };
        verifyAuth();
    }, []);

    // --- Laboratory Access ---
    const handleLabAccess = () => {
        // Todos los usuarios necesitan código secreto
        setShowSecretPrompt(true);
    };

    // --- Laboratory View ---
    if (view === 'laboratory') {
        return <SquadLaboratory
            onBack={() => setView('dashboard')}
            rankingData={ALL_BROKERS}
            monthlyGoal={MONTHLY_GOAL}
            selectedMonth={selectedMonth}
            onMonthChange={setSelectedMonth}
        />;
    }

    // --- Broker Profile View ---
    if (view === 'broker_profile' && selectedBrokerProfile) {
        return <BrokerProfile
            broker={selectedBrokerProfile}
            onBack={() => {
                setView('strategic_lab');
                setSelectedBrokerProfile(null);
            }}
            selectedMonth={selectedMonth}
        />;
    }

    // --- Strategic Lab View (Carlos Only) ---
    if (view === 'strategic_lab') {
        return <StrategicLab
            onBack={() => setView('dashboard')}
            rankingData={ALL_BROKERS}
            monthlyGoal={MONTHLY_GOAL}
            userEmail={userEmail}
            selectedMonth={selectedMonth}
            onMonthChange={setSelectedMonth}
            onBrokerClick={(broker: any) => {
                setSelectedBrokerProfile(broker);
                setView('broker_profile');
            }}
        />;
    }

    // --- Login View ---
    if (!isAuthenticated) {
        return <Login onLogin={handleLogin} />;
    }

    // --- Main Render ---
    return (
        <div className="min-h-screen bg-[#101622] text-slate-200 font-sans pb-20 selection:bg-blue-500/30 selection:text-white">

            {/* Header */}
            <header className="relative pt-10 pb-20 px-6 overflow-hidden">
                <div className="absolute top-[-20%] left-[-10%] w-[500px] h-[500px] bg-blue-600/20 rounded-full blur-[120px] pointer-events-none"></div>
                <div className="absolute top-[-20%] right-[-10%] w-[500px] h-[500px] bg-indigo-600/10 rounded-full blur-[120px] pointer-events-none"></div>

                <div className="container mx-auto relative z-10 flex flex-col lg:flex-row justify-between items-start gap-12 border-b border-[#324467] pb-12">
                    <div className="flex-1 w-full">
                        <div className="flex items-center justify-between mb-10">
                            <div className="flex items-center gap-4">
                                <img src="/logo_white.png" alt="Assetplan" className="h-40 w-auto opacity-100" />
                                <div className="h-12 w-px bg-[#324467]"></div>
                                <div>
                                    <h1 className="text-white font-black uppercase text-base tracking-widest leading-none">Home Operativo</h1>
                                    <div className="flex items-center gap-3 mt-2">
                                        <h2 className="text-blue-400 font-bold uppercase text-xs tracking-widest">
                                            Ranking {selectedMonth === 'total-year' ? 'Total Año' : selectedMonth === '2026-01' ? 'Enero' : selectedMonth === '2026-02' ? 'Febrero' : selectedMonth === '2026-03' ? 'Marzo' : selectedMonth === '2026-04' ? 'Abril' : selectedMonth === '2026-05' ? 'Mayo' : selectedMonth === '2026-06' ? 'Junio' : selectedMonth === '2026-07' ? 'Julio' : selectedMonth === '2026-08' ? 'Agosto' : selectedMonth === '2026-09' ? 'Septiembre' : selectedMonth === '2026-10' ? 'Octubre' : selectedMonth === '2026-11' ? 'Noviembre' : selectedMonth === '2026-12' ? 'Diciembre' : '2026'} 2026
                                        </h2>
                                        <MonthSelector selected={selectedMonth} onChange={setSelectedMonth} />
                                    </div>
                                </div>
                            </div>

                            {/* User Info + Logout */}
                            <div className="flex items-center gap-4">
                                <div className="text-right hidden lg:block">
                                    <p className="text-[10px] text-slate-500 font-bold uppercase">Conectado como</p>
                                    <p className="text-white font-bold text-sm">{userEmail}</p>
                                </div>
                                <button
                                    onClick={handleLogout}
                                    className="flex items-center gap-2 px-4 py-3 rounded-xl bg-red-500/20 hover:bg-red-500/30 border border-red-500/50 text-red-400 hover:text-red-300 transition-all text-xs font-bold uppercase tracking-widest"
                                >
                                    <LogOut size={16} />
                                    <span className="hidden lg:inline">Salir</span>
                                </button>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 max-w-6xl relative">
                            {/* COL 1: OPERATIONAL (RESERVATIONS) */}
                            <div className="space-y-6">
                                <div className="flex items-center gap-1.5 opacity-80">
                                    <Zap size={14} className="text-yellow-500" />
                                    <p className="text-slate-400 text-xs font-bold uppercase tracking-widest">Gestión de Reservas</p>
                                </div>
                                <div className="flex items-baseline gap-4">
                                    <span className="text-8xl font-black text-white tracking-tighter drop-shadow-2xl leading-none">{stats.totalActual}</span>
                                    <div className="flex flex-col items-start">
                                        <div className="text-2xl font-bold text-slate-500 flex items-baseline gap-1.5">
                                            <span>/</span>
                                            <span>{(currentMonthData.reservation_goal || 2174).toLocaleString('es-CL')}</span>
                                            <span className="text-xs uppercase opacity-60">Meta</span>
                                        </div>
                                        <div className={`text-base font-bold flex items-center gap-1 mt-1 ${trendDiff >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                                            {trendDiff > 0 ? '+' : ''}{trendDiff} vs 2025
                                        </div>
                                    </div>
                                </div>
                                {/* Reservation Progress Bar */}
                                <div className="space-y-3 pt-2">
                                    <div className="flex justify-between text-xs font-bold uppercase tracking-tight">
                                        <span className="text-slate-500">Avance de Reservas</span>
                                        <span className="text-blue-400 font-black">{progressPercentage.toFixed(1)}%</span>
                                    </div>
                                    <div className="h-2 w-full bg-[#1e293b] rounded-full overflow-hidden border border-[#324467]/50">
                                        <div className="h-full bg-blue-500 relative transition-all duration-1000 ease-out" style={{ width: `${progressPercentage}%` }}>
                                            <div className="absolute inset-0 bg-white/20 animate-[shimmer_2s_infinite]"></div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Vertical Divider (Desktop) */}
                            <div className="hidden lg:block absolute left-[45%] top-8 bottom-4 w-px bg-[#324467]/30"></div>

                            {/* COL 2: STRATEGIC (CONTRACTS) */}
                            <div className="space-y-6 lg:pl-16">
                                <div className="flex items-center gap-1.5 opacity-80">
                                    <Target size={14} className="text-emerald-500" />
                                    <p className="text-slate-400 text-xs font-bold uppercase tracking-widest">Contratos</p>
                                </div>
                                <div className="flex items-baseline gap-4">
                                    <span className="text-8xl font-black text-emerald-400 tracking-tighter drop-shadow-2xl leading-none">
                                        {stats.totalContracts.toLocaleString('es-CL')}
                                    </span>
                                    <div className="flex flex-col items-start">
                                        <div className="text-2xl font-bold text-slate-500 flex items-baseline gap-1.5">
                                            <span>/</span>
                                            <span>{contractGoal.toLocaleString('es-CL')}</span>
                                            <span className="text-xs uppercase opacity-60">Meta</span>
                                        </div>
                                        <div className="text-[10px] font-bold text-slate-400 mt-2 bg-slate-800/80 px-2 py-1 rounded border border-slate-700/50 uppercase tracking-widest">
                                            Real • Proy: {projectedContracts.toLocaleString('es-CL')}
                                        </div>
                                    </div>
                                </div>

                                {/* Contract Progress Bar */}
                                <div className="space-y-3 pt-2">
                                    <div className="flex justify-between text-[10px] font-bold uppercase tracking-tight">
                                        <div className="flex items-center gap-4">
                                            <div className="flex items-center gap-1.5">
                                                <span className="text-slate-500">Avance Real:</span>
                                                <span className="text-emerald-500 font-black">{contractProgressReal.toFixed(1)}%</span>
                                            </div>
                                            <div className="w-px h-2.5 bg-[#324467]"></div>
                                            <div className="flex items-center gap-1.5">
                                                <span className="text-slate-500">Proyección:</span>
                                                <span className="text-emerald-400 font-extrabold">{contractProgressProyected.toFixed(1)}%</span>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="h-2 w-full bg-[#1e293b] rounded-full overflow-hidden border border-[#324467]/50 relative">
                                        {/* Background projection fill */}
                                        <div className="h-full bg-emerald-900/30 absolute" style={{ width: `${contractProgressProyected}%` }}></div>
                                        {/* Solid actual fill */}
                                        <div className="h-full bg-emerald-500 relative transition-all duration-1000 ease-out shadow-[0_0_15px_rgba(16,185,129,0.2)]" style={{ width: `${contractProgressReal}%` }}>
                                            <div className="absolute inset-0 bg-white/20 animate-[shimmer_2s_infinite]"></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="mt-12 pt-6 border-t border-[#324467]/30 flex justify-between items-center max-w-6xl">
                            <div className="text-[10px] text-slate-500 font-bold flex items-center gap-2 uppercase tracking-widest opacity-80">
                                <Clock size={12} className="text-blue-500" />
                                {daysRemaining > 0 ? `Quedan ${daysRemaining} días de gestión operativa` : 'Mes Finalizado'}
                            </div>
                            <div className="text-[10px] text-slate-600 font-bold uppercase tracking-widest opacity-60">
                                Datos hasta: {LAST_DB_UPDATE}
                            </div>
                        </div>
                    </div>
                </div>
            </header>

            {/* Secret Code Modal */}
            {
                showSecretPrompt && (
                    <div className="fixed inset-0 z-[200] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
                        <div className="bg-[#1e293b] p-8 rounded-3xl border border-[#324467] shadow-2xl w-full max-w-sm animate-in zoom-in-95 duration-200">
                            <div className="text-center mb-6">
                                <div className="w-16 h-16 bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-4 border border-slate-700">
                                    <Shield size={32} className="text-indigo-400" />
                                </div>
                                <h3 className="text-xl font-bold text-white uppercase tracking-widest">Acceso Restringido</h3>
                                <p className="text-xs text-slate-400 mt-2">Ingrese código de seguridad.</p>
                            </div>
                            <input
                                type="password"
                                className="w-full bg-[#101622] text-white text-center text-2xl font-mono tracking-[0.5em] py-4 rounded-xl border border-[#324467] focus:border-indigo-500 outline-none mb-6"
                                placeholder="••••"
                                value={secretCodeInput}
                                onChange={(e) => {
                                    const val = e.target.value;
                                    setSecretCodeInput(val);
                                    if (val === '2183') {
                                        setVerifiedLabAccess(true);
                                        setShowSecretPrompt(false);
                                        setSecretCodeInput('');

                                        if (userEmail === 'carlos.echeverria@assetplan.cl') {
                                            setView('strategic_lab');
                                        }
                                    }
                                }}
                                autoFocus
                                maxLength={4}
                            />
                            <button
                                onClick={() => setShowSecretPrompt(false)}
                                className="w-full py-3 rounded-xl border border-slate-700 text-slate-400 hover:text-white hover:bg-slate-800 transition-all text-xs font-bold uppercase tracking-widest"
                            >
                                Cancelar
                            </button>
                        </div>
                    </div>
                )
            }

            {/* Ranking / Squads / Chart Content */}
            <main className="container mx-auto px-4 -mt-6 relative z-20">

                {/* Navigation Pills */}
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

                {/* --- Podium --- */}
                <div id="ranking" className="scroll-mt-32">
                    {!searchTerm && top3.length >= 3 && (
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16 items-end max-w-5xl mx-auto">
                            {/* 2nd Place */}
                            <div className="order-2 md:order-1 relative group">
                                <div className="text-center mb-4"><span className="text-slate-400 font-bold text-xs uppercase tracking-widest">2° Lugar</span></div>
                                <div className="bg-[#1e293b] p-6 rounded-3xl border border-[#324467] text-center shadow-xl relative overflow-hidden group-hover:border-slate-400/50 transition-colors">
                                    <div className="absolute top-0 left-0 w-full h-1 bg-slate-400"></div>
                                    <h3 className="font-bold text-slate-200 truncate">{top3[1].name}</h3>
                                    <div className="mt-4 text-4xl font-black text-white">{top3[1].val}</div>
                                    <p className="text-[10px] text-slate-500 uppercase font-bold mt-1">Reservas</p>
                                </div>
                            </div>

                            {/* 1st Place */}
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
                                </div>
                            </div>

                            {/* 3rd Place */}
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

                    {/* Table */}
                    <div className="bg-[#1e293b] rounded-3xl border border-[#324467] overflow-hidden shadow-2xl mb-12">
                        <div className="p-6 border-b border-[#324467] flex flex-col md:flex-row justify-between items-center gap-6">
                            <div className="flex flex-col md:flex-row gap-4 flex-1">
                                {/* Search Input */}
                                <div className="relative w-full md:w-72">
                                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
                                    <input
                                        type="text"
                                        value={searchTerm}
                                        onChange={(e) => setSearchTerm(e.target.value)}
                                        placeholder="Filtrar por nombre..."
                                        className="w-full bg-[#101622] text-slate-200 pl-12 pr-4 py-3 rounded-xl border border-[#324467] focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-all"
                                    />
                                </div>

                                {/* Squad Filter */}
                                <select
                                    value={selectedSquad}
                                    onChange={(e) => setSelectedSquad(e.target.value)}
                                    className="bg-[#101622] text-slate-200 px-4 py-3 rounded-xl border border-[#324467] focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none transition-all text-sm font-bold cursor-pointer"
                                >
                                    <option value="all">Todos los Equipos</option>
                                    {Object.entries(TEAMS).map(([email, team]) => (
                                        <option key={email} value={email}>
                                            {team.name}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            <div className="flex gap-4">
                                <div className="text-right">
                                    <p className="text-[10px] text-slate-500 font-bold uppercase">Corredores Activos</p>
                                    <p className="text-white font-bold text-lg">{filteredData.length}</p>
                                </div>
                                <div className="w-px h-10 bg-[#324467] self-center"></div>
                                <div className="text-right">
                                    <p className="text-[10px] text-slate-500 font-bold uppercase">Salud del Equipo</p>
                                    <p className="text-emerald-400 font-bold text-lg">{stats.teamHealth.pct.toFixed(0)}%</p>
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
                                        <th className="px-6 py-4 text-center text-slate-300 border-l border-[#324467]/30">Reservas</th>
                                        <th className="px-6 py-4 text-center text-white bg-[#324467]/20 border-l border-[#324467]">Contratos</th>
                                        <th className="px-6 py-4 text-center text-yellow-400">Aceleración</th>
                                        <th className="px-10 py-4 text-center text-emerald-400">Progreso</th>
                                        <th className="px-6 py-4 text-center text-orange-400">Faltan</th>
                                        <th className="px-6 py-4 text-center">Estado</th>
                                        <th className="px-6 py-4 text-center text-indigo-400">Mi Meta</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-[#324467] text-sm">
                                    {filteredData.map((item, index) => {
                                        const rank = index + 1;
                                        const team = TEAMS[item.coord];
                                        const TeamIcon = team ? IconMap[team.icon as keyof typeof IconMap] : null;
                                        const isTop3 = rank <= 3;
                                        const history = HISTORY_2025[item.name];
                                        const isCarlosSquad = item.coord === 'carlos.echeverria@assetplan.cl';

                                        return (
                                            <tr key={item.name} className={`group transition-all duration-300 ${rank === 1 ? 'bg-yellow-500/10 hover:bg-yellow-500/20 shadow-lg shadow-yellow-500/5' :
                                                rank === 2 ? 'bg-slate-400/5 hover:bg-slate-400/10 shadow-md shadow-slate-400/5' :
                                                    rank === 3 ? 'bg-orange-800/10 hover:bg-orange-800/20 shadow-md shadow-orange-800/5' :
                                                        'hover:bg-[#324467]/20'
                                                }`}>
                                                <td className="px-6 py-4 text-center">
                                                    {rank === 1 ? (
                                                        <div className="flex justify-center"><Crown className="text-yellow-400 drop-shadow-[0_0_8px_rgba(250,204,21,0.5)]" size={18} /></div>
                                                    ) : isTop3 ? (
                                                        <span className={`font-black ${rank === 2 ? 'text-slate-300' : 'text-orange-400'}`}>{rank}</span>
                                                    ) : (
                                                        <span className="font-mono text-slate-500 group-hover:text-white">{rank}</span>
                                                    )}
                                                </td>
                                                <td className="px-6 py-4">
                                                    <div className="flex items-center gap-3">
                                                        {TeamIcon && (
                                                            <div className={`p-1.5 rounded-lg bg-[#101622] border border-[#324467] ${team.color}`}>
                                                                <TeamIcon size={14} />
                                                            </div>
                                                        )}
                                                        <div>
                                                            <div className={`font-bold group-hover:text-white flex items-center gap-2 ${isTop3 ? 'text-white text-base' : 'text-slate-200'}`}>
                                                                {item.name}
                                                                {!history && (
                                                                    <span className="bg-indigo-500/20 text-indigo-300 text-[9px] px-1.5 py-0.5 rounded font-bold uppercase tracking-wide border border-indigo-500/30">Nuevo</span>
                                                                )}
                                                            </div>
                                                            {NAMES_WITH_AGENDA.includes(item.name) && (
                                                                <div className="text-[9px] text-blue-400 flex items-center gap-1 mt-0.5 font-bold uppercase tracking-wide">
                                                                    <Calendar size={8} /> Agenda Activa
                                                                </div>
                                                            )}
                                                        </div>
                                                    </div>
                                                </td>
                                                <td className={`px-6 py-4 text-center font-bold text-slate-300`}>
                                                    {item.leads || 0}
                                                </td>
                                                <td className={`px-6 py-4 text-center font-bold text-slate-300`}>
                                                    {item.agendas || 0}
                                                </td>
                                                <td className={`px-6 py-4 text-center border-l border-[#324467]/30`}>
                                                    <div className="flex flex-col items-center">
                                                        <div className="flex items-baseline gap-1">
                                                            <span className="text-xl font-black text-slate-200">{item.val + item.fallen}</span>
                                                            {item.fallen > 0 && (
                                                                <span className="text-[10px] font-bold text-red-500">-{item.fallen}</span>
                                                            )}
                                                        </div>
                                                        <p className="text-[10px] font-bold text-slate-500 uppercase leading-none mt-1">Reservas</p>
                                                    </div>
                                                </td>
                                                <td className={`px-6 py-4 text-center bg-[#324467]/10 border-l border-[#324467] relative`}>
                                                    <span className="text-xl font-black text-white">{item.contracts || 0}</span>
                                                    <p className="text-[10px] font-bold text-slate-500 uppercase">Contratos</p>
                                                </td>
                                                <td className="px-6 py-4 text-center">
                                                    {(() => {
                                                        const monthProgress = stats.accMetaToToday / (resGoal || 1);
                                                        const brokerProgress = item.val / (item.personalMeta || 1);
                                                        const acceleration = brokerProgress / (monthProgress || 0.01);

                                                        return (
                                                            <div className="flex flex-col items-center gap-1">
                                                                {acceleration > 1.2 ? (
                                                                    <div className="flex items-center gap-1 text-yellow-400">
                                                                        <Zap size={14} className="fill-yellow-400 animate-pulse" />
                                                                        <span className="text-[10px] font-black">FAST</span>
                                                                    </div>
                                                                ) : acceleration > 1 ? (
                                                                    <div className="flex items-center gap-1 text-emerald-400">
                                                                        <ArrowUpRight size={14} />
                                                                        <span className="text-[10px] font-bold">ON PACE</span>
                                                                    </div>
                                                                ) : (
                                                                    <span className="text-[10px] text-slate-600 font-bold">STEADY</span>
                                                                )}
                                                                <div className="w-8 h-1 bg-[#101622] rounded-full overflow-hidden">
                                                                    <div
                                                                        className={`h-full transition-all duration-500 ${acceleration > 1 ? 'bg-emerald-500' : 'bg-slate-700'}`}
                                                                        style={{ width: `${Math.min(acceleration * 50, 100)}%` }}
                                                                    ></div>
                                                                </div>
                                                            </div>
                                                        );
                                                    })()}
                                                </td>
                                                <td className="px-10 py-4">
                                                    {(() => {
                                                        const goal = item.personalMeta || 10;
                                                        const progress = Math.min((item.val / goal) * 100, 150);
                                                        const isCompleted = item.val >= goal;
                                                        return (
                                                            <div className="flex flex-col gap-1.5 min-w-[140px]">
                                                                <div className="flex justify-between items-end">
                                                                    <span className={`text-[11px] font-black ${isCompleted ? 'text-emerald-400' : 'text-slate-400'}`}>
                                                                        {Math.round(progress)}%
                                                                    </span>
                                                                    <span className="text-[9px] text-slate-500 font-bold">META {goal}</span>
                                                                </div>
                                                                <div className="h-2 w-full bg-[#101622] rounded-full overflow-hidden border border-[#324467]">
                                                                    <div
                                                                        className={`h-full rounded-full transition-all duration-1000 ${isCompleted ? 'bg-gradient-to-r from-emerald-600 to-emerald-400 animate-pulse shadow-[0_0_10px_rgba(52,211,153,0.5)]' :
                                                                            progress > 70 ? 'bg-gradient-to-r from-blue-600 to-blue-400' :
                                                                                'bg-gradient-to-r from-slate-600 to-slate-400'
                                                                            }`}
                                                                        style={{ width: `${progress}%` }}
                                                                    ></div>
                                                                </div>
                                                            </div>
                                                        );
                                                    })()}
                                                </td>
                                                <td className="px-6 py-4 text-center">
                                                    {(() => {
                                                        const gap = (item.personalMeta || 0) - (item.val || 0);
                                                        return gap > 0 ? (
                                                            <div className="flex flex-col items-center">
                                                                <span className="text-lg font-black text-orange-500">-{gap}</span>
                                                                <span className="text-[8px] text-orange-500/50 font-bold uppercase">Por lograr</span>
                                                            </div>
                                                        ) : (
                                                            <div className="flex flex-col items-center">
                                                                <div className="bg-emerald-500/20 text-emerald-400 p-1 rounded-full mb-1">
                                                                    <CheckCircle2 size={12} />
                                                                </div>
                                                                <span className="text-[8px] text-emerald-400 font-bold uppercase tracking-tighter">Cumplido</span>
                                                            </div>
                                                        );
                                                    })()}
                                                </td>
                                                <td className="px-6 py-4 text-center">
                                                    {(() => {
                                                        const perf = (item.contracts / (item.personalMeta || 1)) * 100;
                                                        if (perf >= 100) return <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 shadow-[0_0_10px_rgba(52,211,153,0.1)]">ELITE</span>;
                                                        if (perf >= 70) return <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-blue-500/10 text-blue-400 border border-blue-500/20">SÓLIDO</span>;
                                                        if (perf >= 40) return <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-orange-500/10 text-orange-400 border border-orange-500/20">E-PROCESO</span>;
                                                        return <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-red-500/10 text-red-400 border border-red-500/20">ATENCIÓN</span>;
                                                    })()}
                                                </td>
                                                <td className="px-6 py-4 text-center">
                                                    {(() => {
                                                        const existingGoal = brokerGoals[item.name];
                                                        const hasGoal = existingGoal && existingGoal.personal_goal > 0;

                                                        return (
                                                            <>
                                                                <button
                                                                    onClick={() => handleOpenGoalModal(item)}
                                                                    className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl bg-indigo-500/20 hover:bg-indigo-500/30 border border-indigo-500/50 text-indigo-400 hover:text-indigo-300 transition-all text-xs font-bold uppercase tracking-wide group"
                                                                >
                                                                    <Edit3 size={14} className="group-hover:scale-110 transition-transform" />
                                                                    {hasGoal ? (
                                                                        <span className="text-base font-black">{existingGoal.personal_goal}</span>
                                                                    ) : (
                                                                        <span>Configurar</span>
                                                                    )}
                                                                </button>
                                                                {existingGoal?.commitment_comment && (
                                                                    <div className="mt-2 text-[9px] text-slate-500 flex items-start gap-1 justify-center max-w-[200px]">
                                                                        <MessageSquare size={8} className="mt-0.5 flex-shrink-0" />
                                                                        <span className="italic line-clamp-2">{existingGoal.commitment_comment}</span>
                                                                    </div>
                                                                )}
                                                            </>
                                                        );
                                                    })()}
                                                </td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>

                        {/* Legend / Motivational Footer */}
                        <div className="p-4 bg-[#162032] border-t border-[#324467] flex flex-wrap justify-center gap-6">
                            <div className="flex items-center gap-2">
                                <span className="bg-emerald-500/10 text-emerald-400 text-[10px] font-bold px-2 py-0.5 rounded border border-emerald-500/20">ELITE</span>
                                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-tight">≥ 100% Meta</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <span className="bg-blue-500/10 text-blue-400 text-[10px] font-bold px-2 py-0.5 rounded border border-blue-500/20">SÓLIDO</span>
                                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-tight">≥ 70% Meta</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <span className="bg-orange-500/10 text-orange-400 text-[10px] font-bold px-2 py-0.5 rounded border border-orange-500/20">E-PROCESO</span>
                                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-tight">≥ 40% Meta</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <span className="bg-red-500/10 text-red-400 text-[10px] font-bold px-2 py-0.5 rounded border border-red-500/20">ATENCIÓN</span>
                                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-tight">&lt; 40% Meta</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* --- Squads --- */}
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
                                        <div className="flex gap-4">
                                            <div className="text-right">
                                                <p className="text-3xl font-black text-white">{data.cur}</p>
                                                <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Reservas</p>
                                            </div>
                                            <div className="w-px h-8 bg-[#324467] self-center"></div>
                                            <div className="text-right">
                                                <p className="text-3xl font-black text-emerald-400">{data.contracts || 0}</p>
                                                <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Contratos</p>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="space-y-3">
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

                {/* --- Evolution Chart --- */}
                <div id="grafico" className="scroll-mt-32">
                    <div className="flex justify-between items-end mb-6">
                        <h3 className="text-xl font-bold text-white uppercase tracking-widest flex items-center gap-3">
                            <TrendingUp size={20} className="text-indigo-500" />
                            {viewMode === 'daily' ? 'Evolución Diaria' : 'Progreso Acumulado'}
                        </h3>

                        {/* View Toggle */}
                        <div className="bg-[#101622] p-1 rounded-lg border border-[#324467] flex shadow-inner">
                            <button
                                onClick={() => setViewMode('daily')}
                                className={`px-4 py-1.5 rounded-md text-xs font-bold transition-all ${viewMode === 'daily' ? 'bg-indigo-600 text-white shadow-lg' : 'text-slate-400 hover:text-white'}`}
                            >
                                Diario
                            </button>
                            <button
                                onClick={() => setViewMode('cumulative')}
                                className={`px-4 py-1.5 rounded-md text-xs font-bold transition-all ${viewMode === 'cumulative' ? 'bg-indigo-600 text-white shadow-lg' : 'text-slate-400 hover:text-white'}`}
                            >
                                Acumulado
                            </button>
                        </div>
                    </div>
                    <div className="bg-[#1e293b] p-8 rounded-[2rem] border border-[#324467] mb-20 shadow-2xl">
                        {/* KPI Header */}
                        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-10 pb-8 border-b border-[#324467]/50">
                            <div className="bg-[#101622] p-4 rounded-2xl border border-[#324467]">
                                <p className="text-[10px] text-slate-500 font-bold uppercase mb-1">Meta (Reservas)</p>
                                <p className="text-2xl font-black text-white">{stats.accMetaToToday.toFixed(0)}</p>
                            </div>
                            <div className="bg-[#101622] p-4 rounded-2xl border border-[#324467]">
                                <p className="text-[10px] text-slate-500 font-bold uppercase mb-1">Real Acumulado</p>
                                <p className="text-2xl font-black text-blue-400">{stats.accRealToToday}</p>
                            </div>
                            <div className="bg-[#101622] p-4 rounded-2xl border border-[#324467]">
                                <p className="text-[10px] text-slate-500 font-bold uppercase mb-1">Brecha (Gap)</p>
                                <p className={`text-2xl font-black ${stats.accRealToToday >= stats.accMetaToToday ? 'text-emerald-400' : 'text-red-400'}`}>
                                    {stats.accRealToToday >= stats.accMetaToToday ? '+' : ''}{(stats.accRealToToday - stats.accMetaToToday).toFixed(0)}
                                </p>
                            </div>
                            <div className="bg-[#101622] p-4 rounded-2xl border border-[#324467]">
                                <p className="text-[10px] text-slate-500 font-bold uppercase mb-1">% Cumplimiento</p>
                                <p className="text-2xl font-black text-white">
                                    {((stats.accRealToToday / (stats.accMetaToToday || 1)) * 100).toFixed(1)}%
                                </p>
                            </div>
                        </div>

                        {/* Chart Area */}
                        <div className="h-[400px] w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                {viewMode === 'daily' ? (
                                    <ComposedChart data={processedDailyStats}>
                                        <defs>
                                            <linearGradient id="goalGradient" x1="0" y1="0" x2="1" y2="0">
                                                <stop offset="0%" stopColor="#ef4444" />
                                                <stop offset="100%" stopColor="#f87171" />
                                            </linearGradient>
                                        </defs>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} vertical={false} />
                                        <XAxis
                                            dataKey="date"
                                            stroke="#64748b"
                                            fontSize={10}
                                            tickFormatter={(val) => val.split('-')[2]}
                                            axisLine={false}
                                            tickLine={false}
                                            dy={10}
                                        />
                                        <YAxis
                                            stroke="#64748b"
                                            fontSize={10}
                                            axisLine={false}
                                            tickLine={false}
                                            dx={-10}
                                        />
                                        <Tooltip
                                            contentStyle={{ backgroundColor: '#101622', borderColor: '#324467', borderRadius: '12px' }}
                                            itemStyle={{ fontSize: '12px', fontWeight: 'bold' }}
                                            labelStyle={{ color: '#94a3b8', fontSize: '10px', textTransform: 'uppercase', fontWeight: 'bold', marginBottom: '8px', display: 'block' }}
                                        />
                                        <Legend
                                            iconType="circle"
                                            wrapperStyle={{ paddingTop: '20px' }}
                                        />
                                        {/* Goal Line - Dashed Red Line */}
                                        <Line
                                            type="monotone"
                                            dataKey="goal"
                                            name="Meta Diaria"
                                            stroke="#ef4444"
                                            strokeWidth={2}
                                            dot={false}
                                            strokeDasharray="4 4"
                                        />

                                        {/* Stacked Bars for Squads */}
                                        {Object.entries(TEAMS).map(([email, config]) => {
                                            let hex = '#64748b';
                                            if (email.includes('carlos')) hex = '#f97316';
                                            if (email.includes('luis')) hex = '#3b82f6';
                                            if (email.includes('nataly')) hex = '#4f46e5';
                                            if (email.includes('angely')) hex = '#db2777';
                                            if (email.includes('maria')) hex = '#eab308';

                                            return (
                                                <Bar
                                                    key={email}
                                                    dataKey={email}
                                                    name={config.name}
                                                    stackId="a"
                                                    fill={hex}
                                                    radius={[0, 0, 0, 0]}
                                                    barSize={32}
                                                />
                                            );
                                        })}
                                    </ComposedChart>
                                ) : (
                                    <AreaChart data={processedDailyStats} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
                                        <defs>
                                            <linearGradient id="colorAcc" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.5} />
                                                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                            </linearGradient>
                                        </defs>
                                        <XAxis
                                            dataKey="date"
                                            tickFormatter={(val) => val.split('-')[2]}
                                            axisLine={false}
                                            tickLine={false}
                                            tick={{ fill: '#64748b', fontSize: 12 }}
                                        />
                                        <YAxis
                                            axisLine={false}
                                            tickLine={false}
                                            tick={{ fill: '#64748b', fontSize: 12 }}
                                        />
                                        <Tooltip
                                            contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px' }}
                                            itemStyle={{ color: '#e2e8f0' }}
                                        />
                                        <Legend wrapperStyle={{ paddingTop: '20px' }} />
                                        <CartesianGrid vertical={false} stroke="#334155" strokeDasharray="3 3" opacity={0.3} />

                                        <Area
                                            type="monotone"
                                            dataKey="accReal"
                                            stroke="#3b82f6"
                                            fill="url(#colorAcc)"
                                            strokeWidth={3}
                                            name="Real Acumulado"
                                            isAnimationActive={false}
                                        />
                                        <Line
                                            type="monotone"
                                            dataKey="accGoal"
                                            stroke="#eab308"
                                            strokeWidth={3}
                                            dot={false}
                                            name="Meta Acumulada"
                                            strokeDasharray="5 5"
                                            isAnimationActive={false}
                                        />
                                    </AreaChart>
                                )}
                            </ResponsiveContainer>
                        </div>
                    </div>
                </div>

            </main>

            {/* Botón de acceso al Strategic Lab (Solo Carlos) */}
            {userEmail === 'carlos.echeverria@assetplan.cl' && (
                <button
                    onClick={handleLabAccess}
                    className="fixed bottom-8 right-8 z-50 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white p-4 rounded-2xl shadow-2xl border border-indigo-400/50 transition-all hover:scale-110 group"
                >
                    <Brain size={28} className="group-hover:animate-pulse" />
                    <span className="absolute -top-10 right-0 bg-indigo-900/90 text-white text-[10px] font-bold uppercase tracking-widest px-3 py-1.5 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
                        Laboratorio Estratégico
                    </span>
                </button>
            )}

            {/* Botón de acceso al Laboratorio Clásico eliminado para otros usuarios */}

            {/* Goal Setting Modal */}
            {selectedBrokerForGoal && (
                <GoalSettingModal
                    isOpen={showGoalModal}
                    onClose={() => {
                        setShowGoalModal(false);
                        setSelectedBrokerForGoal(null);
                    }}
                    brokerName={selectedBrokerForGoal.name}
                    brokerEmail={selectedBrokerForGoal.coord}
                    currentGoal={brokerGoals[selectedBrokerForGoal.name]?.personal_goal}
                    currentReservas={selectedBrokerForGoal.val}
                    selectedMonth={selectedMonth}
                    onSave={handleSaveGoal}
                    isEditing={!!brokerGoals[selectedBrokerForGoal.name]?.personal_goal}
                />
            )}
            <SpeedInsights />
        </div >
    );
};

export default App;
