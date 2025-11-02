import React, { useState, useEffect } from 'react';
import MetricCard from './MetricCard';

const BASE_URL = 'http://127.0.0.1:8000';

function DashboardConsistency() {
    const [consistencyData, setConsistencyData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchConsistencyData = async () => {
            try {
                setLoading(true);

                // Check for overdue tasks (this breaks the streak)
                const overdueResponse = await fetch(
                    `${BASE_URL}/tasks/overdue`,
                    {
                        headers: {
                            'Authorization': `Bearer ${localStorage.getItem('token')}`
                        }
                    }
                );

                if (!overdueResponse.ok) {
                    throw new Error(`HTTP error! status: ${overdueResponse.status}`);
                }

                const overdueResult = await overdueResponse.json();
                
                // If there are overdue tasks, streak is broken (0 days)
                if (overdueResult.success && overdueResult.data.length > 0) {
                    setConsistencyData({
                        streak: 0,
                        status: 'broken',
                        overdueCount: overdueResult.data.length
                    });
                    setLoading(false);
                    return;
                }

                // If no overdue tasks, calculate consecutive completed days
                await calculateStreak();

            } catch (e) {
                console.error("API Error:", e.message);
                setError(e.message);
                setLoading(false);
            }
        };

        const calculateStreak = async () => {
            try {
                // Fetch all completed tasks to analyze completion patterns
                const response = await fetch(
                    `${BASE_URL}/tasks/?status=completed&page=1&limit=1000`,
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
                    const streak = calculateConsecutiveDays(result.data);
                    setConsistencyData({
                        streak,
                        status: 'active'
                    });
                } else {
                    throw new Error(result.message || 'Failed to fetch task data.');
                }

            } catch (e) {
                console.error("Streak calculation error:", e.message);
                setError(e.message);
            } finally {
                setLoading(false);
            }
        };

        fetchConsistencyData();
    }, []);

    const calculateConsecutiveDays = (completedTasks) => {
        if (!completedTasks || completedTasks.length === 0) return 0;

        // Group tasks by completion date
        const tasksByDate = {};
        completedTasks.forEach(task => {
            if (task.completion_date) {
                const date = new Date(task.completion_date).toDateString();
                if (!tasksByDate[date]) {
                    tasksByDate[date] = [];
                }
                tasksByDate[date].push(task);
            }
        });

        // Get sorted dates (most recent first)
        const sortedDates = Object.keys(tasksByDate).sort((a, b) => new Date(b) - new Date(a));
        
        let streak = 0;
        const today = new Date().toDateString();
        let currentDate = new Date();

        // Start from today and work backwards
        for (let i = 0; i < 30; i++) { // Check last 30 days max
            const dateStr = currentDate.toDateString();
            
            // If we have completed tasks on this date, continue streak
            if (tasksByDate[dateStr] && tasksByDate[dateStr].length > 0) {
                streak++;
            } else {
                // If no tasks completed on this date, break the streak
                // But don't break on today if it's still early
                const isToday = dateStr === today;
                const currentHour = new Date().getHours();
                
                if (!isToday || currentHour > 18) { // Give until 6 PM today
                    break;
                }
            }
            
            // Move to previous day
            currentDate.setDate(currentDate.getDate() - 1);
        }

        return streak;
    };

    if (loading) {
        return (
            <MetricCard title="Consistency" colorClass="metric-card-green">
                <p className="metric-card-value">Loading...</p>
            </MetricCard>
        );
    }
    
    if (error) {
        return (
            <MetricCard title="Consistency" colorClass="metric-card-green">
                <p style={{fontSize: '1rem'}}>Error loading data.</p>
            </MetricCard>
        );
    }

    const streakDays = consistencyData ? consistencyData.streak : 0;
    const isStreakBroken = consistencyData && consistencyData.status === 'broken';
    
    return (
        <MetricCard 
            title="Consistency Streak"
            value={streakDays}
            unit={streakDays === 1 ? "day" : "days"}
            colorClass="metric-card-green"
        >
            {isStreakBroken && (
                <p style={{fontSize: '0.875rem', color: 'rgba(255, 255, 255, 0.8)', margin: '0.5rem 0 0'}}>
                    Streak broken - {consistencyData.overdueCount} overdue task{consistencyData.overdueCount !== 1 ? 's' : ''}
                </p>
            )}
        </MetricCard>
    );
}

export default DashboardConsistency;