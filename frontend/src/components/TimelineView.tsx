import React from 'react';
import { 
  Clock, 
  Lock, 
  CheckCircle2, 
  Circle, 
  Coffee, 
  Utensils, 
  Moon, 
  Edit3,
  Award,
  Sparkles,
  AlertCircle
} from 'lucide-react';
import { ScheduledBlock } from '../types';

interface TimelineViewProps {
  blocks: ScheduledBlock[];
  isEditable?: boolean;
  onEditBlock?: (block: ScheduledBlock) => void;
  onToggleStatus?: (blockId: number, currentStatus: string) => void;
}

export const TimelineView: React.FC<TimelineViewProps> = ({
  blocks,
  isEditable = false,
  onEditBlock,
  onToggleStatus,
}) => {
  const getBlockStyle = (block: ScheduledBlock) => {
    switch (block.block_type) {
      case 'FIXED':
        return {
          cardBg: 'bg-slate-900/90 border-slate-700/80',
          accent: 'border-l-4 border-l-slate-400',
          badgeBg: 'bg-slate-800 text-slate-300 border-slate-700',
          icon: Lock,
          iconColor: 'text-slate-400',
        };
      case 'BREAK':
        return {
          cardBg: 'bg-slate-950/60 border-dashed border-emerald-500/30',
          accent: 'border-l-4 border-l-emerald-500/60',
          badgeBg: 'bg-emerald-950/40 text-emerald-300 border-emerald-800/40',
          icon: Coffee,
          iconColor: 'text-emerald-400',
        };
      case 'REST':
        return {
          cardBg: 'bg-slate-950/60 border-dashed border-purple-500/30',
          accent: 'border-l-4 border-l-purple-500/60',
          badgeBg: 'bg-purple-950/40 text-purple-300 border-purple-800/40',
          icon: Moon,
          iconColor: 'text-purple-400',
        };
      default: {
        // Dynamic category styling for Tasks
        const cat = (block.category || '').toLowerCase();
        if (cat.includes('dsa')) {
          return {
            cardBg: 'bg-slate-900/95 border-indigo-500/30 hover:border-indigo-500/60',
            accent: 'border-l-4 border-l-indigo-500',
            badgeBg: 'bg-indigo-950/60 text-indigo-300 border-indigo-700/40',
            icon: Sparkles,
            iconColor: 'text-indigo-400',
          };
        }
        if (cat.includes('project')) {
          return {
            cardBg: 'bg-slate-900/95 border-purple-500/30 hover:border-purple-500/60',
            accent: 'border-l-4 border-l-purple-500',
            badgeBg: 'bg-purple-950/60 text-purple-300 border-purple-700/40',
            icon: Sparkles,
            iconColor: 'text-purple-400',
          };
        }
        if (cat.includes('internship')) {
          return {
            cardBg: 'bg-slate-900/95 border-cyan-500/30 hover:border-cyan-500/60',
            accent: 'border-l-4 border-l-cyan-500',
            badgeBg: 'bg-cyan-950/60 text-cyan-300 border-cyan-700/40',
            icon: Sparkles,
            iconColor: 'text-cyan-400',
          };
        }
        return {
          cardBg: 'bg-slate-900/95 border-amber-500/30 hover:border-amber-500/60',
          accent: 'border-l-4 border-l-amber-500',
          badgeBg: 'bg-amber-950/60 text-amber-300 border-amber-700/40',
          icon: Sparkles,
          iconColor: 'text-amber-400',
        };
      }
    }
  };

  if (!blocks || blocks.length === 0) {
    return (
      <div className="text-center py-12 bg-slate-900/40 border border-slate-800 rounded-2xl">
        <Clock className="w-10 h-10 text-slate-600 mx-auto mb-3" />
        <h3 className="text-base font-semibold text-slate-300">No scheduled timeline yet</h3>
        <p className="text-xs text-slate-500 mt-1">Run "Plan Tomorrow" to generate an optimized daily timeline.</p>
      </div>
    );
  }

  return (
    <div className="relative pl-6 sm:pl-8 space-y-4 before:absolute before:left-3 sm:before:left-4 before:top-3 before:bottom-3 before:w-0.5 before:bg-slate-800">
      {blocks.map((block) => {
        const style = getBlockStyle(block);
        const Icon = style.icon;
        const isCompleted = block.status === 'COMPLETED';

        return (
          <div
            key={block.id || `${block.start_time}-${block.title}`}
            className="relative group transition-all"
          >
            {/* Timeline Dot */}
            <div className={`absolute -left-6 sm:-left-8 top-4 w-3.5 h-3.5 rounded-full border-2 border-slate-900 transition-all ${
              block.block_type === 'FIXED'
                ? 'bg-slate-500'
                : block.block_type === 'BREAK'
                ? 'bg-emerald-400'
                : isCompleted
                ? 'bg-emerald-500 shadow-sm shadow-emerald-500'
                : 'bg-indigo-500 shadow-sm shadow-indigo-500'
            }`} />

            {/* Block Card */}
            <div
              className={`rounded-xl border p-4 shadow-lg transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3 ${style.cardBg} ${style.accent} ${
                isCompleted ? 'opacity-70 bg-slate-950/40' : ''
              }`}
            >
              {/* Left Details */}
              <div className="flex items-start sm:items-center space-x-3">
                {/* Completion Checkbox for Tasks */}
                {block.block_type === 'TASK' && onToggleStatus && (
                  <button
                    onClick={() => onToggleStatus(block.id, block.status)}
                    className="mt-0.5 sm:mt-0 text-slate-500 hover:text-emerald-400 transition-colors"
                  >
                    {isCompleted ? (
                      <CheckCircle2 className="w-5 h-5 text-emerald-400 fill-emerald-500/20" />
                    ) : (
                      <Circle className="w-5 h-5 text-slate-600 hover:text-indigo-400" />
                    )}
                  </button>
                )}

                <div>
                  <div className="flex items-center space-x-2 flex-wrap gap-y-1">
                    <span className={`text-sm font-bold tracking-tight ${isCompleted ? 'line-through text-slate-400' : 'text-slate-100'}`}>
                      {block.title}
                    </span>
                    {block.block_type === 'FIXED' && (
                      <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                        Fixed
                      </span>
                    )}
                    {block.category && (
                      <span className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded border ${style.badgeBg}`}>
                        {block.category}
                      </span>
                    )}
                    {block.xp_earned > 0 && (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/30 flex items-center gap-1">
                        <Award className="w-3 h-3" /> +{block.xp_earned} XP
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-400 mt-1 flex items-center gap-1.5 font-medium">
                    <Clock className="w-3 h-3 text-slate-500" />
                    {block.start_time} – {block.end_time}
                    <span className="text-slate-600">•</span>
                    <span className="text-slate-400">{block.duration_minutes} min</span>
                  </p>
                </div>
              </div>

              {/* Right Controls */}
              {isEditable && block.block_type === 'TASK' && onEditBlock && (
                <div className="flex items-center space-x-2 self-end sm:self-center">
                  <button
                    onClick={() => onEditBlock(block)}
                    className="flex items-center space-x-1 text-xs px-2.5 py-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-700 transition"
                  >
                    <Edit3 className="w-3.5 h-3.5 text-indigo-400" />
                    <span>Edit Slot</span>
                  </button>
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};
