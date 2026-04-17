import { useState } from 'react';

interface AppBlockOverlayProps {
  active: boolean;
}

export function AppBlockOverlay({ active }: AppBlockOverlayProps) {
  const [hold, setHold] = useState(0);
  const [unlocked, setUnlocked] = useState(false);

  if (!active || unlocked) return null;

  const startHold = () => {
    const started = Date.now();
    const interval = setInterval(() => {
      const percent = Math.min(((Date.now() - started) / 2500) * 100, 100);
      setHold(percent);
      if (percent === 100) {
        clearInterval(interval);
        setUnlocked(true);
      }
    }, 100);

    const stop = () => {
      clearInterval(interval);
      setHold(0);
      window.removeEventListener('mouseup', stop);
      window.removeEventListener('touchend', stop);
    };

    window.addEventListener('mouseup', stop);
    window.addEventListener('touchend', stop);
  };

  return (
    <div className="modal-backdrop app-block">
      <div className="modal card">
        <h3>Stay focused</h3>
        <p className="muted">This app is blocked during focus sessions (simulated).</p>
        <button className="hold-button" onMouseDown={startHold} onTouchStart={startHold}>
          Unlock ({Math.round(hold)}%)
        </button>
      </div>
    </div>
  );
}
