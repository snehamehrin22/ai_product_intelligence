import React, { useState } from 'react';
import './TaskItem.css';

const PRIORITY_COLORS = {
  low: '#3498db',
  medium: '#f39c12',
  high: '#e67e22',
  urgent: '#e74c3c'
};

function TaskItem({ task, onUpdate, onDelete, onToggleStatus }) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(task.title);
  const [editDescription, setEditDescription] = useState(task.description || '');
  const [saving, setSaving] = useState(false);

  const isCompleted = task.status === 'completed';

  const handleSaveEdit = async () => {
    if (!editTitle.trim()) {
      alert('Title cannot be empty');
      return;
    }

    setSaving(true);
    try {
      await onUpdate(task.task_id, {
        title: editTitle.trim(),
        description: editDescription.trim() || null
      });
      setIsEditing(false);
    } catch (err) {
      // Error handled by parent
    } finally {
      setSaving(false);
    }
  };

  const handleCancelEdit = () => {
    setEditTitle(task.title);
    setEditDescription(task.description || '');
    setIsEditing(false);
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      await onDelete(task.task_id);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return null;
    const date = new Date(dateStr);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className={`task-item ${isCompleted ? 'completed' : ''}`}>
      <div className="task-main">
        <button
          className="checkbox"
          onClick={() => onToggleStatus(task)}
          aria-label={isCompleted ? 'Mark as pending' : 'Mark as completed'}
        >
          {isCompleted && <span className="checkmark">✓</span>}
        </button>

        <div className="task-content">
          {isEditing ? (
            <div className="edit-form">
              <input
                type="text"
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                placeholder="Task title"
                maxLength={200}
                autoFocus
              />
              <textarea
                value={editDescription}
                onChange={(e) => setEditDescription(e.target.value)}
                placeholder="Description (optional)"
                rows={2}
                maxLength={2000}
              />
              <div className="edit-actions">
                <button onClick={handleSaveEdit} disabled={saving} className="save-btn">
                  {saving ? 'Saving...' : 'Save'}
                </button>
                <button onClick={handleCancelEdit} disabled={saving} className="cancel-btn">
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <>
              <h4 className="task-title">{task.title}</h4>
              {task.description && (
                <p className="task-description">{task.description}</p>
              )}
              <div className="task-meta">
                <span
                  className="priority-badge"
                  style={{ backgroundColor: PRIORITY_COLORS[task.priority] }}
                >
                  {task.priority}
                </span>
                {task.due_date && (
                  <span className="due-date">Due: {formatDate(task.due_date)}</span>
                )}
              </div>
            </>
          )}
        </div>
      </div>

      {!isEditing && (
        <div className="task-actions">
          <button
            onClick={() => setIsEditing(true)}
            className="action-btn edit-btn"
            aria-label="Edit task"
          >
            Edit
          </button>
          <button
            onClick={handleDelete}
            className="action-btn delete-btn"
            aria-label="Delete task"
          >
            Delete
          </button>
        </div>
      )}
    </div>
  );
}

export default TaskItem;
