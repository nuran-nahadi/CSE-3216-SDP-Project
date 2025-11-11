/**
 * Centralized event type definitions
 * Prevents typos and makes events discoverable
 * 
 * Usage:
 * import { EXPENSE_CREATED } from './utils/eventTypes';
 * eventBus.publish(EXPENSE_CREATED, data);
 */

// ============================================
// Expense Events
// ============================================
export const EXPENSE_CREATED = 'expense:created';
export const EXPENSE_UPDATED = 'expense:updated';
export const EXPENSE_DELETED = 'expense:deleted';

// ============================================
// Task Events
// ============================================
export const TASK_CREATED = 'task:created';
export const TASK_UPDATED = 'task:updated';
export const TASK_DELETED = 'task:deleted';
export const TASK_COMPLETED = 'task:completed';

// ============================================
// Event Events (Calendar)
// ============================================
export const EVENT_CREATED = 'event:created';
export const EVENT_UPDATED = 'event:updated';
export const EVENT_DELETED = 'event:deleted';

// ============================================
// User Events
// ============================================
export const USER_PROFILE_UPDATED = 'user:profile:updated';
export const USER_AVATAR_UPDATED = 'user:avatar:updated';

// ============================================
// System Events
// ============================================
export const NOTIFICATION_SHOW = 'notification:show';
export const DATA_REFRESH_REQUESTED = 'data:refresh:requested';
