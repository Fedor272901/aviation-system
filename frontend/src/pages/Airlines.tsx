import { useState, useEffect } from 'react';
import { flightApi } from '../services/api';
import { useApi } from '../hooks/useApi';
import { Loading, ErrorMessage, PageHeader, ConfirmDialog } from '../components/ui';
import type { Airline } from '../types';

export function Airlines() {
  const [items, setItems] = useState<Airline[]>([]);
  const listApi = useApi<Airline[]>();
  const createApi = useApi<Airline>();
  const deleteApi = useApi<any>();
  const [deleteId, setDeleteId] = useState<number | null>(null);

  const [form, setForm] = useState({ name: '', code: '', country: '' });

  const load = () => listApi.execute(flightApi.getAirlines()).then((d) => { if (d) setItems(d); });

  useEffect(() => { load(); }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    const result = await createApi.execute(flightApi.createAirline(form));
    if (result) { setForm({ name: '', code: '', country: '' }); load(); }
  };

  const handleDelete = async () => {
    if (!deleteId) return;
    const result = await deleteApi.execute(flightApi.deleteAirline(deleteId));
    if (result) { setDeleteId(null); load(); }
  };

  if (listApi.loading && items.length === 0) return <Loading />;
  if (listApi.error) return <ErrorMessage message={listApi.error} onRetry={load} />;

  return (
    <div>
      <PageHeader title="Авиакомпании" />
      <form onSubmit={handleCreate} className="card" style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        <input placeholder="Название" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required style={{ flex: 2, padding: 8, borderRadius: 6, border: '1px solid #ddd' }} />
        <input placeholder="Код (SU)" value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value })} required style={{ flex: 1, padding: 8, borderRadius: 6, border: '1px solid #ddd' }} />
        <input placeholder="Страна" value={form.country} onChange={(e) => setForm({ ...form, country: e.target.value })} style={{ flex: 1, padding: 8, borderRadius: 6, border: '1px solid #ddd' }} />
        <button type="submit" className="btn btn-primary" disabled={createApi.loading}>Добавить</button>
      </form>

      <ConfirmDialog isOpen={!!deleteId} title="Удалить авиакомпанию?" message="Убедитесь, что нет рейсов этой авиакомпании." onConfirm={handleDelete} onCancel={() => setDeleteId(null)} />

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <table className="table">
          <thead><tr><th>Код</th><th>Название</th><th>Страна</th><th></th></tr></thead>
          <tbody>
            {items.map((a) => (
              <tr key={a.id}>
                <td><strong>{a.code}</strong></td>
                <td>{a.name}</td>
                <td>{a.country || '—'}</td>
                <td><button onClick={() => setDeleteId(a.id)} className="btn btn-danger" style={{ padding: '4px 12px', fontSize: 13 }}>Удалить</button></td>
              </tr>
            ))}
            {items.length === 0 && <tr><td colSpan={4} style={{ textAlign: 'center', color: '#999', padding: 40 }}>Авиакомпании не добавлены</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}