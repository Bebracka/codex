import type { FocusSession, Task } from '../../app/types';

const dayKey = (iso: string) => new Date(iso).toISOString().slice(0, 10);

export const sessionsToday = (sessions: FocusSession[]) => {
  const today = new Date().toISOString().slice(0, 10);
  return sessions.filter((s) => dayKey(s.completedAt) === today).length;
};

export const tasksCompletedToday = (tasks: Task[]) => {
  return tasks.filter((t) => t.completed && dayKey(t.createdAt) === new Date().toISOString().slice(0, 10)).length;
};

export const streakDays = (sessions: FocusSession[]) => {
  if (!sessions.length) return 0;

  const uniqueDays = Array.from(new Set(sessions.map((s) => dayKey(s.completedAt)))).sort().reverse();
  const today = new Date();
  let streak = 0;

  for (let i = 0; i < uniqueDays.length; i += 1) {
    const expected = new Date(today);
    expected.setDate(today.getDate() - i);
    if (dayKey(expected.toISOString()) === uniqueDays[i]) {
      streak += 1;
    } else {
      break;
    }
  }

  return streak;
};
