
export interface CorredorData {
  name: string;
  val: number;
  fallen: number;
  leads: number;
  agendas: number;
  coord: string;
  contracts: number;
  personalMeta?: number; // Added for individual goal tracking
  hidden?: boolean;
}

export interface HistoryData {
  c: number; // reservas partial
  t: number; // reservas total
  l?: number; // leads total (optional)
  a?: number; // agendas total (optional)
}

export interface TeamConfig {
  name: string;
  icon: string;
  color: string;
  bg: string;
  my: boolean;
}

export interface SquadStats {
  cur: number; // Reservations
  contracts: number; // Contracts
  past: number;
  qual: number;
  others: number;
  totalMembers: number;
  activeMembers: number;
  totalLeads: number;
  totalAgendas: number;
}

export interface DiagnosticItem {
  name: string;
  diff: number;
}

export interface DashboardStats {
  totalActual: number; // Reservas
  totalContracts: number; // Contratos Reales BI
  total2025Today: number;
  globalQualified: number;
  squadStats: Record<string, SquadStats>;
  accMetaToToday: number; // Meta Reservas
  accRealToToday: number; // Real Reservas
  accMetaContractsToToday: number; // Meta Contratos
  accRealContractsToToday: number; // Real Contratos
  teamHealth: {
    total: number;
    meeting: number;
    pct: number;
  };
  diagnostics: {
    loss: DiagnosticItem[];
    lossVolume: number;
    slowdown: DiagnosticItem[];
    slowdownVolume: number;
    growth: DiagnosticItem[];
    growthVolume: number;
  };
}

export interface DailyStat {
  date: string;
  coord: string;
  count: number;
}

export interface MonthData {
  goal: number;
  contract_goal: number;
  ranking: CorredorData[];
  others: CorredorData[];
  daily_stats: DailyStat[];
  daily_goals: Record<number, number>;
  reservation_goal?: number;
  total_2025_ytd: number;
  history: Record<string, HistoryData>;
}

// ============================================
// GOAL MANAGEMENT TYPES
// ============================================

export interface BrokerGoalData {
  broker_name: string;
  broker_email?: string;
  goal_month: string;  // Format: YYYY-MM-01
  personal_goal: number;
  suggested_goal?: number;
  commitment_comment?: string;
  calculation_method?: 'historical_avg' | 'projection' | 'manual' | 'coordinator_defined';
  created_at?: string;
  updated_at?: string;
  created_by?: 'system' | 'broker' | 'coordinator';
}

export interface SuggestedGoalCalculation {
  suggested_goal: number;
  breakdown: {
    historical_avg_3m?: number;
    max_last_3m?: number;
    prev_year_same_month?: number;
    current_projection?: number;
    current_reservas?: number;
  };
  confidence: 'low' | 'medium' | 'high';
  calculation_method: string;
}

export interface GoalWithCalculation extends BrokerGoalData {
  suggested_goal_calc?: SuggestedGoalCalculation;
}