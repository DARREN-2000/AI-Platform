import React from 'react';

const Infrastructure: React.FC = () => {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-4 text-gray-800">Infrastructure (AI Hypervisor)</h1>
      <div className="bg-white rounded-lg shadow p-6 border border-gray-100">
        <p className="text-gray-600 mb-4">View GPU allocation, compute node status, and virtualization layers.</p>
        <div className="border border-dashed border-gray-300 rounded-lg p-12 text-center bg-gray-50">
          <p className="text-gray-500 font-medium">Hardware Orchestration Control Plane</p>
          <p className="text-sm text-gray-400 mt-2">Connects to backend later...</p>
        </div>
      </div>
    </div>
  );
};
export default Infrastructure;
