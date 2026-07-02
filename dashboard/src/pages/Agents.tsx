import React from 'react';
import { Network, Play } from 'lucide-react';

const Agents: React.FC = () => {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-4 text-gray-800">Agents (IntentGraph)</h1>
      <div className="bg-white rounded-lg shadow p-6 border border-gray-100">
        <p className="text-gray-600 mb-6">Design, orchestrate, and monitor DAG-based agentic workflows.</p>

        <div className="border border-gray-200 rounded-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Agent Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              <tr>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <Network className="text-indigo-500 mr-2" size={18} />
                    <div className="text-sm font-medium text-gray-900">Financial Analyst Agent</div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Ready</span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  <button className="text-indigo-600 hover:text-indigo-900 flex items-center">
                    <Play size={16} className="mr-1" /> Run
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
export default Agents;
