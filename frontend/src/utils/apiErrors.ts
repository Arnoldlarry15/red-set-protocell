import axios from 'axios';
import { API_BASE_URL } from './config';

export const getUserFriendlyApiError = (error: unknown, fallback = 'An unexpected error occurred'): string => {
  if (axios.isAxiosError(error)) {
    if (error.response?.data?.detail) return String(error.response.data.detail);
    if (error.message === 'Network Error' || error.code === 'ERR_NETWORK') {
      return `Cannot reach backend at ${API_BASE_URL}. Check VITE_API_BASE_URL, backend availability, and CORS origin settings.`;
    }
    return error.message || fallback;
  }
  return String(error);
};
