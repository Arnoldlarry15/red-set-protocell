import axios from 'axios';
<<<<<<< copilot/sub-pr-155-again

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Converts an unknown thrown value into a human-readable error string.
 * Uses axios.isAxiosError for safe, type-narrowed access to response details.
 */
export const getUserFriendlyApiError = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    if (error.response?.data?.detail) return String(error.response.data.detail);

    if (error.message === 'Network Error' || error.code === 'ERR_NETWORK') {
      return `Cannot reach backend at ${API_BASE_URL}. Check VITE_API_BASE_URL, backend availability, and CORS origin settings.`;
    }

    return error.message || 'An unexpected error occurred';
  }

=======
import { API_BASE_URL } from './config';

export const getUserFriendlyApiError = (error: unknown, fallback = 'An unexpected error occurred'): string => {
  if (axios.isAxiosError(error)) {
    if (error.response?.data?.detail) return String(error.response.data.detail);
    if (error.message === 'Network Error' || error.code === 'ERR_NETWORK') {
      return `Cannot reach backend at ${API_BASE_URL}. Check VITE_API_BASE_URL, backend availability, and CORS origin settings.`;
    }
    return error.message || fallback;
  }
>>>>>>> main
  return String(error);
};
