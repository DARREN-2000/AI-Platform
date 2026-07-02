import React from 'react';
import { Menu, User, Bell } from 'lucide-react';

export const Header: React.FC<{ toggleSidebar: () => void }> = ({ toggleSidebar }) => {
  return (
    <header className="bg-white border-b border-gray-200 h-16 flex items-center justify-between px-4 sm:px-6 lg:px-8">
      <div className="flex items-center">
        <button
          onClick={toggleSidebar}
          className="text-gray-500 hover:text-gray-700 focus:outline-none lg:hidden mr-4"
        >
          <Menu size={24} />
        </button>
        <h2 className="text-xl font-semibold text-gray-800">Enterprise AI Platform</h2>
      </div>
      <div className="flex items-center space-x-4">
        <button className="text-gray-500 hover:text-gray-700">
          <Bell size={20} />
        </button>
        <button className="text-gray-500 hover:text-gray-700">
          <User size={20} />
        </button>
      </div>
    </header>
  );
};
