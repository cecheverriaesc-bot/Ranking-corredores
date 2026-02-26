/**
 * Store de Estado Global con Zustand
 * Centraliza el estado de la aplicación y elimina prop drilling
 */

import { create } from 'zustand';
import { CorredorData } from '../types';

// ===================================================================
// TIPOS DEL STORE
// ===================================================================

interface User {
  email: string;
  role: 'admin' | 'coordinator' | 'broker';
  squad?: string;
  name?: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
}

interface RankingState {
  // Estado de selección
  selectedMonth: string;
  selectedSquad: string;
  view: 'dashboard' | 'laboratory' | 'strategic_lab' | 'broker_profile';
  searchTerm: string;
  selectedBrokerProfile: any | null;

  // Datos
  rankingData: CorredorData[];
  othersData: CorredorData[];
  dailyStats: any[];
  isLoading: boolean;
  error: string | null;

  // Autenticación
  auth: AuthState;

  // Actions - Selección
  setSelectedMonth: (month: string) => void;
  setSelectedSquad: (squad: string) => void;
  setView: (view: 'dashboard' | 'laboratory' | 'strategic_lab' | 'broker_profile') => void;
  setSearchTerm: (term: string) => void;
  setSelectedBrokerProfile: (broker: any | null) => void;

  // Actions - Datos
  setRankingData: (ranking: CorredorData[], others: CorredorData[]) => void;
  setDailyStats: (stats: any[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;

  // Actions - Autenticación
  login: (token: string, user: User) => void;
  logout: () => void;
  updateUser: (user: Partial<User>) => void;

  // Actions asíncronas
  fetchRankingData: (year: number, month: number) => Promise<void>;
  verifyAuth: () => Promise<boolean>;
  reset: () => void;
}

// ===================================================================
// STORE PRINCIPAL
// ===================================================================

export const useAppStore = create<RankingState>((set, get) => ({
  // Estado inicial
  selectedMonth: '2026-02',
  selectedSquad: 'all',
  view: 'dashboard',
  searchTerm: '',

  selectedBrokerProfile: null,

  rankingData: [],
  othersData: [],
  dailyStats: [],
  isLoading: false,
  error: null,

  auth: {
    user: null,
    token: null,
    isAuthenticated: false,
  },

  // Actions - Selección
  setSelectedMonth: (month) => set({ selectedMonth: month }),

  setSelectedSquad: (squad) => set({ selectedSquad: squad }),

  setView: (view) => set({ view }),

  setSearchTerm: (term) => set({ searchTerm: term }),

  setSelectedBrokerProfile: (broker) => set({ selectedBrokerProfile: broker }),

  // Actions - Datos
  setRankingData: (ranking, others) => set({
    rankingData: ranking,
    othersData: others,
    error: null
  }),

  setDailyStats: (stats) => set({ dailyStats: stats }),

  setLoading: (loading) => set({ isLoading: loading }),

  setError: (error) => set({ error, isLoading: false }),

  // Actions - Autenticación
  login: (token, user) => set({
    auth: {
      token,
      user,
      isAuthenticated: true,
    }
  }),

  logout: () => set({
    auth: {
      token: null,
      user: null,
      isAuthenticated: false,
    }
  }),

  updateUser: (userData) => set((state) => ({
    auth: {
      ...state.auth,
      user: state.auth.user ? { ...state.auth.user, ...userData } : null,
    }
  })),

  // Actions asíncronas
  fetchRankingData: async (year, month) => {
    set({ isLoading: true, error: null });

    try {
      const response = await fetch(
        `/api/ranking?year=${year}&month=${month}`
      );

      if (!response.ok) {
        throw new Error('Error al cargar datos del ranking');
      }

      const data = await response.json();

      set({
        rankingData: data.ranking || [],
        othersData: data.others || [],
        dailyStats: data.daily_stats || [],
        isLoading: false,
      });
    } catch (error) {
      console.error('Error fetching ranking data:', error);
      set({
        error: error instanceof Error ? error.message : 'Error desconocido',
        isLoading: false
      });
    }
  },

  verifyAuth: async () => {
    const token = localStorage.getItem('auth_token');

    if (!token) {
      return false;
    }

    try {
      const response = await fetch('/api/auth/verify', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      const data = await response.json();

      if (data.valid) {
        set({
          auth: {
            token,
            user: data.user,
            isAuthenticated: true,
          }
        });
        return true;
      } else {
        // Token inválido, limpiar
        localStorage.removeItem('auth_token');
        return false;
      }
    } catch {
      return false;
    }
  },

  // Resetear estado
  reset: () => set({
    selectedMonth: '2026-02',
    selectedSquad: 'all',
    view: 'dashboard',
    searchTerm: '',
    selectedBrokerProfile: null,
    rankingData: [],
    othersData: [],
    dailyStats: [],
    isLoading: false,
    error: null,
    auth: {
      user: null,
      token: null,
      isAuthenticated: false,
    }
  }),
}));

// ===================================================================
// SELECTORES DERIVADOS
// ===================================================================

export const useFilteredBrokers = () => {
  const rankingData = useAppStore((state) => state.rankingData);
  const othersData = useAppStore((state) => state.othersData);
  const searchTerm = useAppStore((state) => state.searchTerm);
  const selectedSquad = useAppStore((state) => state.selectedSquad);

  const allBrokers = [...rankingData, ...othersData];

  let filtered = allBrokers.filter(broker =>
    broker.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (selectedSquad !== 'all') {
    filtered = filtered.filter(broker => broker.coord === selectedSquad);
  }

  return filtered;
};

export const useTopBrokers = (limit: number = 3) => {
  const filteredBrokers = useFilteredBrokers();

  return [...filteredBrokers]
    .sort((a, b) => b.val - a.val)
    .slice(0, limit);
};

export const useAuth = () => {
  const auth = useAppStore((state) => state.auth);
  const login = useAppStore((state) => state.login);
  const logout = useAppStore((state) => state.logout);
  const updateUser = useAppStore((state) => state.updateUser);

  return {
    ...auth,
    login,
    logout,
    updateUser,
  };
};

export const useSelectedMonth = () => {
  const selectedMonth = useAppStore((state) => state.selectedMonth);
  const setSelectedMonth = useAppStore((state) => state.setSelectedMonth);

  return { selectedMonth, setSelectedMonth };
};

export const useView = () => {
  const view = useAppStore((state) => state.view);
  const setView = useAppStore((state) => state.setView);
  const selectedBrokerProfile = useAppStore((state) => state.selectedBrokerProfile);
  const setSelectedBrokerProfile = useAppStore((state) => state.setSelectedBrokerProfile);

  return { view, setView, selectedBrokerProfile, setSelectedBrokerProfile };
};
