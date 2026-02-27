import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const tokens = localStorage.getItem('health_ai_tokens');
    if (tokens) {
      const { access } = JSON.parse(tokens);
      config.headers.Authorization = `Bearer ${access}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
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
