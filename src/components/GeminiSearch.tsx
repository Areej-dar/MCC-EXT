import React from 'react';
import { Bot, X } from 'lucide-react';

interface GeminiSearchProps {
  query: string;
  setQuery: (query: string) => void;
  onSearch: (e: React.FormEvent) => void;
}

export const GeminiSearch: React.FC<GeminiSearchProps> = ({ query, setQuery, onSearch }) => {
  return (
    <form onSubmit={onSearch} className="relative">
      <div className="flex items-center border-2 rounded-lg border-gray-300 focus-within:border-red-500 transition-all duration-300">
        <Bot className="h-5 w-5 text-gray-400 ml-4" />
        
        <textarea
          placeholder="Enter merchant details for risk analysis..."
          className="w-full py-3 px-4 text-gray-700 focus:outline-none min-h-[100px] resize-y"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        
        {query && (
          <button
            type="button"
            onClick={() => setQuery('')}
            className="p-2 absolute top-2 right-20 text-gray-400 hover:text-gray-600 focus:outline-none"
          >
            <X className="h-5 w-5" />
          </button>
        )}
        
        <button
          type="submit"
          className="bg-red-500 hover:bg-red-600 text-white px-6 py-3 rounded-r-lg transition-colors duration-300 focus:outline-none absolute bottom-2 right-2"
        >
          Analyze
        </button>
      </div>
    </form>
  );
};