export function Loading({ text = 'Загрузка...' }: { text?: string }) {
  return (
    <div className="card" style={{ textAlign: 'center', padding: 40 }}>
      <div style={{ fontSize: 18, color: '#666' }}>{text}</div>
    </div>
  );
}