import React, { useState, useEffect } from 'react';

const BASE_URL = 'http://127.0.0.1:8000';

function TodaysTasks() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchTodaysTasks();
  }, []);

  const fetchTodaysTasks = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `${BASE_URL}/tasks/today`,
        {
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      if (result.success) {
        setTasks(result.data);
      } else {
        throw new Error(result.message || 'Failed to fetch today\'s tasks');
      }
    } catch (e) {
      console.error('Error fetching today\'s tasks:', e);
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const completeTask = async (taskId) => {
    try {
      const response = await fetch(
        `${BASE_URL}/tasks/${taskId}/complete`,
        {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      if (result.success) {
        // Update the task in the local state
        setTasks(prevTasks => 
          prevTasks.map(task => 
            task.id === taskId 
              ? { ...task, is_completed: true, status: 'completed' }
              : task
          )
        );
      }
    } catch (e) {
      console.error('Error completing task:', e);
    }
  };

  const formatTime = (dateString) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  const getPriorityColor = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'high': return '#ef4444';
      case 'medium': return '#f59e0b';
      case 'low': return '#10b981';
      default: return '#6b7280';
    }
  };

  const getPriorityAccentColor = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'high': return '#fef2f2';
      case 'medium': return '#fffbeb';
      case 'low': return '#f0fdf4';
      default: return '#f9fafb';
    }
  };

  // Sort tasks: incomplete first, then completed (grayed out) at bottom
  const sortedTasks = [...tasks].sort((a, b) => {
    if (a.is_completed !== b.is_completed) {
      return a.is_completed ? 1 : -1;
    }
    return new Date(a.created_at) - new Date(b.created_at);
  });

  if (loading) {
    return (
      <div className="todays-tasks-container">
        <h3 className="todays-tasks-title">Today's Tasks</h3>
        <div className="todays-tasks-loading">Loading tasks...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="todays-tasks-container">
        <h3 className="todays-tasks-title">Today's Tasks</h3>
        <div className="todays-tasks-error">Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="modern-tasks-container">
      <div className="modern-tasks-header">
        <h3 className="modern-tasks-title">Today's Tasks</h3>
        <div className="tasks-summary">
          <span className="tasks-completed">{tasks.filter(t => t.is_completed).length}</span>
          <span className="tasks-divider">/</span>
          <span className="tasks-total">{tasks.length}</span>
        </div>
      </div>
      
      <div className="modern-tasks-list">
        {sortedTasks.length === 0 ? (
          <div className="modern-tasks-empty">
            <div className="empty-icon">📝</div>
            <p>No tasks for today</p>
            <span>You're all caught up!</span>
          </div>
        ) : (
          sortedTasks.map((task) => (
            <div 
              key={task.id} 
              className={`modern-task-item ${task.is_completed ? 'task-completed' : ''}`}
              style={{
                borderLeft: `4px solid ${getPriorityColor(task.priority)}`,
                backgroundColor: task.is_completed ? '#f9fafb' : getPriorityAccentColor(task.priority)
              }}
            >
              <div className="modern-task-checkbox">
                <input
                  type="checkbox"
                  checked={task.is_completed}
                  onChange={() => !task.is_completed && completeTask(task.id)}
                  className="modern-checkbox"
                  disabled={task.is_completed}
                />
                <div className="modern-checkmark">
                  {task.is_completed && (
                    <svg className="checkmark-icon" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  )}
                </div>
              </div>
              
              <div className="modern-task-content">
                <div className="modern-task-main">
                  <div className="modern-task-title">{task.title}</div>
                  <div 
                    className="modern-priority-indicator"
                    style={{ backgroundColor: getPriorityColor(task.priority) }}
                  ></div>
                </div>
                
                {task.description && (
                  <div className="modern-task-description">{task.description}</div>
                )}
                
                <div className="modern-task-meta">
                  {task.due_date && (
                    <span className="modern-task-time">
                      🕒 {formatTime(task.due_date)}
                    </span>
                  )}
                  {task.estimated_duration && (
                    <span className="modern-task-duration">
                      ⏱️ {task.estimated_duration}min
                    </span>
                  )}
                </div>
                
                {task.tags && task.tags.length > 0 && (
                  <div className="modern-task-tags">
                    {task.tags.slice(0, 3).map((tag, index) => (
                      <span key={index} className="modern-task-tag">
                        #{tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default TodaysTasks;
