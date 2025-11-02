import React, { useState, useEffect } from 'react';

const BASE_URL = 'http://127.0.0.1:8000';

function TaskHeatmap() {
  const [taskData, setTaskData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());

  useEffect(() => {
    fetchTaskData();
  }, [selectedYear]);

  const fetchTaskData = async () => {
    setLoading(true);
    try {
      // Fetch all tasks first to test the basic endpoint
      const response = await fetch(
        `${BASE_URL}/tasks/`,
        {
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Task fetch error:', response.status, errorText);
        throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
      }

      const result = await response.json();
      if (result.success) {
        // Filter completed tasks and by selected year on frontend
        const completedTasks = result.data.filter(task => {
          // First filter for completed tasks
          if (task.status !== 'completed' || !task.completion_date) return false;
          // Then filter by selected year
          const taskYear = new Date(task.completion_date).getFullYear();
          return taskYear === selectedYear;
        });
        processTaskData(completedTasks);
      } else {
        throw new Error(result.message || 'Failed to fetch task data');
      }
    } catch (e) {
      console.error('Error fetching task data:', e);
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const processTaskData = (tasks) => {
    const tasksByDate = {};
    
    tasks.forEach(task => {
      if (task.completion_date) {
        const completionDate = new Date(task.completion_date);
        const dateKey = completionDate.toISOString().split('T')[0];
        tasksByDate[dateKey] = (tasksByDate[dateKey] || 0) + 1;
      }
    });

    // Generate all days for the year organized by weeks
    const yearStart = new Date(selectedYear, 0, 1);
    const yearEnd = new Date(selectedYear, 11, 31);
    
    // Find the first Sunday of the year (or before if year doesn't start on Sunday)
    const firstSunday = new Date(yearStart);
    firstSunday.setDate(yearStart.getDate() - yearStart.getDay());
    
    const weeks = [];
    let currentDate = new Date(firstSunday);
    
    while (currentDate <= yearEnd || weeks.length < 53) {
      const weekData = [];
      
      for (let dayOfWeek = 0; dayOfWeek < 7; dayOfWeek++) {
        const dateKey = currentDate.toISOString().split('T')[0];
        const completedCount = tasksByDate[dateKey] || 0;
        const isCurrentYear = currentDate.getFullYear() === selectedYear;
        
        // Calculate completion percentage
        let completionPercentage = 0;
        if (completedCount > 0) {
          if (completedCount <= 2) completionPercentage = 25;
          else if (completedCount <= 4) completionPercentage = 50;
          else if (completedCount <= 6) completionPercentage = 75;
          else completionPercentage = 100;
        }
        
        weekData.push({
          date: new Date(currentDate),
          count: completedCount,
          completionPercentage: completionPercentage,
          isCurrentYear: isCurrentYear,
          dayOfWeek: dayOfWeek
        });
        
        currentDate.setDate(currentDate.getDate() + 1);
      }
      
      weeks.push(weekData);
      
      // Stop after we've covered the full year or have 53 weeks
      if (currentDate > yearEnd && weeks.length >= 53) break;
    }
    
    setTaskData(weeks);
    console.log('Generated weeks data:', weeks.length, 'weeks');
  };

  // Get month labels for the top of the grid
  const getMonthLabels = () => {
    if (taskData.length === 0) return [];
    
    const labels = [];
    let lastMonth = -1;
    
    taskData.forEach((week, weekIndex) => {
      // Check the first day of each week to see if it's a new month
      const firstDay = week[0];
      if (firstDay && firstDay.isCurrentYear) {
        const month = firstDay.date.getMonth();
        if (month !== lastMonth) {
          labels.push({
            month: monthNames[month],
            weekIndex: weekIndex
          });
          lastMonth = month;
        }
      }
    });
    
    return labels;
  };

  const getIntensityClass = (completionPercentage) => {
    if (completionPercentage === 0) return 'completion-0';
    if (completionPercentage <= 25) return 'completion-25';
    if (completionPercentage <= 50) return 'completion-50';
    if (completionPercentage <= 75) return 'completion-75';
    return 'completion-100';
  };

  const formatTooltip = (dayData) => {
    const date = dayData.date.toLocaleDateString();
    const taskText = dayData.count === 1 ? 'task' : 'tasks';
    if (dayData.count === 0) {
      return `No tasks completed on ${date}`;
    }
    return `${dayData.count} ${taskText} completed on ${date} (${dayData.completionPercentage}% completion)`;
  };

  const monthNames = [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
  ];

  const weekDayLabels = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']; // Show all weekdays
  const weekDayIndices = [0, 1, 2, 3, 4, 5, 6]; // All days of the week

  if (loading) {
    return (
      <div className="task-heatmap-container">
        <div className="task-heatmap-header">
          <h3>Task Completion Heatmap</h3>
        </div>
        <div className="task-heatmap-loading">Loading heatmap data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="task-heatmap-container">
        <div className="task-heatmap-header">
          <h3>Task Completion Heatmap</h3>
        </div>
        <div className="task-heatmap-error">Error loading data: {error}</div>
      </div>
    );
  }

  return (
    <div className="task-heatmap-container">
      <div className="task-heatmap-header">
        <h3>Task Completion Heatmap - {selectedYear}</h3>
        <select 
          value={selectedYear} 
          onChange={(e) => setSelectedYear(parseInt(e.target.value))}
          className="task-heatmap-year-select"
        >
          {Array.from({length: 5}, (_, i) => new Date().getFullYear() - i).map(year => (
            <option key={year} value={year}>{year}</option>
          ))}
        </select>
      </div>
      
      <div className="task-heatmap-content">
        {/* Month labels */}
        <div className="task-heatmap-month-labels">
          {getMonthLabels().map((label, index) => (
            <div 
              key={index} 
              className="task-heatmap-month-label"
              style={{ gridColumnStart: label.weekIndex + 2 }}
            >
              {label.month}
            </div>
          ))}
        </div>
        
        <div className="task-heatmap-grid">
          {/* Weekdays column on the left */}
          <div className="task-heatmap-weekdays">
            {weekDayLabels.map((day, index) => (
              <div key={day} className="task-heatmap-weekday">{day}</div>
            ))}
          </div>
          
          {/* Week columns */}
          {taskData.map((weekData, weekIndex) => (
            <div key={weekIndex} className="task-heatmap-week">
              {weekData.map((dayData, dayIndex) => {
                // Show all days of the week
                return (
                  <div
                    key={dayIndex}
                    className={`task-heatmap-day ${getIntensityClass(dayData.completionPercentage)} ${!dayData.isCurrentYear ? 'out-of-year' : ''}`}
                    title={formatTooltip(dayData)}
                  />
                );
              })}
            </div>
          ))}
        </div>
        
        <div className="task-heatmap-legend">
          <span className="task-heatmap-legend-label">Less</span>
          <div className="task-heatmap-legend-scale">
            <div className="task-heatmap-legend-item completion-0" title="0% completion"></div>
            <div className="task-heatmap-legend-item completion-25" title="25% completion"></div>
            <div className="task-heatmap-legend-item completion-50" title="50% completion"></div>
            <div className="task-heatmap-legend-item completion-75" title="75% completion"></div>
            <div className="task-heatmap-legend-item completion-100" title="100% completion"></div>
          </div>
          <span className="task-heatmap-legend-label">More</span>
        </div>
      </div>
    </div>
  );
}

export default TaskHeatmap;
