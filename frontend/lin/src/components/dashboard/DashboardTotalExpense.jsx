import React, { useState, useEffect, useCallback } from 'react';
import MetricCard from './MetricCard';
import { useEventBus } from '../../hooks/useEventBus';
import { EXPENSE_CREATED, EXPENSE_UPDATED, EXPENSE_DELETED } from '../../utils/eventTypes';

// UPDATED: The base URL for your API is now hardcoded.
const BASE_URL = 'http://127.0.0.1:8000'; 

function DashboardTotalExpense() {
    const [expenseData, setExpenseData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchExpenseData = useCallback(async () => {
        // Get the current year and month
        const now = new Date();
        const year = now.getFullYear();
        const month = now.getMonth() + 1; // JS months are 0-indexed

        try {
            setLoading(true);
            // UPDATED: The fetch URL now correctly constructs the endpoint.
            const response = await fetch(`${BASE_URL}/expenses/monthly/${year}/${month}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            if (result.success) {
                setExpenseData(result.data);
            } else {
                throw new Error(result.message || 'Failed to fetch expense data.');
            }

        } catch (e) {
            console.error("API Error:", e.message);
            setError(e.message);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchExpenseData();
    }, [fetchExpenseData]); // The empty dependency array ensures this effect runs only once on mount

    // Listen for expense events and refresh data
    useEventBus(EXPENSE_CREATED, () => {
        console.log('💰 New expense detected, refreshing dashboard...');
        fetchExpenseData();
    });

    useEventBus(EXPENSE_UPDATED, () => {
        console.log('✏️ Expense updated, refreshing dashboard...');
        fetchExpenseData();
    });

    useEventBus(EXPENSE_DELETED, () => {
        console.log('🗑️ Expense deleted, refreshing dashboard...');
        fetchExpenseData();
    });

    if (loading) {
        return (
            <MetricCard title="This Month's Spending" colorClass="metric-card-yellow">
                <p className="metric-card-value">Loading...</p>
            </MetricCard>
        );
    }
    
    if (error) {
         return (
            <MetricCard title="This Month's Spending" colorClass="metric-card-yellow">
                <p style={{fontSize: '1rem'}}>Error loading data.</p>
            </MetricCard>
        );
    }
    
    // Once data is loaded successfully
    return (
        <MetricCard 
            title={`Spending for ${new Date().toLocaleString('default', { month: 'long' })}`} 
            value={expenseData ? `$${expenseData.total_amount.toLocaleString()}` : '$0'}
            unit={expenseData ? `from ${expenseData.count} transactions` : '0 transactions'}
            colorClass="metric-card-blue"
        />
    );
}

export default DashboardTotalExpense;
