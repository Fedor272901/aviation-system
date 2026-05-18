import { useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import { isAdmin, isStaff } from './utils/roles';
import { Layout } from './components/Layout';
import { Home } from './pages/Home';
import { Persons } from './pages/Persons';
import { Flights } from './pages/Flights';
import { FlightDetail } from './pages/FlightDetail';
import { FlightCreate } from './pages/FlightCreate';
import { FlightEdit } from './pages/FlightEdit';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Profile } from './pages/Profile';
import { MyTickets } from './pages/MyTickets';
import { Tickets } from './pages/Tickets';
import { TicketBuy } from './pages/TicketBuy';
import { CrewPage } from './pages/Crew';
import { AircraftList } from './pages/AircraftList';
import { AircraftDetail } from './pages/AircraftDetail';
import { AircraftCreate } from './pages/AircraftCreate';
import { AircraftEdit } from './pages/AircraftEdit';
import { Airports } from './pages/Airports';
import { Airlines } from './pages/Airlines';
import { FlightStatuses } from './pages/FlightStatuses';
import { SeatClasses } from './pages/SeatClasses';
import { CrewRoles } from './pages/CrewRoles';
import { NotFound } from './pages/NotFound';
import { ErrorBoundary } from './components/ErrorBoundary';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const isLoading = useAuthStore((s) => s.isLoading);
  if (isLoading) return <div style={{ padding: 40, textAlign: 'center' }}>Загрузка...</div>;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

function AdminRoute({ children }: { children: React.ReactNode }) {
  const user = useAuthStore((s) => s.user);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (!isAdmin(user)) return <Navigate to="/" replace />;
  return <>{children}</>;
}

function StaffRoute({ children }: { children: React.ReactNode }) {
  const user = useAuthStore((s) => s.user);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (!isAdmin(user) && !isStaff(user)) return <Navigate to="/" replace />;
  return <>{children}</>;
}

function App() {
  const checkAuth = useAuthStore((s) => s.checkAuth);
  useEffect(() => { checkAuth(); }, [checkAuth]);

  return (
    <ErrorBoundary>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Home />} />
          <Route path="/flights" element={<Flights />} />
          <Route path="/flights/:id" element={<FlightDetail />} />

          <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
          <Route path="/tickets/my" element={<ProtectedRoute><MyTickets /></ProtectedRoute>} />
          <Route path="/tickets/buy" element={<ProtectedRoute><TicketBuy /></ProtectedRoute>} />

          <Route path="/persons" element={<AdminRoute><Persons /></AdminRoute>} />
          <Route path="/tickets" element={<AdminRoute><Tickets /></AdminRoute>} />
          <Route path="/aircraft" element={<AdminRoute><AircraftList /></AdminRoute>} />
          <Route path="/aircraft/new" element={<AdminRoute><AircraftCreate /></AdminRoute>} />
          <Route path="/aircraft/:id" element={<AdminRoute><AircraftDetail /></AdminRoute>} />
          <Route path="/aircraft/:id/edit" element={<AdminRoute><AircraftEdit /></AdminRoute>} />
          <Route path="/flights/new" element={<AdminRoute><FlightCreate /></AdminRoute>} />
          <Route path="/flights/:id/edit" element={<AdminRoute><FlightEdit /></AdminRoute>} />
          <Route path="/airports" element={<AdminRoute><Airports /></AdminRoute>} />
          <Route path="/airlines" element={<AdminRoute><Airlines /></AdminRoute>} />
          <Route path="/flight-statuses" element={<AdminRoute><FlightStatuses /></AdminRoute>} />
          <Route path="/seat-classes" element={<AdminRoute><SeatClasses /></AdminRoute>} />
          <Route path="/crew-roles" element={<AdminRoute><CrewRoles /></AdminRoute>} />

          <Route path="/crew" element={<StaffRoute><CrewPage /></StaffRoute>} />
        </Route>

        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </ErrorBoundary>
  );
}

export default App;