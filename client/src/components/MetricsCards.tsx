import React from 'react';
import { TrendingUp, TrendingDown, DollarSign } from 'lucide-react';

interface MetricsCardsProps {
  totalIncome: number;
  totalExpenses: number;
  netBalance: number;
}

export function MetricsCards({ totalIncome, totalExpenses, netBalance }: MetricsCardsProps) {
  return (
    <div className="grid grid-cols-3 gap-4 mb-6">
      {/* Total Income Card */}
      <div className="bg-white p-5 rounded-lg border border-gray-200">
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm text-gray-600">Total Income</span>
          <div className="w-8 h-8 bg-green-50 rounded-lg flex items-center justify-center">
            <TrendingUp className="w-4 h-4 text-green-600" />
          </div>
        </div>
        <div className="text-2xl text-green-600">
          ${totalIncome.toFixed(2)}
        </div>
      </div>

      {/* Total Expenses Card */}
      <div className="bg-white p-5 rounded-lg border border-gray-200">
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm text-gray-600">Total Expenses</span>
          <div className="w-8 h-8 bg-red-50 rounded-lg flex items-center justify-center">
            <TrendingDown className="w-4 h-4 text-red-600" />
          </div>
        </div>
        <div className="text-2xl text-red-600">
          ${totalExpenses.toFixed(2)}
        </div>
      </div>

      {/* Net Balance Card */}
      <div className="bg-white p-5 rounded-lg border border-gray-200">
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm text-gray-600">Net for Period</span>
          <div className="w-8 h-8 bg-slate-50 rounded-lg flex items-center justify-center">
            <DollarSign className="w-4 h-4 text-slate-600" />
          </div>
        </div>
        <div className={`text-2xl ${netBalance >= 0 ? 'text-slate-900' : 'text-red-600'}`}>
          ${netBalance.toFixed(2)}
        </div>
      </div>
    </div>
  );
}