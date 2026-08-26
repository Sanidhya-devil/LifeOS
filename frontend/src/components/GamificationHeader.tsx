import React from 'react';
import { Trophy, Flame, Zap, Award } from 'lucide-react';

interface GamificationHeaderProps {
  username?: string;
  level: number;
  totalXp: number;
  todayXp?: number;
  completedQuests?: number;
  totalQuests?: number;
}

export const GamificationHeader: React.FC<GamificationHeaderProps> = ({
  username = "Hero",
  level,
  totalXp,
  todayXp = 0,
  completedQuests = 0,
  totalQuests = 0,
}) => {
  // XP to next level: every level is 100 XP
  const xpCurrentLevel = totalXp % 100;
  const progressPercent = Math.min(100, Math.max(0, xpCurrentLevel));

  return (
    <div className="bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 border border-slate-800 rounded-2xl p-4 sm:p-6 shadow-xl mb-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* User Identity & Level */}
        <div className="flex items-center space-x-4">
          <div className="relative">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 p-0.5 shadow-lg shadow-indigo-500/20 flex items-center justify-center">
              <div className="w-full h-full bg-slate-900 rounded-2xl flex items-center justify-center">
                <Trophy className="w-7 h-7 text-amber-400" />
              </div>
            </div>
            <div className="absolute -bottom-1 -right-1 bg-amber-500 text-slate-950 font-black text-xs px-1.5 py-0.5 rounded-full border border-slate-900 shadow">
              L{level}
            </div>
          </div>

          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-xl font-bold text-white tracking-tight">{username}</h2>
              <span className="bg-indigo-500/20 text-indigo-300 text-xs px-2 py-0.5 rounded-md font-semibold border border-indigo-500/30">
                Level {level} Architect
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              {100 - xpCurrentLevel} XP needed for Level {level + 1}
            </p>
          </div>
        </div>

        {/* Level XP Progress Bar */}
        <div className="flex-1 max-w-md">
          <div className="flex justify-between text-xs font-semibold mb-1.5">
            <span className="text-slate-400 flex items-center gap-1">
              <Zap className="w-3.5 h-3.5 text-amber-400" /> Current Level Progress
            </span>
            <span className="text-indigo-300">{xpCurrentLevel} / 100 XP</span>
          </div>
          <div className="w-full bg-slate-800/80 rounded-full h-3 p-0.5 border border-slate-700/50">
            <div
              className="bg-gradient-to-r from-indigo-500 via-purple-500 to-amber-400 h-2 rounded-full transition-all duration-500 shadow-sm shadow-indigo-500/50"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>

        {/* Quick Stats Pills */}
        <div className="flex items-center space-x-2 sm:space-x-3">
          <div className="bg-slate-950/60 border border-slate-800 px-3.5 py-2 rounded-xl text-center min-w-[70px]">
            <span className="text-[10px] uppercase font-bold text-slate-500 block">Today XP</span>
            <span className="text-sm font-bold text-emerald-400">+{todayXp} XP</span>
          </div>
          <div className="bg-slate-950/60 border border-slate-800 px-3.5 py-2 rounded-xl text-center min-w-[70px]">
            <span className="text-[10px] uppercase font-bold text-slate-500 block">Quests</span>
            <span className="text-sm font-bold text-purple-300">{completedQuests}/{totalQuests}</span>
          </div>
          <div className="bg-slate-950/60 border border-slate-800 px-3.5 py-2 rounded-xl text-center min-w-[70px]">
            <span className="text-[10px] uppercase font-bold text-slate-500 block">Streak</span>
            <span className="text-sm font-bold text-amber-400 flex items-center justify-center gap-0.5">
              <Flame className="w-3.5 h-3.5 fill-amber-400 text-amber-400" /> 7d
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
