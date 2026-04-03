import React, { useState } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

interface Transaction {
  id: string | number;
  date: string;
  merchant: string;
  category: string;
  amount: number;
}

interface TransactionsTableProps {
  transactions: Transaction[];
}

const ITEMS_PER_PAGE = 10;

export function TransactionsTable({ transactions }: TransactionsTableProps) {
  const [currentPage, setCurrentPage] = useState(1);
  
  const totalPages = Math.ceil(transactions.length / ITEMS_PER_PAGE);
  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
  const endIndex = startIndex + ITEMS_PER_PAGE;
  const currentTransactions = transactions.slice(startIndex, endIndex);

  const goToNextPage = () => {
    setCurrentPage(prev => Math.min(prev + 1, totalPages));
  };

  const goToPreviousPage = () => {
    setCurrentPage(prev => Math.max(prev - 1, 1));
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200">
      <div className="px-5 py-4 border-b border-gray-200">
        <h3 className="text-sm text-gray-900">Recent Transactions</h3>
      </div>
      
      <div className="overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-5 py-3 text-left text-xs text-gray-600">Date</th>
              <th className="px-5 py-3 text-left text-xs text-gray-600">Description</th>
              <th className="px-5 py-3 text-left text-xs text-gray-600">Category</th>
              <th className="px-5 py-3 text-right text-xs text-gray-600">Amount</th>
            </tr>
          </thead>
          <tbody>
            {currentTransactions.map((transaction) => (
              <tr key={transaction.id} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                <td className="px-5 py-3 text-xs text-gray-700">
                  {transaction.date}
                </td>
                <td className="px-5 py-3 text-xs text-gray-900">
                  {transaction.merchant}
                </td>
                <td className="px-5 py-3">
                  <span className="inline-block px-2 py-1 text-xs rounded-md bg-slate-100 text-slate-700">
                    {transaction.category}
                  </span>
                </td>
                <td className={`px-5 py-3 text-right text-xs ${
                  transaction.amount > 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {transaction.amount > 0 ? '+' : ''}${Math.abs(transaction.amount).toFixed(2)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {/* Pagination Controls */}
        <div className="px-5 py-3 bg-gray-50 flex items-center justify-between">
          <div className="text-xs text-gray-600">
            {startIndex + 1}–{Math.min(endIndex, transactions.length)} of {transactions.length}
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={goToPreviousPage}
              disabled={currentPage === 1}
              className="px-3 py-1.5 rounded-md border border-gray-300 bg-white text-xs text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1 transition-colors"
            >
              <ChevronLeft className="w-3 h-3" />
              Prev
            </button>
            
            <div className="px-3 text-xs text-gray-700">
              {currentPage} / {totalPages}
            </div>
            
            <button
              onClick={goToNextPage}
              disabled={currentPage === totalPages}
              className="px-3 py-1.5 rounded-md border border-gray-300 bg-white text-xs text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1 transition-colors"
            >
              Next
              <ChevronRight className="w-3 h-3" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
