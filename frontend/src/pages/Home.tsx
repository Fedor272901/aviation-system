import { Link } from 'react-router-dom';

export function Home() {
  return (
    <div>
      <h1 style={{ marginBottom: 8 }}>Система управления авиаперевозками</h1>
      <p style={{ color: '#666', marginBottom: 24 }}>
        Базовый фронтенд на React + Vite
      </p>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
        <Link to="/persons" className="card" style={{ display: 'block' }}>
          <h3>👤 Пользователи</h3>
          <p style={{ color: '#666', fontSize: 14, marginTop: 4 }}>
            Управление пассажирами и экипажем
          </p>
        </Link>
        <Link to="/flights" className="card" style={{ display: 'block' }}>
          <h3>✈️ Рейсы</h3>
          <p style={{ color: '#666', fontSize: 14, marginTop: 4 }}>
            Поиск и управление рейсами
          </p>
        </Link>
        <div className="card">
          <h3>🎫 Билеты</h3>
          <p style={{ color: '#666', fontSize: 14, marginTop: 4 }}>
            Продажа и бронирование (в разработке)
          </p>
        </div>
      </div>
    </div>
  );
}