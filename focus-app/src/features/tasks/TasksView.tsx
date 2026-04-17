import { useMemo, useState } from 'react';
import type { Priority, Task, TaskSection } from '../../app/types';

interface TasksViewProps {
  tasks: Task[];
  onAddTask: (title: string, section: TaskSection, priority: Priority) => void;
  onDeleteTask: (id: string) => void;
  onToggleTask: (id: string) => void;
}

const sections: TaskSection[] = ['today', 'later'];

export function TasksView({ tasks, onAddTask, onDeleteTask, onToggleTask }: TasksViewProps) {
  const [title, setTitle] = useState('');
  const [priority, setPriority] = useState<Priority>('medium');
  const [section, setSection] = useState<TaskSection>('today');

  const grouped = useMemo(
    () => sections.map((name) => ({ name, tasks: tasks.filter((task) => task.section === name) })),
    [tasks],
  );

  const submit = (event: React.FormEvent) => {
    event.preventDefault();
    if (!title.trim()) return;
    onAddTask(title.trim(), section, priority);
    setTitle('');
    setPriority('medium');
    setSection('today');
  };

  return (
    <section className="screen">
      <header>
        <h2>Tasks</h2>
        <p className="muted">Keep this lightweight. Focus mode does the heavy lifting.</p>
      </header>

      <form className="card task-form" onSubmit={submit}>
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Add a meaningful task"
          aria-label="Task title"
        />
        <div className="inline-fields">
          <select value={section} onChange={(e) => setSection(e.target.value as TaskSection)}>
            <option value="today">Today</option>
            <option value="later">Later</option>
          </select>
          <select value={priority} onChange={(e) => setPriority(e.target.value as Priority)}>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
          <button type="submit">Add</button>
        </div>
      </form>

      {grouped.map((group) => (
        <article key={group.name} className="task-group">
          <h3>{group.name === 'today' ? 'Today' : 'Later'}</h3>
          <div className="task-list">
            {group.tasks.map((task) => (
              <div key={task.id} className="card task-item">
                <button className={`checkbox ${task.completed ? 'checked' : ''}`} onClick={() => onToggleTask(task.id)}>
                  {task.completed ? '✓' : ''}
                </button>
                <div>
                  <p className={task.completed ? 'line-through' : ''}>{task.title}</p>
                  <small className={`priority ${task.priority}`}>{task.priority}</small>
                </div>
                <button className="ghost" onClick={() => onDeleteTask(task.id)} aria-label="Delete task">
                  Delete
                </button>
              </div>
            ))}
          </div>
        </article>
      ))}
    </section>
  );
}
