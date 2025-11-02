import React, { useState } from 'react';

function AddEventModal({ 
  isOpen, 
  selectedDate, 
  onClose, 
  onSubmit, 
  loading 
}) {
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    startTime: '09:00',
    endTime: '10:00',
    location: "",
    priority: 'medium'
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.title.trim()) return;
    
    const [startHours, startMinutes] = formData.startTime.split(':');
    const [endHours, endMinutes] = formData.endTime.split(':');
    
    const startDateTime = new Date(selectedDate);
    startDateTime.setHours(parseInt(startHours), parseInt(startMinutes), 0, 0);
    
    const endDateTime = new Date(selectedDate);
    endDateTime.setHours(parseInt(endHours), parseInt(endMinutes), 0, 0);

    const payload = {
      title: formData.title,
      description: formData.description || "",
      start_time: startDateTime.toISOString(),
      end_time: endDateTime.toISOString(),
      location: formData.location || "",
      priority: formData.priority,
      tags: [],
      is_all_day: false
    };

    const success = await onSubmit(payload);
    if (success) {
      // Reset form
      setFormData({
        title: "",
        description: "",
        startTime: '09:00',
        endTime: '10:00',
        location: "",
        priority: 'medium'
      });
    }
  };

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  if (!isOpen) return null;

  return (
    <div className="calendar-modal-bg" onClick={onClose}>
      <div className="calendar-modal" onClick={e => e.stopPropagation()}>
        <button className="calendar-modal-close" onClick={onClose} title="Close">×</button>
        <div className="calendar-modal-title">
          Add Event for {selectedDate && selectedDate.toLocaleDateString()}
        </div>
        
        <form onSubmit={handleSubmit} className="calendar-form">
          <div className="calendar-form-group">
            <label className="calendar-form-label">Title *</label>
            <input 
              type="text" 
              value={formData.title} 
              onChange={e => handleChange('title', e.target.value)} 
              required 
              className="calendar-form-input"
              placeholder="Enter event title"
            />
          </div>
          
          <div className="calendar-form-group">
            <label className="calendar-form-label">Description</label>
            <textarea 
              value={formData.description} 
              onChange={e => handleChange('description', e.target.value)} 
              className="calendar-form-textarea"
              placeholder="Enter event description (optional)"
            />
          </div>

          <div className="calendar-form-group">
            <label className="calendar-form-label">Priority</label>
            <select 
              value={formData.priority} 
              onChange={e => handleChange('priority', e.target.value)}
              className="calendar-form-select"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </div>
          
          <div className="calendar-form-row">
            <div className="calendar-form-group">
              <label className="calendar-form-label">Start Time</label>
              <input 
                type="time" 
                value={formData.startTime} 
                onChange={e => handleChange('startTime', e.target.value)}
                className="calendar-form-input"
              />
            </div>
            <div className="calendar-form-group">
              <label className="calendar-form-label">End Time</label>
              <input 
                type="time" 
                value={formData.endTime} 
                onChange={e => handleChange('endTime', e.target.value)}
                className="calendar-form-input"
              />
            </div>
          </div>
          
          <div className="calendar-form-group">
            <label className="calendar-form-label">Location</label>
            <input 
              type="text" 
              value={formData.location} 
              onChange={e => handleChange('location', e.target.value)} 
              className="calendar-form-input"
              placeholder="Enter location (optional)"
            />
          </div>
          
          <button 
            type="submit" 
            disabled={loading || !formData.title.trim()} 
            className={`calendar-form-submit ${(loading || !formData.title.trim()) ? 'disabled' : ''}`}
          >
            {loading ? 'Creating Event...' : 'Create Event'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default AddEventModal;
