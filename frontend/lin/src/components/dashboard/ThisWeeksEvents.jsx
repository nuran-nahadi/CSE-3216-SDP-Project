import React, { useState, useEffect } from 'react';

const BASE_URL = 'http://127.0.0.1:8000';

function ThisWeeksEvents() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchUpcomingEvents();
  }, []);

  const fetchUpcomingEvents = async () => {
    setLoading(true);
    try {
      // Calculate date range for this week (next 7 days)
      const now = new Date();
      const endDate = new Date(now);
      endDate.setDate(now.getDate() + 7);
      
      const startDateStr = now.toISOString();
      const endDateStr = endDate.toISOString();
      
      const response = await fetch(
        `${BASE_URL}/events?start_date=${startDateStr}&end_date=${endDateStr}&limit=50`,
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
        setEvents(result.data || []);
      } else {
        throw new Error(result.message || 'Failed to fetch upcoming events');
      }
    } catch (e) {
      console.error('Error fetching upcoming events:', e);
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (dateString) => {
    return new Date(dateString).toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  const formatDateHeader = (date) => {
    return date.toLocaleDateString('en-US', {
      month: 'short'
    });
  };

  const getPriorityColor = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'high': return '#ef4444';
      case 'medium': return '#f59e0b';
      case 'low': return '#10b981';
      default: return '#3b82f6';
    }
  };

  const getTimeSlot = (dateString) => {
    const hour = new Date(dateString).getHours();
    return Math.floor(hour / 2); // 2-hour slots: 0-1, 2-3, 4-5, etc.
  };

  const getEventDuration = (startTime, endTime) => {
    if (!startTime || !endTime) return 1;
    const start = new Date(startTime);
    const end = new Date(endTime);
    const durationHours = (end - start) / (1000 * 60 * 60);
    return Math.max(Math.ceil(durationHours / 2), 1); // Convert to 2-hour slots, minimum 1
  };

  // Generate 7 days starting from today
  const generateWeekDays = () => {
    const days = [];
    const today = new Date();
    for (let i = 0; i < 7; i++) {
      const date = new Date(today);
      date.setDate(today.getDate() + i);
      days.push(date);
    }
    return days;
  };

  // Generate time slots (12 slots for 24 hours, 2-hour intervals)
  const generateTimeSlots = () => {
    const slots = [];
    for (let i = 0; i < 12; i++) {
      const startHour = i * 2;
      const endHour = startHour + 2;
      slots.push({
        slot: i,
        label: `${startHour.toString().padStart(2, '0')}:00`
      });
    }
    return slots;
  };

  const weekDays = generateWeekDays();
  const timeSlots = generateTimeSlots();

  // Group events by date and time slot
  const eventsByDateAndTime = {};
  events.forEach(event => {
    const eventDate = new Date(event.start_time).toDateString();
    const timeSlot = getTimeSlot(event.start_time);
    const duration = getEventDuration(event.start_time, event.end_time);
    
    if (!eventsByDateAndTime[eventDate]) {
      eventsByDateAndTime[eventDate] = {};
    }
    
    // Place event in appropriate time slots based on duration
    for (let i = 0; i < duration; i++) {
      const currentSlot = timeSlot + i;
      if (currentSlot < 12) { // Don't exceed our time grid
        if (!eventsByDateAndTime[eventDate][currentSlot]) {
          eventsByDateAndTime[eventDate][currentSlot] = [];
        }
        // Only add the event to the first slot, but mark its span
        if (i === 0) {
          eventsByDateAndTime[eventDate][currentSlot].push({
            ...event,
            duration: duration
          });
        }
      }
    }
  });

  if (loading) {
    return (
      <div className="weekly-calendar-container">
        <h3 className="weekly-calendar-title">Upcoming Events</h3>
        <div className="weekly-calendar-loading">Loading events...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="weekly-calendar-container">
        <h3 className="weekly-calendar-title">Upcoming Events</h3>
        <div className="weekly-calendar-error">Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="weekly-calendar-container">
      <h3 className="weekly-calendar-title">Upcoming Events</h3>
      <div className="weekly-calendar-grid">
        {/* Header row with dates */}
        <div className="calendar-header">
          {weekDays.map((day, index) => (
            <div key={index} className="date-header">
              <div className="date-label">{formatDateHeader(day)}</div>
              <div className="date-number">{day.getDate()}</div>
            </div>
          ))}
        </div>
        
        {/* Time slots and events */}
        <div className="calendar-body">
          {timeSlots.map((timeSlot) => (
            <div key={timeSlot.slot} className="calendar-row">
              <div className="time-label">{timeSlot.label}</div>
              {weekDays.map((day, dayIndex) => {
                const dateKey = day.toDateString();
                const eventsInSlot = eventsByDateAndTime[dateKey]?.[timeSlot.slot] || [];
                
                return (
                  <div key={dayIndex} className="calendar-cell">
                    {eventsInSlot.map((event, eventIndex) => (
                      <div
                        key={event.id}
                        className="calendar-event"
                        style={{
                          backgroundColor: getPriorityColor(event.priority),
                          gridRow: `span ${event.duration}`,
                          height: `${event.duration * 40 - 2}px`
                        }}
                        title={`${event.title} - ${formatTime(event.start_time)} to ${formatTime(event.end_time)}`}
                      >
                        <div className="event-title">{event.title}</div>
                        {event.duration === 1 && (
                          <div className="event-time">{formatTime(event.start_time)}</div>
                        )}
                      </div>
                    ))}
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default ThisWeeksEvents;
