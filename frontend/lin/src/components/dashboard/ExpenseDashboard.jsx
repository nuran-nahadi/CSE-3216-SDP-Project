import React, { useState, useEffect, useCallback } from 'react';
import { useEventBus } from '../../hooks/useEventBus';
import { EXPENSE_CREATED, EXPENSE_UPDATED, EXPENSE_DELETED } from '../../utils/eventTypes';

const BASE_URL = 'http://127.0.0.1:8000';

function ExpenseDashboard() {
  const [totalSpendData, setTotalSpendData] = useState(null);
  const [categoryBreakdown, setCategoryBreakdown] = useState([]);
  const [spendTrend, setSpendTrend] = useState([]);
  const [topTransactions, setTopTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboardData = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const headers = {
        'Content-Type': 'application/json'
      };

      console.log('Fetching expense data...');

      // First, try to fetch basic expenses data
      const expensesResponse = await fetch(`${BASE_URL}/expenses/`, { headers });
      
      if (!expensesResponse.ok) {
        const errorText = await expensesResponse.text();
        console.error('Expenses fetch error:', expensesResponse.status, errorText);
        throw new Error(`Failed to fetch expenses: ${expensesResponse.status} - ${errorText}`);
      }

      const expensesResult = await expensesResponse.json();
      console.log('Expenses response:', expensesResult);

      if (expensesResult.success && expensesResult.data) {
        // Process the expenses data for dashboard display
        const expenses = expensesResult.data;
        console.log('Processing', expenses.length, 'expenses');
        
        // Process total spend data
        const now = new Date();
        const currentMonth = now.getMonth();
        const currentYear = now.getFullYear();
        const previousMonth = currentMonth === 0 ? 11 : currentMonth - 1;
        const previousYear = currentMonth === 0 ? currentYear - 1 : currentYear;

        console.log('Current month/year:', currentMonth, currentYear);
        console.log('Previous month/year:', previousMonth, previousYear);

        const currentMonthExpenses = expenses.filter(expense => {
          const expenseDate = new Date(expense.date);
          const isCurrentMonth = expenseDate.getMonth() === currentMonth && expenseDate.getFullYear() === currentYear;
          if (isCurrentMonth) {
            console.log('Current month expense:', expense.description, expense.amount, expense.date);
          }
          return isCurrentMonth;
        });

        const previousMonthExpenses = expenses.filter(expense => {
          const expenseDate = new Date(expense.date);
          return expenseDate.getMonth() === previousMonth && expenseDate.getFullYear() === previousYear;
        });

        console.log('Current month expenses:', currentMonthExpenses.length);
        console.log('Previous month expenses:', previousMonthExpenses.length);

        const currentMonthTotal = currentMonthExpenses.reduce((sum, expense) => sum + expense.amount, 0);
        const previousMonthTotal = previousMonthExpenses.reduce((sum, expense) => sum + expense.amount, 0);
        
        const percentageChange = previousMonthTotal === 0 ? 
          (currentMonthTotal > 0 ? 100 : 0) : 
          ((currentMonthTotal - previousMonthTotal) / previousMonthTotal) * 100;

        const processedTotalSpend = {
          current_month: currentMonthTotal,
          previous_month: previousMonthTotal,
          percentage_change: Math.abs(percentageChange),
          change_direction: percentageChange > 0 ? 'increase' : percentageChange < 0 ? 'decrease' : 'same'
        };

        // Process category breakdown
        const categoryTotals = {};
        currentMonthExpenses.forEach(expense => {
          const category = expense.category || 'other';
          categoryTotals[category] = (categoryTotals[category] || 0) + expense.amount;
        });

        const totalSpent = currentMonthTotal;
        const processedCategories = Object.entries(categoryTotals)
          .map(([category, amount]) => ({
            category,
            amount,
            percentage: totalSpent > 0 ? (amount / totalSpent) * 100 : 0,
            transaction_count: currentMonthExpenses.filter(e => (e.category || 'other') === category).length
          }))
          .sort((a, b) => b.amount - a.amount)
          .slice(0, 4);

        // Process spend trend (last 30 days)
        const thirtyDaysAgo = new Date();
        thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

        console.log('30 days ago:', thirtyDaysAgo.toISOString());

        const recent30DaysExpenses = expenses.filter(expense => {
          const expenseDate = new Date(expense.date);
          const isRecent = expenseDate >= thirtyDaysAgo;
          if (isRecent) {
            console.log('Recent expense:', expense.description, expense.amount, expense.date);
          }
          return isRecent;
        });

        console.log('Recent 30 days expenses:', recent30DaysExpenses.length);

        // Group by date
        const dailyTotals = {};
        recent30DaysExpenses.forEach(expense => {
          const expenseDate = new Date(expense.date);
          const dateKey = expenseDate.toISOString().split('T')[0]; // YYYY-MM-DD format
          dailyTotals[dateKey] = (dailyTotals[dateKey] || 0) + expense.amount;
          console.log('Adding to date', dateKey, ':', expense.amount, 'new total:', dailyTotals[dateKey]);
        });

        console.log('Daily totals:', dailyTotals);

        const processedTrend = [];
        for (let i = 29; i >= 0; i--) {
          const date = new Date();
          date.setDate(date.getDate() - i);
          const dateKey = date.toISOString().split('T')[0];
          const amount = dailyTotals[dateKey] || 0;
          processedTrend.push({
            date: dateKey,
            amount: amount,
            transaction_count: recent30DaysExpenses.filter(e => 
              new Date(e.date).toISOString().split('T')[0] === dateKey
            ).length
          });
        }

        console.log('Processed trend sample:', processedTrend.slice(-5));

        // Process top transactions (current month)
        const processedTopTransactions = currentMonthExpenses
          .sort((a, b) => b.amount - a.amount)
          .slice(0, 5)
          .map(expense => ({
            id: expense.id,
            amount: expense.amount,
            category: expense.category || 'other',
            merchant: expense.merchant,
            description: expense.description,
            date: expense.date
          }));

        // Set all processed data
        setTotalSpendData(processedTotalSpend);
        setCategoryBreakdown(processedCategories);
        setSpendTrend(processedTrend);
        setTopTransactions(processedTopTransactions);

        console.log('Processed data:', {
          totalSpend: processedTotalSpend,
          categories: processedCategories,
          trend: processedTrend.length,
          topTransactions: processedTopTransactions.length
        });

      } else {
        console.log('No expense data found or API returned unsuccessful response');
        // Set empty data
        setTotalSpendData({ current_month: 0, previous_month: 0, percentage_change: 0, change_direction: 'same' });
        setCategoryBreakdown([]);
        setSpendTrend([]);
        setTopTransactions([]);
      }

    } catch (e) {
      console.error('Error fetching dashboard data:', e);
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  // Listen for expense events and refresh data
  useEventBus(EXPENSE_CREATED, () => {
    console.log('📊 Expense created, refreshing expense dashboard...');
    fetchDashboardData();
  });

  useEventBus(EXPENSE_UPDATED, () => {
    console.log('📊 Expense updated, refreshing expense dashboard...');
    fetchDashboardData();
  });

  useEventBus(EXPENSE_DELETED, () => {
    console.log('📊 Expense deleted, refreshing expense dashboard...');
    fetchDashboardData();
  });

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric'
    });
  };

  const getChangeColor = (direction) => {
    switch (direction) {
      case 'increase': return 'text-red-600';
      case 'decrease': return 'text-green-600';
      default: return 'text-gray-600';
    }
  };

  const getChangeIcon = (direction) => {
    switch (direction) {
      case 'increase': return '↗';
      case 'decrease': return '↘';
      default: return '→';
    }
  };

  if (loading) {
    return (
      <div className="expense-dashboard">
        <div className="expense-dashboard-loading">
          Loading expense dashboard...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="expense-dashboard">
        <div className="expense-dashboard-error">
          Error loading dashboard: {error}
        </div>
      </div>
    );
  }

  return (
    <div className="expense-dashboard">
      <h2 className="expense-dashboard-title">Expense Analytics</h2>
      
      <div className="expense-dashboard-grid">
        {/* Category Breakdown - 1st */}
        {categoryBreakdown.length > 0 && (
          <div className="expense-card category-breakdown-card">
            <h3 className="expense-card-title">Categories</h3>
            <div className="category-breakdown-content">
              {categoryBreakdown.slice(0, 4).map((category, index) => (
                <div key={category.category} className="category-item">
                  <div className="category-info">
                    <div className="category-name">{category.category}</div>
                    <div className="category-amount-value">{formatCurrency(category.amount)}</div>
                  </div>
                  <div className="category-percentage">{category.percentage.toFixed(0)}%</div>
                  <div 
                    className="category-bar"
                    style={{ width: `${category.percentage}%` }}
                  ></div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Top Transactions - 2nd */}
        {topTransactions.length > 0 && (
          <div className="expense-card top-transactions-card">
            <h3 className="expense-card-title">Top Transactions</h3>
            <div className="top-transactions-list">
              {topTransactions.slice(0, 3).map((transaction, index) => (
                <div key={transaction.id} className="transaction-item">
                  <div className="transaction-details">
                    <div className="transaction-description">
                      {transaction.description || transaction.merchant || 'Expense'}
                    </div>
                    <div className="transaction-category">{transaction.category}</div>
                  </div>
                  <div className="transaction-amount">
                    {formatCurrency(transaction.amount)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Total Spend Card - 3rd */}
        {totalSpendData && (
          <div className="expense-card total-spend-card">
            <h3 className="expense-card-title">Monthly Spending</h3>
            <div className="total-spend-amount">
              {formatCurrency(totalSpendData.current_month)}
            </div>
            <div className={`total-spend-change ${getChangeColor(totalSpendData.change_direction)}`}>
              <span className="change-icon">{getChangeIcon(totalSpendData.change_direction)}</span>
              <span className="change-percentage">{Math.abs(totalSpendData.percentage_change).toFixed(1)}%</span>
              <span className="change-text">vs last month</span>
            </div>
            <div className="total-spend-previous">
              Previous: {formatCurrency(totalSpendData.previous_month)}
            </div>
          </div>
        )}
      </div>

      {/* 30-Day Spend Trend Chart - Bottom (Full Width) */}
      <div className="expense-card spend-trend-card full-width">
        <h3 className="expense-card-title">30-Day Spend Trend</h3>
        {spendTrend.length > 0 ? (
          <div className="spend-trend-chart">
            <div className="trend-line-chart">
              <svg viewBox="0 0 800 240" className="trend-svg">
                {/* Grid lines */}
                <defs>
                  <pattern id="grid" width="40" height="20" patternUnits="userSpaceOnUse">
                    <path d="M 40 0 L 0 0 0 20" fill="none" stroke="#f1f5f9" strokeWidth="1"/>
                  </pattern>
                </defs>
                <rect width="100%" height="100%" fill="url(#grid)" />
                
                {/* Y-axis labels and lines */}
                {(() => {
                  const maxAmount = Math.max(...spendTrend.map(d => d.amount), 100);
                  const ySteps = 5;
                  const stepValue = maxAmount / ySteps;
                  
                  return Array.from({length: ySteps + 1}, (_, i) => {
                    const value = stepValue * (ySteps - i);
                    const y = (i / ySteps) * 160 + 20; // Adjusted for more space at bottom
                    return (
                      <g key={i}>
                        <line x1="80" y1={y} x2="780" y2={y} stroke="#e2e8f0" strokeWidth="1"/>
                        <text x="75" y={y + 4} textAnchor="end" className="trend-y-label">
                          {formatCurrency(value)}
                        </text>
                      </g>
                    );
                  });
                })()}
                
                {/* Trend line */}
                {(() => {
                  const maxAmount = Math.max(...spendTrend.map(d => d.amount), 100);
                  const points = spendTrend.slice(-30).map((day, index) => {
                    const x = 80 + (index / 29) * 700;
                    const y = 180 - ((day.amount / maxAmount) * 160);
                    return `${x},${y}`;
                  }).join(' ');
                  
                  return (
                    <g>
                      {/* Main trend line */}
                      <polyline
                        points={points}
                        fill="none"
                        stroke="#3b82f6"
                        strokeWidth="3"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                      {/* Data points */}
                      {spendTrend.slice(-30).map((day, index) => {
                        const x = 80 + (index / 29) * 700;
                        const y = 180 - ((day.amount / maxAmount) * 160);
                        return (
                          <circle
                            key={index}
                            cx={x}
                            cy={y}
                            r="4"
                            fill="#3b82f6"
                            className="trend-point"
                          >
                            <title>{`${formatDate(day.date)}: ${formatCurrency(day.amount)}`}</title>
                          </circle>
                        );
                      })}
                    </g>
                  );
                })()}
                
                {/* X-axis line */}
                <line x1="80" y1="180" x2="780" y2="180" stroke="#e2e8f0" strokeWidth="2"/>
                
                {/* X-axis labels - with more spacing */}
                {spendTrend.slice(-30).filter((_, i) => i % 6 === 0 || i === 29).map((day, index, filteredArray) => {
                  const actualIndex = index === filteredArray.length - 1 ? 29 : index * 6;
                  const x = 80 + (actualIndex / 29) * 700;
                  return (
                    <text
                      key={day.date}
                      x={x}
                      y="200"
                      textAnchor="middle"
                      className="trend-x-label"
                    >
                      {new Date(day.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                    </text>
                  );
                })}
              </svg>
              
              {/* Summary stats */}
              <div className="trend-stats">
                <div className="trend-stat">
                  <span className="trend-stat-label">Total (30 days)</span>
                  <span className="trend-stat-value">
                    {formatCurrency(spendTrend.reduce((sum, day) => sum + day.amount, 0))}
                  </span>
                </div>
                <div className="trend-stat">
                  <span className="trend-stat-label">Daily Average</span>
                  <span className="trend-stat-value">
                    {formatCurrency(spendTrend.reduce((sum, day) => sum + day.amount, 0) / 30)}
                  </span>
                </div>
                <div className="trend-stat">
                  <span className="trend-stat-label">Peak Day</span>
                  <span className="trend-stat-value">
                    {formatCurrency(Math.max(...spendTrend.map(d => d.amount)))}
                  </span>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="trend-chart-empty">
            <p>No spending data available for the last 30 days</p>
          </div>
        )}
      </div>

      {/* Show data summary for debugging */}
      {(totalSpendData && totalSpendData.current_month === 0 && 
        categoryBreakdown.length === 0 && 
        spendTrend.length === 0 && 
        topTransactions.length === 0) && (
        <div className="expense-card no-data-card">
          <h3 className="expense-card-title">No Expense Data</h3>
          <p>No expenses found. Add some expenses to see your spending analytics.</p>
        </div>
      )}
    </div>
  );
}

export default ExpenseDashboard;
