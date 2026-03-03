import { useMemo } from 'react';
import { CorredorData, MonthData } from '../../types';

export interface UseRankingDataReturn {
    currentMonthData: MonthData;
    filteredBrokers: CorredorData[];
    topBrokers: CorredorData[];
    squadBrokers: CorredorData[];
    otherBrokers: CorredorData[];
    totalReservas: number;
    totalContracts: number;
    totalLeads: number;
    totalAgendas: number;
    goalProgress: number;
}

export function useRankingData(
    monthlyData: Record<string, MonthData>,
    selectedMonth: string,
    selectedSquad: string,
    searchTerm: string
): UseRankingDataReturn {
    const currentMonthData = useMemo(() => {
        if (selectedMonth === 'total-year') {
            const months = Object.keys(monthlyData || {});
            if (months.length === 0) return monthlyData['2026-02'] || { goal: 0, ranking: [], others: [] };

            const aggregatedRanking: Record<string, CorredorData> = {};
            let totalGoal = 0;
            let totalReservationGoal = 0;
            let totalContractGoal = 0;
            let total2025Ytd = 0;

            months.forEach(monthKey => {
                const monthInfo = monthlyData[monthKey];
                totalGoal += monthInfo.goal || 0;
                totalReservationGoal += monthInfo.reservation_goal || 0;
                totalContractGoal += monthInfo.contract_goal || 0;
                total2025Ytd += monthInfo.total_2025_ytd || 0;

                monthInfo.ranking?.forEach((broker: CorredorData) => {
                    if (!aggregatedRanking[broker.name]) {
                        aggregatedRanking[broker.name] = { ...broker };
                    } else {
                        aggregatedRanking[broker.name].val += broker.val;
                        aggregatedRanking[broker.name].fallen += broker.fallen;
                        aggregatedRanking[broker.name].leads += broker.leads || 0;
                        aggregatedRanking[broker.name].agendas += broker.agendas || 0;
                        aggregatedRanking[broker.name].contracts += broker.contracts || 0;
                        aggregatedRanking[broker.name].personalMeta =
                            (aggregatedRanking[broker.name].personalMeta || 0) + (broker.personalMeta || 0);
                    }
                });

                monthInfo.others?.forEach((broker: CorredorData) => {
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
            const lastMonthKey = months[months.length - 1];
            const lastMonthData = monthlyData[lastMonthKey];
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
        return monthlyData[selectedMonth] || { goal: 0, ranking: [], others: [], daily_stats: [], daily_goals: {} };
    }, [monthlyData, selectedMonth]);

    const allBrokers = useMemo(() => {
        return [...(currentMonthData.ranking || []), ...(currentMonthData.others || [])];
    }, [currentMonthData]);

    const filteredBrokers = useMemo(() => {
        let filtered = allBrokers;

        if (selectedSquad !== 'all') {
            filtered = filtered.filter(broker => broker.coord === selectedSquad);
        }

        if (searchTerm) {
            filtered = filtered.filter(broker =>
                broker.name.toLowerCase().includes(searchTerm.toLowerCase())
            );
        }

        return filtered;
    }, [allBrokers, selectedSquad, searchTerm]);

    const topBrokers = useMemo(() => {
        return [...filteredBrokers]
            .sort((a, b) => b.val - a.val)
            .slice(0, 3);
    }, [filteredBrokers]);

    const squadBrokers = useMemo(() => {
        return currentMonthData.ranking || [];
    }, [currentMonthData]);

    const otherBrokers = useMemo(() => {
        return currentMonthData.others || [];
    }, [currentMonthData]);

    const totals = useMemo(() => {
        return allBrokers.reduce((acc, broker) => ({
            reservas: acc.reservas + (broker.val || 0),
            contracts: acc.contracts + (broker.contracts || 0),
            leads: acc.leads + (broker.leads || 0),
            agendas: acc.agendas + (broker.agendas || 0)
        }), { reservas: 0, contracts: 0, leads: 0, agendas: 0 });
    }, [allBrokers]);

    const goalProgress = useMemo(() => {
        if (!currentMonthData.goal) return 0;
        return Math.round((totals.reservas / currentMonthData.goal) * 100);
    }, [totals.reservas, currentMonthData.goal]);

    return {
        currentMonthData,
        filteredBrokers,
        topBrokers,
        squadBrokers,
        otherBrokers,
        totalReservas: totals.reservas,
        totalContracts: totals.contracts,
        totalLeads: totals.leads,
        totalAgendas: totals.agendas,
        goalProgress
    };
}
