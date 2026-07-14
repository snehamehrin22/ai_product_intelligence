import React, { useState } from 'react';
import './TaskForm.css';

const PRIORITY_OPTIONS = [
  { value: 'low', label: 'Low' },
  { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' },
  { value: 'urgent', label: 'Urgent' }
];

function TaskForm({ onSubmit }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState('medium');
  const [dueDate, setDueDate] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!title.trim()) {
      alert('Task title is required');
      return;
    }

    setSubmitting(true);
    try {
      await onSubmit({
        title: title.trim(),
        description: description.trim() || null,
        priority,
        status: 'pending',
        due_date: dueDate || null,
      });

      // Reset form on success
      setTitle('');
      setDescription('');
      setPriority('medium');
      setDueDate('');
    } catch (err) {
      // Error handled by parent
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form className="task-form" onSubmit={handleSubmit}>
      <h2>Create New Task</h2>

      <div className="form-group">
        <label htmlFor="title">
          Title <span className="required">*</span>
        </label>
        <input
          id="title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="What needs to be done?"
          maxLength={200}
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="description">Description</label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Add more details (optional)"
          rows={3}
          maxLength={2000}
        />
      </div>

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="priority">Priority</label>
          <select
            id="priority"
            value={priority}
            onChange={(e) => setPriority(e.target.value)}
          >
            {PRIORITY_OPTIONS.map(opt => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="dueDate">Due Date</label>
          <input
            id="dueDate"
            type="datetime-local"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
          />
        </div>
      </div>

      <button
        type="submit"
        className="submit-btn"
        disabled={submitting || !title.trim()}
      >
        {submitting ? 'Creating...' : 'Create Task'}
      </button>
    </form>
  );
}

export default TaskForm;
