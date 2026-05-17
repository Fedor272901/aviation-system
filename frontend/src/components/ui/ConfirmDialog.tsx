import { useEffect } from 'react';

interface ConfirmDialogProps {
  title: string;
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
  isOpen: boolean;
}

export function ConfirmDialog({ title, message, onConfirm, onCancel, isOpen }: ConfirmDialogProps) {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onCancel();
    };
    if (isOpen) window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [isOpen, onCancel]);

  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000,
    }}>
      <div className="card" style={{ maxWidth: 400, width: '90%' }}>
        <h3 style={{ marginBottom: 8 }}>{title}</h3>
        <p style={{ color: '#666', marginBottom: 24 }}>{message}</p>
        <div style={{ display: 'flex', gap: 12, justifyContent: 'flex-end' }}>
          <button onClick={onCancel} className="btn" style={{ background: '#f5f5f5', color: '#333' }}>
            Отмена
          </button>
          <button onClick={onConfirm} className="btn btn-danger">
            Подтвердить
          </button>
        </div>
      </div>
    </div>
  );
}