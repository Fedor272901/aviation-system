import { Link } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { HomeBase } from './HomeBase';

export function HomeStaff() {
  const user = useAuthStore((state) => state.user);

  return (
    <HomeBase
      title={`Кабинет сотрудника`}
      subtitle={`${user?.last_name} ${user?.first_name} — экипаж`}
    >
      <Link to="/flights" className="card" style={{ display: 'block' }}>
        <h3>✈️ Расписание рейсов</h3>
        <p style={{ color: '#666', fontSize: 14, marginTop: 4 }}>
          Общий список рейсов и назначений
        </p>
      </Link>

      <div className="card">
        <h3>📋 Мои назначения</h3>
        <p style={{ color: '#666', fontSize: 14, marginTop: 4 }}>
          Ближайшие рейсы, на которые вы назначены
        </p>
      </div>

      <Link to="/crew" className="card" style={{ display: 'block' }}>
        <h3>🧑‍✈️ Состав экипажа</h3>
        <p style={{ color: '#666', fontSize: 14, marginTop: 4 }}>
          Коллеги и должности на рейсах
        </p>
      </Link>
    </HomeBase>
  );
}