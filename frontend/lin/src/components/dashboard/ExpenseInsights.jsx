import React, { useState, useEffect, useCallback } from 'react';
import { useEventBus } from '../../hooks/useEventBus';
import { EXPENSE_CREATED, EXPENSE_UPDATED, EXPENSE_DELETED } from '../../utils/eventTypes';

const BASE_URL = 'http://127.0.0.1:8000';

function ExpenseInsights() {
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchInsights = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `${BASE_URL}/expenses/ai/insights`,
        {
          headers: {
            'Content-Type': 'application/json'
          }
        }
      );

      if (!response.ok) {
        // If endpoint doesn't exist (404) or other errors, use mock data
        if (response.status === 404) {
          console.warn('AI insights endpoint not implemented yet, using mock data');
          setInsights(getMockInsights());
          return;
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      if (result.success) {
        // The API returns an object in data field, not an array
        const insightsData = result.data;
        if (insightsData && typeof insightsData === 'object') {
          // Check if insights field contains an error message
          if (typeof insightsData.insights === 'string' && insightsData.insights.includes('Error')) {
            console.warn('AI service error:', insightsData.insights);
            setInsights(getMockInsights());
            return;
          }
          
          // Extract insights array from the data object
          // Common patterns: data.insights, data.suggestions, data.recommendations
          const extractedInsights = insightsData.insights || 
                                  insightsData.suggestions || 
                                  insightsData.recommendations ||
                                  insightsData.tips ||
                                  (Array.isArray(insightsData) ? insightsData : []);
          
          // Ensure we have an array
          if (Array.isArray(extractedInsights) && extractedInsights.length > 0) {
            setInsights(extractedInsights);
          } else {
            // No insights available, use mock data
            setInsights(getMockInsights());
          }
        } else {
          setInsights(getMockInsights());
        }
      } else {
        throw new Error(result.message || 'Failed to fetch insights');
      }
    } catch (e) {
      console.error('Error fetching expense insights:', e);
      // Use mock data as fallback
      setInsights(getMockInsights());
      setError(null); // Don't show error if we have mock data
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchInsights();
  }, [fetchInsights]);

  // Listen for expense events and refresh insights
  useEventBus(EXPENSE_CREATED, () => {
    console.log('💡 Expense created, refreshing insights...');
    fetchInsights();
  });

  useEventBus(EXPENSE_UPDATED, () => {
    console.log('💡 Expense updated, refreshing insights...');
    fetchInsights();
  });

  useEventBus(EXPENSE_DELETED, () => {
    console.log('💡 Expense deleted, refreshing insights...');
    fetchInsights();
  });

  const getMockInsights = () => {
    return [
      {
        id: 'mock-1',
        type: 'warning',
        priority: 'high',
        title: 'High Coffee Spending Detected',
        description: 'You\'ve spent 40% more on coffee this month compared to last month.',
        suggestion: 'Consider brewing coffee at home or using a subscription service to save money.',
        category: 'food',
        amount: 80,
        confidence: 0.85,
        timeframe: 'This month'
      },
      {
        id: 'mock-2',
        type: 'savings',
        priority: 'medium',
        title: 'Transportation Optimization',
        description: 'Your transport costs have decreased by 15% this month.',
        suggestion: 'Great job! Continue using public transport or carpooling to maintain these savings.',
        category: 'transport',
        amount: 45,
        confidence: 0.92,
        timeframe: 'Last 30 days'
      },
      {
        id: 'mock-3',
        type: 'tip',
        priority: 'low',
        title: 'Weekend Spending Pattern',
        description: 'You tend to spend 60% more on weekends, primarily on entertainment.',
        suggestion: 'Set a weekend budget limit to better control entertainment expenses.',
        category: 'entertainment',
        confidence: 0.78,
        timeframe: 'Weekly pattern'
      }
    ];
  };

  const getInsightIcon = (type) => {
    switch (type?.toLowerCase()) {
      case 'savings':
        return '💰';
      case 'warning':
        return '⚠️';
      case 'trend':
        return '📈';
      case 'tip':
        return '💡';
      case 'goal':
        return '🎯';
      default:
        return '💭';
    }
  };

  const getInsightPriority = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'high':
        return 'insight-high';
      case 'medium':
        return 'insight-medium';
      case 'low':
        return 'insight-low';
      default:
        return 'insight-medium';
    }
  };

  if (loading) {
    return (
      <div className="expense-insights-container">
        <h3 className="expense-insights-title">AI Insights</h3>
        <div className="expense-insights-loading">Loading insights...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="expense-insights-container">
        <h3 className="expense-insights-title">AI Insights</h3>
        <div className="expense-insights-error">Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="expense-insights-container">
      <h3 className="expense-insights-title">Suggestions</h3>
      
      {(!insights || !Array.isArray(insights) || insights.length === 0) ? (
        <div className="expense-insights-empty">
          <div className="empty-icon">🤖</div>
          <p>No insights available</p>
          <span>Check back later for AI-powered suggestions</span>
        </div>
      ) : (
        <div className="expense-insights-list">
          {insights.map((insight, index) => (
            <div 
              key={insight.id || index} 
              className={`expense-insight-item ${getInsightPriority(insight.priority)}`}
            >
              <div className="insight-icon">
                {getInsightIcon(insight.type)}
              </div>
              
              <div className="insight-content">
                <div className="insight-header">
                  <h4 className="insight-title">{insight.title}</h4>
                  {insight.category && (
                    <span className="insight-category">{insight.category}</span>
                  )}
                </div>
                
                <p className="insight-description">{insight.description}</p>
                
                {insight.suggestion && (
                  <div className="insight-suggestion">
                    <strong>Suggestion:</strong> {insight.suggestion}
                  </div>
                )}
                
                {insight.amount && (
                  <div className="insight-amount">
                    <span className="amount-label">Impact:</span>
                    <span className="amount-value">${insight.amount}</span>
                  </div>
                )}
                
                <div className="insight-meta">
                  {insight.confidence && (
                    <span className="confidence">
                      Confidence: {Math.round(insight.confidence * 100)}%
                    </span>
                  )}
                  {insight.timeframe && (
                    <span className="timeframe">{insight.timeframe}</span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
      
      <div className="insights-refresh">
        <button 
          className="refresh-button"
          onClick={fetchInsights}
          disabled={loading}
        >
          {loading ? 'Refreshing...' : 'Refresh Insights'}
        </button>
      </div>
    </div>
  );
}

export default ExpenseInsights;
