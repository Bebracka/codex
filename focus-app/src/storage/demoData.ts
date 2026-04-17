import type { AppData } from '../app/types';

const now = new Date();
const iso = (daysAgo: number) => {
  const d = new Date(now);
  d.setDate(now.getDate() - daysAgo);
  return d.toISOString();
};

export const demoData: AppData = {
  tasks: [
    { id: 't1', title: 'Write product draft', section: 'today', priority: 'high', completed: false, createdAt: iso(0) },
    { id: 't2', title: 'Review onboarding notes', section: 'today', priority: 'medium', completed: false, createdAt: iso(0) },
    { id: 't3', title: 'Inbox cleanup', section: 'later', priority: 'low', completed: true, createdAt: iso(1) },
    { id: 't4', title: 'Plan weekly deep work blocks', section: 'later', priority: 'medium', completed: false, createdAt: iso(2) }
  ],
  sessions: [
    { id: 's1', taskName: 'Write product draft', startedAt: iso(0), completedAt: iso(0), durationSeconds: 1500 },
    { id: 's2', taskName: 'Design review', startedAt: iso(1), completedAt: iso(1), durationSeconds: 1500 },
    { id: 's3', taskName: 'Research notes', startedAt: iso(2), completedAt: iso(2), durationSeconds: 1200 }
  ]
};
