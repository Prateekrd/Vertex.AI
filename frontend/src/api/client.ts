import axios from 'axios';

const API_BASE = '/api/v1';

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Upload
export const uploadAPI = {
  uploadFile: (file: File) => {
    const form = new FormData();
    form.append('file', file);
    return api.post('/upload/', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  getSamples: () => api.get('/upload/samples'),
  loadSample: (sampleId: string) => api.post(`/upload/load-sample/${sampleId}`),
};

// Processing
export const processingAPI = {
  getJobStatus: (jobId: string) => api.get(`/process/status/${jobId}`),
  connectWebSocket: (jobId: string): WebSocket => {
    const wsUrl = `/ws/process/ws/${jobId}`;
    return new WebSocket(wsUrl);
  },
};

// Review
export const reviewAPI = {
  getQueue: () => api.get('/review/queue'),
  getHistory: () => api.get('/review/history'),
  submitReview: (data: any) => api.post('/review/submit', data),
};

// Metrics
export const metricsAPI = {
  getDashboard: () => api.get('/metrics/dashboard'),
  getHistory: () => api.get('/metrics/history'),
  saveMetrics: (data: any) => api.post('/metrics/save', data),
};

// Search
export const searchAPI = {
  search: (query: string, topK: number = 10) =>
    api.post('/search/', { query, top_k: topK }),
  byCode: (code: string) => api.get(`/search/by-code/${code}`),
};

// Standard codes
export const codesAPI = {
  list: (category?: string) => api.get('/codes/', { params: { category } }),
  get: (code: string) => api.get(`/codes/${code}`),
  match: (description: string) => api.post('/codes/match', { description }),
};

export default api;