import React from 'react';
import { TeamConfig } from '../../types';

interface SquadFilterProps {
    teams: TeamConfig[];
    selectedSquad: string;
    onSquadChange: (squad: string) => void;
}

const SquadFilter: React.FC<SquadFilterProps> = ({
    teams,
    selectedSquad,
    onSquadChange
}) => {
    return (
        <div className="flex items-center gap-2 flex-wrap">
            <button
                onClick={() => onSquadChange('all')}
                className={`px-4 py-2 rounded-xl text-xs font-bold uppercase tracking-wider transition-all ${
                    selectedSquad === 'all'
                        ? 'bg-gradient-to-r from-blue-500 to-indigo-500 text-white shadow-lg shadow-blue-500/20'
                        : 'bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-white'
                }`}
            >
                Todos
            </button>
            {teams.filter(t => t.my).map(team => (
                <button
                    key={team.name}
                    onClick={() => onSquadChange(team.name)}
                    className={`px-4 py-2 rounded-xl text-xs font-bold uppercase tracking-wider transition-all ${
                        selectedSquad === team.name
                            ? 'bg-gradient-to-r from-blue-500 to-indigo-500 text-white shadow-lg shadow-blue-500/20'
                            : 'bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-white'
                    }`}
                    style={{
                        backgroundColor: selectedSquad === team.name ? undefined : undefined
                    }}
                >
                    {team.icon} {team.name.split('@')[0]}
                </button>
            ))}
        </div>
    );
};

export default SquadFilter;
