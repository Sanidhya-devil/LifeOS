import React, { useEffect, useState } from 'react';
import { 
  Moon, 
  Sparkles, 
  CheckCircle2, 
  XCircle, 
  Clock, 
  AlertTriangle, 
  Flame, 
  ArrowRight,
  RefreshCw,
  Award,
  Zap,
  BatteryCharging
} from 'lucide-react';
import { getTodaySummary, submitDailyReview } from '../api';
import { TodaySummary } from '../types';

interface ReviewTodayProps {
  onProceedToPlan: (reviewId?: number) => void;
}

export const ReviewToday: React.FC<ReviewTodayProps> = ({ onProceedToPlan }) => {
  const [summary, setSummary] = useState<TodaySummary | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [submitting, setSubmitting] = useState<boolean>(false);

  // Review Form State
  const [energyRating, setEnergyRating] = useState<number>(4);
  const [completedNotes, setCompletedNotes] = useState<string>('');
  const [missedReasons, setMissedReasons] = useState<string>('');
  const [tomorrowPriorities, setTomorrowPriorities] = useState<string>('');
  const [deadlineChanges, setDeadlineChanges] = useState<string>('');
  const [taskStatusOverrides, setTaskStatusOverrides] = useState<Record<number, string>>({});

  const fetchSummary = async () => {
    setLoading(true);
    try {
      const res = await getTodaySummary();
      setSummary(res);
    } catch (err) {
      console.error('Error fetching today summary:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary();
  }, []);

  const handleQuickStatusChange = (taskId: number, newStatus: string) => {
    setTaskStatusOverrides(prev => ({
      ...prev,
      [taskId]: newStatus,
    }));
  };

  const handleSubmitReview = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const res = await submitDailyReview({
        energy_rating: energyRating,
        completed_notes: completedNotes,
        missed_reasons: missedReasons,
        tomorrow_priorities: tomorrowPriorities,
        deadline_changes: deadlineChanges,
        task_statuses: taskStatusOverrides,
      });
      onProceedToPlan(res.id);
    } catch (err) {
      console.error('Error submitting daily review:', err);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading && !summary) {
    return (
      <div className="flex items-center justify-center py-24">
        <RefreshCw className="w-8 h-8 text-indigo-400 animate-spin" />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-fade-in pb-16">
      {/* Header Banner */}
      <div className="rounded-3xl bg-gradient-to-r from-purple-950/60 via-slate-900 to-indigo-950/60 border border-purple-500/30 p-6 sm:p-8 shadow-2xl">
        <div className="flex items-center space-x-3 mb-2">
          <div className="w-10 h-10 rounded-xl bg-purple-500/20 border border-purple-500/40 flex items-center justify-center text-purple-300">
            <Moon className="w-5 h-5" />
          </div>
          <div>
            <span className="text-xs uppercase font-bold tracking-wider text-purple-400">Nightly Review Loop</span>
            <h1 className="text-2xl font-extrabold text-white">Review Today's Execution</h1>
          </div>
        </div>
        <p className="text-sm text-slate-300 max-w-2xl mt-1">
          Reflect on what you completed, log energy and hurdles, and prepare inputs for the AI to synthesize tomorrow's optimal schedule.
        </p>

        {/* Quick Review Stats */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-6">
          <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-3 text-center">
            <span className="text-[10px] uppercase font-bold text-slate-500 block">Completed</span>
            <span className="text-lg font-bold text-emerald-400">{summary?.completed_tasks.length || 0} tasks</span>
          </div>
          <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-3 text-center">
            <span className="text-[10px] uppercase font-bold text-slate-500 block">Missed / Postponed</span>
            <span className="text-lg font-bold text-rose-400">{summary?.missed_tasks.length || 0} tasks</span>
          </div>
          <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-3 text-center">
            <span className="text-[10px] uppercase font-bold text-slate-500 block">XP Earned Today</span>
            <span className="text-lg font-bold text-amber-400">+{summary?.total_xp_today || 0} XP</span>
          </div>
          <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-3 text-center">
            <span className="text-[10px] uppercase font-bold text-slate-500 block">Review Reward</span>
            <span className="text-lg font-bold text-purple-300">+50 XP</span>
          </div>
        </div>
      </div>

      {/* Task Quick-Review Status Matrix */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
        <h2 className="text-base font-bold text-white flex items-center gap-2">
          <CheckCircle2 className="w-5 h-5 text-indigo-400" />
          Quick Task Status Toggles
        </h2>
        <p className="text-xs text-slate-400">
          Mark tasks as completed, skipped, or carry-over to inform the Priority Engine.
        </p>

        {summary?.scheduled_tasks.length === 0 ? (
          <p className="text-xs text-slate-500 italic">No tasks were explicitly scheduled on the timeline today.</p>
        ) : (
          <div className="space-y-3">
            {summary?.scheduled_tasks.filter(b => b.block_type === 'TASK').map((b) => {
              const currentOverride = b.task_id ? taskStatusOverrides[b.task_id] : undefined;
              const status = currentOverride || b.status;

              return (
                <div
                  key={b.id}
                  className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80"
                >
                  <div>
                    <span className="text-sm font-bold text-slate-200">{b.title}</span>
                    <span className="text-xs text-slate-500 block font-medium">
                      {b.start_time}–{b.end_time} • {b.duration_minutes}m
                    </span>
                  </div>

                  {/* Quick Action Buttons */}
                  <div className="flex flex-wrap items-center gap-1.5">
                    <button
                      type="button"
                      onClick={() => b.task_id && handleQuickStatusChange(b.task_id, 'COMPLETED')}
                      className={`text-xs px-2.5 py-1 rounded-lg font-semibold transition ${
                        status === 'COMPLETED'
                          ? 'bg-emerald-500 text-slate-950 font-bold'
                          : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                      }`}
                    >
                      Completed
                    </button>
                    <button
                      type="button"
                      onClick={() => b.task_id && handleQuickStatusChange(b.task_id, 'PARTIAL')}
                      className={`text-xs px-2.5 py-1 rounded-lg font-semibold transition ${
                        status === 'PARTIAL'
                          ? 'bg-amber-500 text-slate-950 font-bold'
                          : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                      }`}
                    >
                      Partial
                    </button>
                    <button
                      type="button"
                      onClick={() => b.task_id && handleQuickStatusChange(b.task_id, 'POSTPONED')}
                      className={`text-xs px-2.5 py-1 rounded-lg font-semibold transition ${
                        status === 'POSTPONED'
                          ? 'bg-indigo-500 text-white font-bold'
                          : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                      }`}
                    >
                      Move to Tomorrow
                    </button>
                    <button
                      type="button"
                      onClick={() => b.task_id && handleQuickStatusChange(b.task_id, 'SKIPPED')}
                      className={`text-xs px-2.5 py-1 rounded-lg font-semibold transition ${
                        status === 'SKIPPED'
                          ? 'bg-rose-500 text-white font-bold'
                          : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                      }`}
                    >
                      Skipped
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* 6 Structured Review Questions Form */}
      <form onSubmit={handleSubmitReview} className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
        <h2 className="text-base font-bold text-white flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-purple-400" />
          Nightly Reflection Questions
        </h2>

        {/* 1. Energy Rating */}
        <div>
          <label className="block text-sm font-semibold text-slate-200 mb-2">
            1. How was your energy today? (1–5)
          </label>
          <div className="flex items-center space-x-3">
            {[1, 2, 3, 4, 5].map((val) => (
              <button
                key={val}
                type="button"
                onClick={() => setEnergyRating(val)}
                className={`w-12 h-12 rounded-xl font-black text-sm transition flex flex-col items-center justify-center gap-0.5 border ${
                  energyRating === val
                    ? 'bg-gradient-to-br from-indigo-500 to-purple-600 text-white border-indigo-400 shadow-lg shadow-indigo-500/30 scale-105'
                    : 'bg-slate-950/60 text-slate-400 border-slate-800 hover:bg-slate-800'
                }`}
              >
                <span>{val}</span>
                <span className="text-[9px] font-normal opacity-80">
                  {val === 1 ? 'Low' : val === 3 ? 'Med' : val === 5 ? 'High' : ''}
                </span>
              </button>
            ))}
          </div>
        </div>

        {/* 2. What did you complete? */}
        <div>
          <label className="block text-sm font-semibold text-slate-200 mb-1.5">
            2. What major wins / quests did you complete today?
          </label>
          <textarea
            value={completedNotes}
            onChange={(e) => setCompletedNotes(e.target.value)}
            rows={2}
            placeholder="e.g. Mastered binary search tree traversals, solved 4 LeetCode mediums..."
            className="w-full bg-slate-950/70 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500/80 transition"
          />
        </div>

        {/* 3. Why did you miss any important task? */}
        <div>
          <label className="block text-sm font-semibold text-slate-200 mb-1.5">
            3. Why did you miss or skip any important task?
          </label>
          <textarea
            value={missedReasons}
            onChange={(e) => setMissedReasons(e.target.value)}
            rows={2}
            placeholder="e.g. College lab session ran over by 45 minutes; energy dipped in late afternoon..."
            className="w-full bg-slate-950/70 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500/80 transition"
          />
        </div>

        {/* 4. Priorities for Tomorrow */}
        <div>
          <label className="block text-sm font-semibold text-slate-200 mb-1.5">
            4. Is there anything top-priority or mandatory for tomorrow?
          </label>
          <textarea
            value={tomorrowPriorities}
            onChange={(e) => setTomorrowPriorities(e.target.value)}
            rows={2}
            placeholder="e.g. Must finish Internship Applications for Google and Stripe before 6 PM..."
            className="w-full bg-slate-950/70 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500/80 transition"
          />
        </div>

        {/* 5. Deadline changes */}
        <div>
          <label className="block text-sm font-semibold text-slate-200 mb-1.5">
            5. Did any project, syllabus, or internship deadline change?
          </label>
          <input
            type="text"
            value={deadlineChanges}
            onChange={(e) => setDeadlineChanges(e.target.value)}
            placeholder="e.g. Operating Systems assignment moved to Thursday..."
            className="w-full bg-slate-950/70 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500/80 transition"
          />
        </div>

        {/* Submit & Proceed Button */}
        <div className="pt-4 border-t border-slate-800 flex justify-end">
          <button
            type="submit"
            disabled={submitting}
            className="px-6 py-3.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-bold text-sm shadow-xl shadow-indigo-500/30 transition flex items-center gap-2"
          >
            {submitting ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Synthesizing Review (+50 XP)...</span>
              </>
            ) : (
              <>
                <Award className="w-4 h-4 text-amber-300" />
                <span>Submit Review (+50 XP) & Plan Tomorrow</span>
                <ArrowRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
