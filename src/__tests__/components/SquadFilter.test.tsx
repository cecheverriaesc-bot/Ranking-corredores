/**
 * @jest-environment jsdom
 */

import { render, screen, fireEvent } from '@testing-library/react';
import SquadFilter from '../../components/dashboard/SquadFilter';
import { TeamConfig } from '../../../types';

const mockTeams: TeamConfig[] = [
    { name: 'carlos@assetplan.cl', icon: '🔥', color: 'red', bg: 'bg-red-500', my: true },
    { name: 'luis@assetplan.cl', icon: '💧', color: 'blue', bg: 'bg-blue-500', my: true },
    { name: 'otro@assetplan.cl', icon: '⭐', color: 'yellow', bg: 'bg-yellow-500', my: false }
];

describe('SquadFilter', () => {
    const mockOnSquadChange = jest.fn();

    beforeEach(() => {
        jest.clearAllMocks();
    });

    it('renders Todos button', () => {
        render(
            <SquadFilter
                teams={mockTeams}
                selectedSquad="all"
                onSquadChange={mockOnSquadChange}
            />
        );

        expect(screen.getByText('Todos')).toBeInTheDocument();
    });

    it('renders only my teams', () => {
        render(
            <SquadFilter
                teams={mockTeams}
                selectedSquad="all"
                onSquadChange={mockOnSquadChange}
            />
        );

        expect(screen.getByText((content, element) => 
            element?.tagName.toLowerCase() === 'button' && content.includes('carlos')
        )).toBeInTheDocument();
        expect(screen.getByText((content, element) => 
            element?.tagName.toLowerCase() === 'button' && content.includes('luis')
        )).toBeInTheDocument();
        expect(screen.queryByText('otro')).not.toBeInTheDocument();
    });

    it('calls onSquadChange with all when Todos is clicked', () => {
        render(
            <SquadFilter
                teams={mockTeams}
                selectedSquad="carlos@assetplan.cl"
                onSquadChange={mockOnSquadChange}
            />
        );

        fireEvent.click(screen.getByText('Todos'));
        expect(mockOnSquadChange).toHaveBeenCalledWith('all');
    });

    it('calls onSquadChange with team email when team button is clicked', () => {
        render(
            <SquadFilter
                teams={mockTeams}
                selectedSquad="all"
                onSquadChange={mockOnSquadChange}
            />
        );

        const carlosButton = screen.getByText((content, element) => 
            element?.tagName.toLowerCase() === 'button' && content.includes('carlos')
        );
        fireEvent.click(carlosButton);
        expect(mockOnSquadChange).toHaveBeenCalledWith('carlos@assetplan.cl');
    });

    it('highlights selected squad', () => {
        render(
            <SquadFilter
                teams={mockTeams}
                selectedSquad="luis@assetplan.cl"
                onSquadChange={mockOnSquadChange}
            />
        );

        const luisButton = screen.getByText((content, element) => 
            element?.tagName.toLowerCase() === 'button' && content.includes('luis')
        );
        expect(luisButton).toHaveClass('from-blue-500');
    });
});
