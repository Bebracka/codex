import type { FocusState, Task } from '../../app/types';

interface FocusViewProps {
  state: FocusState;
  selectedTaskName: string;
  secondsLeft: number;
  totalSeconds: number;
  onTaskChange: (taskName: string) => void;
  onStart: () => void;
  onPause: () => void;
  onResume: () => void;
  onAttemptExit: () => void;
  tasks: Task[];
}

const labelByState: Record<FocusState, string> = {
  idle: 'Start Focus',
  running: 'Pause',
  paused: 'Resume',
  finished: 'Focus Complete',
};

const toClock = (seconds: number) => {
  const m = String(Math.floor(seconds / 60)).padStart(2, '0');
  const s = String(seconds % 60).padStart(2, '0');
  return `${m}:${s}`;
};

export function FocusView({
  state,
  selectedTaskName,
  secondsLeft,
  totalSeconds,
  onTaskChange,
  onStart,
  onPause,
  onResume,
  onAttemptExit,
  tasks,
}: FocusViewProps) {
  const progress = ((totalSeconds - secondsLeft) / totalSeconds) * 100;

  const onPrimaryAction = () => {
    if (state === 'idle' || state === 'finished') onStart();
    if (state === 'running') onPause();
    if (state === 'paused') onResume();
  };

  return (
    <section className={`screen focus-screen ${state === 'running' ? 'immersive' : ''}`}>
      <p className="eyebrow">Focus Mode</p>
      <div className="timer-wrap card">
        <div className="timer-ring" style={{ ['--progress' as string]: `${progress}%` }}>
          <div className="timer-center">
            <p className="timer-value">{toClock(secondsLeft)}</p>
            <p className="muted">{selectedTaskName || 'Choose a task'}</p>
          </div>
        </div>
      </div>

      <label className="task-picker card">
        <span>Current Task</span>
        <select value={selectedTaskName} onChange={(e) => onTaskChange(e.target.value)} disabled={state === 'running'}>
          <option value="">Deep Work (No task)</option>
          {tasks.filter((t) => !t.completed).map((task) => (
            <option key={task.id} value={task.title}>
              {task.title}
            </option>
          ))}
        </select>
      </label>

      <button className="primary-action" onClick={onPrimaryAction}>
        {labelByState[state]}
      </button>

      {state === 'running' && (
        <button className="exit-focus" onClick={onAttemptExit}>
          Exit Focus
        </button>
      )}
    </section>
  );
}
