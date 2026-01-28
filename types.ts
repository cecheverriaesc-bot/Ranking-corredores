
export interface CorredorData {
  name: string;
  val: number;
  fallen: number;
  leads: number;
  agendas: number;
  coord: string;
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
  cur: number;
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
  totalActual: number;
  total2025Today: number;
  globalQualified: number;
  squadStats: Record<string, SquadStats>;
  accMetaToToday: number;
  accRealToToday: number;
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