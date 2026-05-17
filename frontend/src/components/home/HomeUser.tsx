import { Link } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { HomeBase } from './HomeBase';

export function HomeUser() {
  const user = useAuthStore((state) => state.user);

  return (
    <HomeBase
      title={`Добро пожаловать, ${user?.first_name}!`}
      subtitle="Личный кабинет пассажира"
    >
      <Link to="/flights" className="card" style={{ display: 'block' }}>
        <h3>✈️ Поиск рейсов</h3>
        <p style={{ color: '#666', fontSize: 14, marginTop: 4 }}>
          Найдите и забронируйте подходящий рейс
        </p>
      </Link>

      <Link to="/tickets/my" className="card" style={{ display: 'block' }}>
        <h3>🎫 Мои билеты</h3>
        <p style={{ color: '#666', fontSize: 14, marginTop: 4 }}>
          История покупок, посадочные талоны, возврат билетов
        </p>
      </Link>

      <div className="card">
        <h3>👤 Профиль</h3>
        <p style={{ color: '#666', fontSize: 14, marginTop: 4 }}>
          {user?.last_name} {user?.first_name}<br />
          {user?.email}
        </p>
      </div>
    </HomeBase>
  );
}