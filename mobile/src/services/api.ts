import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import * as SecureStore from 'expo-secure-store';

const BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'https://api.cropmind.app/api/v1';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: BASE_URL,
      timeout: 30000,
      headers: { 'Content-Type': 'application/json' },
    });

    // Attach token to every request
    this.client.interceptors.request.use(async (config) => {
      const token = await SecureStore.getItemAsync('access_token');
      if (token) config.headers.Authorization = `Bearer ${token}`;
      return config;
    });

    // Handle 401 globally
    this.client.interceptors.response.use(
      (res) => res,
      async (error) => {
        if (error.response?.status === 401) {
          await SecureStore.deleteItemAsync('access_token');
          // Navigate to login — handled by router
        }
        return Promise.reject(error);
      }
    );
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const res = await this.client.get<T>(url, config);
    return res.data;
  }

  async post<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    const res = await this.client.post<T>(url, data, config);
    return res.data;
  }
}

export const api = new ApiClient();

// ─── Auth ───────────────────────────────────────────────────────────────────

export interface RegisterPayload {
  phone?: string;
  email?: string;
  password: string;
  full_name?: string;
  language?: string;
  country_code?: string;
}

export interface LoginPayload {
  identifier: string;
  password: string;
}

export const authApi = {
  register: (payload: RegisterPayload) =>
    api.post<{ access_token: string; user: User }>('/auth/register', payload),
  login: (payload: LoginPayload) =>
    api.post<{ access_token: string; user: User }>('/auth/login', payload),
  me: () => api.get<User>('/auth/me'),
};

// ─── Diagnosis ──────────────────────────────────────────────────────────────

export interface DiagnosePayload {
  device_prediction: string;
  device_confidence: number;
  crop_type: string;
  farm_id?: string;
  image_key?: string;
  latitude?: number;
  longitude?: number;
  language?: string;
}

export const diagnoseApi = {
  enrich: (payload: DiagnosePayload) =>
    api.post<DiagnosisResult>('/diagnose/enrich', payload),
  voiceQuestion: (formData: FormData) =>
    api.post<{ question: string; answer: string }>('/diagnose/voice-question', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
};

// ─── Balance ────────────────────────────────────────────────────────────────

export const balanceApi = {
  get: () => api.get<{ balance_rwf: number }>('/balance/'),
  topup: (amount_rwf: number, payment_reference?: string) =>
    api.post<{ balance_rwf: number }>('/balance/topup', { amount_rwf, payment_reference }),
  transactions: (limit = 20, offset = 0) =>
    api.get<Transaction[]>(`/balance/transactions?limit=${limit}&offset=${offset}`),
};

// ─── History ────────────────────────────────────────────────────────────────

export const historyApi = {
  list: (limit = 20, offset = 0) =>
    api.get<HistoryItem[]>(`/history/?limit=${limit}&offset=${offset}`),
};

// ─── Types ──────────────────────────────────────────────────────────────────

export interface User {
  id: string;
  phone?: string;
  email?: string;
  full_name?: string;
  language: string;
  country_code?: string;
  region?: string;
  balance_rwf: number;
  diagnosis_count: number;
  is_verified: boolean;
  created_at: string;
}

export interface TreatmentStep {
  step: number;
  action: string;
  product?: string;
  timing?: string;
}

export interface SupplierResult {
  id: string;
  name: string;
  phone?: string;
  whatsapp?: string;
  distance_km: number;
  address?: string;
  is_verified: boolean;
  rating: number;
}

export interface MarketPrice {
  crop: string;
  price_per_kg_rwf: number;
  price_per_kg_usd: number;
  market: string;
  updated_at: string;
}

export interface DiagnosisResult {
  diagnosis_id: string;
  is_enriched: boolean;
  cost_rwf: number;
  balance_remaining: number;
  result: {
    disease_display_name: string;
    severity: string;
    confidence: number;
    description: string;
    urgency_message: string;
    treatment_steps: TreatmentStep[];
    prevention_tips: string[];
    suppliers: SupplierResult[];
    market_prices: MarketPrice[];
    language: string;
  };
  created_at: string;
}

export interface Transaction {
  id: string;
  type: string;
  amount_rwf: number;
  balance_after: number;
  description?: string;
  created_at: string;
}

export interface HistoryItem {
  id: string;
  disease: string;
  crop: string;
  severity: string;
  confidence: number;
  cost_rwf: number;
  created_at: string;
}
