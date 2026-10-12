import axios from "axios";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

const handleRequest = async (request) => {
  try {
    const response = await request();
    return response.data;
  } catch (error) {
    console.error("API request failed:", error);
    throw error;
  }
};

export const getTickers = () =>
  handleRequest(() => axios.get(`${API_BASE}/tickers`)).then((data) => data?.tickers ?? []);
export const getProcessed = (ticker) =>
  handleRequest(() => axios.get(`${API_BASE}/processed/${ticker}`)).then((data) => data ?? []);
export const getPredictions = (ticker) =>
  handleRequest(() => axios.get(`${API_BASE}/predictions/${ticker}`)).then((data) => data ?? []);
export const getAlerts = (ticker) =>
  handleRequest(() => axios.get(`${API_BASE}/alerts/${ticker}`)).then((data) => data ?? []);
export const getLatestPredictions = () =>
  handleRequest(() => axios.get(`${API_BASE}/predictions/latest`)).then((data) => data ?? []);
export const simulateMarketShock = (payload) =>
  handleRequest(() => axios.post(`${API_BASE}/simulation/market-shock`, payload));
