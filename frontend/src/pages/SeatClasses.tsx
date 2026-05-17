import { useState, useEffect } from 'react';
import { aircraftApi } from '../services/api';
import { useApi } from '../hooks/useApi';
import { Loading, ErrorMessage, PageHeader, ConfirmDialog } from '../components/ui';
import type { SeatClass } from '../types';

export function SeatClasses() {
  const [items, setItems] = useState<SeatClass[]>([]);
  const listApi = useApi<SeatClass[]>();
  const createApi = useApi<SeatClass>();
  const deleteApi = useApi<any>();
  const [deleteId, setDeleteId] = useState<number | null>(null);

  const [form, setForm] = useState({ class_name: '', price_multiplier: '1.0', description: '' });

  const load = () => listApi.execute(aircraftApi.getSeatClasses()).then((d) => { if (d) setItems(d); });

  useEffect(() => { load(); }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    const result = await createApi.execute(aircraftApi.createSeatClass({
      class_name: form.class_name,
      price_multiplier: form.price_multiplier,
      description: form.description || undefined,
    }));
    if (result) { setForm({ class_name: '', price_multiplier: '1.0', description: '' }); load(); }
  };

  const handleDelete = async () => {
    if (!deleteId) return;
    const result = await deleteApi.execute(aircraftApi.deleteSeatClass(deleteId));
    if (result) { setDeleteId(null); load(); }
  };

  if (listApi.loading && items.length === 0) return <Loading />;
  if (listApi.error) return <ErrorMessage message={listApi.error} onRetry={load} />;

  return (
    <div>
      <PageHeader title="Классы мест" />
      <form onSubmit={handleCreate} className="card" style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        <input placeholder="Название (Эконом)" value={form.class_name} onChange={(e) => setForm({ ...form, class_name: e.target.value })} required style={{ flex: 1, padding: 8, borderRadius: 6, border: '1px solid #ddd' }} />
        <input placeholder="Множитель цены" value={form.price_multiplier} onChange={(e) => setForm({ ...form, price_multiplier: e.target.value })} required style={{ width: 120, padding: 8, borderRadius: 6, border: '1px solid #ddd' }} />
        <input placeholder="Описание" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} style={{ flex: 1, padding: 8, borderRadius: 6, border: '1px solid #ddd' }} />
        <button type="submit" className="btn btn-primary" disabled={createApi.loading}>Добавить</button>
      </form>

      <ConfirmDialog isOpen={!!deleteId} title="Удалить класс?" message="Убедитесь, что класс не используется." onConfirm={handleDelete} onCancel={() => setDeleteId(null)} />

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <table className="table">
          <thead><tr><th>ID</th><th>Название</th><th>Множитель</th><th>Описание</th><th></th></tr></thead>
          <tbody>
            {items.map((s) => (
              <tr key={s.id}><td>{s.id}</td><td>{s.class_name}</td><td>{s.price_multiplier}</td><td>{s.description || '—'}</td><td><button onClick={() => setDeleteId(s.id)} className="btn btn-danger" style={{ padding: '4px 12px', fontSize: 13 }}>Удалить</button></td></tr>
            ))}
            {items.length === 0 && <tr><td colSpan={5} style={{ textAlign: 'center', color: '#999', padding: 40 }}>Классы не добавлены</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}