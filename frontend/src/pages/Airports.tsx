import { useState, useEffect } from 'react';
import { flightApi } from '../services/api';
import { useApi } from '../hooks/useApi';
import { Loading, ErrorMessage, PageHeader, ConfirmDialog } from '../components/ui';
import type { Airport } from '../types';

export function Airports() {
  const [items, setItems] = useState<Airport[]>([]);
  const listApi = useApi<Airport[]>();
  const createApi = useApi<Airport>();
  const deleteApi = useApi<any>();
  const [deleteId, setDeleteId] = useState<number | null>(null);

  const [form, setForm] = useState({ code: '', name: '', city: '' });

  const load = () => listApi.execute(flightApi.getAirports()).then((d) => { if (d) setItems(d); });

  useEffect(() => { load(); }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    const result = await createApi.execute(flightApi.createAirport(form));
    if (result) { setForm({ code: '', name: '', city: '' }); load(); }
  };

  const handleDelete = async () => {
    if (!deleteId) return;
    const result = await deleteApi.execute(flightApi.deleteAirport(deleteId));
    if (result) { setDeleteId(null); load(); }
  };

  if (listApi.loading && items.length === 0) return <Loading />;
  if (listApi.error) return <ErrorMessage message={listApi.error} onRetry={load} />;

  return (
    <div>
      <PageHeader title="Аэропорты" />
      <form onSubmit={handleCreate} className="card" style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        <input placeholder="Код (LED)" value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value })} required style={{ flex: 1, padding: 8, borderRadius: 6, border: '1px solid #ddd' }} />
        <input placeholder="Название" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} style={{ flex: 2, padding: 8, borderRadius: 6, border: '1px solid #ddd' }} />
        <input placeholder="Город" value={form.city} onChange={(e) => setForm({ ...form, city: e.target.value })} required style={{ flex: 2, padding: 8, borderRadius: 6, border: '1px solid #ddd' }} />
        <button type="submit" className="btn btn-primary" disabled={createApi.loading}>Добавить</button>
      </form>

      <ConfirmDialog isOpen={!!deleteId} title="Удалить аэропорт?" message="Убедитесь, что нет рейсов из/в этот аэропорт." onConfirm={handleDelete} onCancel={() => setDeleteId(null)} />

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <table className="table">
          <thead><tr><th>Код</th><th>Название</th><th>Город</th><th></th></tr></thead>
          <tbody>
            {items.map((a) => (
              <tr key={a.id}>
                <td><strong>{a.code}</strong></td>
                <td>{a.name || '—'}</td>
                <td>{a.city}</td>
                <td><button onClick={() => setDeleteId(a.id)} className="btn btn-danger" style={{ padding: '4px 12px', fontSize: 13 }}>Удалить</button></td>
              </tr>
            ))}
            {items.length === 0 && <tr><td colSpan={4} style={{ textAlign: 'center', color: '#999', padding: 40 }}>Аэропорты не добавлены</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}