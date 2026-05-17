import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { isAdmin, isStaff } from '../utils/roles';

export function Layout() {
  const user = useAuthStore((state) => state.user);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
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
          <NavLink to="/" end>Главная</NavLink>
          <NavLink to="/flights">Рейсы</NavLink>

          {isAuthenticated && (
            <>
              <NavLink to="/tickets/my">Мои билеты</NavLink>
              <NavLink to="/profile">Профиль</NavLink>
            </>
          )}

          {isAuthenticated && isAdmin(user) && (
            <>
              <NavLink to="/persons">Пользователи</NavLink>
              <NavLink to="/tickets">Билеты</NavLink>
              <NavLink to="/aircraft">Самолёты</NavLink>
              <NavLink to="/crew">Экипаж</NavLink>
              <NavLink to="/airports">Аэропорты</NavLink>
              <NavLink to="/airlines">Авиакомпании</NavLink>
            </>
          )}

          {isAuthenticated && isStaff(user) && !isAdmin(user) && (
            <NavLink to="/crew">Экипаж</NavLink>
          )}

          <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 16 }}>
            {user ? (
              <>
                <span style={{ fontSize: 14, color: '#555' }}>
                  {user.last_name} {user.first_name}
                  {isAdmin(user) && ' (админ)'}
                  {isStaff(user) && !isAdmin(user) && ' (экипаж)'}
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
              <>
                <NavLink to="/login" style={{ fontSize: 14 }}>Вход</NavLink>
                <NavLink to="/register" style={{ fontSize: 14 }}>Регистрация</NavLink>
              </>
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