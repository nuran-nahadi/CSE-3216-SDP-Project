import React from 'react';
import TodaysTasks from './TodaysTasks';
import ThisWeeksEvents from './ThisWeeksEvents';

function TasksAndEvents() {
  return (
    <div className="tasks-and-events-container">
      <TodaysTasks />
      <ThisWeeksEvents />
    </div>
  );
}

export default TasksAndEvents;
