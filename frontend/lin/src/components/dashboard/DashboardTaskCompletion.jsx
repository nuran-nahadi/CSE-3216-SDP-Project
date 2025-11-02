import React, { useState, useEffect } from 'react';
import MetricCard from './MetricCard';

const BASE_URL = 'http://127.0.0.1:8000';

function DashboardTaskCompletion() {
    const [taskData, setTaskData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchTaskData = async () => {
            try {
                setLoading(true);
                
                // Get current month's date range
                const now = new Date();
                const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
                const endOfMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0);
                
                // Fetch completed tasks for this month
                const response = await fetch(
                    `${BASE_URL}/tasks/?status=completed&page=1&limit=100`,
                    {
                        headers: {
                            'Authorization': `Bearer ${localStorage.getItem('token')}` // Adjust based on your auth
                        }
                    }
                );

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const result = await response.json();

                if (result.success) {
                    // Filter tasks completed in current month
                    const thisMonthCompleted = result.data.filter(task => {
                        const completionDate = new Date(task.completion_date);
                        return completionDate >= startOfMonth && completionDate <= endOfMonth;
                    });

                    setTaskData({
                        completedThisMonth: thisMonthCompleted.length,
                        totalTasks: result.meta.total || thisMonthCompleted.length
                    });
                } else {
                    throw new Error(result.message || 'Failed to fetch task data.');
                }

            } catch (e) {
                console.error("API Error:", e.message);
                setError(e.message);
            } finally {
                setLoading(false);
            }
        };

        fetchTaskData();
    }, []);

    if (loading) {
        return (
            <MetricCard title="Task Completion" colorClass="metric-card-blue">
                <p className="metric-card-value">Loading...</p>
            </MetricCard>
        );
    }
    
    if (error) {
        return (
            <MetricCard title="Task Completion" colorClass="metric-card-blue">
                <p style={{fontSize: '1rem'}}>Error loading data.</p>
            </MetricCard>
        );
    }

    const completionPercentage = taskData ? 
        Math.round((taskData.completedThisMonth / Math.max(taskData.totalTasks, 1)) * 100) : 0;
    
    return (
        <MetricCard 
            title={`Task Completion (${new Date().toLocaleString('default', { month: 'long' })})`}
            value={completionPercentage}
            unit="%"
            colorClass="metric-card-purple"
        >
            <p style={{fontSize: '0.875rem', color: 'rgba(255, 255, 255, 0.8)', margin: '0.5rem 0 0'}}>
                {taskData ? `${taskData.completedThisMonth} of ${taskData.totalTasks} tasks` : '0 tasks'}
            </p>
        </MetricCard>
    );
}

export default DashboardTaskCompletion;