import { Link } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { HomeBase } from './HomeBase';

export function HomeAdmin() {
  const user = useAuthStore((state) => state.user);

  return (
    <HomeBase
      title="Панель администратора"
      subtitle={`Вы вошли как ${user?.last_name} ${user?.first_name}`}
    >
      <Link to="/persons" className="card" style={{ display: 'block' }}>
        <h3>👥 Пользователи</h3>
        <p style={{ color: '#666', fontSize: 14, marginTop: 4 }}>
          Управление пассажирами и ролями
        </p>
      </Link>

      <Link to="/flights" className="card" style={{ display: 'block' }}>
        <h3>✈️ Рейсы</h3>
        <p style={{ color: '#666', fontSize: 14, marginTop: 4 }}>
          Расписание, создание и редактирование
        </p>
      </Link>

      <Link to="/aircraft" className="card" style={{ display: 'block' }}>
        <h3>🛩️ Самолёты</h3>
        <p style={{ color: '#666', fontSize: 14, marginTop: 4 }}>
          Парк воздушных судов, модели, аренда
        </p>
      </Link>

      <Link to="/tickets" className="card" style={{ display: 'block' }}>
        <h3>🎫 Билеты</h3>
        <p style={{ color: '#666', fontSize: 14, marginTop: 4 }}>
          Все продажи и статистика
        </p>
      </Link>

      <Link to="/crew" className="card" style={{ display: 'block' }}>
        <h3>🧑‍✈️ Экипаж</h3>
        <p style={{ color: '#666', fontSize: 14, marginTop: 4 }}>
          Назначения на рейсы
        </p>
      </Link>
    </HomeBase>
  );
}