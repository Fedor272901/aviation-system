import { useState, useEffect } from 'react';
import { NavLink, Outlet, useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { isAdmin, isStaff } from '../utils/roles';

interface NavItem {
  label: string;
  to: string;
  icon?: string;
  adminOnly?: boolean;
  staffOnly?: boolean;
  authOnly?: boolean;
}

export function Layout() {
  const user = useAuthStore((state) => state.user);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const logout = useAuthStore((state) => state.logout);
  const navigate = useNavigate();
  const location = useLocation();

  const [menuOpen, setMenuOpen] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Закрытие меню при навигации
  useEffect(() => {
    setMenuOpen(false);
    setSidebarOpen(false);
  }, [location.pathname]);

  // Закрытие по ESC
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setSidebarOpen(false);
      }
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const closeSidebar = () => setSidebarOpen(false);

  // ==========================================
  // МЕНЮ НАВИГАЦИИ
  // ==========================================
  const navItems: NavItem[] = [
    // Общие ссылки
    { label: 'Главная', to: '/', icon: '🏠' },
    { label: 'Рейсы', to: '/flights', icon: '✈️' },
    { label: 'Мои билеты', to: '/tickets/my', icon: '🎫', authOnly: true },
    { label: 'Профиль', to: '/profile', icon: '👤', authOnly: true },

    // Staff (экипаж)
    { label: 'Экипаж', to: '/crew', icon: '👨‍✈️', staffOnly: true },

    // Admin (справочники)
    { label: 'Пользователи', to: '/persons', icon: '👥', adminOnly: true },
    { label: 'Билеты', to: '/tickets', icon: '🎟️', adminOnly: true },
    { label: 'Самолёты', to: '/aircraft', icon: '🛩️', adminOnly: true },
    { label: 'Экипаж', to: '/crew', icon: '👨‍✈️', adminOnly: true },
    { label: 'Аэропорты', to: '/airports', icon: '🛫', adminOnly: true },
    { label: 'Авиакомпании', to: '/airlines', icon: '✈️', adminOnly: true },
    { label: 'Статусы рейсов', to: '/flight-statuses', icon: '📊', adminOnly: true },
    { label: 'Классы мест', to: '/seat-classes', icon: '💺', adminOnly: true },
    { label: 'Роли экипажа', to: '/crew-roles', icon: '🎭', adminOnly: true },
  ];

  const getVisibleItems = () => {
    return navItems.filter((item) => {
      if (item.authOnly && !isAuthenticated) return false;
      if (item.adminOnly && !isAdmin(user)) return false;
      if (item.staffOnly && !isStaff(user)) return false;
      return true;
    });
  };

  const visibleItems = getVisibleItems();

  // Группировка для сайдбара
  const groupBySection = (items: NavItem[]) => {
    const sections: { title: string; items: NavItem[] }[] = [];
    let currentSection: { title: string; items: NavItem[] } | null = null;

    items.forEach((item) => {
      if (item.adminOnly) {
        if (!currentSection?.title.includes('Администратор')) {
          if (currentSection) sections.push(currentSection);
          currentSection = { title: 'Администрирование', items: [] };
        }
      } else if (item.staffOnly) {
        if (!currentSection?.title.includes('Персонал')) {
          if (currentSection) sections.push(currentSection);
          currentSection = { title: 'Персонал', items: [] };
        }
      } else {
        if (!currentSection?.title.includes('Основное')) {
          if (currentSection) sections.push(currentSection);
          currentSection = { title: 'Основное', items: [] };
        }
      }
      currentSection?.items.push(item);
    });

    if (currentSection) sections.push(currentSection);
    return sections;
  };

  const sections = groupBySection(visibleItems);

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* ==========================================
          ВЕРХНЯЯ ШАПКА
          ========================================== */}
      <header className="navbar" style={{
        background: '#fff',
        borderBottom: '1px solid #e0e0e0',
        position: 'sticky',
        top: 0,
        zIndex: 100,
      }}>
        <div style={{
          maxWidth: 1400,
          margin: '0 auto',
          padding: '0 20px',
          height: 60,
          display: 'flex',
          alignItems: 'center',
          gap: 16,
        }}>
          {/* Бургер-кнопка */}
          <button
            onClick={() => setSidebarOpen(true)}
            className="btn"
            style={{
              background: 'transparent',
              padding: '8px 12px',
              border: 'none',
              cursor: 'pointer',
              fontSize: 20,
            }}
            aria-label="Меню"
          >
            ☰
          </button>

          {/* Бренд */}
          <NavLink to="/" end style={{
            textDecoration: 'none',
            fontSize: 18,
            fontWeight: 600,
            color: '#1976d2',
          }}>
            ✈️ Aviation
          </NavLink>

          {/* Информация о пользователе */}
          <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 16 }}>
            {user ? (
              <>
                <div style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'flex-end',
                }}>
                  <span style={{
                    fontSize: 14,
                    fontWeight: 500,
                    color: '#333',
                  }}>
                    {user.last_name} {user.first_name}
                  </span>
                  <span style={{
                    fontSize: 12,
                    color: '#666',
                  }}>
                    {isAdmin(user) && 'Администратор'}
                    {isStaff(user) && !isAdmin(user) && 'Персонал'}
                    {!isAdmin(user) && !isStaff(user) && 'Пассажир'}
                  </span>
                </div>
                <button
                  onClick={handleLogout}
                  className="btn"
                  style={{
                    background: '#f5f5f5',
                    color: '#666',
                    padding: '6px 16px',
                    fontSize: 13,
                  }}
                >
                  Выйти
                </button>
              </>
            ) : (
              <>
                <NavLink to="/login" style={({ isActive }) => ({
                  textDecoration: 'none',
                  fontSize: 14,
                  color: isActive ? '#1976d2' : '#666',
                  fontWeight: isActive ? 600 : 400,
                })}>
                  Вход
                </NavLink>
                <NavLink to="/register" style={({ isActive }) => ({
                  textDecoration: 'none',
                  fontSize: 14,
                  color: isActive ? '#1976d2' : '#666',
                  fontWeight: isActive ? 600 : 400,
                })}>
                  Регистрация
                </NavLink>
              </>
            )}
          </div>
        </div>
      </header>

      {/* ==========================================
          ОВЕРЛЕЙ ДЛЯ САЙДБАРА
          ========================================== */}
      {sidebarOpen && (
        <div
          onClick={closeSidebar}
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0,0,0,0.5)',
            zIndex: 1000,
            cursor: 'pointer',
          }}
        />
      )}

      {/* ==========================================
          БОКОВОЕ МЕНЮ (SIDEBAR)
          ========================================== */}
      <aside style={{
        position: 'fixed',
        top: 0,
        left: sidebarOpen ? 0 : -320,
        width: 300,
        height: '100vh',
        background: '#fff',
        boxShadow: '2px 0 10px rgba(0,0,0,0.2)',
        zIndex: 1001,
        transition: 'left 0.3s ease',
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column',
      }}>
        {/* Заголовок сайдбара */}
        <div style={{
          padding: '20px 16px',
          borderBottom: '1px solid #e0e0e0',
          background: '#f5f5f5',
        }}>
          <h3 style={{
            margin: 0,
            fontSize: 16,
            fontWeight: 600,
            color: '#333',
          }}>
            Навигация
          </h3>
        </div>

        {/* Ссылки */}
        <nav style={{ flex: 1, padding: '8px 0' }}>
          {sections.map((section, idx) => (
            <div key={idx} style={{ marginBottom: 16 }}>
              <div style={{
                padding: '8px 16px',
                fontSize: 12,
                fontWeight: 600,
                color: '#666',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
              }}>
                {section.title}
              </div>
              {section.items.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  style={({ isActive }) => ({
                    display: 'flex',
                    alignItems: 'center',
                    gap: 12,
                    padding: '10px 20px',
                    textDecoration: 'none',
                    color: isActive ? '#1976d2' : '#333',
                    background: isActive ? '#e3f2fd' : 'transparent',
                    fontWeight: isActive ? 600 : 400,
                    borderLeft: isActive ? '3px solid #1976d2' : '3px solid transparent',
                    transition: 'all 0.15s',
                  })}
                >
                  <span style={{ fontSize: 18 }}>{item.icon}</span>
                  <span style={{ flex: 1 }}>{item.label}</span>
                </NavLink>
              ))}
            </div>
          ))}
        </nav>

        {/* Подвал сайдбара (кнопка закрытия для мобильных) */}
        <div style={{
          padding: '16px',
          borderTop: '1px solid #e0e0e0',
          display: 'flex',
          justifyContent: 'center',
        }}>
          <button
            onClick={closeSidebar}
            className="btn"
            style={{
              background: '#f5f5f5',
              color: '#666',
              padding: '8px 24px',
            }}
          >
            Закрыть
          </button>
        </div>
      </aside>

      {/* ==========================================
          ОСНОВНОЙ КОНТЕНТ
          ========================================== */}
      <main style={{
        flex: 1,
        padding: '24px',
        maxWidth: 1400,
        margin: '0 auto',
        width: '100%',
        boxSizing: 'border-box',
      }}>
        <Outlet />
      </main>
    </div>
  );
}