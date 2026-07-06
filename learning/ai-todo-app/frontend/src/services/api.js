/**
 * API client for backend REST API
 */

const API_BASE_URL = 'http://localhost:8000';

/**
 * Fetch all tasks for a user
 * @param {string} userId - User ID
 * @param {string} [status] - Optional status filter
 * @returns {Promise<Array>} List of tasks
 */
export async function getTasks(userId, status = null) {
  const params = new URLSearchParams({ user_id: userId });
  if (status) {
    params.append('status', status);
  }

  const response = await fetch(`${API_BASE_URL}/tasks?${params}`);
  if (!response.ok) {
    throw new Error(`Failed to fetch tasks: ${response.statusText}`);
  }

  const data = await response.json();
  return data.tasks;
}

/**
 * Create a new task
 * @param {Object} task - Task data
 * @returns {Promise<Object>} Created task
 */
export async function createTask(task) {
  const response = await fetch(`${API_BASE_URL}/tasks`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(task),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create task');
  }

  return response.json();
}

/**
 * Update a task
 * @param {string} taskId - Task ID
 * @param {Object} updates - Fields to update
 * @returns {Promise<Object>} Updated task
 */
export async function updateTask(taskId, updates) {
  const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(updates),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to update task');
  }

  return response.json();
}

/**
 * Delete a task
 * @param {string} taskId - Task ID
 * @returns {Promise<void>}
 */
export async function deleteTask(taskId) {
  const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to delete task');
  }
}

/**
 * Send message to AI agent
 * @param {string} message - Natural language message
 * @param {string} userId - User ID
 * @returns {Promise<Object>} Agent response
 */
export async function sendAgentMessage(message, userId) {
  const params = new URLSearchParams({
    message,
    user_id: userId
  });

  const response = await fetch(`${API_BASE_URL}/agent/chat?${params}`, {
    method: 'POST',
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to send message to agent');
  }

  return response.json();
}
