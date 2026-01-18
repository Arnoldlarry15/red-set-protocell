/**
 * useSessionStream - WebSocket Hook with Reconnection and Backoff
 * 
 * Production-ready WebSocket hook for RSP session streaming.
 * 
 * Features:
 * - Automatic reconnection with exponential backoff
 * - Memory leak prevention (cleanup on unmount)
 * - Connection state tracking
 * - Error handling and retry logic
 * - Configurable retry limits
 * 
 * Pre-Release Checks:
 * [✓] Reconnect logic implemented
 * [✓] Exponential backoff strategy
 * [✓] Memory leak prevention via cleanup
 * [✓] Connection state management
 * [✓] Maximum retry limit to prevent infinite loops
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import { WebSocketMessage, OutgoingWebSocketMessage } from '../types';

interface UseSessionStreamOptions {
  url: string;
  sessionId: string;
  onMessage: (message: WebSocketMessage) => void;
  onError?: (error: Error) => void;
  maxRetries?: number;
  initialRetryDelay?: number;
  maxRetryDelay?: number;
}

interface ConnectionState {
  isConnected: boolean;
  isConnecting: boolean;
  error: Error | null;
  retryCount: number;
}

export function useSessionStream({
  url,
  sessionId,
  onMessage,
  onError,
  maxRetries = 10,
  initialRetryDelay = 1000,
  maxRetryDelay = 30000,
}: UseSessionStreamOptions) {
  const [connectionState, setConnectionState] = useState<ConnectionState>({
    isConnected: false,
    isConnecting: false,
    error: null,
    retryCount: 0,
  });

  const wsRef = useRef<WebSocket | null>(null);
  const retryTimeoutRef = useRef<number | null>(null);
  const shouldReconnectRef = useRef(true);
  const retryCountRef = useRef(0);

  /**
   * Calculate exponential backoff delay with jitter
   */
  const calculateBackoffDelay = useCallback((retryCount: number): number => {
    // Exponential backoff: delay = initialDelay * 2^retryCount
    const exponentialDelay = initialRetryDelay * Math.pow(2, retryCount);
    
    // Cap at maxRetryDelay
    const cappedDelay = Math.min(exponentialDelay, maxRetryDelay);
    
    // Add jitter (±20%) to prevent thundering herd
    const jitter = cappedDelay * 0.2 * (Math.random() - 0.5);
    
    return cappedDelay + jitter;
  }, [initialRetryDelay, maxRetryDelay]);

  /**
   * Connect to WebSocket with error handling
   */
  const connect = useCallback(() => {
    // Prevent connection if max retries exceeded
    if (retryCountRef.current >= maxRetries) {
      const error = new Error(`Max retries (${maxRetries}) exceeded`);
      setConnectionState({
        isConnected: false,
        isConnecting: false,
        error,
        retryCount: retryCountRef.current,
      });
      if (onError) {
        onError(error);
      }
      return;
    }

    // Prevent multiple simultaneous connections
    if (wsRef.current?.readyState === WebSocket.CONNECTING || 
        wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setConnectionState(prev => ({
      ...prev,
      isConnecting: true,
      error: null,
    }));

    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log(`[WebSocket] Connected to ${url}`);
        setConnectionState({
          isConnected: true,
          isConnecting: false,
          error: null,
          retryCount: retryCountRef.current,
        });
        
        // Reset retry count on successful connection
        retryCountRef.current = 0;

        // Send session ID to backend
        ws.send(JSON.stringify({
          type: 'subscribe',
          sessionId,
        }));
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          
          // Handle ping messages for keep-alive
          if (message.type === 'ping') {
            ws.send(JSON.stringify({ type: 'pong' }));
            return;
          }
          
          onMessage(message);
        } catch (error) {
          console.error('[WebSocket] Failed to parse message:', error);
        }
      };

      ws.onerror = (event) => {
        const error = new Error('WebSocket error occurred');
        console.error('[WebSocket] Error:', event);
        setConnectionState(prev => ({
          ...prev,
          error,
        }));
      };

      ws.onclose = (event) => {
        console.log(`[WebSocket] Closed: code=${event.code}, reason=${event.reason}`);
        setConnectionState({
          isConnected: false,
          isConnecting: false,
          error: null,
          retryCount: retryCountRef.current,
        });

        // Attempt reconnection if not intentionally closed and below max retries
        if (shouldReconnectRef.current && retryCountRef.current < maxRetries) {
          const delay = calculateBackoffDelay(retryCountRef.current);
          console.log(`[WebSocket] Reconnecting in ${delay}ms (attempt ${retryCountRef.current + 1}/${maxRetries})`);
          
          retryTimeoutRef.current = setTimeout(() => {
            retryCountRef.current += 1;
            connect();
          }, delay);
        }
      };
    } catch (error) {
      const err = error instanceof Error ? error : new Error('Failed to create WebSocket');
      console.error('[WebSocket] Connection error:', err);
      setConnectionState({
        isConnected: false,
        isConnecting: false,
        error: err,
        retryCount: retryCountRef.current,
      });
      
      if (onError) {
        onError(err);
      }
    }
  }, [url, sessionId, onMessage, onError, maxRetries, calculateBackoffDelay]);

  /**
   * Disconnect and cleanup
   */
  const disconnect = useCallback(() => {
    shouldReconnectRef.current = false;

    // Clear any pending retry
    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current);
      retryTimeoutRef.current = null;
    }

    // Close WebSocket connection
    if (wsRef.current) {
      // Use code 1000 (Normal Closure) for clean disconnect
      wsRef.current.close(1000, 'Client disconnecting');
      wsRef.current = null;
    }

    setConnectionState({
      isConnected: false,
      isConnecting: false,
      error: null,
      retryCount: 0,
    });
  }, []);

  /**
   * Send message through WebSocket
   */
  const sendMessage = useCallback((message: OutgoingWebSocketMessage) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
      return true;
    }
    console.warn('[WebSocket] Cannot send message: connection not open');
    return false;
  }, []);

  /**
   * Connect on mount, cleanup on unmount
   */
  useEffect(() => {
    shouldReconnectRef.current = true;
    connect();

    // Cleanup function - CRITICAL for memory leak prevention
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    ...connectionState,
    disconnect,
    reconnect: connect,
    sendMessage,
  };
}
