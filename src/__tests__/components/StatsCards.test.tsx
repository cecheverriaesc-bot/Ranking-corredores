import { render, screen } from '@testing-library/react';
import StatsCards from '../../components/dashboard/StatsCards';

describe('StatsCards', () => {
    const defaultProps = {
        totalReservas: 100,
        totalContracts: 80,
        totalLeads: 500,
        totalAgendas: 150,
        goal: 120,
        contractGoal: 100,
        goalProgress: 83,
        globalQualified: 25,
        teamHealth: { total: 10, meeting: 8, pct: 80 },
        reservationGoal: 120
    };

    it('renders total reservas', () => {
        render(<StatsCards {...defaultProps} />);
        expect(screen.getByText('100')).toBeInTheDocument();
    });

    it('renders total contracts', () => {
        render(<StatsCards {...defaultProps} />);
        expect(screen.getByText('80')).toBeInTheDocument();
    });

    it('renders total leads', () => {
        render(<StatsCards {...defaultProps} />);
        expect(screen.getByText('500')).toBeInTheDocument();
    });

    it('renders total agendas', () => {
        render(<StatsCards {...defaultProps} />);
        expect(screen.getByText('150')).toBeInTheDocument();
    });

    it('renders goal progress percentage', () => {
        render(<StatsCards {...defaultProps} />);
        expect(screen.getByText('83%')).toBeInTheDocument();
    });

    it('renders qualified count', () => {
        render(<StatsCards {...defaultProps} />);
        expect(screen.getByText('25')).toBeInTheDocument();
    });

    it('renders team health percentage', () => {
        render(<StatsCards {...defaultProps} />);
        expect(screen.getByText('80%')).toBeInTheDocument();
    });

    it('renders all card labels', () => {
        render(<StatsCards {...defaultProps} />);
        
        expect(screen.getByText('Reservas')).toBeInTheDocument();
        expect(screen.getByText('Contratos')).toBeInTheDocument();
        expect(screen.getByText('Leads')).toBeInTheDocument();
        expect(screen.getByText('Agendas')).toBeInTheDocument();
        expect(screen.getByText('Progreso')).toBeInTheDocument();
        expect(screen.getByText('Calificados')).toBeInTheDocument();
        expect(screen.getByText('Equipo Salud')).toBeInTheDocument();
    });
});
