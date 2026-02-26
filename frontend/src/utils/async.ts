/**
 * Utility for safely handling async operations that may fail.
 * Catches promise rejections and logs them as warnings instead of causing unhandled rejections.
 */
export const safeAsync = (fn: () => Promise<void>) => {
  fn().catch((err) => console.warn('Async cleanup failed', err));
};
