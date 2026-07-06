import React from 'react';
import TaskItem from './TaskItem';
import './TaskList.css';

function TaskList({ tasks, onUpdate, onDelete, onToggleStatus }) {
  if (tasks.length === 0) {
    return (
      <div className="empty-state">
        <p>No tasks found</p>
        <p className="empty-hint">Create your first task above!</p>
      </div>
    );
  }

  // Group tasks by status
  const pendingTasks = tasks.filter(t => t.status === 'pending' || t.status === 'in_progress');
  const completedTasks = tasks.filter(t => t.status === 'completed');

  return (
    <div className="task-list">
      {pendingTasks.length > 0 && (
        <div className="task-group">
          <h3 className="group-title">
            Pending Tasks <span className="count">({pendingTasks.length})</span>
          </h3>
          <div className="tasks">
            {pendingTasks.map(task => (
              <TaskItem
                key={task.task_id}
                task={task}
                onUpdate={onUpdate}
                onDelete={onDelete}
                onToggleStatus={onToggleStatus}
              />
            ))}
          </div>
        </div>
      )}

      {completedTasks.length > 0 && (
        <div className="task-group">
          <h3 className="group-title">
            Completed Tasks <span className="count">({completedTasks.length})</span>
          </h3>
          <div className="tasks">
            {completedTasks.map(task => (
              <TaskItem
                key={task.task_id}
                task={task}
                onUpdate={onUpdate}
                onDelete={onDelete}
                onToggleStatus={onToggleStatus}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default TaskList;
