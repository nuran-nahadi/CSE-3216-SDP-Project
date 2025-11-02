import React from 'react';

const months = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"
];

function CalendarHeader({ currentDate, onMonthChange, onYearChange, onPrevMonth, onNextMonth }) {
  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();
  const yearRange = Array.from({length: 21}, (_, i) => year - 10 + i);

  const handleMonthChange = (e) => {
    const newMonth = months.indexOf(e.target.value);
    onMonthChange(newMonth);
  };

  const handleYearChange = (e) => {
    const newYear = parseInt(e.target.value, 10);
    onYearChange(newYear);
  };

  return (
    <div className="calendar-card">
      <div className="calendar-header" style={{ backgroundColor: '#8b5cf6', color: 'white', position: 'relative', width: '100%', margin: 0, padding: '1.5rem 2rem' }}>
        <div style={{ display: 'flex', gap: 8, flexShrink: 0 }}>
          <div style={{ position: 'relative', display: 'inline-block' }}>
            <select 
              value={months[month]} 
              onChange={handleMonthChange}
              className="calendar-select"
              style={{ paddingRight: '30px', appearance: 'none' }}
            >
              {months.map((m) => (
                <option key={m} value={m}>{m}</option>
              ))}
            </select>
            <svg 
              style={{ 
                position: 'absolute', 
                right: '8px', 
                top: '50%', 
                transform: 'translateY(-50%)', 
                pointerEvents: 'none',
                width: '12px',
                height: '12px'
              }} 
              viewBox="0 0 24 24" 
              fill="none"
            >
              <path d="M6 9l6 6 6-6" stroke="#6366f1" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <div style={{ position: 'relative', display: 'inline-block' }}>
            <select
              value={year}
              onChange={handleYearChange}
              className="calendar-select"
              style={{ paddingRight: '30px', appearance: 'none' }}
            >
              {yearRange.map((y) => (
                <option key={y} value={y}>{y}</option>
              ))}
            </select>
            <svg 
              style={{ 
                position: 'absolute', 
                right: '8px', 
                top: '50%', 
                transform: 'translateY(-50%)', 
                pointerEvents: 'none',
                width: '12px',
                height: '12px'
              }} 
              viewBox="0 0 24 24" 
              fill="none"
            >
              <path d="M6 9l6 6 6-6" stroke="#6366f1" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
        </div>
        <div className="calendar-controls" style={{ position: 'absolute', left: '50%', transform: 'translateX(-50%)', flexShrink: 0 }}>
          <button onClick={onPrevMonth}>
            <svg width="18" height="18" viewBox="0 0 24 24">
              <path d="M15 6l-6 6 6 6" stroke="white" strokeWidth="2.5" fill="none" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
          <span>{months[month]} {year}</span>
          <button onClick={onNextMonth}>
            <svg width="18" height="18" viewBox="0 0 24 24">
              <path d="M9 6l6 6-6 6" stroke="white" strokeWidth="2.5" fill="none" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        </div>
        <div style={{ width: '200px' }}></div>
      </div>
    </div>
  );
}

export default CalendarHeader;
