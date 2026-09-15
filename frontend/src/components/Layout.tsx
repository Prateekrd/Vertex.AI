import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { LayoutGrid, Upload, BarChart3, Search, FileText } from 'lucide-react';

const navItems = [
  { name: 'Upload', path: '/upload', icon: Upload },
  { name: 'Process', path: '/process', icon: FileText },
  { name: 'Review', path: '/review', icon: LayoutGrid },
  { name: 'Results', path: '/results', icon: BarChart3 },
  { name: 'Search', path: '/search', icon: Search },
];

export default function Layout({ children }: { children: React.ReactNode }) {
  const location = useLocation();

  return (
    <div className="min-h-screen flex">
      <aside className="w-64 bg-secondary-900 border-r border-secondary-700 flex flex-col">
        {/* Header / Logo */}
        <div className="p-5 border-b border-secondary-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 flex items-center justify-center flex-shrink-0">
              <svg width="36" height="36" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect width="36" height="36" rx="8" fill="#2563eb"/>
                <path d="M10 26L18 10L26 26" stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
                <path d="M12.5 20H23.5" stroke="white" strokeWidth="2" strokeLinecap="round"/>
              </svg>
            </div>
            <div>
              <h1 className="text-white font-semibold text-base leading-tight tracking-tight">
                Vertex
              </h1>
              <p className="text-secondary-400 text-xs leading-none mt-0.5">Material Harmonization</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-primary-600 text-white'
                    : 'text-secondary-300 hover:bg-secondary-800 hover:text-white'
                }`}
              >
                <Icon size={18} />
                {item.name}
              </Link>
            );
          })}
        </nav>
      </aside>

      <main className="flex-1 overflow-auto">
        {children}
      </main>
    </div>
  );
}
