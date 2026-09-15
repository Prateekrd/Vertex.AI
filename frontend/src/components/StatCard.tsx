import React from 'react';

interface StatCardProps {
  label: string;
  value: string | number;
  change?: string;
  icon: React.ReactNode;
  color?: 'primary' | 'success' | 'warning' | 'danger' | 'secondary';
}

export default function StatCard({
  label,
  value,
  change,
  icon,
  color = 'primary',
}: StatCardProps) {
  const colorMap = {
    primary: 'bg-primary-500/10 text-primary-400',
    success: 'bg-success-500/10 text-success-500',
    warning: 'bg-warning-500/10 text-warning-500',
    danger: 'bg-danger-500/10 text-danger-500',
    secondary: 'bg-secondary-700/50 text-secondary-300',
  };

  return (
    <div className="bg-secondary-800 rounded-lg p-4 border border-secondary-700">
      <div className="flex items-center justify-between">
        <div className={`p-2 rounded-lg ${colorMap[color]}`}>{icon}</div>
        {change && (
          <span className="text-xs text-success-500 bg-success-500/10 px-2 py-1 rounded">
            {change}
          </span>
        )}
      </div>
      <div className="mt-3">
        <p className="text-secondary-400 text-sm">{label}</p>
        <p className="text-2xl font-bold text-white mt-1">{value}</p>
      </div>
    </div>
  );
}