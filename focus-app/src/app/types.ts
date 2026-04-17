export type Priority = 'low' | 'medium' | 'high';
export type TaskSection = 'today' | 'later';

export interface Task {
  id: string;
  title: string;
  section: TaskSection;
  priority: Priority;
  completed: boolean;
  createdAt: string;
}

export interface FocusSession {
  id: string;
  taskId?: string;
  taskName: string;
  startedAt: string;
  completedAt: string;
  durationSeconds: number;
}

export interface AppData {
  tasks: Task[];
  sessions: FocusSession[];
}

export type FocusState = 'idle' | 'running' | 'paused' | 'finished';
