/**
 * @jest-environment jsdom
 */

import { renderHook } from '@testing-library/react';
import { useRankingData } from '../../hooks/useRankingData';
import { MonthData } from '../../../types';

const mockMonthlyData: Record<string, MonthData> = {
    '2026-01': {
        goal: 100,
        contract_goal: 100,
        ranking: [
            { name: 'Juan Perez', val: 50, fallen: 2, leads: 100, agendas: 20, contracts: 45, coord: 'carlos@assetplan.cl' },
            { name: 'Maria Garcia', val: 40, fallen: 1, leads: 80, agendas: 15, contracts: 35, coord: 'luis@assetplan.cl' }
        ],
        others: [
            { name: 'Pedro Lopez', val: 30, fallen: 0, leads: 50, agendas: 10, contracts: 25, coord: 'carlos@assetplan.cl' }
        ],
        daily_stats: [],
        daily_goals: {},
        total_2025_ytd: 500,
        reservation_goal: 100,
        history: {}
    },
    '2026-02': {
        goal: 120,
        contract_goal: 110,
        ranking: [
            { name: 'Juan Perez', val: 55, fallen: 3, leads: 110, agendas: 25, contracts: 50, coord: 'carlos@assetplan.cl' },
            { name: 'Maria Garcia', val: 45, fallen: 2, leads: 90, agendas: 18, contracts: 40, coord: 'luis@assetplan.cl' }
        ],
        others: [
            { name: 'Pedro Lopez', val: 35, fallen: 1, leads: 60, agendas: 12, contracts: 30, coord: 'carlos@assetplan.cl' }
        ],
        daily_stats: [],
        daily_goals: {},
        total_2025_ytd: 600,
        reservation_goal: 120,
        history: {}
    }
};

describe('useRankingData', () => {
    it('returns correct data for selected month', () => {
        const { result } = renderHook(() =>
            useRankingData(mockMonthlyData, '2026-01', 'all', '')
        );

        expect(result.current.currentMonthData.goal).toBe(100);
        expect(result.current.totalReservas).toBe(120);
        expect(result.current.squadBrokers).toHaveLength(2);
        expect(result.current.otherBrokers).toHaveLength(1);
    });

    it('filters brokers by squad', () => {
        const { result } = renderHook(() =>
            useRankingData(mockMonthlyData, '2026-01', 'carlos@assetplan.cl', '')
        );

        expect(result.current.filteredBrokers).toHaveLength(2);
        expect(result.current.filteredBrokers.every(b => b.coord === 'carlos@assetplan.cl')).toBe(true);
    });

    it('filters brokers by search term', () => {
        const { result } = renderHook(() =>
            useRankingData(mockMonthlyData, '2026-01', 'all', 'Juan')
        );

        expect(result.current.filteredBrokers).toHaveLength(1);
        expect(result.current.filteredBrokers[0].name).toBe('Juan Perez');
    });

    it('returns top 3 brokers', () => {
        const { result } = renderHook(() =>
            useRankingData(mockMonthlyData, '2026-01', 'all', '')
        );

        expect(result.current.topBrokers).toHaveLength(3);
        expect(result.current.topBrokers[0].name).toBe('Juan Perez');
        expect(result.current.topBrokers[1].name).toBe('Maria Garcia');
        expect(result.current.topBrokers[2].name).toBe('Pedro Lopez');
    });

    it('calculates goal progress correctly', () => {
        const { result } = renderHook(() =>
            useRankingData(mockMonthlyData, '2026-01', 'all', '')
        );

        expect(result.current.goalProgress).toBe(120);
    });

    it('aggregates data for total-year view', () => {
        const { result } = renderHook(() =>
            useRankingData(mockMonthlyData, 'total-year', 'all', '')
        );

        expect(result.current.currentMonthData.goal).toBe(220);
        expect(result.current.totalReservas).toBe(255);
    });

    it('returns empty data for non-existent month', () => {
        const { result } = renderHook(() =>
            useRankingData(mockMonthlyData, '2026-12', 'all', '')
        );

        expect(result.current.currentMonthData.goal).toBe(0);
        expect(result.current.filteredBrokers).toHaveLength(0);
    });
});
