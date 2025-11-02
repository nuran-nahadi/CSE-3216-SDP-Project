import React from 'react';
import MetricCard from './MetricCard';
import DashboardTotalExpense from './DashboardTotalExpense';
import DashboardTaskCompletion from './DashboardTaskCompletion';
import DashboardConsistency from './DashboardConsistency';
import DashboardUpcomingEvents from './DashboardUpcomingEvents';
import TasksAndEvents from './TasksAndEvents';
import TaskHeatmap from './TaskHeatmap';
import ExpenseDashboard from './ExpenseDashboard';
import ExpenseInsights from './ExpenseInsights';

const MoreIcon = () => ( <svg xmlns="http://www.w3.org/2000/svg" className="icon more-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h.01M12 12h.01M19 12h.01M5 12a1 1 0 110-2 1 1 0 010 2zm7 0a1 1 0 110-2 1 1 0 010 2zm7 0a1 1 0 110-2 1 1 0 010 2z" /></svg> );

function Dashboard({ data }) {
    return (
        <main className="dashboard-main">
            <header className="dashboard-header">
                <h2 className="dashboard-title">Dashboard</h2>
                <button className="dashboard-more-button">
                    <MoreIcon />
                </button>
            </header>

            <div className="dashboard-content">
                {/* Quick Metrics Row */}
                <div className="metric-cards-grid">
                    <DashboardTaskCompletion />
                    <DashboardConsistency />
                    <DashboardUpcomingEvents />
                    <DashboardTotalExpense />
                </div>

                {/* Tasks and Events - Right after metrics */}
                <div className="dashboard-tile">
                    <TasksAndEvents />
                </div>

                {/* Task Heatmap - Full Width */}
                <div className="dashboard-tile">
                    <TaskHeatmap />
                </div>

                {/* Expense Analytics Dashboard */}
                <div className="dashboard-tile">
                    <ExpenseDashboard />
                </div>

                {/* AI Insights & Suggestions */}
                <div className="dashboard-tile">
                    <ExpenseInsights />
                </div>
            </div>
        </main>
    );
}

export default Dashboard;
