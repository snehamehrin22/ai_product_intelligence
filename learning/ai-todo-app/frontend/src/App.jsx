import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import TaskList from './components/TaskList';
import TaskForm from './components/TaskForm';
import { getTasks, createTask, updateTask, deleteTask } from './services/api';

const TEST_USER_ID = 'test-user-001';

function App() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all'); // all, pending, completed

  const loadTasks = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const statusFilter = filter === 'all' ? null : filter;
      const fetchedTasks = await getTasks(TEST_USER_ID, statusFilter);
      setTasks(fetchedTasks);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [filter]);

  // Load tasks on mount and when filter changes
  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  const handleCreateTask = async (taskData) => {
    try {
      setError(null);
      const newTask = await createTask({
        ...taskData,
        user_id: TEST_USER_ID,
      });
      setTasks([newTask, ...tasks]);
      return newTask;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const handleUpdateTask = async (taskId, updates) => {
    try {
      setError(null);
      const updatedTask = await updateTask(taskId, updates);
      setTasks(tasks.map(t => t.task_id === taskId ? updatedTask : t));
      return updatedTask;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const handleDeleteTask = async (taskId) => {
    try {
      setError(null);
      await deleteTask(taskId);
      setTasks(tasks.filter(t => t.task_id !== taskId));
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const handleToggleStatus = async (task) => {
    const newStatus = task.status === 'completed' ? 'pending' : 'completed';
    await handleUpdateTask(task.task_id, { status: newStatus });
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>AI Todo App</h1>
        <p className="subtitle">Manage your tasks with AI assistance</p>
      </header>

      <main className="App-main">
        <div className="container">
          {/* Task Creation Form */}
          <section className="form-section">
            <TaskForm onSubmit={handleCreateTask} />
          </section>

          {/* Error Display */}
          {error && (
            <div className="error-banner">
              <strong>Error:</strong> {error}
            </div>
          )}

          {/* Filter Tabs */}
          <div className="filter-tabs">
            <button
              className={filter === 'all' ? 'active' : ''}
              onClick={() => setFilter('all')}
            >
              All Tasks
            </button>
            <button
              className={filter === 'pending' ? 'active' : ''}
              onClick={() => setFilter('pending')}
            >
              Pending
            </button>
            <button
              className={filter === 'completed' ? 'active' : ''}
              onClick={() => setFilter('completed')}
            >
              Completed
            </button>
          </div>

          {/* Task List */}
          <section className="task-list-section">
            {loading ? (
              <div className="loading">Loading tasks...</div>
            ) : (
              <TaskList
                tasks={tasks}
                onUpdate={handleUpdateTask}
                onDelete={handleDeleteTask}
                onToggleStatus={handleToggleStatus}
              />
            )}
          </section>
        </div>
      </main>
    </div>
  );
}

export default App;
