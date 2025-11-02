import React from 'react';

// --- Icons ---
const DashboardIcon = () => ( <svg xmlns="http://www.w3.org/2000/svg" className="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" /></svg> );
const TodoListIcon = () => ( <svg xmlns="http://www.w3.org/2000/svg" className="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" /></svg> );
const ExpenseTrackerIcon = () => ( <svg xmlns="http://www.w3.org/2000/svg" className="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" /></svg> );
const CalendarIcon = () => ( <svg xmlns="http://www.w3.org/2000/svg" className="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg> );
// NEW: Icons for Profile and Logout
const ProfileIcon = () => ( <svg xmlns="http://www.w3.org/2000/svg" className="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg> );
const LogoutIcon = () => ( <svg xmlns="http://www.w3.org/2000/svg" className="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg> );


function Sidebar({ activePage, setActivePage }) {
    const navItems = [
        { name: 'Dashboard', icon: <DashboardIcon /> },
        { name: 'To Do List', icon: <TodoListIcon /> },
        { name: 'Expense Tracker', icon: <ExpenseTrackerIcon /> },
        { name: 'Calendar', icon: <CalendarIcon /> },
    ];

    return (
        <aside className="sidebar">
            <div>
                <h1 className="sidebar-title">{activePage}</h1>
                <nav className="sidebar-nav">
                    <ul className="sidebar-nav-list">
                        {navItems.map(item => (
                            <li key={item.name} className="sidebar-nav-item-wrapper">
                                <button
                                    onClick={() => setActivePage(item.name)}
                                    className={`sidebar-nav-item ${
                                        activePage === item.name ? 'sidebar-nav-item-active' : ''
                                    }`}
                                >
                                    {item.icon}
                                    <span className="sidebar-nav-item-text">{item.name}</span>
                                </button>
                            </li>
                        ))}
                    </ul>
                </nav>
            </div>

            {/* NEW: Profile/Logout button section at the bottom */}
            <div>
                {activePage === 'User Profile' ? (
                    <button className="sidebar-logout-button">
                        <LogoutIcon />
                        <span>Logout</span>
                    </button>
                ) : (
                    <button
                        onClick={() => setActivePage('User Profile')}
                        className={`sidebar-nav-item ${
                            activePage === 'User Profile' ? 'sidebar-nav-item-active' : ''
                        }`}
                    >
                        <ProfileIcon />
                        <span className="sidebar-nav-item-text">User Profile</span>
                    </button>
                )}
            </div>
        </aside>
    );
}

export default Sidebar;
