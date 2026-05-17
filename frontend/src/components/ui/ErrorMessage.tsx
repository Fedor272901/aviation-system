export function ErrorMessage({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="card" style={{ background: '#fee', color: '#c00' }}>
      <p>⚠️ {message}</p>
      {onRetry && (
        <button onClick={onRetry} className="btn" style={{ marginTop: 12, background: '#c00', color: 'white' }}>
          Повторить
        </button>
      )}
    </div>
  );
}