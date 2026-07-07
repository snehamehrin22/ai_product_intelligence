/**
 * EventEmitter service for tracking platform events
 *
 * Features:
 * - Session ID generation and persistence
 * - Event batching (max 10 events or 5 seconds)
 * - Retry logic with exponential backoff
 * - Graceful degradation on errors
 */

const API_BASE_URL = 'http://localhost:8000';
const MAX_BATCH_SIZE = 10;
const BATCH_TIMEOUT_MS = 5000; // 5 seconds
const MAX_RETRIES = 3;
const INITIAL_RETRY_DELAY_MS = 1000; // 1 second

class EventEmitter {
  constructor() {
    this.sessionId = this._initializeSessionId();
    this.eventQueue = [];
    this.batchTimer = null;
    this.isSending = false;
  }

  /**
   * Initialize or retrieve session ID from sessionStorage
   * @private
   * @returns {string} Session ID (UUID v4)
   */
  _initializeSessionId() {
    // Check if session ID already exists
    let sessionId = sessionStorage.getItem('session_id');

    if (!sessionId) {
      // Generate new session ID (UUID v4)
      sessionId = crypto.randomUUID();
      sessionStorage.setItem('session_id', sessionId);
      console.log('[EventEmitter] Generated new session ID:', sessionId);
    } else {
      console.log('[EventEmitter] Using existing session ID:', sessionId);
    }

    return sessionId;
  }

  /**
   * Get current session ID
   * @returns {string} Session ID
   */
  getSessionId() {
    return this.sessionId;
  }

  /**
   * Emit a platform event
   *
   * @param {string} eventName - Name of the event (e.g., 'page_viewed', 'task_created')
   * @param {string} userId - User ID
   * @param {Object} [properties={}] - Event-specific properties
   *
   * @example
   * eventEmitter.emit('page_viewed', 'user-123', { page: '/tasks' });
   */
  emit(eventName, userId, properties = {}) {
    const event = {
      event_name: eventName,
      user_id: userId,
      session_id: this.sessionId,
      properties: properties
    };

    // Add event to queue
    this.eventQueue.push(event);
    console.log(`[EventEmitter] Queued event: ${eventName} (queue size: ${this.eventQueue.length})`);

    // Flush if batch size reached
    if (this.eventQueue.length >= MAX_BATCH_SIZE) {
      console.log('[EventEmitter] Batch size reached, flushing...');
      this.flush();
    } else {
      // Set timer to flush after timeout
      this._scheduleBatchFlush();
    }
  }

  /**
   * Schedule a batch flush after timeout
   * @private
   */
  _scheduleBatchFlush() {
    // Clear existing timer
    if (this.batchTimer) {
      clearTimeout(this.batchTimer);
    }

    // Schedule new flush
    this.batchTimer = setTimeout(() => {
      console.log('[EventEmitter] Batch timeout reached, flushing...');
      this.flush();
    }, BATCH_TIMEOUT_MS);
  }

  /**
   * Immediately flush all queued events to backend
   * @returns {Promise<void>}
   */
  async flush() {
    // Clear batch timer
    if (this.batchTimer) {
      clearTimeout(this.batchTimer);
      this.batchTimer = null;
    }

    // Skip if no events or already sending
    if (this.eventQueue.length === 0 || this.isSending) {
      return;
    }

    // Get events to send
    const eventsToSend = [...this.eventQueue];
    this.eventQueue = [];
    this.isSending = true;

    try {
      await this._sendEvents(eventsToSend);
      console.log(`[EventEmitter] Successfully sent ${eventsToSend.length} events`);
    } catch (error) {
      console.error('[EventEmitter] Failed to send events after retries:', error);
      // Graceful degradation - events are lost but app continues
    } finally {
      this.isSending = false;
    }
  }

  /**
   * Send events to backend with retry logic
   * @private
   * @param {Array} events - Events to send
   * @param {number} [retryCount=0] - Current retry attempt
   * @returns {Promise<Object>} Response from backend
   */
  async _sendEvents(events, retryCount = 0) {
    try {
      const response = await fetch(`${API_BASE_URL}/events`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Session-Id': this.sessionId
        },
        body: JSON.stringify({
          events: events
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      // Log validation errors if any
      if (data.validation_errors && data.validation_errors.length > 0) {
        console.warn('[EventEmitter] Some events failed validation:', data.validation_errors);
      }

      return data;

    } catch (error) {
      // Retry logic
      if (retryCount < MAX_RETRIES) {
        const delay = INITIAL_RETRY_DELAY_MS * Math.pow(2, retryCount); // Exponential backoff
        console.warn(`[EventEmitter] Send failed (attempt ${retryCount + 1}/${MAX_RETRIES + 1}), retrying in ${delay}ms...`);

        await new Promise(resolve => setTimeout(resolve, delay));
        return this._sendEvents(events, retryCount + 1);
      } else {
        throw error;
      }
    }
  }

  /**
   * Clear session ID and generate a new one
   * Useful for testing or manual session reset
   */
  resetSession() {
    sessionStorage.removeItem('session_id');
    this.sessionId = this._initializeSessionId();
    console.log('[EventEmitter] Session reset');
  }
}

// Create singleton instance
const eventEmitter = new EventEmitter();

export default eventEmitter;
