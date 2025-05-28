import React from 'react';
import { Search, Bot } from 'lucide-react';
import { GoogleSearch } from './GoogleSearch';
import { GeminiSearch } from './GeminiSearch';

export interface GoogleAPIItem {
  title: string;
  link: string;
  snippet: string;
}

export interface GeminiAPIItem {
  title?: string;
  description?: string;
  content?: string;
}

export interface SearchResult {
  id: number;
  title: string;
  description: string;
  source: 'google' | 'gemini';
  link?: string;
}

interface SearchSectionProps {
  query: string;
  setQuery: (query: string) => void;
  onSearch: (e: React.FormEvent) => void;
  results: SearchResult[];
  isSearching: boolean;
  activeTab: 'google' | 'gemini';
  setActiveTab: (tab: 'google' | 'gemini') => void;
}

export const SearchSection: React.FC<SearchSectionProps> = ({
  query,
  setQuery,
  onSearch,
  results,
  isSearching,
  activeTab,
  setActiveTab
}) => {
  return (
    <section className="bg-white rounded-xl shadow-md overflow-hidden transition-all duration-300">
      <div className="p-6">
        <div className="flex space-x-4 mb-4">
          <button
            onClick={() => setActiveTab('google')}
            className={`px-4 py-2 rounded-lg flex items-center ${
              activeTab === 'google' ? 'bg-red-500 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <Search className="h-4 w-4 mr-2" />
            Google Search
          </button>
          <button
            onClick={() => setActiveTab('gemini')}
            className={`px-4 py-2 rounded-lg flex items-center ${
              activeTab === 'gemini' ? 'bg-red-500 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <Bot className="h-4 w-4 mr-2" />
            Gemini Analysis
          </button>
        </div>

        {activeTab === 'google' ? (
          <GoogleSearch query={query} setQuery={setQuery} onSearch={onSearch} />
        ) : (
          <GeminiSearch query={query} setQuery={setQuery} onSearch={onSearch} />
        )}
      </div>

      <div className="bg-gray-50 p-6 border-t border-gray-100">
        {isSearching && <p className="text-gray-500">Searching...</p>}
        {!isSearching && results.length === 0 && (
          <p className="text-gray-400 text-sm italic">No results yet. Try searching for something.</p>
        )}
        {!isSearching && results.length > 0 && (
          <ul className="space-y-3">
            {results.map((result) => (
              <li
                key={result.id}
                className="bg-white p-4 rounded-lg border border-gray-200 hover:border-red-300 hover:shadow-sm transition-all duration-300"
              >
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-base font-medium text-gray-800">
                    {result.source === 'google' && result.link ? (
                      <a
                        href={result.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline"
                      >
                        {result.title}
                      </a>
                    ) : (
                      result.title
                    )}</h4>
                  <span
                    className={`px-2 py-1 rounded text-xs ${
                      result.source === 'gemini'
                        ? 'bg-purple-100 text-purple-700'
                        : 'bg-blue-100 text-blue-700'
                    }`}
                  >
                    {result.source === 'gemini' ? 'Gemini' : 'Google'}
                  </span>
                </div>
                <p className="text-sm text-gray-500">{result.description}</p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
};