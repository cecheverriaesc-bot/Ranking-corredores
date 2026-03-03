import React from 'react';
import { Trophy } from 'lucide-react';
import { MonthData } from '../../../types';

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

interface MonthSelectorProps {
    selected: string;
    onChange: (month: string) => void;
    monthlyData: Record<string, MonthData>;
    year?: number;
}

const MonthSelector: React.FC<MonthSelectorProps> = ({
    selected,
    onChange,
    monthlyData,
    year = 2026
}) => {
    const availableMonths = Object.keys(monthlyData || {}).sort();
    const currentYear = availableMonths.some(m => m.startsWith(String(year)))
        ? String(year)
        : availableMonths[0]?.split('-')[0] || String(year);
    const allMonths = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'];

    const lastAvailableMonth = availableMonths.length > 0
        ? availableMonths[availableMonths.length - 1]
        : null;
    const lastAvailableMonthNum = lastAvailableMonth
        ? parseInt(lastAvailableMonth.split('-')[1], 10)
        : 0;
    const isTotalYear = selected === 'total-year';

    return (
        <div className="flex items-center gap-3">
            <div className="flex flex-col items-center">
                <span className="text-2xl font-black text-white tracking-tight">{currentYear}</span>
            </div>
            <div className="flex items-center gap-1 bg-slate-800/30 px-4 py-3 rounded-2xl border border-slate-700/50">
                {allMonths.map((monthNum, index) => {
                    const monthKey = `${currentYear}-${monthNum}`;
                    const monthName = MONTH_NAMES[monthNum];
                    const hasData = (monthlyData || {})[monthKey];
                    const isSelected = selected === monthKey;
                    const monthIndex = parseInt(monthNum, 10);
                    const isCompleted = hasData || (lastAvailableMonthNum > 0 && monthIndex <= lastAvailableMonthNum);
                    const isFuture = !hasData && monthIndex > lastAvailableMonthNum;

                    return (
                        <React.Fragment key={monthKey}>
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
                                {hasData && !isSelected && (
                                    <span className="absolute -bottom-0.5 w-1 h-1 bg-emerald-400 rounded-full"></span>
                                )}
                                {isSelected && (
                                    <span className="absolute -bottom-0.5 w-1 h-1 bg-white rounded-full animate-pulse"></span>
                                )}
                            </button>
                            {index < allMonths.length - 1 && (
                                <div className={`w-1 h-0.5 transition-colors duration-300 ${isCompleted && allMonths[index + 1] && (
                                    (monthlyData || {})[`${currentYear}-${allMonths[index + 1]}`] ||
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

export default MonthSelector;
