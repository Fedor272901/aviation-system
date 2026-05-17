import { useEffect, useState } from 'react';
import { crewApi, flightApi, personApi } from '../services/api';
import { isAdmin } from '../utils/roles';
import { useAuthStore } from '../store/authStore';
import { useApi } from '../hooks/useApi';
import { Loading, ErrorMessage, PageHeader, ConfirmDialog } from '../components/ui';
import type { Crew, FlightRole, CrewAssignment, Flight } from '../types';

export function CrewPage() {
  const user = useAuthStore((s) => s.user);
  const isAdminUser = isAdmin(user);

  const [crew, setCrew] = useState<Crew[]>([]);
  const [roles, setRoles] = useState<FlightRole[]>([]);
  const [assignments, setAssignments] = useState<CrewAssignment[]>([]);
  const [flights, setFlights] = useState<Flight[]>([]);
  const [persons, setPersons] = useState<any[]>([]);

  const crewApiState = useApi<Crew[]>();
  const rolesApi = useApi<FlightRole[]>();
  const assignmentsApi = useApi<CrewAssignment[]>();
  const flightsApi = useApi<Flight[]>();
  const personsApi = useApi<any[]>();
  const createCrewApi = useApi<Crew>();
  const createAssignApi = useApi<CrewAssignment>();
  const deleteAssignApi = useApi<any>();

  const [newPersonId, setNewPersonId] = useState('');
  const [assignForm, setAssignForm] = useState({ crew_id: '', flight_id: '', role_id: '' });
  const [deleteAssignId, setDeleteAssignId] = useState<number | null>(null);

  const loadData = () => {
    crewApiState.execute(crewApi.getAll()).then((d) => { if (d) setCrew(d); });
    rolesApi.execute(crewApi.getRoles()).then((d) => { if (d) setRoles(d); });
    assignmentsApi.execute(crewApi.getAssignments()).then((d) => { if (d) setAssignments(d); });
    flightsApi.execute(flightApi.getAll()).then((d) => { if (d) setFlights(d); });
    personsApi.execute(personApi.getAll()).then((d) => { if (d) setPersons(d); });
  };

  useEffect(() => { loadData(); }, []);

  const handleCreateCrew = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newPersonId) return;
    const result = await createCrewApi.execute(crewApi.create({ person_id: Number(newPersonId) }));
    if (result) { setNewPersonId(''); loadData(); }
  };

  const handleCreateAssignment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!assignForm.crew_id || !assignForm.flight_id || !assignForm.role_id) return;
    const result = await createAssignApi.execute(crewApi.createAssignment({
      id_crew: Number(assignForm.crew_id),
      id_flight: Number(assignForm.flight_id),
      id_flight_role: Number(assignForm.role_id),
    }));
    if (result) {
      setAssignForm({ crew_id: '', flight_id: '', role_id: '' });
      loadData();
    }
  };

  const handleDeleteAssignment = async () => {
    if (!deleteAssignId) return;
    const result = await deleteAssignApi.execute(crewApi.deleteAssignment(deleteAssignId));
    if (result) { setDeleteAssignId(null); loadData(); }
  };

  if (crewApiState.loading && crew.length === 0) return <Loading />;
  if (crewApiState.error) return <ErrorMessage message={crewApiState.error} />;

  const getPersonEmail = (personId: number) => persons.find((p) => p.id === personId)?.email || personId;
  const getFlightNum = (flightId: number) => flights.find((f) => f.id === flightId)?.flight_number || flightId;
  const getRoleName = (roleId: number) => roles.find((r) => r.id === roleId)?.role_name || roleId;

  return (
    <div>
      <PageHeader title="Экипаж" />

      <ConfirmDialog isOpen={!!deleteAssignId} title="Снять с рейса?" message="Назначение будет удалено." onConfirm={handleDeleteAssignment} onCancel={() => setDeleteAssignId(null)} />

      {isAdminUser && (
        <>
          <div className="card" style={{ marginBottom: 16 }}>
            <h3 style={{ marginBottom: 12 }}>Новый сотрудник</h3>
            <form onSubmit={handleCreateCrew} style={{ display: 'flex', gap: 8 }}>
              <select value={newPersonId} onChange={(e) => setNewPersonId(e.target.value)} required style={{ flex: 1, padding: 8, borderRadius: 6, border: '1px solid #ddd' }}>
                <option value="">Выберите пользователя</option>
                {persons.map((p) => (
                  <option key={p.id} value={p.id}>{p.last_name} {p.first_name} ({p.email})</option>
                ))}
              </select>
              <button type="submit" className="btn btn-primary" disabled={createCrewApi.loading}>Добавить в экипаж</button>
            </form>
          </div>

          <div className="card" style={{ marginBottom: 16 }}>
            <h3 style={{ marginBottom: 12 }}>Назначить на рейс</h3>
            <form onSubmit={handleCreateAssignment} style={{ display: 'flex', gap: 8 }}>
              <select value={assignForm.crew_id} onChange={(e) => setAssignForm({ ...assignForm, crew_id: e.target.value })} required style={{ flex: 1, padding: 8, borderRadius: 6, border: '1px solid #ddd' }}>
                <option value="">Сотрудник</option>
                {crew.map((c) => (
                  <option key={c.id} value={c.id}>{getPersonEmail(c.person_id)}</option>
                ))}
              </select>
              <select value={assignForm.flight_id} onChange={(e) => setAssignForm({ ...assignForm, flight_id: e.target.value })} required style={{ flex: 1, padding: 8, borderRadius: 6, border: '1px solid #ddd' }}>
                <option value="">Рейс</option>
                {flights.map((f) => (
                  <option key={f.id} value={f.id}>{f.flight_number}</option>
                ))}
              </select>
              <select value={assignForm.role_id} onChange={(e) => setAssignForm({ ...assignForm, role_id: e.target.value })} required style={{ flex: 1, padding: 8, borderRadius: 6, border: '1px solid #ddd' }}>
                <option value="">Должность</option>
                {roles.map((r) => (
                  <option key={r.id} value={r.id}>{r.role_name}</option>
                ))}
              </select>
              <button type="submit" className="btn btn-primary" disabled={createAssignApi.loading}>Назначить</button>
            </form>
          </div>
        </>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <div className="card">
          <h3 style={{ marginBottom: 12 }}>Сотрудники ({crew.length})</h3>
          <table className="table">
            <thead><tr><th>ID</th><th>Сотрудник</th></tr></thead>
            <tbody>
              {crew.map((c) => (
                <tr key={c.id}><td>{c.id}</td><td>{getPersonEmail(c.person_id)}</td></tr>
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
          <thead><tr><th>Рейс</th><th>Сотрудник</th><th>Должность</th>{isAdminUser && <th></th>}</tr></thead>
          <tbody>
            {assignments.map((a) => (
              <tr key={a.id}>
                <td>{getFlightNum(a.id_flight)}</td>
                <td>{getPersonEmail(a.id_crew)}</td>
                <td>{getRoleName(a.id_flight_role)}</td>
                {isAdminUser && <td><button onClick={() => setDeleteAssignId(a.id)} className="btn btn-danger" style={{ padding: '4px 12px', fontSize: 13 }}>Снять</button></td>}
              </tr>
            ))}
            {assignments.length === 0 && <tr><td colSpan={isAdminUser ? 4 : 3} style={{ textAlign: 'center', color: '#999', padding: 40 }}>Назначений нет</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}