import React from 'react';
import { Users, Activity, HardDrive, Cpu, ShieldAlert } from 'lucide-react';

const Home: React.FC = () => {
  const stats = [
    { name: 'Active Agents', value: '24', icon: <Users size={24} className="text-blue-500" /> },
    { name: 'API Requests (24h)', value: '1.2M', icon: <Activity size={24} className="text-indigo-500" /> },
    { name: 'Knowledge Docs', value: '45,219', icon: <HardDrive size={24} className="text-purple-500" /> },
    { name: 'GPU Utilization', value: '78%', icon: <Cpu size={24} className="text-emerald-500" /> },
    { name: 'Blocked Injections', value: '143', icon: <ShieldAlert size={24} className="text-red-500" /> },
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6 text-gray-800">Platform Overview</h1>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4 mb-8">
        {stats.map((stat) => (
          <div key={stat.name} className="bg-white rounded-lg p-5 shadow-sm border border-gray-100 flex items-center">
            <div className="p-3 rounded-full bg-gray-50 mr-4">
              {stat.icon}
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">{stat.name}</p>
              <p className="text-xl font-bold text-gray-900">{stat.value}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Recent Agent Executions</h2>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                <div className="flex items-center">
                  <div className="w-2 h-2 rounded-full bg-green-500 mr-3"></div>
                  <span className="text-sm font-medium text-gray-700">Financial Report Analysis</span>
                </div>
                <span className="text-xs text-gray-500">2 mins ago</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">GuardrailX Alerts</h2>
           <div className="space-y-4">
            {[1, 2].map((i) => (
              <div key={i} className="flex items-center justify-between p-3 bg-red-50 rounded-md border border-red-100">
                <div className="flex items-center">
                  <ShieldAlert size={16} className="text-red-500 mr-2" />
                  <span className="text-sm font-medium text-red-700">PII Data Blocked (SSN)</span>
                </div>
                <span className="text-xs text-red-500">15 mins ago</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
