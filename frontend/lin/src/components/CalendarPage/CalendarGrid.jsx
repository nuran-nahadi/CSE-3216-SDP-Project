import React from 'react';

function CalendarGrid({ 
  currentDate, 
  eventsByDate, 
  tasksByDate, 
  onDateClick,
  loading 
}) {
  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();
  
  const getDaysInMonth = (year, month) => {
    return new Date(year, month + 1, 0).getDate();
  };

  const getFirstDayOfWeek = (year, month) => {
    return new Date(year, month, 1).getDay();
  };

  const daysInMonth = getDaysInMonth(year, month);
  const firstDayOfWeek = getFirstDayOfWeek(year, month);

  // Build calendar grid
  const calendarDays = [];
  for (let i = 0; i < firstDayOfWeek; i++) {
    calendarDays.push(null);
  }
  for (let d = 1; d <= daysInMonth; d++) {
    calendarDays.push(d);
  }
  while (calendarDays.length % 7 !== 0) {
    calendarDays.push(null);
  }

  const getEventTaskSummary = (events, tasks) => {
    const eventCount = events.length;
    const taskCount = tasks.length;
    
    if (eventCount === 0 && taskCount === 0) return null;

    return (
      <div className="calendar-event-summary">
        {eventCount > 0 && (
          <div className="calendar-event-text">
            {eventCount} event{eventCount !== 1 ? 's' : ''} pending
          </div>
        )}
        {taskCount > 0 && (
          <div className="calendar-task-text">
            {taskCount} task{taskCount !== 1 ? 's' : ''} pending
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return <div style={{ textAlign: "center", padding: 24 }}>Loading calendar...</div>;
  }

  return (
    <table className="calendar-table">
      <thead>
        <tr>
          <th>Sun</th>
          <th>Mon</th>
          <th>Tue</th>
          <th>Wed</th>
          <th>Thu</th>
          <th>Fri</th>
          <th>Sat</th>
        </tr>
      </thead>
      <tbody>
        {Array.from({ length: calendarDays.length / 7 }).map((_, weekIdx) => (
          <tr key={weekIdx}>
            {calendarDays.slice(weekIdx * 7, weekIdx * 7 + 7).map((day, i) => {
              const today = new Date();
              const dateStr = day ? `${year}-${String(month + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}` : null;
              const isCurrentDate = day && year === today.getFullYear() && month === today.getMonth() && day === today.getDate();
              
              const dayEvents = dateStr ? eventsByDate[dateStr] || [] : [];
              const dayTasks = dateStr ? tasksByDate[dateStr] || [] : [];
              
              return (
                <td 
                  key={i} 
                  className={isCurrentDate ? 'current-cell' : ''} 
                  onClick={() => day && onDateClick(new Date(year, month, day))} 
                  style={{ position: 'relative' }}
                >
                  <div className={`calendar-day-number${isCurrentDate ? ' current' : ''}${day ? '' : ' empty'}`}>
                    {day || ""}
                  </div>
                  {getEventTaskSummary(dayEvents, dayTasks)}
                </td>
              );
            })}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default CalendarGrid;
