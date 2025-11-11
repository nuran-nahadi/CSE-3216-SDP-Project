import { useEffect } from 'react';
import { eventBus } from '../utils/eventBus';

/**
 * Custom hook for subscribing to events
 * Automatically unsubscribes on component unmount
 * 
 * @param {string} event - Event name to subscribe to
 * @param {Function} callback - Function to call when event is published
 * 
 * @example
 * useEventBus('expense:created', (expense) => {
 *   console.log('New expense:', expense);
 *   refetchData();
 * });
 */
export function useEventBus(event, callback) {
  useEffect(() => {
    const unsubscribe = eventBus.subscribe(event, callback);
    
    // Cleanup on unmount
    return unsubscribe;
  }, [event, callback]);
}

/**
 * Hook for subscribing to multiple events
 * 
 * @param {Object} eventHandlers - Object mapping event names to handlers
 * 
 * @example
 * useEventBusMultiple({
 *   'expense:created': handleExpenseCreated,
 *   'expense:deleted': handleExpenseDeleted,
 * });
 */
export function useEventBusMultiple(eventHandlers) {
  useEffect(() => {
    const unsubscribers = Object.entries(eventHandlers).map(([event, handler]) =>
      eventBus.subscribe(event, handler)
    );
    
    // Cleanup all subscriptions
    return () => {
      unsubscribers.forEach(unsubscribe => unsubscribe());
    };
  }, [eventHandlers]);
}
