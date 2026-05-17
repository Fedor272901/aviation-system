import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { personApi } from '../services/api';
import { useApi } from '../hooks/useApi';
import { Loading, ErrorMessage, PageHeader, ConfirmDialog } from '../components/ui';
import type { Person } from '../types';

export function Persons() {
  const [persons, setPersons] = useState<Person[]>([]);
  const [editId, setEditId] = useState<number | null>(null);
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const listApi = useApi<Person[]>();
  const updateApi = useApi<Person>();
  const deleteApi = useApi<any>();

  const [form, setForm] = useState({ first_name: '', last_name: '', email: '', phone: '', passport: '' });

  const loadData = () => {
    listApi.execute(personApi.getAll()).then((data) => {
      if (data) setPersons(data);
    });
  };

  useEffect(() => {
    loadData();
  }, []);

  const startEdit = (p: Person) => {
    setEditId(p.id);
    setForm({
      first_name: p.first_name,
      last_name: p.last_name,
      email: p.email,
      phone: p.phone || '',
      passport: p.passport,
    });
  };

  const handleUpdate = async () => {
    if (!editId) return;
    const result = await updateApi.execute(personApi.update(editId, form));
    if (result) {
      setEditId(null);
      loadData();
    }
  };

  const handleDelete = async () => {
    if (!deleteId) return;
    const result = await deleteApi.execute(personApi.delete(deleteId));
    if (result) {
      setDeleteId(null);
      loadData();
    }
  };

  if (listApi.loading && persons.length === 0) return <Loading />;
  if (listApi.error) return <ErrorMessage message={listApi.error} onRetry={loadData} />;

  return (
    <div>
      <PageHeader title="Пользователи" action={<Link to="/register" className="btn btn-primary">+ Добавить</Link>} />

      <ConfirmDialog
        isOpen={!!deleteId}
        title="Удалить пользователя?"
        message="Это действие нельзя отменить."
        onConfirm={handleDelete}
        onCancel={() => setDeleteId(null)}
      />

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <table className="table">
          <thead>
            <tr><th>ID</th><th>ФИО</th><th>Email</th><th>Телефон</th><th>Паспорт</th><th></th></tr>
          </thead>
          <tbody>
            {persons.map((p) => (
              <tr key={p.id}>
                {editId === p.id ? (
                  <>
                    <td>{p.id}</td>
                    <td>
                      <input value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} style={{ width: 80, padding: 4 }} placeholder="Имя" />
                      <input value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} style={{ width: 80, padding: 4, marginLeft: 4 }} placeholder="Фамилия" />
                    </td>
                    <td><input value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} style={{ width: 140, padding: 4 }} /></td>
                    <td><input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} style={{ width: 100, padding: 4 }} /></td>
                    <td><input value={form.passport} onChange={(e) => setForm({ ...form, passport: e.target.value })} style={{ width: 100, padding: 4 }} /></td>
                    <td>
                      <div style={{ display: 'flex', gap: 4 }}>
                        <button onClick={handleUpdate} className="btn btn-primary" style={{ padding: '4px 8px', fontSize: 12 }} disabled={updateApi.loading}>Сохранить</button>
                        <button onClick={() => setEditId(null)} className="btn" style={{ padding: '4px 8px', fontSize: 12, background: '#f5f5f5' }}>Отмена</button>
                      </div>
                    </td>
                  </>
                ) : (
                  <>
                    <td>{p.id}</td>
                    <td>{p.last_name} {p.first_name}</td>
                    <td>{p.email}</td>
                    <td>{p.phone || '—'}</td>
                    <td>{p.passport}</td>
                    <td>
                      <div style={{ display: 'flex', gap: 4 }}>
                        <button onClick={() => startEdit(p)} className="btn" style={{ padding: '4px 8px', fontSize: 12, background: '#e3f2fd', color: '#1565c0' }}>Редактировать</button>
                        <button onClick={() => setDeleteId(p.id)} className="btn btn-danger" style={{ padding: '4px 8px', fontSize: 12 }}>Удалить</button>
                      </div>
                    </td>
                  </>
                )}
              </tr>
            ))}
            {persons.length === 0 && (
              <tr><td colSpan={6} style={{ textAlign: 'center', color: '#999', padding: 40 }}>Пользователи не найдены</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}