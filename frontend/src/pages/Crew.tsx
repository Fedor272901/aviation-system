import { useEffect, useState } from 'react';
import { crewApi } from '../services/api';
import { isAdmin } from '../utils/roles';
import { useAuthStore } from '../store/authStore';
import { useApi } from '../hooks/useApi';
import { Loading, ErrorMessage, PageHeader } from '../components/ui';
import { Navigate } from 'react-router-dom';
import type { Crew, FlightRole, CrewAssignment } from '../types';

export function CrewPage() {
  const user = useAuthStore((s) => s.user);
  const isAdminUser = isAdmin(user);

  const [crew, setCrew] = useState<Crew[]>([]);
  const [roles, setRoles] = useState<FlightRole[]>([]);
  const [assignments, setAssignments] = useState<CrewAssignment[]>([]);
  const crewApiState = useApi<Crew[]>();
  const rolesApi = useApi<FlightRole[]>();
  const assignmentsApi = useApi<CrewAssignment[]>();



  const loadData = () => {
    crewApiState.execute(crewApi.getAll()).then((data) => { if (data) setCrew(data); });
    rolesApi.execute(crewApi.getRoles()).then((data) => { if (data) setRoles(data); });
    assignmentsApi.execute(crewApi.getAssignments()).then((data) => { if (data) setAssignments(data); });
  };

  useEffect(() => {
      loadData();
    }, []
  );

  if (!isAdminUser) return <Navigate to="/" replace />;
  if (crewApiState.loading) return <Loading />;

  return (
    <div>
      <PageHeader title="Экипаж" />

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <div className="card">
          <h3 style={{ marginBottom: 12 }}>Сотрудники ({crew.length})</h3>
          <table className="table">
            <thead><tr><th>ID</th><th>Person ID</th></tr></thead>
            <tbody>
              {crew.map((c) => (
                <tr key={c.id}><td>{c.id}</td><td>{c.person_id}</td></tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="card">
          <h3 style={{ marginBottom: 12 }}>Должности ({roles.length})</h3>
          <table className="table">
            <thead><tr><th>ID</th><th>Название</th></tr></thead>
            <tbody>
              {roles.map((r) => (
                <tr key={r.id}><td>{r.id}</td><td>{r.role_name}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="card" style={{ marginTop: 16 }}>
        <h3 style={{ marginBottom: 12 }}>Назначения ({assignments.length})</h3>
        <table className="table">
          <thead>
            <tr><th>ID</th><th>Рейс</th><th>Сотрудник</th><th>Должность</th></tr>
          </thead>
          <tbody>
            {assignments.map((a) => (
              <tr key={a.id}>
                <td>{a.id}</td>
                <td>{a.flight_number || a.id_flight}</td>
                <td>{a.crew_person_email || a.id_crew}</td>
                <td>{a.flight_role_name || a.id_flight_role}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}