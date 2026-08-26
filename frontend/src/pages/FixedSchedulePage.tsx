import React, { useEffect, useState } from 'react';
import { 
  Clock, 
  Lock, 
  Plus, 
  Trash2, 
  RefreshCw, 
  ShieldCheck,
  AlertCircle
} from 'lucide-react';
import { getFixedSchedules, createFixedSchedule, deleteFixedSchedule } from '../api';
import { FixedSchedule } from '../types';

export const FixedSchedulePage: React.FC = () => {
  const [schedules, setSchedules] = useState<FixedSchedule[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);

  // Form state
  const [title, setTitle] = useState<string>('');
  const [startTime, setStartTime] = useState<string>('07:30');
  const [endTime, setEndTime] = useState<string>('12:50');

  const fetchFixedSchedules = async () => {
    setLoading(true);
    try {
      const data = await getFixedSchedules();
      setSchedules(data);
    } catch (err) {
      console.error('Error loading fixed schedule:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFixedSchedules();
  }, []);

  const handleDelete = async (id: number) => {
    try {
      await deleteFixedSchedule(id);
      await fetchFixedSchedules();
    } catch (err) {
      console.error('Error deleting fixed schedule block:', err);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createFixedSchedule({
        title,
        start_time: startTime,
        end_time: endTime,
        days_of_week: 'mon,tue,wed,thu,fri,sat,sun',
        is_active: true,
      });
      setIsModalOpen(false);
      setTitle('');
      await fetchFixedSchedules();
    } catch (err) {
      console.error('Error creating fixed schedule:', err);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in pb-16">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-2">
            <Lock className="w-6 h-6 text-indigo-400" />
            Fixed Recurring Schedule
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Non-negotiable blocks. LifeOS guarantees flexible tasks will never be scheduled over these intervals.
          </p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/30 flex items-center gap-2 self-start sm:self-center"
        >
          <Plus className="w-4 h-4" />
          <span>Add Fixed Block</span>
        </button>
      </div>

      {/* Guaranteed Protection Note */}
      <div className="rounded-2xl bg-indigo-950/30 border border-indigo-500/20 p-4 flex items-start space-x-3 text-xs text-indigo-200">
        <ShieldCheck className="w-5 h-5 text-indigo-400 shrink-0 mt-0.5" />
        <div>
          <strong className="text-white block font-bold">Hard Constraint Guarantee</strong>
          The priority & scheduling engine calculates available time windows exclusively outside these hours. You can adjust or add blocks at any time.
        </div>
      </div>

      {/* Fixed Block Cards */}
      {loading ? (
        <div className="flex justify-center py-16">
          <RefreshCw className="w-8 h-8 text-indigo-400 animate-spin" />
        </div>
      ) : (
        <div className="space-y-3">
          {schedules.map((item) => (
            <div
              key={item.id}
              className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 sm:p-5 flex items-center justify-between shadow-lg"
            >
              <div className="flex items-center space-x-4">
                <div className="w-10 h-10 rounded-xl bg-slate-800 flex items-center justify-center text-slate-400">
                  <Clock className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <h3 className="text-sm font-bold text-white">{item.title}</h3>
                    <span className="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-bold border border-slate-700">
                      Locked Block
                    </span>
                  </div>
                  <p className="text-xs text-indigo-400 font-mono mt-0.5 font-bold">
                    {item.start_time} – {item.end_time}
                  </p>
                </div>
              </div>

              <button
                onClick={() => handleDelete(item.id)}
                className="text-slate-600 hover:text-rose-400 p-2 rounded-lg hover:bg-slate-800 transition"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Add Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <form onSubmit={handleCreate} className="bg-slate-900 border border-slate-700 rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <h3 className="text-base font-bold text-white">Add Fixed Commitment</h3>
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">Title</label>
              <input
                type="text"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. College Lecture"
                className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white"
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">Start Time (HH:MM)</label>
                <input
                  type="text"
                  required
                  value={startTime}
                  onChange={(e) => setStartTime(e.target.value)}
                  placeholder="07:30"
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white font-mono"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">End Time (HH:MM)</label>
                <input
                  type="text"
                  required
                  value={endTime}
                  onChange={(e) => setEndTime(e.target.value)}
                  placeholder="12:50"
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white font-mono"
                />
              </div>
            </div>
            <div className="flex justify-end space-x-2 pt-3">
              <button
                type="button"
                onClick={() => setIsModalOpen(false)}
                className="px-4 py-2 rounded-xl bg-slate-800 text-slate-400 hover:text-white text-xs font-semibold"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/30"
              >
                Save Fixed Block
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};
