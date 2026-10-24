import axios from 'axios';
import dotenv from 'dotenv';

dotenv.config();

const PYTHON_API_URL = process.env.PYTHON_API_URL || 'http://127.0.0.1:8000';
const INTERNAL_SERVICE_SECRET = process.env.INTERNAL_SERVICE_SECRET || 'stellar_secret_internal_microservice_key_2026';

/**
 * Pre-configured Axios instance for secure internal microservice-to-microservice
 * communication between Node.js Express Gateway and Python FastAPI agent.
 */
export const internalAgentApi = axios.create({
  baseURL: PYTHON_API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'X-Internal-Service-Key': INTERNAL_SERVICE_SECRET,
  },
});

/**
 * Forward request with user's JWT Authorization token preserved.
 */
export const forwardWithAuth = (req) => {
  const headers = {
    'Content-Type': 'application/json',
    'X-Internal-Service-Key': INTERNAL_SERVICE_SECRET,
  };
  if (req.headers && req.headers.authorization) {
    headers['Authorization'] = req.headers.authorization;
  }
  return axios.create({
    baseURL: PYTHON_API_URL,
    timeout: 30000,
    headers,
  });
};

export default internalAgentApi;
