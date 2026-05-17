import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

export function Layout() {
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div>
      <nav className="nav">
        <div className="nav-inner">
          <span className="nav-brand">✈️ Aviation</span>
          <NavLink to="/">Главная</NavLink>
          <NavLink to="/persons">Пользователи</NavLink>
          <NavLink to="/flights">Рейсы</NavLink>

          <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 16 }}>
            {user ? (
              <>
                <span style={{ fontSize: 14, color: '#555' }}>
                  {user.last_name} {user.first_name}
                </span>
                <button
                  onClick={handleLogout}
                  className="btn"
                  style={{ background: '#f5f5f5', color: '#666' }}
                >
                  Выход
                </button>
              </>
            ) : (
              <NavLink to="/login" style={{ fontSize: 14 }}>
                Вход
              </NavLink>
            )}
          </div>
        </div>
      </nav>
      <main className="container">
        <Outlet />
      </main>
    </div>
  );
}