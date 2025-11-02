import React from 'react';

function MetricCard({ title, value, unit, colorClass, children }) {
    return (
        <div className={`metric-card ${colorClass}`}>
            <h3 className="metric-card-title">{title}</h3>
            <div className="metric-card-content">
                <div className="metric-card-value-container">
                    <span className="metric-card-value">{value}</span>
                    {unit && <span className="metric-card-unit">{unit}</span>}
                </div>
                {children && (
                    <div className="metric-card-subtext">
                        {children}
                    </div>
                )}
            </div>
        </div>
    );
}

export default MetricCard;
