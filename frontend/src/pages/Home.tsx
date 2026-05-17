import { Link } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

export function Home() {
  const user = useAuthStore((state) => state.user);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  return (
    <div>
      <h1 style={{ marginBottom: 8 }}>Система управления авиаперевозками</h1>
      <p style={{ color: '#666', marginBottom: 24 }}>
        {isAuthenticated
          ? `Добро пожаловать, ${user?.last_name} ${user?.first_name}!`
          : 'Базовый фронтенд на React + Vite'}
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
      {!isAuthenticated && (
        <div style={{ marginTop: 32, textAlign: 'center' }}>
          <Link to="/login" className="btn btn-primary">
            Войти в систему
          </Link>
          <span style={{ margin: '0 16px', color: '#ccc' }}>или</span>
          <Link to="/register" className="btn" style={{ background: '#e0e0e0' }}>
            Зарегистрироваться
          </Link>
        </div>
      )}
    </div>
  );
}