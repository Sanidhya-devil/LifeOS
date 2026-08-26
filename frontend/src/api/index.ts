import api from './client';
import {
  Task,
  FixedSchedule,
  DailyPlan,
  TodaySummary,
  MorningDashboardData,
  PlanEditConflictResponse,
} from '../types';

// Tasks API
export const getTasks = async (status?: string, category?: string): Promise<Task[]> => {
  const params: any = {};
  if (status) params.status = status;
  if (category) params.category = category;
  const res = await api.get<Task[]>('/tasks', { params });
  return res.data;
};

export const createTask = async (task: Partial<Task>): Promise<Task> => {
  const res = await api.post<Task>('/tasks', task);
  return res.data;
};

export const updateTaskStatus = async (
  taskId: number,
  status: string,
  actualMinutes?: number,
  notes?: string
): Promise<Task> => {
  const res = await api.patch<Task>(`/tasks/${taskId}/status`, {
    status,
    actual_minutes: actualMinutes,
    notes,
  });
  return res.data;
};

export const deleteTask = async (taskId: number): Promise<void> => {
  await api.delete(`/tasks/${taskId}`);
};

// Fixed Schedule API
export const getFixedSchedules = async (): Promise<FixedSchedule[]> => {
  const res = await api.get<FixedSchedule[]>('/fixed-schedule');
  return res.data;
};

export const createFixedSchedule = async (schedule: Partial<FixedSchedule>): Promise<FixedSchedule> => {
  const res = await api.post<FixedSchedule>('/fixed-schedule', schedule);
  return res.data;
};

export const updateFixedSchedule = async (
  id: number,
  schedule: Partial<FixedSchedule>
): Promise<FixedSchedule> => {
  const res = await api.put<FixedSchedule>(`/fixed-schedule/${id}`, schedule);
  return res.data;
};

export const deleteFixedSchedule = async (id: number): Promise<void> => {
  await api.delete(`/fixed-schedule/${id}`);
};

// Review API
export const getTodaySummary = async (): Promise<TodaySummary> => {
  const res = await api.get<TodaySummary>('/reviews/today');
  return res.data;
};

export const submitDailyReview = async (review: {
  energy_rating: number;
  completed_notes?: string;
  missed_reasons?: string;
  tomorrow_priorities?: string;
  deadline_changes?: string;
  task_statuses?: Record<number, string>;
}): Promise<any> => {
  const res = await api.post('/reviews', review);
  return res.data;
};

// Plans API
export const generatePlan = async (payload: {
  target_date?: string;
  review_id?: number;
  strategy?: string;
}): Promise<any> => {
  const res = await api.post('/plans/generate', payload);
  return res.data;
};

export const getLatestPlan = async (targetDate?: string): Promise<DailyPlan | null> => {
  const params: any = {};
  if (targetDate) params.target_date = targetDate;
  const res = await api.get<DailyPlan | null>('/plans/latest', { params });
  return res.data;
};

export const validatePlanEdit = async (
  planId: number,
  blockId: number,
  newStartTime: string,
  newEndTime: string
): Promise<PlanEditConflictResponse> => {
  const res = await api.post<PlanEditConflictResponse>(`/plans/${planId}/validate-edit`, {
    block_id: blockId,
    new_start_time: newStartTime,
    new_end_time: newEndTime,
  });
  return res.data;
};

export const approvePlan = async (planId: number): Promise<DailyPlan> => {
  const res = await api.post<DailyPlan>(`/plans/${planId}/approve`);
  return res.data;
};

export const regeneratePlan = async (planId: number): Promise<any> => {
  const res = await api.post(`/plans/${planId}/regenerate`);
  return res.data;
};

// Dashboard API
export const getMorningDashboard = async (targetDate?: string): Promise<MorningDashboardData> => {
  const params: any = {};
  if (targetDate) params.target_date = targetDate;
  const res = await api.get<MorningDashboardData>('/dashboard/morning', { params });
  return res.data;
};

export const updateBlockStatus = async (blockId: number, status: string): Promise<any> => {
  const res = await api.post('/dashboard/block-status', {
    block_id: blockId,
    status,
  });
  return res.data;
};
