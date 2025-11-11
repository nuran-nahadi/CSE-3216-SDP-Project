/**
 * Simple Event Bus for component communication
 * Implements the Observer pattern
 * 
 * @example
 * // Subscribe to an event
 * const unsubscribe = eventBus.subscribe('expense:created', (data) => {
 *   console.log('New expense:', data);
 * });
 * 
 * // Publish an event
 * eventBus.publish('expense:created', { id: 1, amount: 100 });
 * 
 * // Unsubscribe when done
 * unsubscribe();
 */
class EventBus {
  constructor() {
    this.events = {};
  }

  /**
   * Subscribe to an event
   * @param {string} event - Event name
   * @param {Function} callback - Function to call when event is published
   * @returns {Function} Unsubscribe function
   */
  subscribe(event, callback) {
    if (!this.events[event]) {
      this.events[event] = [];
    }
    
    this.events[event].push(callback);
    
    // Return unsubscribe function
    return () => {
      this.events[event] = this.events[event].filter(cb => cb !== callback);
    };
  }

  /**
   * Publish an event with optional data
   * @param {string} event - Event name
   * @param {*} data - Data to pass to subscribers
   */
  publish(event, data) {
    if (!this.events[event]) {
      return;
    }
    
    this.events[event].forEach(callback => {
      try {
        callback(data);
      } catch (error) {
        console.error(`Error in event handler for "${event}":`, error);
      }
    });
  }

  /**
   * Get all subscribers for an event (for debugging)
   * @param {string} event - Event name
   * @returns {number} Number of subscribers
   */
  getSubscriberCount(event) {
    return this.events[event]?.length || 0;
  }

  /**
   * Clear all subscribers for an event
   * @param {string} event - Event name
   */
  clear(event) {
    if (event) {
      delete this.events[event];
    } else {
      this.events = {};
    }
  }
}

// Export singleton instance
export const eventBus = new EventBus();

// Export class for testing
export default EventBus;
