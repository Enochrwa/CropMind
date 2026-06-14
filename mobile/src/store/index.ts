import { create } from 'zustand';
import { User, DiagnosisResult } from '../services/api';

interface AppState {
  // Auth
  user: User | null;
  token: string | null;
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  logout: () => void;

  // Current diagnosis
  currentDiagnosis: DiagnosisResult | null;
  setCurrentDiagnosis: (d: DiagnosisResult | null) => void;

  // Language
  language: string;
  setLanguage: (lang: string) => void;

  // Offline queue
  offlineQueue: Array<{ id: string; payload: unknown; createdAt: string }>;
  addToOfflineQueue: (payload: unknown) => void;
  clearOfflineQueue: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  user: null,
  token: null,
  setUser: (user) => set({ user }),
  setToken: (token) => set({ token }),
  logout: () => set({ user: null, token: null }),

  currentDiagnosis: null,
  setCurrentDiagnosis: (currentDiagnosis) => set({ currentDiagnosis }),

  language: 'en',
  setLanguage: (language) => set({ language }),

  offlineQueue: [],
  addToOfflineQueue: (payload) =>
    set((state) => ({
      offlineQueue: [
        ...state.offlineQueue,
        { id: Date.now().toString(), payload, createdAt: new Date().toISOString() },
      ],
    })),
  clearOfflineQueue: () => set({ offlineQueue: [] }),
}));
