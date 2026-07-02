import React from 'react';
import { BrainCircuit } from 'lucide-react';

const Models: React.FC = () => {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-4 text-gray-800">Models (Inference Control Plane)</h1>
      <div className="bg-white rounded-lg shadow p-6 border border-gray-100">
        <p className="text-gray-600 mb-6">Manage LLM routing, provider API keys, and global rate limits.</p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="border border-gray-200 rounded-lg p-4 flex items-center justify-between">
            <div className="flex items-center">
              <BrainCircuit className="text-blue-500 mr-3" size={24} />
              <div>
                <h3 className="font-medium text-gray-900">GPT-4 Turbo</h3>
                <p className="text-sm text-gray-500">OpenAI Provider</p>
              </div>
            </div>
            <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">Active</span>
          </div>

          <div className="border border-gray-200 rounded-lg p-4 flex items-center justify-between">
            <div className="flex items-center">
              <BrainCircuit className="text-purple-500 mr-3" size={24} />
              <div>
                <h3 className="font-medium text-gray-900">Claude 3 Opus</h3>
                <p className="text-sm text-gray-500">Anthropic Provider</p>
              </div>
            </div>
            <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">Active</span>
          </div>
        </div>
      </div>
    </div>
  );
};
export default Models;
