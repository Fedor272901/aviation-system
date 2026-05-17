import { Link } from 'react-router-dom';
import { HomeBase } from './HomeBase';

export function HomeGuest() {
  return (
    <HomeBase
      title="Система управления авиаперевозками"
      subtitle="Бронируйте билеты, отслеживайте рейсы и управляйте полётами в одном месте"
    >
      <Link to="/flights" className="card" style={{ display: 'block' }}>
        <h3>✈️ Поиск рейсов</h3>
        <p style={{ color: '#666', fontSize: 14, marginTop: 4 }}>
          Просмотр расписания и доступных рейсов без регистрации
        </p>
      </Link>

      <Link to="/login" className="card" style={{ display: 'block' }}>
        <h3>🔐 Вход</h3>
        <p style={{ color: '#666', fontSize: 14, marginTop: 4 }}>
          Войдите в личный кабинет для покупки билетов
        </p>
      </Link>

      <Link to="/register" className="card" style={{ display: 'block' }}>
        <h3>📝 Регистрация</h3>
        <p style={{ color: '#666', fontSize: 14, marginTop: 4 }}>
          Создайте аккаунт пассажира за пару минут
        </p>
      </Link>

      <div className="card">
        <h3>🎫 Билеты онлайн</h3>
        <p style={{ color: '#666', fontSize: 14, marginTop: 4 }}>
          Бронирование, возврат и управление бронированиями
        </p>
      </div>
    </HomeBase>
  );
}