import React from 'react';
import { Terminal as TerminalIcon } from 'lucide-react';

interface TerminalProps {
  output: string[];
}

export const Terminal: React.FC<TerminalProps> = ({ output }) => {
  return (
    <div className="fixed bottom-0 left-0 right-0 bg-gray-900 text-gray-100 font-mono text-sm z-50">
      <div className="flex items-center justify-between px-4 py-2 bg-gray-800 border-b border-gray-700">
        <div className="flex items-center">
          <TerminalIcon className="h-4 w-4 mr-2" />
          <span>Terminal Output</span>
        </div>
        <div className="flex space-x-2">
          <div className="h-3 w-3 rounded-full bg-red-500"></div>
          <div className="h-3 w-3 rounded-full bg-yellow-500"></div>
          <div className="h-3 w-3 rounded-full bg-green-500"></div>
        </div>
      </div>
      <div className="p-4 max-h-48 overflow-y-auto">
        {output.map((line, index) => (
          <div key={index} className="font-mono">
            <span className="text-green-400">$</span> {line}
          </div>
        ))}
      </div>
    </div>
  );
};