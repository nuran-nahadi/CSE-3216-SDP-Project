import React from 'react';
import TaskHeatmap from '../components/dashboard/TaskHeatmap';
import ExpenseDashboard from '../components/dashboard/ExpenseDashboard';

function AnalyticsPage() {
  return (
    <div className="analytics-page">
      <div className="analytics-header">
        <h1 className="analytics-title">Analytics & Insights</h1>
        <p className="analytics-subtitle">
          Visualize your productivity and spending patterns
        </p>
      </div>
      
      <div className="analytics-content">
        {/* Task Heatmap - Full Width */}
        <section className="analytics-section">
          <TaskHeatmap />
        </section>
        
        {/* Expense Dashboard - Full Width */}
        <section className="analytics-section">
          <ExpenseDashboard />
        </section>
      </div>
    </div>
  );
}

export default AnalyticsPage;
