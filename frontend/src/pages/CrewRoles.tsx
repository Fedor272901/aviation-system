import { useState, useEffect } from 'react';
import { crewApi } from '../services/api';
import { useApi } from '../hooks/useApi';
import { Loading, ErrorMessage, PageHeader, ConfirmDialog } from '../components/ui';
import type { FlightRole } from '../types';

export function CrewRoles() {
  const [items, setItems] = useState<FlightRole[]>([]);
  const listApi = useApi<FlightRole[]>();
  const createApi = useApi<FlightRole>();
  const deleteApi = useApi<any>();
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [name, setName] = useState('');

  const load = () => listApi.execute(crewApi.getRoles()).then((d) => { if (d) setItems(d); });

  useEffect(() => { load(); }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    const result = await createApi.execute(crewApi.createRole({ role_name: name }));
    if (result) { setName(''); load(); }
  };

  const handleDelete = async () => {
    if (!deleteId) return;
    const result = await deleteApi.execute(crewApi.deleteRole(deleteId));
    if (result) { setDeleteId(null); load(); }
  };

  if (listApi.loading && items.length === 0) return <Loading />;
  if (listApi.error) return <ErrorMessage message={listApi.error} onRetry={load} />;

  return (
    <div>
      <PageHeader title="Должности экипажа" />
      <form onSubmit={handleCreate} className="card" style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        <input placeholder="Название должности" value={name} onChange={(e) => setName(e.target.value)} required style={{ flex: 1, padding: 8, borderRadius: 6, border: '1px solid #ddd' }} />
        <button type="submit" className="btn btn-primary" disabled={createApi.loading}>Добавить</button>
      </form>

      <ConfirmDialog isOpen={!!deleteId} title="Удалить должность?" message="Убедитесь, что нет назначений с этой ролью." onConfirm={handleDelete} onCancel={() => setDeleteId(null)} />

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <table className="table">
          <thead><tr><th>ID</th><th>Название</th><th></th></tr></thead>
          <tbody>
            {items.map((r) => (
              <tr key={r.id}><td>{r.id}</td><td>{r.role_name}</td><td><button onClick={() => setDeleteId(r.id)} className="btn btn-danger" style={{ padding: '4px 12px', fontSize: 13 }}>Удалить</button></td></tr>
            ))}
            {items.length === 0 && <tr><td colSpan={3} style={{ textAlign: 'center', color: '#999', padding: 40 }}>Должности не добавлены</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}