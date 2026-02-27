import axios from "axios";

const API_BASE = "/api"; // This will be proxied to localhost:5002

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error("API Error:", error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const agentAPI = {
  // Health check
  health: () => api.get("/health"),

  // Onboarding
  onboarding: (data) => api.post("/onboarding", data),

  // Company Analysis
  analyzeCompanies: (data) => api.post("/company-analysis", data),
  getCompanyProblems: (company) => api.get(`/company/${company}/problems`),
  listCompanies: () => api.get("/companies/list"),

  // Planner
  createPlan: (data) => api.post("/planner", data),

  // Evaluator
  evaluateResponse: (data) => api.post("/evaluator", data),
  submitCode: (data) => api.post("/code/submit", data),

  // Tutor
  getTutoring: (data) => api.post("/tutor", data),

  // Scheduler
  createSchedule: (data) => api.post("/scheduler", data),

  // Recommender
  getRecommendation: (userId) => api.get(`/recommendation/${userId}`),
  getProblemRecommendation: (userId) =>
    api.get(`/problems/recommend/${userId}`),

  // Analytics
  getAnalytics: (userId) => api.get(`/analytics/${userId}`),
  getUserProgress: (userId) => api.get(`/user/${userId}/progress`),

  // Daily Cycle
  getDailyCycle: (userId) => api.get(`/daily-cycle/${userId}`),
};

export default api;
