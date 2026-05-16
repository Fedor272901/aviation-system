import { useEffect, useState } from 'react';
import { personApi } from '../services/api';
import type { Person } from '../types';

export function Persons() {
  const [persons, setPersons] = useState<Person[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    personApi.getAll()
      .then(({ data }) => setPersons(data))
      .catch(() => setError('Не удалось загрузить пользователей'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="card">Загрузка...</div>;
  if (error) return <div className="card" style={{ color: '#d32f2f' }}>{error}</div>;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <h1>Пользователи</h1>
        <button className="btn btn-primary">+ Добавить</button>
      </div>
      <table className="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>ФИО</th>
            <th>Email</th>
            <th>Телефон</th>
            <th>Паспорт</th>
          </tr>
        </thead>
        <tbody>
          {persons.map((p) => (
            <tr key={p.id}>
              <td>{p.id}</td>
              <td>{p.last_name} {p.first_name} {p.middle_name || ''}</td>
              <td>{p.email}</td>
              <td>{p.phone || '—'}</td>
              <td>{p.passport}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}