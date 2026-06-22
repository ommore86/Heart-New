/**
 * Axios API client configured to talk to the FastAPI backend.
 * Base URL can be overridden via VITE_API_URL environment variable.
 */
import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
});

/**
 * POST /predict
 * @param {Object} patientData
 * @returns {Promise<PredictResponse>}
 */
export async function predictRisk(patientData) {
  const { data } = await api.post('/predict', patientData);
  return data;
}

/**
 * POST /simulate
 * @param {Object} patient
 * @param {Object} scenario
 * @returns {Promise<SimulateResponse>}
 */
export async function simulateRisk(patient, scenario) {
  const { data } = await api.post('/simulate', { patient, scenario });
  return data;
}

/**
 * GET /health
 * @returns {Promise<HealthResponse>}
 */
export async function checkHealth() {
  const { data } = await api.get('/health');
  return data;
}
