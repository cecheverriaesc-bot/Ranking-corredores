/**
 * @jest-environment jsdom
 */

import { render, screen, fireEvent } from '@testing-library/react';
import MonthSelector from '../../components/dashboard/MonthSelector';
import { MonthData } from '../../../types';

const mockMonthlyData: Record<string, MonthData> = {
    '2026-01': {
        goal: 100,
        contract_goal: 100,
        ranking: [],
        others: [],
        daily_stats: [],
        daily_goals: {},
        total_2025_ytd: 500,
        history: {},
        reservation_goal: 100
    },
    '2026-02': {
        goal: 120,
        contract_goal: 120,
        ranking: [],
        others: [],
        daily_stats: [],
        daily_goals: {},
        total_2025_ytd: 600,
        history: {},
        reservation_goal: 120
    }
};

describe('MonthSelector', () => {
    const mockOnChange = jest.fn();

    beforeEach(() => {
        jest.clearAllMocks();
    });

    it('renders all 12 months', () => {
        render(
            <MonthSelector
                selected="2026-01"
                onChange={mockOnChange}
                monthlyData={mockMonthlyData}
            />
        );

        expect(screen.getByText('Ene')).toBeInTheDocument();
        expect(screen.getByText('Feb')).toBeInTheDocument();
        expect(screen.getByText('Mar')).toBeInTheDocument();
    });

    it('renders year label', () => {
        render(
            <MonthSelector
                selected="2026-01"
                onChange={mockOnChange}
                monthlyData={mockMonthlyData}
            />
        );

        expect(screen.getByText('2026')).toBeInTheDocument();
    });

    it('renders Total button', () => {
        render(
            <MonthSelector
                selected="2026-01"
                onChange={mockOnChange}
                monthlyData={mockMonthlyData}
            />
        );

        expect(screen.getByText('Total')).toBeInTheDocument();
    });

    it('calls onChange when month is clicked', () => {
        render(
            <MonthSelector
                selected="2026-01"
                onChange={mockOnChange}
                monthlyData={mockMonthlyData}
            />
        );

        fireEvent.click(screen.getByText('Feb'));
        expect(mockOnChange).toHaveBeenCalledWith('2026-02');
    });

    it('calls onChange with total-year when Total is clicked', () => {
        render(
            <MonthSelector
                selected="2026-01"
                onChange={mockOnChange}
                monthlyData={mockMonthlyData}
            />
        );

        fireEvent.click(screen.getByText('Total'));
        expect(mockOnChange).toHaveBeenCalledWith('total-year');
    });

    it('highlights selected month', () => {
        render(
            <MonthSelector
                selected="2026-02"
                onChange={mockOnChange}
                monthlyData={mockMonthlyData}
            />
        );

        const febButton = screen.getByText('Feb');
        expect(febButton).toHaveClass('scale-110');
    });

    it('disables future months', () => {
        render(
            <MonthSelector
                selected="2026-01"
                onChange={mockOnChange}
                monthlyData={mockMonthlyData}
            />
        );

        const decButton = screen.getByText('Dic');
        expect(decButton).toBeDisabled();
    });
});
