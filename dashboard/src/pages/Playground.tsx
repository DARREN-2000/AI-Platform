import React, { useState } from 'react';
import { Send, Bot, User, Settings2 } from 'lucide-react';

const Playground: React.FC = () => {
  const [messages, setMessages] = useState([
    { role: 'system', content: 'Welcome to the Enterprise AI Playground. Connect to an agent to start.' }
  ]);
  const [input, setInput] = useState('');

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    setMessages([...messages, { role: 'user', content: input }, { role: 'system', content: 'Connecting to backend...' }]);
    setInput('');
  };

  return (
    <div className="h-[calc(100vh-10rem)] flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold text-gray-800">Agent Playground</h1>
        <button className="flex items-center px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50">
          <Settings2 size={16} className="mr-2" />
          Configure Agent
        </button>
      </div>

      <div className="flex-1 bg-white rounded-t-lg shadow-sm border-x border-t border-gray-200 p-4 overflow-y-auto">
        <div className="space-y-4">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`flex max-w-[80%] ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                <div className={`flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center ${msg.role === 'user' ? 'bg-indigo-100 ml-3' : 'bg-slate-100 mr-3'}`}>
                  {msg.role === 'user' ? <User size={16} className="text-indigo-600" /> : <Bot size={16} className="text-slate-600" />}
                </div>
                <div className={`p-3 rounded-lg ${msg.role === 'user' ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-800'}`}>
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-b-lg p-4 shadow-sm">
        <form onSubmit={handleSend} className="flex space-x-4">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message to the agent..."
            className="flex-1 min-w-0 block w-full px-4 py-3 rounded-md border-gray-300 focus:border-indigo-500 focus:ring-indigo-500 border outline-none"
          />
          <button
            type="submit"
            className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <Send size={18} className="mr-2" />
            Send
          </button>
        </form>
      </div>
    </div>
  );
};

export default Playground;
