import React, { useEffect, useState } from 'react';
import { 
  Sun, 
  Sparkles, 
  Award, 
  CheckCircle2, 
  Circle, 
  ArrowRight, 
  Clock, 
  Flame, 
  Zap,
  RefreshCw
} from 'lucide-react';
import { GamificationHeader } from '../components/GamificationHeader';
import { TimelineView } from '../components/TimelineView';
import { getMorningDashboard, updateBlockStatus } from '../api';
import { MorningDashboardData } from '../types';

interface MorningDashboardProps {
  onNavigateToReview: () => void;
  onNavigateToPlan: () => void;
}

export const MorningDashboard: React.FC<MorningDashboardProps> = ({
  onNavigateToReview,
  onNavigateToPlan,
}) => {
  const [data, setData] = useState<MorningDashboardData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [updatingBlockId, setUpdatingBlockId] = useState<number | null>(null);

  const fetchDashboard = async () => {
    setLoading(true);
    try {
      const res = await getMorningDashboard();
      setData(res);
    } catch (err) {
      console.error('Error fetching morning dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  const handleToggleBlock = async (blockId: number, currentStatus: string) => {
    setUpdatingBlockId(blockId);
    try {
      const nextStatus = currentStatus === 'COMPLETED' ? 'PENDING' : 'COMPLETED';
      await updateBlockStatus(blockId, nextStatus);
      await fetchDashboard();
    } catch (err) {
      console.error('Error updating block status:', err);
    } finally {
      setUpdatingBlockId(null);
    }
  };

  if (loading && !data) {
    return (
      <div className="flex items-center justify-center py-24">
        <RefreshCw className="w-8 h-8 text-indigo-400 animate-spin" />
      </div>
    );
  }

  const completedCount = data?.main_quests.filter(q => q.status === 'COMPLETED').length || 0;
  const totalQuests = data?.main_quests.length || 0;

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Gamification Level & XP Header */}
      <GamificationHeader
        username={data?.user.username || "Hero"}
        level={data?.user.current_level || 12}
        totalXp={data?.user.total_xp || 170}
        todayXp={data?.timeline.filter(b => b.status === 'COMPLETED').reduce((acc, curr) => acc + (curr.xp_earned || 0), 0)}
        completedQuests={completedCount}
        totalQuests={totalQuests}
      />

      {/* Morning Greeting & Level Quest Ready Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-indigo-900/60 via-purple-900/40 to-slate-900 border border-indigo-500/30 p-6 sm:p-8 shadow-2xl">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="flex items-center space-x-2 text-amber-400 font-bold text-sm tracking-wider uppercase mb-1">
              <Sun className="w-5 h-5 animate-spin-slow" />
              <span>Good Morning, Hero</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Your Level {data?.user.current_level || 12} quests are ready.
            </h1>
            <p className="text-sm text-slate-300 mt-2 max-w-xl">
              Execute your planned blocks today to earn XP, level up your skills, and keep your streak alive.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={onNavigateToPlan}
              className="px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-sm shadow-lg shadow-indigo-600/30 transition flex items-center gap-2"
            >
              <Sparkles className="w-4 h-4" />
              <span>View / Adjust Plan</span>
            </button>
            <button
              onClick={onNavigateToReview}
              className="px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-sm border border-slate-700 transition flex items-center gap-2"
            >
              <span>Nightly Review</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Quests Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Zap className="w-5 h-5 text-amber-400" />
            <h2 className="text-lg font-bold text-white tracking-tight">Today's Main Quests</h2>
          </div>
          <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            {totalQuests} active quest{totalQuests === 1 ? '' : 's'}
          </span>
        </div>

        {data?.main_quests.length === 0 ? (
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-8 text-center">
            <p className="text-slate-400 text-sm">No main quests scheduled yet.</p>
            <button
              onClick={onNavigateToPlan}
              className="mt-3 inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-bold transition"
            >
              <Sparkles className="w-3.5 h-3.5" /> Plan Tomorrow's Quests
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {data?.main_quests.map((quest) => {
              const isCompleted = quest.status === 'COMPLETED';
              return (
                <div
                  key={quest.block_id}
                  onClick={() => handleToggleBlock(quest.block_id, quest.status)}
                  className={`cursor-pointer rounded-2xl border p-5 transition-all shadow-lg flex items-center justify-between gap-4 ${
                    isCompleted
                      ? 'bg-slate-950/60 border-emerald-500/40 opacity-75'
                      : 'bg-slate-900/90 border-slate-800 hover:border-indigo-500/50 hover:scale-[1.01]'
                  }`}
                >
                  <div className="flex items-center space-x-4">
                    <button
                      className="text-slate-500 hover:text-emerald-400 transition"
                      disabled={updatingBlockId === quest.block_id}
                    >
                      {isCompleted ? (
                        <CheckCircle2 className="w-6 h-6 text-emerald-400 fill-emerald-500/20" />
                      ) : (
                        <Circle className="w-6 h-6 text-slate-600 hover:text-indigo-400" />
                      )}
                    </button>
                    <div>
                      <div className="flex items-center space-x-2">
                        <h4 className={`text-sm font-bold ${isCompleted ? 'line-through text-slate-400' : 'text-slate-100'}`}>
                          {quest.title}
                        </h4>
                        <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                          {quest.category}
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 mt-1 flex items-center gap-1 font-medium">
                        <Clock className="w-3.5 h-3.5 text-slate-500" />
                        {quest.start_time} – {quest.end_time}
                      </p>
                    </div>
                  </div>

                  <div className="text-right">
                    <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-black bg-amber-500/10 text-amber-400 border border-amber-500/30">
                      <Award className="w-3.5 h-3.5" /> +{quest.xp} XP
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Complete Timeline Section */}
      <div className="space-y-4 pt-4 border-t border-slate-800">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Clock className="w-5 h-5 text-indigo-400" />
            <h2 className="text-lg font-bold text-white tracking-tight">Complete Daily Timeline</h2>
          </div>
          <span className="text-xs text-slate-400">
            {data?.timeline.length || 0} scheduled blocks
          </span>
        </div>

        <TimelineView
          blocks={data?.timeline || []}
          onToggleStatus={handleToggleBlock}
        />
      </div>
    </div>
  );
};
