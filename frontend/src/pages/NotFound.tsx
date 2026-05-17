import { Link } from 'react-router-dom';

export function NotFound() {
  return (
    <div className="card" style={{ textAlign: 'center', padding: 60 }}>
      <h1 style={{ fontSize: 64, marginBottom: 16 }}>404</h1>
      <p style={{ color: '#666', marginBottom: 24 }}>Страница не найдена</p>
      <Link to="/" className="btn btn-primary">На главную</Link>
    </div>
  );
}