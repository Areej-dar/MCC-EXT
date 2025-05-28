import { Search, X } from 'lucide-react';
import React from 'react';

interface GoogleSearchProps {
  query: string;
  setQuery: (query: string) => void;
  onSearch: (e: React.FormEvent) => void;
}

export const GoogleSearch: React.FC<GoogleSearchProps> = ({ query, setQuery, onSearch }) => {
  return (
    <form onSubmit={onSearch} className="relative">
      <div className="flex items-center border-2 rounded-full border-gray-300 focus-within:border-red-500 transition-all duration-300">
        <Search className="h-5 w-5 text-gray-400 ml-4" />

        <input
          type="text"
          placeholder="Search merchant information..."
          className="w-full py-3 px-4 text-gray-700 focus:outline-none"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />

        {query && (
          <button
            type="button"
            onClick={() => setQuery('')}
            className="p-2 mr-1 text-gray-400 hover:text-gray-600 focus:outline-none"
          >
            <X className="h-5 w-5" />
          </button>
        )}

        <button
          type="submit"
          className="bg-red-500 hover:bg-red-600 text-white px-6 py-3 rounded-r-full transition-colors duration-300 focus:outline-none"
        >
          Search
        </button>
      </div>
    </form>
  );
};