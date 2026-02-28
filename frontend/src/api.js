import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

const authApi = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

let refreshPromise = null;

const decodeJwtPayload = (token) => {
  try {
    const payload = token.split('.')[1];
    return JSON.parse(atob(payload));
  } catch (err) {
    return null;
  }
};

const isTokenExpired = (token, skewSeconds = 30) => {
  const payload = decodeJwtPayload(token);
  if (!payload?.exp) return true;
  const now = Math.floor(Date.now() / 1000);
  return payload.exp <= (now + skewSeconds);
};

const refreshAccessToken = async () => {
  const tokenRaw = localStorage.getItem('health_ai_tokens');
  if (!tokenRaw) return null;

  const parsedTokens = JSON.parse(tokenRaw);
  if (!parsedTokens?.refresh) return null;

  if (!refreshPromise) {
    refreshPromise = authApi.post('/auth/token/refresh/', {
      refresh: parsedTokens.refresh,
    })
      .then((response) => {
        const updatedTokens = {
          ...parsedTokens,
          access: response.data.access,
        };
        localStorage.setItem('health_ai_tokens', JSON.stringify(updatedTokens));
        return updatedTokens.access;
      })
      .catch((error) => {
        localStorage.removeItem('health_ai_tokens');
        localStorage.removeItem('health_ai_user');
        throw error;
      })
      .finally(() => {
        refreshPromise = null;
      });
  }

  return refreshPromise;
};

// Request interceptor to add auth token
api.interceptors.request.use(
  async (config) => {
    const tokens = localStorage.getItem('health_ai_tokens');
    if (tokens) {
      const { access } = JSON.parse(tokens);
      let finalAccess = access;

      if (access && isTokenExpired(access)) {
        finalAccess = await refreshAccessToken();
      }

      if (finalAccess) {
        config.headers.Authorization = `Bearer ${finalAccess}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    const status = error?.response?.status;

    if (status !== 401 || !originalRequest || originalRequest._retry) {
      return Promise.reject(error);
    }

    try {
      originalRequest._retry = true;
      const refreshedAccess = await refreshAccessToken();
      if (!refreshedAccess) {
        return Promise.reject(error);
      }

      originalRequest.headers.Authorization = `Bearer ${refreshedAccess}`;

      return api(originalRequest);
    } catch (refreshError) {
      return Promise.reject(refreshError);
    }
  }
);

export const symptomAPI = {
  analyze: (symptomText) => api.post('/symptom/', { symptom_text: symptomText }),
};

export const reportAPI = {
  upload: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/report/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  analyze: (reportId) => api.post('/report/analyze/', { report_id: reportId }),
  list: () => api.get('/report/list/'),
};

export const recommendationAPI = {
  get: (analysisId) => api.get(`/recommend/${analysisId ? `?analysis_id=${analysisId}` : ''}`),
  history: () => api.get('/recommend/history/'),
};

export const emergencyAPI = {
  check: (symptomText) => api.post('/emergency/', { symptom_text: symptomText }),
  alerts: () => api.get('/emergency/alerts/'),
  acknowledge: (alertId) => api.patch(`/emergency/alerts/${alertId}/acknowledge/`),
};

export const historyAPI = {
  list: (type) => api.get(`/history/${type ? `?type=${type}` : ''}`),
};

export default api;
