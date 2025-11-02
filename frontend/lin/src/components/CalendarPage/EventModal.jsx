import React from 'react';
import { FaTrash } from "react-icons/fa";

function EventModal({ 
  modalDate, 
  events, 
  tasks, 
  onClose, 
  onAddEvent, 
  onDelete 
}) {
  if (!modalDate) return null;

  const dateStr = `${modalDate.getFullYear()}-${String(modalDate.getMonth() + 1).padStart(2, "0")}-${String(modalDate.getDate()).padStart(2, "0")}`;
  const dayEvents = events[dateStr] || [];
  const dayTasks = tasks[dateStr] || [];

  const getPriorityColor = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'high': return { bg: '#fef2f2', border: '#fecaca', text: '#991b1b' };
      case 'medium': return { bg: '#fff7ed', border: '#fed7aa', text: '#c2410c' };
      case 'low': return { bg: '#f0fdf4', border: '#bbf7d0', text: '#065f46' };
      default: return { bg: '#f0f9ff', border: '#bae6fd', text: '#0c4a6e' };
    }
  };

  return (
    <div className="calendar-modal-bg" onClick={onClose}>
      <div className="calendar-modal" onClick={e => e.stopPropagation()}>
        <button className="calendar-modal-close" onClick={onClose} title="Close">×</button>
        <div className="calendar-modal-title">Events for {modalDate.toLocaleDateString()}</div>
        
        {dayEvents.length === 0 && dayTasks.length === 0 ? (
          <div className="calendar-modal-empty">No events or tasks for this date.</div>
        ) : (
          <>
            {dayEvents.length > 0 && (
              <>
                <div style={{ fontWeight: 600, marginBottom: 8, color: '#059669' }}>Events:</div>
                <ul className="calendar-modal-list" style={{ maxHeight: 180, overflowY: 'auto', marginBottom: 16 }}>
                  {dayEvents.map((ev, i) => {
                    const colors = getPriorityColor(ev.priority);
                    return (
                      <li key={"ev" + i} style={{ 
                        display: 'flex', 
                        justifyContent: 'space-between', 
                        alignItems: 'flex-start',
                        marginBottom: 12, 
                        padding: 8, 
                        background: colors.bg, 
                        borderRadius: 8,
                        border: `1px solid ${colors.border}`
                      }}>
                        <div style={{ flex: 1 }}>
                          <div style={{ fontWeight: 600, color: colors.text }}>
                            {ev.title}
                            {ev.priority && (
                              <span style={{ 
                                fontSize: 10, 
                                marginLeft: 8, 
                                padding: '2px 6px', 
                                borderRadius: 4, 
                                background: colors.border,
                                color: colors.text,
                                textTransform: 'uppercase',
                                fontWeight: 700
                              }}>
                                {ev.priority}
                              </span>
                            )}
                          </div>
                          {ev.description && (
                            <div style={{ fontSize: 13, color: colors.text, marginTop: 2, opacity: 0.8 }}>{ev.description}</div>
                          )}
                          <div style={{ fontSize: 12, color: colors.text, marginTop: 4, opacity: 0.7 }}>
                            {new Date(ev.start_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})} - {new Date(ev.end_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                          </div>
                          {ev.location && (
                            <div style={{ fontSize: 12, color: colors.text, marginTop: 2, opacity: 0.7 }}>📍 {ev.location}</div>
                          )}
                        </div>
                        <button 
                          style={{ background: 'none', border: 'none', cursor: 'pointer', marginLeft: 8 }} 
                          title="Delete Event" 
                          onClick={() => onDelete("event", ev.id)}
                        >
                          <FaTrash size={13} color="#dc2626" />
                        </button>
                      </li>
                    );
                  })}
                </ul>
              </>
            )}
            
            {dayTasks.length > 0 && (
              <>
                <div style={{ fontWeight: 600, marginBottom: 8, color: '#dc2626' }}>Tasks:</div>
                <ul className="calendar-modal-list" style={{ maxHeight: 180, overflowY: 'auto' }}>
                  {dayTasks.map((t, i) => {
                    const colors = getPriorityColor(t.priority);
                    return (
                      <li key={"tk" + i} style={{ 
                        display: 'flex', 
                        flexDirection: 'column', 
                        alignItems: 'flex-start', 
                        marginBottom: 12,
                        padding: 8, 
                        background: colors.bg, 
                        borderRadius: 8,
                        border: `1px solid ${colors.border}`
                      }}>
                        <span style={{ fontWeight: 600, color: colors.text }}>
                          {t.title}
                          {t.priority && (
                            <span style={{ 
                              fontSize: 10, 
                              marginLeft: 8, 
                              padding: '2px 6px', 
                              borderRadius: 4, 
                              background: colors.border,
                              color: colors.text,
                              textTransform: 'uppercase',
                              fontWeight: 700
                            }}>
                              {t.priority}
                            </span>
                          )}
                        </span>
                        {t.description && (
                          <span style={{ fontSize: 13, color: colors.text, marginTop: 2, opacity: 0.8 }}>{t.description}</span>
                        )}
                        <div style={{ fontSize: 12, color: colors.text, marginTop: 4, opacity: 0.7 }}>
                          Due: {t.due_date ? new Date(t.due_date).toLocaleString() : 'No due date'}
                        </div>
                        <div style={{ fontSize: 12, color: colors.text, marginTop: 2, opacity: 0.7 }}>
                          Status: {t.status}
                        </div>
                      </li>
                    );
                  })}
                </ul>
              </>
            )}
          </>
        )}
        
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: 16 }}>
          <button 
            className="calendar-add-event-btn"
            onClick={() => onAddEvent(modalDate)}
          >
            ADD EVENT
          </button>
        </div>
      </div>
    </div>
  );
}

export default EventModal;
