import React, { useState, useEffect } from 'react';

const TaskManager = () => {
  const [activeTab, setActiveTab] = useState('today');
  const [todayTasks, setTodayTasks] = useState([]);
  const [overdueTasks, setOverdueTasks] = useState([]);
  const [allTasks, setAllTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedTask, setSelectedTask] = useState(null);
  const [editingTask, setEditingTask] = useState(null);
  const [message, setMessage] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  
  // Form state
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    due_date: '',
    priority: 'medium',
    status: 'pending',
    estimated_duration: 1,
    tags: ''
  });

  const baseURL = "http://127.0.0.1:8000";

  useEffect(() => {
    fetchTasks();
  }, [activeTab]);

  // Set default due date to today at 11:59 PM
  useEffect(() => {
    const today = new Date();
    today.setHours(23, 59, 0, 0);
    const defaultDate = today.toISOString().slice(0, 16);
    setFormData(prev => ({ ...prev, due_date: defaultDate }));
  }, []);

  const fetchTasks = async () => {
    setLoading(true);
    try {
      let url = '';
      if (activeTab === 'today') {
        url = `${baseURL}/tasks/today`;
      } else if (activeTab === 'overdue') {
        url = `${baseURL}/tasks/overdue`;
      } else if (activeTab === 'all') {
        url = `${baseURL}/tasks/`;
      }
  
      const response = await fetch(url);
      const data = await response.json();
  
      const tasks = data.data || [];
  
      // Reverse the order for all tabs
      if (activeTab === 'today') {
        setTodayTasks([...tasks].reverse());
      } else if (activeTab === 'overdue') {
        setOverdueTasks([...tasks].reverse());
      } else if (activeTab === 'all') {
        setAllTasks([...tasks].reverse());
      }
    } catch (error) {
      console.error('Error fetching tasks:', error);
      setMessage('Error fetching tasks');
    } finally {
      setLoading(false);
    }
  };

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const resetForm = () => {
    const today = new Date();
    today.setHours(23, 59, 0, 0);
    const defaultDate = today.toISOString().slice(0, 16);
    
    setFormData({
      title: '',
      description: '',
      due_date: defaultDate,
      priority: 'medium',
      status: 'pending',
      estimated_duration: 1,
      tags: ''
    });
    setShowAddForm(false);
  };

  const handleAddTask = async () => {
    if (!formData.title.trim()) return;
    
    setLoading(true);
    try {
      console.log('Creating task:', formData);
      
      const taskData = {
        title: formData.title,
        description: formData.description,
        due_date: new Date(formData.due_date).toISOString(),
        priority: formData.priority,
        status: formData.status,
        estimated_duration: parseInt(formData.estimated_duration) || 1,
        tags: formData.tags ? formData.tags.split(',').map(tag => tag.trim()).filter(tag => tag) : [],
        parent_task_id: null
      };
      
      console.log('Task data to be created:', taskData);

      const createResponse = await fetch(`${baseURL}/tasks/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(taskData)
      });
      
      console.log('Create response status:', createResponse.status);
      
      if (!createResponse.ok) {
        const errorData = await createResponse.json();
        console.error('Create API error response:', errorData);
        
        // Handle validation errors
        if (errorData.detail) {
          const validationErrors = errorData.detail.map(err => err.msg).join(', ');
          throw new Error(`Validation error: ${validationErrors}`);
        }
        
        throw new Error(`Failed to create task: ${errorData.message || 'Unknown error'}`);
      }
      
      const createResult = await createResponse.json();
      console.log('Task created successfully:', createResult);
      
      if (createResult.success) {
        resetForm();
        setMessage('Task created successfully!');
        
        // Clear message after 3 seconds
        setTimeout(() => setMessage(''), 3000);
        
        // Refresh tasks
        await fetchTasks();
      } else {
        throw new Error(createResult.message || 'Failed to create task');
      }
      
    } catch (error) {
      console.error('Error in handleAddTask:', error);
      setMessage(`Error creating task: ${error.message}`);
      
      // Clear error message after 5 seconds
      setTimeout(() => setMessage(''), 5000);
    } finally {
      setLoading(false);
    }
  };

  const toggleTaskCompletion = async (taskId, actualDuration = 0) => {
    try {
      await fetch(`${baseURL}/tasks/${taskId}/complete`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ actual_duration: 1 })
      });
      setMessage('Task completed!');
      fetchTasks();
    } catch (error) {
      setMessage('Error completing task');
    }
  };

  const deleteTask = async (taskId) => {
    try {
      await fetch(`${baseURL}/tasks/${taskId}`, {
        method: 'DELETE'
      });
      setMessage('Task deleted!');
      fetchTasks();
    } catch (error) {
      setMessage('Error deleting task');
    }
  };

  const updateTask = async (taskId, taskData) => {
    try {
      // Sanitize data before sending
      const safeTaskData = {
        ...taskData,
        actual_duration: Math.max(1, Number(taskData.actual_duration || 0)),
        estimated_duration: Math.max(1, Number(taskData.estimated_duration || 0)),
      };
  
      await fetch(`${baseURL}/tasks/${taskId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(safeTaskData)
      });
  
      setMessage('Task updated!');
      setEditingTask(null);
      fetchTasks();
    } catch (error) {
      setMessage('Error updating task');
      console.error('Update failed:', error);
    }
  };

  const handleSaveEdit = (taskId) => {
    const formElement = document.querySelector(`[data-task-id="${taskId}"]`);
    const inputs = formElement.querySelectorAll('input, textarea, select');
    const formData = {};
    
    inputs.forEach(input => {
      if (input.name) {
        formData[input.name] = input.value;
      }
    });
    
    const taskData = {
      title: formData.title,
      description: formData.description,
      due_date: new Date(formData.due_date).toISOString(),
      priority: formData.priority,
      status: formData.status,
      estimated_duration: parseInt(formData.estimated_duration) || 0,
      actual_duration: parseInt(formData.actual_duration) || 0,
      tags: formData.tags ? formData.tags.split(',').map(tag => tag.trim()).filter(tag => tag) : [],
      parent_task_id: null
    };
    
    updateTask(taskId, taskData);
  };

  const TaskItem = ({ task, showDescription = false }) => (
    <div className="bg-white border border-gray-200 rounded-lg p-4 mb-3 shadow-sm">
      {editingTask === task.id ? (
        <div data-task-id={task.id} className="space-y-3">
          <input
            name="title"
            defaultValue={task.title}
            className="w-full p-2 border border-gray-300 rounded"
            placeholder="Title"
            required
          />
          <textarea
            name="description"
            defaultValue={task.description}
            className="w-full p-2 border border-gray-300 rounded"
            placeholder="Description"
          />
          <div className="grid grid-cols-2 gap-2">
            <input
              name="due_date"
              type="datetime-local"
              defaultValue={task.due_date?.slice(0, 16)}
              className="p-2 border border-gray-300 rounded"
            />
            <select
              name="priority"
              defaultValue={task.priority}
              className="p-2 border border-gray-300 rounded"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </div>
          <div className="grid grid-cols-3 gap-2">
            <select
              name="status"
              defaultValue={task.status}
              className="p-2 border border-gray-300 rounded"
            >
              <option value="pending">Pending</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
            </select>
            <input
              name="estimated_duration"
              type="number"
              defaultValue={task.estimated_duration}
              className="p-2 border border-gray-300 rounded"
              placeholder="Est. Duration (hrs)"
            />
            <input
              name="actual_duration"
              type="number"
              defaultValue={task.actual_duration}
              className="p-2 border border-gray-300 rounded"
              placeholder="Actual Duration (hrs)"
            />
          </div>
          <input
            name="tags"
            defaultValue={task.tags?.join(', ')}
            className="w-full p-2 border border-gray-300 rounded"
            placeholder="Tags (comma separated)"
          />
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => handleSaveEdit(task.id)}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Save
            </button>
            <button
              type="button"
              onClick={() => setEditingTask(null)}
              className="px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
            >
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <div>
          <div className="flex items-center gap-3 mb-2">
            <input
              type="checkbox"
              checked={task.is_completed}
              onChange={() => toggleTaskCompletion(task.id)}
              className="w-5 h-5 text-blue-600"
            />
            <h3 
              className={`flex-1 font-medium cursor-pointer ${task.is_completed ? 'line-through text-gray-500' : ''}`}
              onClick={() => setSelectedTask(selectedTask === task.id ? null : task.id)}
            >
              {task.title}
            </h3>
            <span className={`px-2 py-1 text-xs rounded ${
              task.priority === 'high' ? 'bg-red-100 text-red-800' :
              task.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
              'bg-green-100 text-green-800'
            }`}>
              {task.priority}
            </span>
          </div>
          
          {(selectedTask === task.id || showDescription) && task.description && (
            <p className="text-gray-600 mb-2 text-sm">{task.description}</p>
          )}
          
          <div className="flex items-center justify-between text-sm text-gray-500">
            <span>Due: {new Date(task.due_date).toLocaleDateString()}</span>
            <div className="flex gap-2">
              <button
                onClick={() => setEditingTask(task.id)}
                className="text-blue-600 hover:text-blue-800"
              >
                Edit
              </button>
              <button
                onClick={() => deleteTask(task.id)}
                className="text-red-600 hover:text-red-800"
              >
                Delete
              </button>
            </div>
          </div>
          
          {task.tags && task.tags.length > 0 && (
            <div className="flex gap-1 mt-2">
              {task.tags.map((tag, index) => (
                <span key={index} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );

  const getCurrentTasks = () => {
    switch (activeTab) {
      case 'today':
        return todayTasks;
      case 'overdue':
        return overdueTasks;
      case 'all':
        return allTasks;
      default:
        return [];
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Navigation */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-8 py-6">
          <h1 className="text-2xl font-bold text-gray-800 text-center mb-6">Tasks</h1>
          
          <nav className="flex justify-center">
            <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
              <button
                onClick={() => setActiveTab('today')}
                className={`flex items-center gap-2 px-4 py-2 rounded-md transition-colors ${
                  activeTab === 'today' ? 'bg-white text-blue-700 shadow-sm' : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                <span>📋</span>
                Today's Tasks
              </button>
              
              <button
                onClick={() => setActiveTab('overdue')}
                className={`flex items-center gap-2 px-4 py-2 rounded-md transition-colors ${
                  activeTab === 'overdue' ? 'bg-white text-red-700 shadow-sm' : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                <span>⚠️</span>
                Due Tasks
              </button>
              
              <button
                onClick={() => setActiveTab('all')}
                className={`flex items-center gap-2 px-4 py-2 rounded-md transition-colors ${
                  activeTab === 'all' ? 'bg-white text-gray-700 shadow-sm' : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                <span>📝</span>
                All Tasks
              </button>
            </div>
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-8 py-8 flex flex-col h-[calc(100vh-180px)]">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-3xl font-bold text-gray-800">
            {activeTab === 'today' ? "Today's Tasks" :
             activeTab === 'overdue' ? 'Overdue Tasks' :
             'All Tasks'}
          </h2>
          <div className="flex items-center gap-4">
            <span className="text-gray-500">
              {getCurrentTasks().length} task(s)
            </span>
            {activeTab === 'today' && (
              <button
                onClick={() => setShowAddForm(!showAddForm)}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              >
                {showAddForm ? 'Cancel' : 'Add New Task'}
              </button>
            )}
          </div>
        </div>

        {/* Add Task Form (only for Today's Tasks) */}
        {activeTab === 'today' && showAddForm && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6 flex-shrink-0">
            <h3 className="text-lg font-semibold mb-4">Create New Task</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Title *
                </label>
                <input
                  type="text"
                  name="title"
                  value={formData.title}
                  onChange={handleFormChange}
                  placeholder="Enter task title"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleFormChange}
                  placeholder="Enter task description"
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Due Date
                  </label>
                  <input
                    type="datetime-local"
                    name="due_date"
                    value={formData.due_date}
                    onChange={handleFormChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Priority
                  </label>
                  <select
                    name="priority"
                    value={formData.priority}
                    onChange={handleFormChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Status
                  </label>
                  <select
                    name="status"
                    value={formData.status}
                    onChange={handleFormChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="pending">Pending</option>
                    <option value="in_progress">In Progress</option>
                    <option value="completed">Completed</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Estimated Duration (hours)
                  </label>
                  <input
                    type="number"
                    name="estimated_duration"
                    value={formData.estimated_duration}
                    onChange={handleFormChange}
                    min="1"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tags (comma separated)
                </label>
                <input
                  type="text"
                  name="tags"
                  value={formData.tags}
                  onChange={handleFormChange}
                  placeholder="work, urgent, meeting"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={handleAddTask}
                  disabled={loading || !formData.title.trim()}
                  className="flex-1 px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {loading ? 'Creating...' : 'Create Task'}
                </button>
                <button
                  type="button"
                  onClick={resetForm}
                  className="px-6 py-3 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Message Display */}
        {message && (
          <div className={`border px-4 py-3 rounded mb-4 flex-shrink-0 ${
            message.includes('Error') ? 'bg-red-100 border-red-400 text-red-700' : 'bg-blue-100 border-blue-400 text-blue-700'
          }`}>
            {message}
            <button
              onClick={() => setMessage('')}
              className="float-right hover:opacity-75"
            >
              ×
            </button>
          </div>
        )}

        {/* Tasks List */}
        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
              <p className="text-gray-500 mt-2">Loading tasks...</p>
            </div>
          ) : getCurrentTasks().length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500 text-lg">
                {activeTab === 'today' ? 'No tasks for today. Add one above!' :
                 activeTab === 'overdue' ? 'No overdue tasks. Great job!' :
                 'No tasks found.'}
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {getCurrentTasks().map((task) => (
                <TaskItem 
                  key={task.id} 
                  task={task} 
                  showDescription={activeTab === 'all'}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TaskManager;