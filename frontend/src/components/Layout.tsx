import { NavLink, Outlet } from 'react-router-dom';

export function Layout() {
  return (
    <div>
      <nav className="nav">
        <div className="nav-inner">
          <span className="nav-brand">✈️ Aviation</span>
          <NavLink to="/">Главная</NavLink>
          <NavLink to="/persons">Пользователи</NavLink>
          <NavLink to="/flights">Рейсы</NavLink>
        </div>
      </nav>
      <main className="container">
        <Outlet />
      </main>
    </div>
  );
}