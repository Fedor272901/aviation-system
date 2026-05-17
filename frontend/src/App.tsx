import { useEffect, useCallback } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import { Layout } from './components/Layout';
import { Home } from './pages/Home';
import { Persons } from './pages/Persons';
import { Flights } from './pages/Flights';
import { Login } from './pages/Login';
import { Register } from './pages/Register';

// Компонент для защищённых маршрутов
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

function App() {
  const checkAuth = useAuthStore((state) => state.checkAuth);

  const handleCheckAuth = useCallback(() => {
    checkAuth();
  }, [checkAuth]);

  useEffect(() => {
    handleCheckAuth();
  }, [handleCheckAuth]);

  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Home />} />
        <Route
          path="/persons"
          element={
            <ProtectedRoute>
              <Persons />
            </ProtectedRoute>
          }
        />
        <Route path="/flights" element={<Flights />} />
      </Route>

      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
    </Routes>
  );
}

export default App;