import React from 'react';
import { 
  Sun, 
  Moon, 
  Sparkles, 
  CheckSquare, 
  Clock, 
  Flame,
  LayoutDashboard
} from 'lucide-react';

interface NavbarProps {
  activeTab: 'morning' | 'review' | 'planner' | 'tasks' | 'fixed';
  setActiveTab: (tab: 'morning' | 'review' | 'planner' | 'tasks' | 'fixed') => void;
  userLevel: number;
  totalXp: number;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  userLevel,
  totalXp,
}) => {
  const navItems = [
    { id: 'morning', label: 'Morning Quests', icon: Sun },
    { id: 'review', label: 'Review Today', icon: Moon },
    { id: 'planner', label: 'Plan Tomorrow', icon: Sparkles },
    { id: 'tasks', label: 'Tasks Bank', icon: CheckSquare },
    { id: 'fixed', label: 'Fixed Schedule', icon: Clock },
  ] as const;

  return (
    <header className="bg-surface/80 backdrop-blur-md border-b border-surface-border sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('morning')}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <Sparkles className="w-5 h-5 text-white animate-pulse" />
            </div>
            <div>
              <span className="text-xl font-bold bg-gradient-to-r from-indigo-400 via-purple-300 to-pink-400 bg-clip-text text-transparent">
                LifeOS
              </span>
              <span className="hidden sm:inline-block ml-2 text-xs uppercase tracking-wider px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-semibold">
                AI Planner
              </span>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="flex space-x-1 sm:space-x-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/40 shadow-inner'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-indigo-400' : ''}`} />
                  <span className="hidden md:inline">{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* User Gamification Pill */}
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-slate-900 border border-indigo-500/30 text-xs font-semibold shadow-sm">
              <div className="w-6 h-6 rounded-full bg-indigo-500 text-white flex items-center justify-center font-bold text-[10px]">
                {userLevel}
              </div>
              <div className="flex flex-col">
                <span className="text-[10px] text-slate-400 leading-none">LVL {userLevel}</span>
                <span className="text-indigo-300 font-bold leading-none">{totalXp} XP</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
