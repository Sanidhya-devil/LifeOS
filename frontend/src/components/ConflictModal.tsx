import React from 'react';
import { AlertTriangle, X, ArrowRight, Clock } from 'lucide-react';
import { ScheduledBlock } from '../types';

interface ConflictModalProps {
  isOpen: boolean;
  onClose: () => void;
  message: string;
  suggestedOptions: string[];
  onSelectOption: (option: string) => void;
  targetBlock?: ScheduledBlock | null;
  conflictingBlock?: ScheduledBlock | null;
}

export const ConflictModal: React.FC<ConflictModalProps> = ({
  isOpen,
  onClose,
  message,
  suggestedOptions,
  onSelectOption,
  targetBlock,
  conflictingBlock,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fade-in">
      <div className="bg-slate-900 border border-rose-500/40 rounded-2xl max-w-lg w-full p-6 shadow-2xl relative">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Warning Header */}
        <div className="flex items-center space-x-3 mb-4">
          <div className="w-10 h-10 rounded-xl bg-rose-500/10 border border-rose-500/30 flex items-center justify-center text-rose-400">
            <AlertTriangle className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">Schedule Conflict Detected</h3>
            <p className="text-xs text-rose-400/90 font-medium">LifeOS Time Protection Engine</p>
          </div>
        </div>

        {/* Message */}
        <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-4 mb-5 text-sm text-slate-200">
          <p className="font-semibold text-rose-300 mb-1">{message}</p>
          {conflictingBlock && (
            <div className="mt-2 text-xs text-slate-400 flex items-center gap-2">
              <Clock className="w-3.5 h-3.5 text-slate-500" />
              <span>
                Conflicting block: <strong className="text-slate-200">{conflictingBlock.title}</strong> ({conflictingBlock.start_time}–{conflictingBlock.end_time})
              </span>
            </div>
          )}
        </div>

        {/* Suggested Actions */}
        <div className="space-y-2 mb-6">
          <span className="text-xs uppercase font-bold text-slate-400 tracking-wider block mb-2">
            Recommended Resolutions:
          </span>
          {suggestedOptions.map((opt, idx) => (
            <button
              key={idx}
              onClick={() => onSelectOption(opt)}
              className="w-full text-left flex items-center justify-between px-4 py-3 rounded-xl bg-slate-800 hover:bg-indigo-600/20 text-slate-200 hover:text-indigo-300 border border-slate-700 hover:border-indigo-500/40 text-xs font-semibold transition group"
            >
              <span>{opt}</span>
              <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-indigo-400 transition" />
            </button>
          ))}
        </div>

        {/* Cancel */}
        <button
          onClick={onClose}
          className="w-full py-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-800 text-slate-400 hover:text-slate-200 text-xs font-semibold transition"
        >
          Cancel & Keep Original Time
        </button>
      </div>
    </div>
  );
};
