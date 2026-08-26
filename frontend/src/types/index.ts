export interface Task {
  id: number;
  user_id: number;
  title: string;
  description?: string;
  category: string;
  estimated_minutes: number;
  importance: number;
  difficulty: number;
  deadline?: string;
  goal_relevance: number;
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'SKIPPED' | 'PARTIAL' | 'POSTPONED' | 'CANCELLED';
  base_xp: number;
  parent_id?: number;
  created_at: string;
  updated_at: string;
}

export interface FixedSchedule {
  id: number;
  user_id: number;
  title: string;
  start_time: string;
  end_time: string;
  days_of_week: string;
  is_active: boolean;
  created_at: string;
}

export interface ScheduledBlock {
  id: number;
  plan_id?: number;
  task_id?: number;
  title: string;
  block_type: 'FIXED' | 'TASK' | 'BREAK' | 'BUFFER' | 'REST';
  start_time: string;
  end_time: string;
  duration_minutes: number;
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'SKIPPED' | 'PARTIAL';
  xp_earned: number;
  display_order: number;
  category?: string;
}

export interface DailyPlan {
  id: number;
  user_id: number;
  plan_date: string;
  status: 'DRAFT' | 'APPROVED' | 'ACTIVE' | 'COMPLETED' | 'ARCHIVED';
  total_planned_minutes: number;
  total_potential_xp: number;
  ai_reasoning?: string;
  generated_at: string;
  approved_at?: string;
  scheduled_blocks: ScheduledBlock[];
}

export interface TodaySummary {
  date: string;
  scheduled_tasks: ScheduledBlock[];
  completed_tasks: { id: number; title: string; category: string; base_xp: number }[];
  missed_tasks: { id: number; title: string; category: string }[];
  partial_tasks: { id: number; title: string; category: string }[];
  total_xp_today: number;
  current_level: number;
  total_xp: number;
  upcoming_deadlines: { id: number; title: string; category: string; deadline?: string; importance: number }[];
}

export interface MorningDashboardData {
  date: string;
  user: {
    username: string;
    current_level: number;
    total_xp: number;
  };
  plan_status: string;
  plan_id?: number;
  ai_reasoning?: string;
  total_potential_xp: number;
  main_quests: {
    block_id: number;
    task_id?: number;
    title: string;
    category: string;
    xp: number;
    status: string;
    start_time: string;
    end_time: string;
  }[];
  timeline: ScheduledBlock[];
}

export interface PlanEditConflictResponse {
  has_conflict: boolean;
  conflicting_block?: ScheduledBlock;
  message: string;
  suggested_options: string[];
}
