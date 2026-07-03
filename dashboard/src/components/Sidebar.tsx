import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  Home,
  TerminalSquare,
  Network,
  BrainCircuit,
  BookOpen,
  ShieldCheck,
  Server,
  X
} from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
  closeSidebar: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, closeSidebar }) => {
  const navItems = [
    { name: 'Dashboard', path: '/', icon: <Home size={20} /> },
    { name: 'Playground', path: '/playground', icon: <TerminalSquare size={20} /> },
    { name: 'Agents', path: '/agents', icon: <Network size={20} /> },
    { name: 'Models', path: '/models', icon: <BrainCircuit size={20} /> },
    { name: 'Knowledge Base', path: '/knowledge', icon: <BookOpen size={20} /> },
    { name: 'Governance', path: '/governance', icon: <ShieldCheck size={20} /> },
    { name: 'Infrastructure', path: '/infrastructure', icon: <Server size={20} /> },
  ];

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-gray-600 bg-opacity-75 z-20 lg:hidden"
          onClick={closeSidebar}
        ></div>
      )}

      {/* Sidebar */}
      <div className={`fixed inset-y-0 left-0 z-30 w-64 bg-slate-900 text-white transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0 ${isOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="flex items-center justify-between h-16 px-4 bg-slate-950 border-b border-slate-800">
          <span className="text-xl font-bold tracking-wider">AI Platform</span>
          <button onClick={closeSidebar} className="lg:hidden text-gray-400 hover:text-white">
            <X size={24} />
          </button>
        </div>
        <nav className="mt-5 px-2">
          {navItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.path}
              className={({ isActive }) =>
                `group flex items-center px-2 py-3 mb-1 text-sm font-medium rounded-md transition-colors ${
                  isActive
                    ? 'bg-indigo-600 text-white'
                    : 'text-gray-300 hover:bg-slate-800 hover:text-white'
                }`
              }
              onClick={() => {
                if (window.innerWidth < 1024) closeSidebar();
              }}
            >
              <div className="mr-3">{item.icon}</div>
              {item.name}
            </NavLink>
          ))}
        </nav>
      </div>
    </>
  );
};
