import axios from "axios";

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || "http://localhost:8000",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export const authApi = {
  login: (data) => api.post("/api/auth/login", data),
  me: () => api.get("/api/auth/me"),
};

export const connectionApi = {
  list: () => api.get("/api/connections"),
  get: (id) => api.get(`/api/connections/${id}`),
  create: (data) => api.post("/api/connections", data),
  update: (id, data) => api.put(`/api/connections/${id}`, data),
  delete: (id) => api.delete(`/api/connections/${id}`),
};

export const flowApi = {
  list: () => api.get("/api/flows"),
  get: (id) => api.get(`/api/flows/${id}`),
  create: (data) => api.post("/api/flows", data),
  update: (id, data) => api.put(`/api/flows/${id}`, data),
  delete: (id) => api.delete(`/api/flows/${id}`),
  run: (id) => api.post(`/api/flows/${id}/run`),
  runs: (id) => api.get(`/api/flows/${id}/runs`),
  validate: (rql) => api.post("/api/flows/validate", { rql }),
};

export default api;
