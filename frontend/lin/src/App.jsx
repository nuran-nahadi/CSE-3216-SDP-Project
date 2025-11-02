import React, { useState, useEffect } from 'react';
import Sidebar from './components/dashboard/Sidebar';
import Dashboard from './components/dashboard/Dashboard';
import ProfilePage from './components/profile/ProfilePage';
import CalendarPage from './components/CalendarPage/CalendarPage';

import ToDo from './components/ToDoList/ToDo';
// import ToDo from './components/ToDoList/ToDo';
import ExpenseTracker from './components/expenseTrack/ExpenseTracker';
import './index.css';

// --- DUMMY DATA ---
const dummyDashboardData = {
    taskCompletion: 75,
    consistency: 5,
    averageMood: "Happy",
    overviewChart: [
        { name: 'Jan', value: 400 }, { name: 'Feb', value: 300 },
        { name: 'Mar', value: 600 }, { name: 'Apr', value: 450 },
        { name: 'May', value: 700 }, { name: 'Jun', value: 500 },
    ],
    suggestions: [
        "Review your budget to identify potential savings in the 'Dining Out' category.",
        "You've completed all high-priority tasks for 3 days in a row. Great job!",
        "Consider scheduling a relaxing activity this weekend. Your mood has been consistently neutral.",
    ]
};

function App() {
    // Start on the Dashboard page
    const [activePage, setActivePage] = useState('Dashboard');
    const [dashboardData, setDashboardData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const timer = setTimeout(() => {
            setDashboardData(dummyDashboardData);
            setLoading(false);
        }, 500);
        return () => clearTimeout(timer);
    }, []);

    const renderPage = () => {
        switch (activePage) {
            case 'Dashboard':
                return <Dashboard data={dashboardData} />;
            case 'User Profile':
                return <ProfilePage />;
            case 'To Do List':
                return <ToDo />;
            case 'Calendar':
                return <CalendarPage />;
            case 'Expense Tracker':
                return <ExpenseTracker/>
            case 'Calendar':
                return <CalendarPage />;

            default:
                return (
                     <div className="under-construction-page text-blue-500">
                        <div className="under-construction-content">
                            <h2 className="under-construction-title">{activePage}</h2>
                            <p className="under-construction-text text-grey-500">This page is under construction.</p>
                        </div>
                    </div>
                );
        }
    };

    return (
        <div className="app-container">
            <Sidebar activePage={activePage} setActivePage={setActivePage} />

            <div className="content-area">
                {loading ? (
                    <div className="loading-message">Loading...</div>
                ) : (
                    renderPage()
                )}
            </div>
        </div>
    );
}

export default App;
