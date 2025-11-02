import React, { useState, useEffect } from 'react';
import MetricCard from './MetricCard';

const BASE_URL = 'http://127.0.0.1:8000';

function DashboardUpcomingEvents() {
    const [eventsData, setEventsData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchUpcomingEvents = async () => {
            try {
                setLoading(true);
                
                // Get current month's date range
                const now = new Date();
                const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
                const endOfMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0);
                
                // Format dates to ISO string
                const startDate = startOfMonth.toISOString();
                const endDate = endOfMonth.toISOString();
                
                // Fetch events for this month
                const response = await fetch(
                    `${BASE_URL}/events?start_date=${startDate}&end_date=${endDate}&limit=100`,
                    {
                        headers: {
                            'Authorization': `Bearer ${localStorage.getItem('token')}`
                        }
                    }
                );

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const result = await response.json();

                if (result.success) {
                    // Filter events that are upcoming (from today onwards)
                    const today = new Date();
                    today.setHours(0, 0, 0, 0); // Start of today
                    
                    const upcomingEvents = result.data.filter(event => {
                        const eventDate = new Date(event.start_time);
                        eventDate.setHours(0, 0, 0, 0); // Start of event day
                        return eventDate >= today;
                    });

                    setEventsData({
                        upcomingCount: upcomingEvents.length,
                        totalMonthEvents: result.data.length,
                        nextEvent: upcomingEvents.length > 0 ? upcomingEvents[0] : null
                    });
                } else {
                    throw new Error(result.message || 'Failed to fetch events data.');
                }

            } catch (e) {
                console.error("API Error:", e.message);
                setError(e.message);
            } finally {
                setLoading(false);
            }
        };

        fetchUpcomingEvents();
    }, []);

    if (loading) {
        return (
            <MetricCard title="Upcoming Events" colorClass="metric-card-orange">
                <p className="metric-card-value">Loading...</p>
            </MetricCard>
        );
    }
    
    if (error) {
        return (
            <MetricCard title="Upcoming Events" colorClass="metric-card-orange">
                <p style={{fontSize: '1rem'}}>Error loading data.</p>
            </MetricCard>
        );
    }

    const upcomingCount = eventsData ? eventsData.upcomingCount : 0;
    const nextEvent = eventsData ? eventsData.nextEvent : null;
    
    return (
        <MetricCard 
            title={`Upcoming Events (${new Date().toLocaleString('default', { month: 'long' })})`}
            value={upcomingCount}
            unit={upcomingCount === 1 ? "event" : "events"}
            colorClass="metric-card-orange"
        >
            {nextEvent && (
                <p style={{fontSize: '0.875rem', color: 'rgba(255, 255, 255, 0.8)', margin: '0.5rem 0 0'}}>
                    Next: {nextEvent.title} on {new Date(nextEvent.start_time).toLocaleDateString()}
                </p>
            )}
            {!nextEvent && upcomingCount === 0 && (
                <p style={{fontSize: '0.875rem', color: 'rgba(255, 255, 255, 0.8)', margin: '0.5rem 0 0'}}>
                    No upcoming events this month
                </p>
            )}
        </MetricCard>
    );
}

export default DashboardUpcomingEvents;