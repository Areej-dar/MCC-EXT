import React, { ReactNode } from 'react';
import { CircleDollarSign } from 'lucide-react';

interface LayoutProps {
  children: ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="flex-shrink-0 bg-red-500 p-2 rounded-full">
                <CircleDollarSign className="h-6 w-6 text-white" />
              </div>
              <div className="ml-3">
                <h1 className="text-xl font-semibold text-gray-800">
                  <span className="text-red-500">Sada</span>pay Merchant Analysis
                </h1>
                <p className="text-sm text-gray-500">Merchant Category Code Extraction Tool</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {children}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col items-center md:flex-row md:justify-between">
            <div className="text-sm text-gray-500">
              &copy; {new Date().getFullYear()} Sadapay.
            </div>
            <div className="mt-4 md:mt-0">
              <p className="text-sm text-gray-500">
                Merchant Analysis Tool.
              </p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};