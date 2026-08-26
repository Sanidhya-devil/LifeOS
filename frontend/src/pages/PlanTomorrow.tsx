import React, { useEffect, useState } from 'react';
import { 
  Sparkles, 
  CheckCircle2, 
  RefreshCw, 
  Edit3, 
  Plus, 
  AlertCircle, 
  Clock, 
  Calendar,
  Award,
  Zap,
  ArrowRight,
  ShieldCheck
} from 'lucide-react';
import { TimelineView } from '../components/TimelineView';
import { ConflictModal } from '../components/ConflictModal';
import { 
  generatePlan, 
  getLatestPlan, 
  approvePlan, 
  regeneratePlan, 
  validatePlanEdit, 
  createTask 
} from '../api';
import { DailyPlan, ScheduledBlock, PlanEditConflictResponse } from '../types';

interface PlanTomorrowProps {
  initialReviewId?: number;
  onPlanApproved: () => void;
}

export const PlanTomorrow: React.FC<PlanTomorrowProps> = ({
  initialReviewId,
  onPlanApproved,
}) => {
  const [plan, setPlan] = useState<DailyPlan | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [approving, setApproving] = useState<boolean>(false);
  const [regenerating, setRegenerating] = useState<boolean>(false);
  const [postponedTasks, setPostponedTasks] = useState<any[]>([]);
  const [isAiPowered, setIsAiPowered] = useState<boolean>(false);

  // Edit Block Modal State
  const [editingBlock, setEditingBlock] = useState<ScheduledBlock | null>(null);
  const [editStartTime, setEditStartTime] = useState<string>('');
  const [editEndTime, setEditEndTime] = useState<string>('');
  const [conflictData, setConflictData] = useState<PlanEditConflictResponse | null>(null);
  const [isConflictModalOpen, setIsConflictModalOpen] = useState<boolean>(false);

  // Quick Add Task Modal State
  const [isAddTaskModalOpen, setIsAddTaskModalOpen] = useState<boolean>(false);
  const [newTaskTitle, setNewTaskTitle] = useState<string>('');
  const [newTaskCategory, setNewTaskCategory] = useState<string>('DSA');
  const [newTaskDuration, setNewTaskDuration] = useState<number>(60);
  const [newTaskImportance, setNewTaskImportance] = useState<number>(4);

  const fetchExistingPlan = async () => {
    try {
      const res = await getLatestPlan();
      if (res) {
        setPlan(res);
      }
    } catch (err) {
      console.error('Error fetching plan:', err);
    }
  };

  useEffect(() => {
    fetchExistingPlan();
  }, []);

  const handleGeneratePlan = async () => {
    setLoading(true);
    try {
      const res = await generatePlan({
        review_id: initialReviewId,
        strategy: 'balanced',
      });
      setPlan({
        id: res.plan_id,
        user_id: 1,
        plan_date: res.plan_date,
        status: res.status,
        total_planned_minutes: res.total_planned_minutes,
        total_potential_xp: res.total_potential_xp,
        ai_reasoning: res.ai_reasoning,
        generated_at: new Date().toISOString(),
        scheduled_blocks: res.timeline_blocks,
      });
      setPostponedTasks(res.postponed_tasks || []);
      setIsAiPowered(res.is_ai_powered || false);
    } catch (err) {
      console.error('Error generating plan:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleApprovePlan = async () => {
    if (!plan) return;
    setApproving(true);
    try {
      await approvePlan(plan.id);
      onPlanApproved();
    } catch (err) {
      console.error('Error approving plan:', err);
    } finally {
      setApproving(false);
    }
  };

  const handleRegenerate = async () => {
    if (!plan) return;
    setRegenerating(true);
    try {
      const res = await regeneratePlan(plan.id);
      setPlan({
        id: res.plan_id,
        user_id: 1,
        plan_date: res.plan_date,
        status: res.status,
        total_planned_minutes: res.total_planned_minutes,
        total_potential_xp: res.total_potential_xp,
        ai_reasoning: res.ai_reasoning,
        generated_at: new Date().toISOString(),
        scheduled_blocks: res.timeline_blocks,
      });
      setPostponedTasks(res.postponed_tasks || []);
    } catch (err) {
      console.error('Error regenerating plan:', err);
    } finally {
      setRegenerating(false);
    }
  };

  const handleOpenEdit = (block: ScheduledBlock) => {
    setEditingBlock(block);
    setEditStartTime(block.start_time);
    setEditEndTime(block.end_time);
  };

  const handleSaveEdit = async () => {
    if (!plan || !editingBlock) return;
    try {
      // Validate for conflicts
      const validation = await validatePlanEdit(
        plan.id,
        editingBlock.id,
        editStartTime,
        editEndTime
      );

      if (validation.has_conflict) {
        setConflictData(validation);
        setIsConflictModalOpen(true);
        return;
      }

      // If valid, update local blocks
      const updatedBlocks = plan.scheduled_blocks.map(b => {
        if (b.id === editingBlock.id) {
          return {
            ...b,
            start_time: editStartTime,
            end_time: editEndTime,
          };
        }
        return b;
      });
      setPlan({ ...plan, scheduled_blocks: updatedBlocks });
      setEditingBlock(null);
    } catch (err) {
      console.error('Error validating block edit:', err);
    }
  };

  const handleCreateQuickTask = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createTask({
        title: newTaskTitle,
        category: newTaskCategory,
        estimated_minutes: newTaskDuration,
        importance: newTaskImportance,
        difficulty: 3,
        goal_relevance: 4,
        base_xp: newTaskDuration >= 90 ? 40 : 25,
      });
      setIsAddTaskModalOpen(false);
      setNewTaskTitle('');
      // Re-run planner
      await handleGeneratePlan();
    } catch (err) {
      console.error('Error adding quick task:', err);
    }
  };

  return (
    <div className="space-y-8 animate-fade-in pb-16">
      {/* Top Banner & Main Trigger */}
      <div className="rounded-3xl bg-gradient-to-r from-indigo-950 via-slate-900 to-purple-950 border border-indigo-500/40 p-6 sm:p-8 shadow-2xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="flex items-center space-x-2 text-indigo-400 font-bold text-xs uppercase tracking-widest mb-1">
              <Sparkles className="w-4 h-4 text-indigo-400 animate-pulse" />
              <span>Autonomous Life Planning</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Plan Tomorrow's Schedule
            </h1>
            <p className="text-sm text-slate-300 mt-1 max-w-xl">
              Synthesizes your fixed commitments (Gym, College, Lunch), candidate tasks, and review reflections into an optimal timeline.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleGeneratePlan}
              disabled={loading}
              className="px-6 py-3.5 rounded-2xl bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 hover:opacity-90 text-white font-extrabold text-sm shadow-xl shadow-indigo-600/40 transition flex items-center gap-2.5 scale-105 active:scale-100"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-5 h-5 animate-spin" />
                  <span>Optimizing Schedule...</span>
                </>
              ) : (
                <>
                  <Zap className="w-5 h-5 fill-amber-300 text-amber-300" />
                  <span>⚡ Plan Tomorrow</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {plan ? (
        <div className="space-y-6">
          {/* Plan Status Bar & Actions */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 sm:p-6 shadow-xl flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="flex items-center space-x-3">
              <div className={`px-3 py-1 rounded-full text-xs font-black uppercase tracking-wider border ${
                plan.status === 'APPROVED'
                  ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                  : 'bg-amber-500/20 text-amber-300 border-amber-500/40'
              }`}>
                {plan.status === 'APPROVED' ? '✓ Plan Approved' : 'Draft Proposal'}
              </div>
              <span className="text-xs text-slate-400 font-semibold">
                {plan.total_planned_minutes} min flexible work • +{plan.total_potential_xp} Potential XP
              </span>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-wrap items-center gap-2">
              <button
                onClick={() => setIsAddTaskModalOpen(true)}
                className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold border border-slate-700 transition flex items-center gap-1.5"
              >
                <Plus className="w-3.5 h-3.5 text-indigo-400" />
                <span>Add Task</span>
              </button>
              <button
                onClick={handleRegenerate}
                disabled={regenerating}
                className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold border border-slate-700 transition flex items-center gap-1.5"
              >
                <RefreshCw className={`w-3.5 h-3.5 text-purple-400 ${regenerating ? 'animate-spin' : ''}`} />
                <span>Regenerate</span>
              </button>
              <button
                onClick={handleApprovePlan}
                disabled={approving || plan.status === 'APPROVED'}
                className={`px-5 py-2 rounded-xl font-bold text-xs transition flex items-center gap-2 shadow-lg ${
                  plan.status === 'APPROVED'
                    ? 'bg-emerald-600 text-white cursor-default'
                    : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-emerald-600/30'
                }`}
              >
                {approving ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    <span>Approving...</span>
                  </>
                ) : (
                  <>
                    <CheckCircle2 className="w-4 h-4" />
                    <span>{plan.status === 'APPROVED' ? 'Approved & Locked' : 'Approve Plan'}</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* AI Plan Reasoning Card ("Why this plan?") */}
          {plan.ai_reasoning && (
            <div className="rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950/30 to-slate-900 border border-indigo-500/30 p-5 sm:p-6 shadow-xl">
              <div className="flex items-center space-x-2 text-indigo-300 font-bold text-sm mb-3">
                <Sparkles className="w-4 h-4 text-indigo-400" />
                <span>Why this plan?</span>
              </div>
              <div className="text-xs sm:text-sm text-slate-200 whitespace-pre-line leading-relaxed space-y-1">
                {plan.ai_reasoning}
              </div>
            </div>
          )}

          {/* Postponed Tasks Warning / Explanation */}
          {postponedTasks.length > 0 && (
            <div className="rounded-2xl bg-slate-950/80 border border-amber-500/30 p-4 sm:p-5 shadow-lg">
              <div className="flex items-center space-x-2 text-amber-400 font-bold text-xs uppercase tracking-wider mb-2">
                <AlertCircle className="w-4 h-4 text-amber-400" />
                <span>Postponed Tasks (Moved Forward to Future Days)</span>
              </div>
              <p className="text-xs text-slate-300 mb-3">
                To protect your sleep and adhere to your daily 8-hour workload limit, these lower-priority tasks were postponed:
              </p>
              <div className="space-y-2">
                {postponedTasks.map((t, idx) => (
                  <div key={idx} className="bg-slate-900/90 border border-slate-800 rounded-xl p-3 flex flex-col sm:flex-row sm:items-center justify-between text-xs gap-1">
                    <span className="font-bold text-slate-200">{t.title} ({t.estimated_minutes}m)</span>
                    <span className="text-slate-400 text-[11px] italic">{t.reason}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Proposed Timeline */}
          <div className="space-y-3 pt-2">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Calendar className="w-4 h-4 text-indigo-400" />
              Proposed Timeline
            </h3>
            <TimelineView
              blocks={plan.scheduled_blocks}
              isEditable={true}
              onEditBlock={handleOpenEdit}
            />
          </div>
        </div>
      ) : (
        <div className="bg-slate-900/50 border border-slate-800 rounded-3xl p-12 text-center space-y-4">
          <Clock className="w-12 h-12 text-indigo-400/50 mx-auto" />
          <h3 className="text-lg font-bold text-white">Ready to generate tomorrow's schedule</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto">
            Click "Plan Tomorrow" above. LifeOS will analyze your fixed blocks, tasks, and today's review reflection to create a balanced schedule.
          </p>
        </div>
      )}

      {/* Edit Block Time Modal */}
      {editingBlock && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <h3 className="text-base font-bold text-white">Adjust Task Slot: {editingBlock.title}</h3>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs text-slate-400 font-semibold mb-1">Start Time (HH:MM)</label>
                <input
                  type="text"
                  value={editStartTime}
                  onChange={(e) => setEditStartTime(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white font-mono"
                  placeholder="13:45"
                />
              </div>
              <div>
                <label className="block text-xs text-slate-400 font-semibold mb-1">End Time (HH:MM)</label>
                <input
                  type="text"
                  value={editEndTime}
                  onChange={(e) => setEditEndTime(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white font-mono"
                  placeholder="15:15"
                />
              </div>
            </div>
            <div className="flex justify-end space-x-2 pt-2">
              <button
                type="button"
                onClick={() => setEditingBlock(null)}
                className="px-4 py-2 rounded-xl bg-slate-800 text-slate-400 hover:text-white text-xs font-semibold"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleSaveEdit}
                className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/30"
              >
                Validate & Apply
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Quick Add Task Modal */}
      {isAddTaskModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <form onSubmit={handleCreateQuickTask} className="bg-slate-900 border border-slate-700 rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <h3 className="text-base font-bold text-white">Add New Candidate Task</h3>
            <div>
              <label className="block text-xs text-slate-400 font-semibold mb-1">Task Title</label>
              <input
                type="text"
                required
                value={newTaskTitle}
                onChange={(e) => setNewTaskTitle(e.target.value)}
                placeholder="e.g. LeetCode Dynamic Programming"
                className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white"
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs text-slate-400 font-semibold mb-1">Category</label>
                <select
                  value={newTaskCategory}
                  onChange={(e) => setNewTaskCategory(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white"
                >
                  <option value="DSA">DSA</option>
                  <option value="Project">Project</option>
                  <option value="Internship">Internship</option>
                  <option value="College">College</option>
                  <option value="Personal">Personal</option>
                </select>
              </div>
              <div>
                <label className="block text-xs text-slate-400 font-semibold mb-1">Duration (min)</label>
                <input
                  type="number"
                  min={15}
                  max={240}
                  step={15}
                  value={newTaskDuration}
                  onChange={(e) => setNewTaskDuration(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white"
                />
              </div>
            </div>
            <div className="flex justify-end space-x-2 pt-2">
              <button
                type="button"
                onClick={() => setIsAddTaskModalOpen(false)}
                className="px-4 py-2 rounded-xl bg-slate-800 text-slate-400 hover:text-white text-xs font-semibold"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/30"
              >
                Add & Replan
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Conflict Modal */}
      <ConflictModal
        isOpen={isConflictModalOpen}
        onClose={() => setIsConflictModalOpen(false)}
        message={conflictData?.message || ''}
        suggestedOptions={conflictData?.suggested_options || []}
        onSelectOption={(opt) => {
          setIsConflictModalOpen(false);
          setEditingBlock(null);
        }}
        conflictingBlock={conflictData?.conflicting_block}
      />
    </div>
  );
};
