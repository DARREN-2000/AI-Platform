import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Settings2, SlidersHorizontal, ChevronDown, Check, X, Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { MLCEngine } from '@mlc-ai/web-llm';
import type { InitProgressReport } from '@mlc-ai/web-llm';


interface Message {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

const AGENTS = [
  { id: 'dev-agent', name: 'Developer Agent', description: 'Assists with code, architecture, and debugging.', icon: '💻' },
  { id: 'sec-agent', name: 'Security Agent', description: 'Focuses on vulnerabilities and compliance.', icon: '🛡️' },
  { id: 'data-agent', name: 'Data Analyst Agent', description: 'Helps analyze data and write SQL.', icon: '📊' },
];

const Playground: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'system', content: 'Welcome to the Enterprise AI Playground. Select an agent to start.' }
  ]);
  const [input, setInput] = useState('');
  const [selectedAgent, setSelectedAgent] = useState(AGENTS[0]);
  const [showConfig, setShowConfig] = useState(false);
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(2048);
  const [isTyping, setIsTyping] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [engine, setEngine] = useState<any>(null);
  const [loadingProgress, setLoadingProgress] = useState<string>('');
  const [isLoadingModel, setIsLoadingModel] = useState(false);
  const [modelError, setModelError] = useState<string>('');
  const [systemPrompt, setSystemPrompt] = useState('');



  const messagesEndRef = useRef<HTMLDivElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);



  // Initialize WebLLM Engine

  useEffect(() => {
    const initEngine = async () => {
      if (engine) return;
      setIsLoadingModel(true);
      setModelError('');
      setLoadingProgress('Initializing WebLLM...');

      try {
        const selectedModel = 'Llama-3.2-1B-Instruct-q4f16_1-MLC';

        const newEngine = new MLCEngine();

        newEngine.setInitProgressCallback((report: InitProgressReport) => {
          setLoadingProgress(report.text);
        });

        await newEngine.reload(selectedModel);

        setEngine(newEngine);
        setLoadingProgress('');
      } catch (err: any) {
        console.error("Failed to load model:", err);
        setModelError(err.message || 'Failed to load model. Check console.');
      } finally {
        setIsLoadingModel(false);
      }
    };
    initEngine();
  }, [engine]);


  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isTyping || !engine) return;

    const userMessage = input.trim();
    setInput('');

    const newMessages: Message[] = [...messages, { role: 'user', content: userMessage }];
    setMessages(newMessages);
    setIsTyping(true);

    // Add empty assistant message
    setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

    try {
      // Prepare chat history for WebLLM
      const chatHistory = newMessages.map(m => ({
        role: m.role,
        content: m.content
      }));

      // If there's a custom system prompt, inject it at the beginning
      if (systemPrompt.trim()) {
         chatHistory.unshift({ role: 'system', content: systemPrompt });
      }

      const chunks = await engine.chat.completions.create({
        messages: chatHistory,
        temperature,
        max_tokens: maxTokens,
        stream: true,
      });

      let currentText = '';
      for await (const chunk of chunks) {
        const delta = chunk.choices[0]?.delta?.content || '';
        currentText += delta;
        setMessages(prev => {
          const updated = [...prev];
          updated[updated.length - 1].content = currentText;
          return updated;
        });
      }
    } catch (err) {
      console.error("Inference error:", err);
      setMessages(prev => {
          const updated = [...prev];
          updated[updated.length - 1].content = "Error generating response. Please try again.";
          return updated;
      });
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="h-[calc(100vh-10rem)] flex flex-col relative">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-4">
          <h1 className="text-2xl font-bold text-gray-800">Agent Playground</h1>
          {isLoadingModel && !modelError && (
            <div className="flex items-center text-sm text-indigo-600 bg-indigo-50 px-3 py-1 rounded-full">
              <Loader2 size={14} className="mr-2 animate-spin" />
              <span className="max-w-xs truncate" title={loadingProgress}>{loadingProgress}</span>
            </div>
          )}
          {modelError && (
             <div className="flex items-center text-sm text-red-600 bg-red-50 px-3 py-1 rounded-full border border-red-200">
               <span className="max-w-md truncate" title={modelError}>Error: {modelError}</span>
             </div>
          )}


          {/* Agent Selector Dropdown */}
          <div className="relative" ref={dropdownRef}>
            <button
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              className="flex items-center space-x-2 bg-white border border-gray-300 rounded-md px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <span>{selectedAgent.icon}</span>
              <span>{selectedAgent.name}</span>
              <ChevronDown size={14} className="text-gray-500" />
            </button>

            {isDropdownOpen && (
              <div className="absolute top-full left-0 mt-1 w-64 bg-white border border-gray-200 rounded-md shadow-lg z-10 py-1">
                {AGENTS.map(agent => (
                  <button
                    key={agent.id}
                    onClick={() => {
                      setSelectedAgent(agent);
                      setIsDropdownOpen(false);
                      setMessages([{ role: 'system', content: `Switched to ${agent.name}. ${agent.description}` }]);
                    }}
                    className="w-full text-left px-4 py-2 hover:bg-gray-50 flex items-start space-x-3"
                  >
                    <span className="text-xl mt-0.5">{agent.icon}</span>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <span className="font-medium text-sm text-gray-900">{agent.name}</span>
                        {selectedAgent.id === agent.id && <Check size={14} className="text-indigo-600" />}
                      </div>
                      <p className="text-xs text-gray-500 mt-0.5">{agent.description}</p>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        <button
          onClick={() => setShowConfig(!showConfig)}
          className={`flex items-center px-3 py-2 border rounded-md shadow-sm text-sm font-medium transition-colors ${
            showConfig ? 'bg-indigo-50 border-indigo-200 text-indigo-700' : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
          }`}
        >
          <SlidersHorizontal size={16} className="mr-2" />
          Configure Agent
        </button>
      </div>

      <div className="flex flex-1 overflow-hidden relative">
        {/* Main Chat Area */}
        <div className={`flex-1 flex flex-col bg-white rounded-t-lg shadow-sm border-x border-t border-gray-200 overflow-hidden transition-all duration-300 ${showConfig ? 'mr-4 rounded-tr-none border-r-0' : ''}`}>
          <div className="flex-1 overflow-y-auto p-4 space-y-6">
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`flex max-w-[85%] ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                  <div className={`flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center ${
                    msg.role === 'user' ? 'bg-indigo-100 ml-3' :
                    msg.role === 'system' ? 'bg-gray-100 mr-3' : 'bg-blue-100 mr-3'
                  }`}>
                    {msg.role === 'user' ? <User size={16} className="text-indigo-600" /> :
                     msg.role === 'system' ? <Settings2 size={16} className="text-gray-600" /> : <Bot size={16} className="text-blue-600" />}
                  </div>
                  <div className={`p-4 rounded-lg shadow-sm ${
                    msg.role === 'user' ? 'bg-indigo-600 text-white' :
                    msg.role === 'system' ? 'bg-gray-50 border border-gray-200 text-gray-600 italic' : 'bg-white border border-gray-200 text-gray-800'
                  }`}>
                    {msg.role === 'user' || msg.role === 'system' ? (
                       <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                    ) : (
                      <div className="text-sm prose prose-sm max-w-none prose-p:leading-relaxed prose-pre:bg-gray-800 prose-pre:text-gray-100 prose-pre:rounded-md prose-pre:p-3 prose-code:text-indigo-600 prose-code:bg-indigo-50 prose-code:px-1 prose-code:py-0.5 prose-code:rounded">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {msg.content}
                        </ReactMarkdown>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
            {isTyping && messages[messages.length - 1].role === 'user' && (
               <div className="flex justify-start">
                 <div className="flex max-w-[85%] flex-row">
                    <div className="flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center bg-blue-100 mr-3">
                      <Bot size={16} className="text-blue-600" />
                    </div>
                    <div className="p-4 rounded-lg shadow-sm bg-white border border-gray-200 flex items-center space-x-2">
                       <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                       <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                       <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                    </div>
                 </div>
               </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Configuration Panel Slide-out */}
        {showConfig && (
          <div className="w-80 bg-gray-50 border border-gray-200 rounded-lg rounded-tl-none shadow-inner p-5 flex flex-col">
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-sm font-semibold text-gray-800 uppercase tracking-wider">Model Configuration</h3>
              <button onClick={() => setShowConfig(false)} className="text-gray-400 hover:text-gray-600">
                <X size={16} />
              </button>
            </div>

            <div className="space-y-6">
              <div>
                <label className="flex justify-between text-sm font-medium text-gray-700 mb-2">
                  <span>Temperature</span>
                  <span className="text-indigo-600 font-mono bg-indigo-50 px-1.5 py-0.5 rounded text-xs">{temperature}</span>
                </label>
                <input
                  type="range"
                  min="0" max="2" step="0.1"
                  value={temperature}
                  onChange={(e) => setTemperature(parseFloat(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                />
                <p className="text-xs text-gray-500 mt-1.5">Higher values make output more random, lower values make it more focused and deterministic.</p>
              </div>

              <div>
                <label className="flex justify-between text-sm font-medium text-gray-700 mb-2">
                  <span>Max Tokens</span>
                  <span className="text-indigo-600 font-mono bg-indigo-50 px-1.5 py-0.5 rounded text-xs">{maxTokens}</span>
                </label>
                <input
                  type="range"
                  min="256" max="8192" step="256"
                  value={maxTokens}
                  onChange={(e) => setMaxTokens(parseInt(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                />
                <p className="text-xs text-gray-500 mt-1.5">The maximum number of tokens to generate in the completion.</p>
              </div>

              <div className="pt-4 border-t border-gray-200">
                 <h4 className="text-sm font-medium text-gray-700 mb-2">System Prompt Overlay</h4>
                 <textarea
                   className="w-full h-24 p-2 text-sm border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                   placeholder="Add additional instructions for the agent..."
                   value={systemPrompt}
                   onChange={(e) => setSystemPrompt(e.target.value)}
                 ></textarea>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="bg-white border border-gray-200 rounded-b-lg p-4 shadow-sm z-10 relative">
        <form onSubmit={handleSend} className="flex space-x-4">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isTyping || isLoadingModel || !engine}
            placeholder={isTyping ? "Agent is typing..." : "Type your message to the agent..."}
            className="flex-1 min-w-0 block w-full px-4 py-3 rounded-md border-gray-300 focus:border-indigo-500 focus:ring-indigo-500 border outline-none disabled:bg-gray-50 disabled:text-gray-500"
          />
          <button
            type="submit"
            disabled={isTyping || isLoadingModel || !input.trim() || !engine}
            className="inline-flex items-center px-6 py-3 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
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
