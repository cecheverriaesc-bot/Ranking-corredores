import React, { useState, useEffect } from 'react';
import {
    X, Target, TrendingUp, Calendar, MessageSquare, Save,
    AlertCircle, CheckCircle2, Sparkles, ArrowUpRight, Info
} from 'lucide-react';
import { BrokerGoalData, SuggestedGoalCalculation } from '../types';

interface GoalSettingModalProps {
    isOpen: boolean;
    onClose: () => void;
    brokerName: string;
    brokerEmail?: string;
    currentGoal?: number;
    currentReservas: number;
    selectedMonth: string;  // Format: YYYY-MM
    onSave: (goalData: BrokerGoalData) => void;
    isEditing?: boolean;
}

const GoalSettingModal: React.FC<GoalSettingModalProps> = ({
    isOpen,
    onClose,
    brokerName,
    brokerEmail: initialBrokerEmail,
    currentGoal,
    currentReservas,
    selectedMonth,
    onSave,
    isEditing = false
}) => {
    const [personalGoal, setPersonalGoal] = useState<number>(currentGoal || 0);
    const [commitmentComment, setCommitmentComment] = useState<string>('');
    const [brokerEmail, setBrokerEmail] = useState<string>(initialBrokerEmail || '');
    const [suggestedGoal, setSuggestedGoal] = useState<SuggestedGoalCalculation | null>(null);
    const [isLoadingSuggestion, setIsLoadingSuggestion] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [showConfetti, setShowConfetti] = useState(false);

    // Month names
    const monthNames: Record<string, string> = {
        '2026-01': 'Enero 2026',
        '2026-02': 'Febrero 2026',
        '2026-03': 'Marzo 2026',
        '2026-04': 'Abril 2026',
        '2026-05': 'Mayo 2026',
        '2026-06': 'Junio 2026',
        '2026-07': 'Julio 2026',
        '2026-08': 'Agosto 2026',
        '2026-09': 'Septiembre 2026',
        '2026-10': 'Octubre 2026',
        '2026-11': 'Noviembre 2026',
        '2026-12': 'Diciembre 2026'
    };

    // Reset form when modal opens
    useEffect(() => {
        if (isOpen) {
            setPersonalGoal(currentGoal || 0);
            setCommitmentComment('');
            setBrokerEmail(initialBrokerEmail || '');
            setSuggestedGoal(null);
            
            // Si ya tiene meta configurada, mostrar mensaje de solo lectura
            if (currentGoal && currentGoal > 0 && isEditing) {
                // En modo edición, solo mostrar info
            }
        }
    }, [isOpen, currentGoal, initialBrokerEmail, isEditing]);

    // Fetch suggested goal when modal opens
    useEffect(() => {
        if (isOpen && !suggestedGoal) {
            fetchSuggestedGoal();
        }
    }, [isOpen]);

    const fetchSuggestedGoal = async () => {
        setIsLoadingSuggestion(true);
        try {
            const response = await fetch(
                `/api/v4_goals/suggest?broker=${encodeURIComponent(brokerName)}&month=${selectedMonth}-01`
            );
            const data = await response.json();
            setSuggestedGoal(data);
        } catch (error) {
            console.error('Error fetching suggested goal:', error);
        } finally {
            setIsLoadingSuggestion(false);
        }
    };

    const handleSave = async () => {
        if (personalGoal <= 0) {
            alert('La meta debe ser mayor a 0');
            return;
        }

        setIsSaving(true);
        try {
            const goalData: BrokerGoalData = {
                broker_name: brokerName,
                broker_email: brokerEmail,
                goal_month: `${selectedMonth}-01`,
                personal_goal: personalGoal,
                suggested_goal: suggestedGoal?.suggested_goal || 0,
                commitment_comment: commitmentComment,
                calculation_method: personalGoal === suggestedGoal?.suggested_goal ? 'projection' : 'manual'
            };

            const response = await fetch('/api/v4_goals', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(goalData)
            });

            const result = await response.json();
            
            if (result.success) {
                setShowConfetti(true);
                setTimeout(() => {
                    setShowConfetti(false);
                    onSave(goalData);
                    onClose();
                }, 1500);
            } else {
                alert('Error al guardar: ' + result.message);
            }
        } catch (error) {
            console.error('Error saving goal:', error);
            alert('Error al guardar la meta');
        } finally {
            setIsSaving(false);
        }
    };

    const useSuggestedGoal = () => {
        if (suggestedGoal) {
            setPersonalGoal(suggestedGoal.suggested_goal);
        }
    };

    if (!isOpen) return null;

    const progressPercentage = currentReservas > 0 && personalGoal > 0 
        ? Math.min((currentReservas / personalGoal) * 100, 150) 
        : 0;

    const isGoalAchieved = currentReservas >= personalGoal && personalGoal > 0;

    return (
        <div className="fixed inset-0 z-[300] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
            {/* Confetti Animation */}
            {showConfetti && (
                <div className="fixed inset-0 pointer-events-none overflow-hidden">
                    {[...Array(50)].map((_, i) => (
                        <div
                            key={i}
                            className="absolute animate-confetti"
                            style={{
                                left: `${Math.random() * 100}%`,
                                top: '-10px',
                                backgroundColor: ['#10b981', '#3b82f6', '#f59e0b', '#ef4444'][Math.floor(Math.random() * 4)],
                                width: `${Math.random() * 10 + 5}px`,
                                height: `${Math.random() * 10 + 5}px`,
                                animationDelay: `${Math.random() * 2}s`,
                                animationDuration: `${Math.random() * 2 + 2}s`
                            }}
                        />
                    ))}
                </div>
            )}

            <div className="bg-[#1e293b] rounded-3xl border border-[#324467] shadow-2xl w-full max-w-2xl animate-in zoom-in-95 duration-200">
                {/* Header */}
                <div className="flex justify-between items-center p-6 border-b border-[#324467]">
                    <div className="flex items-center gap-3">
                        <div className="p-3 bg-gradient-to-br from-emerald-500/20 to-blue-500/20 rounded-2xl border border-emerald-500/30">
                            <Target className="text-emerald-400" size={24} />
                        </div>
                        <div>
                            <h2 className="text-xl font-black text-white uppercase tracking-widest">
                                Configurar Meta Personal
                            </h2>
                            <p className="text-xs text-slate-400 font-bold uppercase tracking-wide mt-0.5">
                                {monthNames[selectedMonth] || selectedMonth}
                            </p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-slate-800 rounded-xl transition-colors text-slate-400 hover:text-white"
                    >
                        <X size={20} />
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 space-y-6">
                    {/* Broker Info */}
                    <div className="bg-[#101622] rounded-2xl p-4 border border-[#324467]">
                        <div className="flex justify-between items-center">
                            <div>
                                <p className="text-xs text-slate-500 font-bold uppercase tracking-wide">Corredor</p>
                                <p className="text-lg font-black text-white mt-0.5">{brokerName}</p>
                            </div>
                            <div className="text-right">
                                <p className="text-xs text-slate-500 font-bold uppercase tracking-wide">Reservas Actuales</p>
                                <p className="text-3xl font-black text-blue-400 mt-0.5">{currentReservas}</p>
                            </div>
                        </div>
                    </div>

                    {/* Suggested Goal Card */}
                    {isLoadingSuggestion ? (
                        <div className="bg-gradient-to-br from-amber-950/30 to-slate-950/50 rounded-2xl p-6 border border-amber-500/20">
                            <div className="flex items-center gap-3">
                                <Sparkles className="text-amber-400 animate-pulse" size={20} />
                                <p className="text-amber-400 font-bold text-sm uppercase tracking-wide">
                                    Calculando meta sugerida...
                                </p>
                            </div>
                        </div>
                    ) : suggestedGoal ? (
                        <div className="bg-gradient-to-br from-amber-950/30 to-slate-950/50 rounded-2xl p-6 border border-amber-500/30">
                            <div className="flex justify-between items-start mb-4">
                                <div className="flex items-center gap-2">
                                    <Sparkles className="text-amber-400" size={20} />
                                    <h3 className="text-sm font-black text-amber-400 uppercase tracking-widest">
                                        Meta Sugerida por IA
                                    </h3>
                                </div>
                                <span className={`px-2 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wide ${
                                    suggestedGoal.confidence === 'high' 
                                        ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                                        : suggestedGoal.confidence === 'medium'
                                        ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30'
                                        : 'bg-slate-500/20 text-slate-400 border border-slate-500/30'
                                }`}>
                                    Confianza: {suggestedGoal.confidence}
                                </span>
                            </div>

                            <div className="grid grid-cols-2 gap-4 mb-4">
                                <div className="bg-slate-950/50 rounded-xl p-4 border border-slate-800">
                                    <p className="text-[10px] text-slate-500 font-bold uppercase mb-1">Meta Sugerida</p>
                                    <p className="text-3xl font-black text-amber-400">{suggestedGoal.suggested_goal}</p>
                                    <p className="text-[9px] text-slate-600 font-bold uppercase mt-1">reservas</p>
                                </div>
                                <div className="bg-slate-950/50 rounded-xl p-4 border border-slate-800">
                                    <p className="text-[10px] text-slate-500 font-bold uppercase mb-1">Proyección Actual</p>
                                    <p className="text-3xl font-black text-blue-400">
                                        {suggestedGoal.breakdown.current_projection?.toFixed(0) || '0'}
                                    </p>
                                    <p className="text-[9px] text-slate-600 font-bold uppercase mt-1">reservas/mes</p>
                                </div>
                            </div>

                            {/* Breakdown */}
                            <div className="grid grid-cols-3 gap-2 text-[10px]">
                                <div className="bg-slate-900/50 rounded-lg p-2 border border-slate-800">
                                    <p className="text-slate-500 font-bold">Promedio 3M</p>
                                    <p className="text-white font-black">{suggestedGoal.breakdown.historical_avg_3m?.toFixed(1) || '0'}</p>
                                </div>
                                <div className="bg-slate-900/50 rounded-lg p-2 border border-slate-800">
                                    <p className="text-slate-500 font-bold">Máx 3M</p>
                                    <p className="text-white font-black">{suggestedGoal.breakdown.max_last_3m || 0}</p>
                                </div>
                                <div className="bg-slate-900/50 rounded-lg p-2 border border-slate-800">
                                    <p className="text-slate-500 font-bold">Feb 2025</p>
                                    <p className="text-white font-black">{suggestedGoal.breakdown.prev_year_same_month || 0}</p>
                                </div>
                            </div>

                            <button
                                onClick={useSuggestedGoal}
                                className="w-full mt-4 py-3 bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/50 rounded-xl text-amber-400 font-bold text-sm uppercase tracking-widest transition-all flex items-center justify-center gap-2"
                            >
                                <ArrowUpRight size={16} />
                                Usar Meta Sugerida ({suggestedGoal.suggested_goal} reservas)
                            </button>
                        </div>
                    ) : null}

                    {/* Personal Goal Input */}
                    <div>
                        <label className="block text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">
                            Tu Meta Personal (reservas)
                        </label>
                        <div className="relative">
                            <input
                                type="number"
                                value={personalGoal || ''}
                                onChange={(e) => setPersonalGoal(parseInt(e.target.value) || 0)}
                                placeholder="Ej: 45"
                                className="w-full bg-[#101622] text-white text-3xl font-black px-6 py-4 rounded-2xl border border-[#324467] focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 outline-none transition-all text-center"
                            />
                            {personalGoal > 0 && (
                                <div className="absolute right-4 top-1/2 -translate-y-1/2">
                                    {isGoalAchieved ? (
                                        <CheckCircle2 className="text-emerald-400" size={24} />
                                    ) : (
                                        <Info className="text-slate-500" size={24} />
                                    )}
                                </div>
                            )}
                        </div>

                        {/* Progress Preview */}
                        {personalGoal > 0 && (
                            <div className="mt-4 space-y-2">
                                <div className="flex justify-between text-xs">
                                    <span className="text-slate-500 font-bold uppercase">Progreso</span>
                                    <span className={`font-black ${isGoalAchieved ? 'text-emerald-400' : 'text-blue-400'}`}>
                                        {progressPercentage.toFixed(0)}%
                                    </span>
                                </div>
                                <div className="h-3 w-full bg-[#101622] rounded-full overflow-hidden border border-[#324467]">
                                    <div
                                        className={`h-full rounded-full transition-all duration-500 ${
                                            isGoalAchieved 
                                                ? 'bg-gradient-to-r from-emerald-600 to-emerald-400 shadow-[0_0_15px_rgba(52,211,153,0.5)]' 
                                                : progressPercentage > 70
                                                ? 'bg-gradient-to-r from-blue-600 to-blue-400'
                                                : 'bg-gradient-to-r from-slate-600 to-slate-400'
                                        }`}
                                        style={{ width: `${progressPercentage}%` }}
                                    />
                                </div>
                                <div className="flex justify-between text-[10px]">
                                    <span className="text-slate-600 font-bold">
                                        {currentReservas} reservas actuales
                                    </span>
                                    <span className="text-slate-600 font-bold">
                                        {personalGoal} meta
                                    </span>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Commitment Comment */}
                    <div>
                        <label className="block text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">
                            <MessageSquare size={14} className="inline mr-1.5" />
                            Tu Compromiso (opcional)
                        </label>
                        <textarea
                            value={commitmentComment}
                            onChange={(e) => setCommitmentComment(e.target.value)}
                            placeholder="Ej: 'Este mes me comprometo a contactar todos los leads en menos de 1 hora y agendar 3 visitas diarias...'"
                            rows={3}
                            className="w-full bg-[#101622] text-white text-sm px-4 py-3 rounded-xl border border-[#324467] focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all resize-none"
                        />
                        <p className="text-[10px] text-slate-600 font-bold mt-2">
                            Este comentario será visible para tu coordinador y te ayudará a mantener el foco.
                        </p>
                    </div>

                    {/* Warning if no goal set */}
                    {!currentGoal && (
                        <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-4 flex items-start gap-3">
                            <AlertCircle className="text-blue-400 flex-shrink-0 mt-0.5" size={18} />
                            <div>
                                <p className="text-xs text-blue-400 font-bold">
                                    Aún no has configurado tu meta este mes
                                </p>
                                <p className="text-[10px] text-slate-500 mt-1">
                                    Los corredores con meta definida tienen 3x más probabilidades de alcanzar sus objetivos.
                                </p>
                            </div>
                        </div>
                    )}
                </div>

                {/* Footer Actions */}
                <div className="p-6 border-t border-[#324467] flex gap-3">
                    <button
                        onClick={onClose}
                        className="flex-1 py-3 rounded-xl border border-slate-700 text-slate-400 hover:text-white hover:bg-slate-800 transition-all text-sm font-bold uppercase tracking-widest"
                    >
                        Cancelar
                    </button>
                    <button
                        onClick={handleSave}
                        disabled={isSaving || personalGoal <= 0}
                        className="flex-1 py-3 rounded-xl bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 disabled:from-slate-700 disabled:to-slate-600 disabled:cursor-not-allowed text-white font-black text-sm uppercase tracking-widest transition-all flex items-center justify-center gap-2 shadow-lg shadow-emerald-500/20"
                    >
                        {isSaving ? (
                            <>
                                <div className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                                Guardando...
                            </>
                        ) : (
                            <>
                                <Save size={18} />
                                Guardar Meta
                            </>
                        )}
                    </button>
                </div>
            </div>

            {/* Custom Confetti Animation */}
            <style>{`
                @keyframes confetti {
                    0% {
                        transform: translateY(0) rotate(0deg);
                        opacity: 1;
                    }
                    100% {
                        transform: translateY(100vh) rotate(720deg);
                        opacity: 0;
                    }
                }
                .animate-confetti {
                    animation: confetti linear forwards;
                }
            `}</style>
        </div>
    );
};

export default GoalSettingModal;
