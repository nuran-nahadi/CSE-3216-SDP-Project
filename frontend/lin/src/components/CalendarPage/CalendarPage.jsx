import React, { useState, useEffect, useCallback } from "react";
import CalendarHeader from './CalendarHeader';
import CalendarGrid from './CalendarGrid';
import EventModal from './EventModal';
import AddEventModal from './AddEventModal';

const BASE_URL = 'http://127.0.0.1:8000';

function CalendarPage() {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [events, setEvents] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalDate, setModalDate] = useState(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [addLoading, setAddLoading] = useState(false);
  
  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();

  const getDaysInMonth = (year, month) => {
    return new Date(year, month + 1, 0).getDate();
  };

  const daysInMonth = getDaysInMonth(year, month);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      // Fetch events using the calendar endpoint for better performance
      const eventRes = await fetch(`${BASE_URL}/events/calendar/${year}/${month + 1}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (eventRes.ok) {
        const eventJson = await eventRes.json();
        if (eventJson.success) {
          setEvents(eventJson.data.events || []);
        }
      } else {
        console.error('Failed to fetch events:', eventRes.status);
        setEvents([]);
      }

      // Fetch tasks for the current month
      const start = new Date(year, month, 1).toISOString();
      const end = new Date(year, month, daysInMonth, 23, 59, 59).toISOString();
      const taskRes = await fetch(`${BASE_URL}/tasks?start_date=${start}&end_date=${end}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (taskRes.ok) {
        const taskJson = await taskRes.json();
        if (taskJson.success && Array.isArray(taskJson.data)) {
          const taskList = taskJson.data.filter(t => {
            if (!t.due_date) return false;
            const d = new Date(t.due_date);
            return d.getFullYear() === year && d.getMonth() === month;
          });
          setTasks(taskList);
        }
      } else {
        console.error('Failed to fetch tasks:', taskRes.status);
        setTasks([]);
      }
    } catch (e) {
      console.error('Error fetching data:', e);
      setEvents([]);
      setTasks([]);
    }
    setLoading(false);
  }, [year, month, daysInMonth]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handlePrevMonth = () => {
    setCurrentDate(new Date(year, month - 1, 1));
  };

  const handleNextMonth = () => {
    setCurrentDate(new Date(year, month + 1, 1));
  };

  const handleMonthChange = (newMonth) => {
    setCurrentDate(new Date(year, newMonth, 1));
  };

  const handleYearChange = (newYear) => {
    setCurrentDate(new Date(newYear, month, 1));
  };

  // Event/task lookup
  const eventsByDate = {};
  events.forEach(ev => {
    if (!ev.start_time) return;
    const date = new Date(ev.start_time);
    const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
    if (!eventsByDate[key]) eventsByDate[key] = [];
    eventsByDate[key].push(ev);
  });

  const tasksByDate = {};
  tasks.forEach(t => {
    if (!t.due_date) return;
    const date = new Date(t.due_date);
    const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
    if (!tasksByDate[key]) tasksByDate[key] = [];
    tasksByDate[key].push(t);
  });

  const handleAddEvent = (selectedDate) => {
    setModalDate(selectedDate);
    setShowAddModal(true);
  };

  const handleAddSubmit = async (payload) => {
    setAddLoading(true);
    try {
      const response = await fetch(`${BASE_URL}/events`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(payload),
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          setShowAddModal(false);
          await fetchData();
          return true;
        } else {
          alert(`Failed to create event: ${result.message || 'Unknown error'}`);
          return false;
        }
      } else {
        const errorData = await response.json();
        alert(`Failed to create event: ${errorData.message || 'Unknown error'}`);
        return false;
      }
    } catch (e) {
      console.error('Error creating event:', e);
      alert(`Error creating event: ${e.message}`);
      return false;
    } finally {
      setAddLoading(false);
    }
  };

  const handleDelete = async (type, id) => {
    if (!window.confirm(`Are you sure you want to delete this ${type}?`)) return;
    
    try {
      const response = await fetch(`${BASE_URL}/${type === "event" ? "events" : "tasks"}/${id}`, { 
        method: "DELETE",
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        await fetchData();
      } else {
        alert(`Failed to delete ${type}`);
      }
    } catch (e) {
      console.error(`Error deleting ${type}:`, e);
      alert(`Error deleting ${type}`);
    }
  };

  return (
    <div className="calendar-outer">
      <CalendarHeader 
        currentDate={currentDate}
        onMonthChange={handleMonthChange}
        onYearChange={handleYearChange}
        onPrevMonth={handlePrevMonth}
        onNextMonth={handleNextMonth}
      />
      
      <CalendarGrid 
        currentDate={currentDate}
        eventsByDate={eventsByDate}
        tasksByDate={tasksByDate}
        onDateClick={setModalDate}
        loading={loading}
      />
      
      <EventModal 
        modalDate={modalDate}
        events={eventsByDate}
        tasks={tasksByDate}
        onClose={() => setModalDate(null)}
        onAddEvent={handleAddEvent}
        onDelete={handleDelete}
      />
      
      <AddEventModal 
        isOpen={showAddModal}
        selectedDate={modalDate}
        onClose={() => { setShowAddModal(false); setModalDate(null); }}
        onSubmit={handleAddSubmit}
        loading={addLoading}
      />
    </div>
  );
}

export default CalendarPage;