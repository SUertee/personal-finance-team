import React from 'react';
import { User, Upload, PanelRightOpen, PanelRightClose } from 'lucide-react';

interface HeaderProps {
  isSidebarOpen: boolean;
  onToggleSidebar: () => void;
  onUploadStatement: (file: File) => void;
  isUploading?: boolean;
}

export function Header({
  isSidebarOpen,
  onToggleSidebar,
  onUploadStatement,
  isUploading,
}: HeaderProps) {
  const handleUpload = () => {
    // File upload handler
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.pdf,.csv,.xlsx';
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        onUploadStatement(file);
      }
    };
    input.click();
  };

  return (
    <header className="bg-white border-b border-gray-200">
      <div className="px-8 py-4 flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-6">
          <div className="text-xl text-slate-900">
            FinReport
          </div>
        </div>

        {/* Actions & User Profile */}
        <div className="flex items-center gap-4">
          <button
            onClick={handleUpload}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-60"
            disabled={isUploading}
          >
            <Upload className="w-4 h-4" />
            {isUploading ? "Uploading..." : "Upload Statement"}
          </button>
          
          <div className="flex items-center gap-3 pl-4 border-l border-gray-200">
            <div className="w-9 h-9 bg-slate-100 rounded-full flex items-center justify-center">
              <User className="w-5 h-5 text-slate-600" />
            </div>
            <span className="text-sm text-gray-700">User #12345</span>
          </div>

          <button
            onClick={onToggleSidebar}
            className="flex items-center gap-2 px-3 py-2 bg-slate-900 text-white rounded-lg hover:bg-slate-800 transition-colors ml-4"
            title={isSidebarOpen ? 'Close AI Center' : 'Open AI Center'}
          >
            {isSidebarOpen ? (
              <PanelRightClose className="w-4 h-4" />
            ) : (
              <PanelRightOpen className="w-4 h-4" />
            )}
            <span className="text-sm">AI Center</span>
          </button>
        </div>
      </div>
    </header>
  );
}
