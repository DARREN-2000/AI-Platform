import React from 'react';

const Governance: React.FC = () => {
  return (
    <div>
      <h1 className="text-2xl font-bold mb-4 text-gray-800">Governance (GuardrailX)</h1>
      <div className="bg-white rounded-lg shadow p-6 border border-gray-100">
        <p className="text-gray-600 mb-4">Monitor compliance, PII redaction rules, and prompt injection filters.</p>
        <div className="border border-dashed border-gray-300 rounded-lg p-12 text-center bg-gray-50">
          <p className="text-gray-500 font-medium">Policy Enforcement Engine</p>
          <p className="text-sm text-gray-400 mt-2">Connects to backend later...</p>
        </div>
      </div>
    </div>
  );
};
export default Governance;
