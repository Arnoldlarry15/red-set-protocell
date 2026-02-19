/**
 * Utility for handling async functions safely without uncaught promise rejections.
 * Useful for cleanup functions where we want to catch errors but not throw.
 */
export const safeAsync = (fn: () => Promise<void>) => {
  fn().catch((err) => console.warn('Async cleanup failed', err));
};
