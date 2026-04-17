import { useEffect, useState } from 'react';

interface ExitGuardModalProps {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
}

export function ExitGuardModal({ open, onClose, onConfirm }: ExitGuardModalProps) {
  const [step, setStep] = useState(1);
  const [holdProgress, setHoldProgress] = useState(0);
  const [countdown, setCountdown] = useState(8);

  useEffect(() => {
    if (!open || step !== 2) return;
    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          onConfirm();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [open, step, onConfirm]);

  useEffect(() => {
    if (!open) {
      setStep(1);
      setHoldProgress(0);
      setCountdown(8);
    }
  }, [open]);

  if (!open) return null;

  const startHold = () => {
    const started = Date.now();
    const interval = setInterval(() => {
      const elapsed = Date.now() - started;
      const percent = Math.min((elapsed / 3000) * 100, 100);
      setHoldProgress(percent);
      if (percent === 100) {
        clearInterval(interval);
        onConfirm();
      }
    }, 100);

    const stop = () => {
      clearInterval(interval);
      setHoldProgress(0);
      window.removeEventListener('mouseup', stop);
      window.removeEventListener('touchend', stop);
    };

    window.addEventListener('mouseup', stop);
    window.addEventListener('touchend', stop);
  };

  return (
    <div className="modal-backdrop">
      <div className="modal card">
        {step === 1 ? (
          <>
            <h3>Are you sure you want to quit?</h3>
            <p className="muted">Breaking now resets your momentum.</p>
            <div className="modal-actions">
              <button className="ghost" onClick={onClose}>Keep Focusing</button>
              <button onClick={() => setStep(2)}>Yes, exit</button>
            </div>
          </>
        ) : (
          <>
            <h3>Unlock exit</h3>
            <p className="muted">Hold 3 seconds or wait {countdown}s.</p>
            <button className="hold-button" onMouseDown={startHold} onTouchStart={startHold}>
              Hold to exit ({Math.round(holdProgress)}%)
            </button>
            <button className="ghost" onClick={onClose}>Back</button>
          </>
        )}
      </div>
    </div>
  );
}
