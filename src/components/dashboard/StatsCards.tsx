import React from 'react';
import { TrendingUp, Users, FileText, Calendar, Target, Award } from 'lucide-react';

interface StatsCardsProps {
    totalReservas: number;
    totalContracts: number;
    totalLeads: number;
    totalAgendas: number;
    goal: number;
    contractGoal: number;
    goalProgress: number;
    globalQualified: number;
    teamHealth: { total: number; meeting: number; pct: number };
    reservationGoal?: number;
}

const StatCard: React.FC<{
    icon: React.ReactNode;
    label: string;
    value: string | number;
    subValue?: string;
    color: string;
    bgColor: string;
}> = ({ icon, label, value, subValue, color, bgColor }) => (
    <div className="bg-slate-800/50 rounded-2xl p-4 border border-slate-700/50">
        <div className="flex items-center gap-3">
            <div className={`p-2.5 rounded-xl ${bgColor}`}>
                {icon}
            </div>
            <div>
                <p className="text-slate-400 text-xs font-bold uppercase tracking-wider">{label}</p>
                <p className={`text-xl font-black ${color}`}>{value}</p>
                {subValue && <p className="text-slate-500 text-[10px]">{subValue}</p>}
            </div>
        </div>
    </div>
);

const StatsCards: React.FC<StatsCardsProps> = ({
    totalReservas,
    totalContracts,
    totalLeads,
    totalAgendas,
    goal,
    contractGoal,
    goalProgress,
    globalQualified,
    teamHealth,
    reservationGoal
}) => {
    return (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
                icon={<TrendingUp className="text-blue-400" size={20} />}
                label="Reservas"
                value={totalReservas}
                subValue={`Meta: ${reservationGoal || goal}`}
                color="text-blue-400"
                bgColor="bg-blue-500/20"
            />
            <StatCard
                icon={<FileText className="text-emerald-400" size={20} />}
                label="Contratos"
                value={totalContracts}
                subValue={`Meta: ${contractGoal}`}
                color="text-emerald-400"
                bgColor="bg-emerald-500/20"
            />
            <StatCard
                icon={<Users className="text-purple-400" size={20} />}
                label="Leads"
                value={totalLeads}
                color="text-purple-400"
                bgColor="bg-purple-500/20"
            />
            <StatCard
                icon={<Calendar className="text-amber-400" size={20} />}
                label="Agendas"
                value={totalAgendas}
                color="text-amber-400"
                bgColor="bg-amber-500/20"
            />
            <StatCard
                icon={<Target className="text-cyan-400" size={20} />}
                label="Progreso"
                value={`${goalProgress}%`}
                subValue={`${totalReservas} / ${reservationGoal || goal}`}
                color="text-cyan-400"
                bgColor="bg-cyan-500/20"
            />
            <StatCard
                icon={<Award className="text-rose-400" size={20} />}
                label="Calificados"
                value={globalQualified}
                color="text-rose-400"
                bgColor="bg-rose-500/20"
            />
            <StatCard
                icon={<Users className="text-emerald-400" size={20} />}
                label="Equipo Salud"
                value={`${teamHealth.pct}%`}
                subValue={`${teamHealth.meeting}/${teamHealth.total} reuniones`}
                color="text-emerald-400"
                bgColor="bg-emerald-500/20"
            />
            <StatCard
                icon={<Target className="text-indigo-400" size={20} />}
                label="Meta Diaria"
                value={Math.round((reservationGoal || goal) / 28)}
                subValue="reservas/día"
                color="text-indigo-400"
                bgColor="bg-indigo-500/20"
            />
        </div>
    );
};

export default StatsCards;
