import axios from 'axios';

/**
 * Returns a human-readable error message for API call failures.
 * Handles Axios network errors, server-side detail payloads, and
 * arbitrary thrown values safely.
 */
export const getUserFriendlyApiError = (error: unknown, apiBaseUrl: string): string => {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (detail) return String(detail);

    if (error.message === 'Network Error' || error.code === 'ERR_NETWORK') {
      return `Cannot reach backend at ${apiBaseUrl}. Check VITE_API_BASE_URL, backend availability, and CORS origin settings.`;
    }

    return error.message || 'An unexpected error occurred';
  }

  return String(error) || 'An unexpected error occurred';
};
