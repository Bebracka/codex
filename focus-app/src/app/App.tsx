import { useEffect, useMemo, useState } from 'react';
import type { FocusState, Priority, Task, TaskSection } from './types';
import { localStore } from '../storage/localStore';
import { FocusView } from '../features/focus/FocusView';
import { TasksView } from '../features/tasks/TasksView';
import { sessionsToday, streakDays, tasksCompletedToday } from '../features/analytics/analytics';
import { StatCard } from '../components/StatCard';
import { ExitGuardModal } from '../components/ExitGuardModal';
import { AppBlockOverlay } from '../components/AppBlockOverlay';

type Tab = 'focus' | 'tasks' | 'analytics';

const FOCUS_DURATION = 25 * 60;

export function App() {
  const [tab, setTab] = useState<Tab>('focus');
  const [data, setData] = useState(localStore.load);
  const [focusState, setFocusState] = useState<FocusState>('idle');
  const [secondsLeft, setSecondsLeft] = useState(FOCUS_DURATION);
  const [selectedTaskName, setSelectedTaskName] = useState('');
  const [showExitGuard, setShowExitGuard] = useState(false);

  useEffect(() => {
    localStore.save(data);
  }, [data]);

  useEffect(() => {
    if (focusState !== 'running') return;
    const timer = setInterval(() => {
      setSecondsLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          setFocusState('finished');
          setData((current) => ({
            ...current,
            sessions: [
              ...current.sessions,
              {
                id: crypto.randomUUID(),
                taskName: selectedTaskName || 'Deep Work',
                startedAt: new Date(Date.now() - FOCUS_DURATION * 1000).toISOString(),
                completedAt: new Date().toISOString(),
                durationSeconds: FOCUS_DURATION,
              },
            ],
          }));
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [focusState, selectedTaskName]);

  const addTask = (title: string, section: TaskSection, priority: Priority) => {
    const task: Task = {
      id: crypto.randomUUID(),
      title,
      section,
      priority,
      completed: false,
      createdAt: new Date().toISOString(),
    };

    setData((prev) => ({ ...prev, tasks: [task, ...prev.tasks] }));
  };

  const toggleTask = (id: string) => {
    setData((prev) => ({
      ...prev,
      tasks: prev.tasks.map((task) => (task.id === id ? { ...task, completed: !task.completed } : task)),
    }));
  };

  const deleteTask = (id: string) => {
    setData((prev) => ({ ...prev, tasks: prev.tasks.filter((task) => task.id !== id) }));
  };

  const metrics = useMemo(
    () => ({
      sessionsToday: sessionsToday(data.sessions),
      streak: streakDays(data.sessions),
      doneToday: tasksCompletedToday(data.tasks),
    }),
    [data],
  );

  const resetFocus = () => {
    setFocusState('idle');
    setSecondsLeft(FOCUS_DURATION);
    setShowExitGuard(false);
  };

  return (
    <main className="app-shell">
      {tab === 'focus' && (
        <FocusView
          state={focusState}
          selectedTaskName={selectedTaskName}
          secondsLeft={secondsLeft}
          totalSeconds={FOCUS_DURATION}
          onTaskChange={setSelectedTaskName}
          onStart={() => {
            setSecondsLeft(FOCUS_DURATION);
            setFocusState('running');
          }}
          onPause={() => setFocusState('paused')}
          onResume={() => setFocusState('running')}
          onAttemptExit={() => setShowExitGuard(true)}
          tasks={data.tasks}
        />
      )}

      {tab === 'tasks' && (
        <TasksView tasks={data.tasks} onAddTask={addTask} onDeleteTask={deleteTask} onToggleTask={toggleTask} />
      )}

      {tab === 'analytics' && (
        <section className="screen analytics-screen">
          <header>
            <h2>Momentum</h2>
            <p className="muted">Simple signals to protect your deep work streak.</p>
          </header>
          <div className="stats-grid">
            <StatCard value={metrics.sessionsToday} label="Focus sessions today" />
            <StatCard value={metrics.streak} label="Day streak" />
            <StatCard value={metrics.doneToday} label="Tasks done today" />
          </div>
          <article className="card mini-chart">
            {Array.from({ length: 7 }).map((_, idx) => {
              const value = Math.max(1, (data.sessions.length + idx) % 4);
              return <div key={idx} style={{ height: `${25 + value * 18}px` }} />;
            })}
          </article>
        </section>
      )}

      <nav className="bottom-nav card">
        <button className={tab === 'focus' ? 'active' : ''} onClick={() => setTab('focus')}>Focus</button>
        <button className={tab === 'tasks' ? 'active' : ''} onClick={() => setTab('tasks')}>Tasks</button>
        <button className={tab === 'analytics' ? 'active' : ''} onClick={() => setTab('analytics')}>Analytics</button>
      </nav>

      <ExitGuardModal open={showExitGuard} onClose={() => setShowExitGuard(false)} onConfirm={resetFocus} />
      <AppBlockOverlay active={focusState === 'running' && tab !== 'focus'} />
    </main>
  );
}
