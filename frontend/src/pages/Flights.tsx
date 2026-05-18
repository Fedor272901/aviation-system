import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { flightApi } from '../services/api';
import { useAuthStore } from '../store/authStore';
import { isAdmin } from '../utils/roles';
import { useApi } from '../hooks/useApi';
import { Loading, ErrorMessage, PageHeader, ConfirmDialog } from '../components/ui';
import type { Flight, Airport } from '../types';

export function Flights() {
  const [flights, setFlights] = useState<Flight[]>([]);
  const [airports, setAirports] = useState<Airport[]>([]);
  const listApi = useApi<Flight[]>();
  const searchApi = useApi<Flight[]>();
  const user = useAuthStore((s) => s.user);
  const isAdminUser = isAdmin(user);

  //  состояния для поиска
  const [searchFrom, setSearchFrom] = useState('');
  const [searchTo, setSearchTo] = useState('');
  const [searchDate, setSearchDate] = useState('');

  // СНАЧАЛА объявляем функцию
  const loadFlights = () => {
    listApi.execute(flightApi.getAll()).then((data) => {
      if (data) setFlights(data);
    });
  };

  useEffect(() => {
    loadFlights();
    flightApi.getAirports().then(({ data }) => setAirports(data));
    // flightApi.getAirlines().then(({ data }) => setAirlines(data));
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const criteria: any = {};
    if (searchFrom) criteria.id_from = Number(searchFrom);
    if (searchTo) criteria.id_to = Number(searchTo);
    if (searchDate) {
      const date = new Date(searchDate);
      criteria.date_from = date.toISOString();
      criteria.date_to = new Date(date.getTime() + 86400000).toISOString();
    }
    searchApi.execute(flightApi.search(criteria)).then((data) => {
      if (data) setFlights(data);
    });
  };

  const deleteApi = useApi<any>();
  const [deleteId, setDeleteId] = useState<number | null>(null);

  const resetSearch = () => {
    setSearchFrom('');
    setSearchTo('');
    setSearchDate('');
    loadFlights();
  };

  if (listApi.loading && flights.length === 0) return <Loading />;
  if (listApi.error) return <ErrorMessage message={listApi.error} onRetry={loadFlights} />;

  return (
    <div>
      <PageHeader
        title="Рейсы"
        action={
          isAdminUser ? (
            <Link to="/flights/new" className="btn btn-primary">
              + Создать рейс
            </Link>
          ) : undefined
        }
      />

      {/* Поиск */}
      <div className="card" style={{ marginBottom: 20 }}>
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'flex-end' }}>
          <div>
            <label style={{ display: 'block', fontSize: 13, color: '#666', marginBottom: 4 }}>Откуда</label>
            <select value={searchFrom} onChange={(e) => setSearchFrom(e.target.value)} style={{ padding: '8px 12px', borderRadius: 6, border: '1px solid #ddd', minWidth: 160 }}>
              <option value="">Все аэропорты</option>
              {airports.map((a) => (
                <option key={a.id} value={a.id}>{a.code} — {a.city}</option>
              ))}
            </select>
          </div>
          <div>
            <label style={{ display: 'block', fontSize: 13, color: '#666', marginBottom: 4 }}>Куда</label>
            <select value={searchTo} onChange={(e) => setSearchTo(e.target.value)} style={{ padding: '8px 12px', borderRadius: 6, border: '1px solid #ddd', minWidth: 160 }}>
              <option value="">Все аэропорты</option>
              {airports.map((a) => (
                <option key={a.id} value={a.id}>{a.code} — {a.city}</option>
              ))}
            </select>
          </div>
          <div>
            <label style={{ display: 'block', fontSize: 13, color: '#666', marginBottom: 4 }}>Дата</label>
            <input type="date" value={searchDate} onChange={(e) => setSearchDate(e.target.value)} style={{ padding: '8px 12px', borderRadius: 6, border: '1px solid #ddd' }} />
          </div>
          <button type="submit" className="btn btn-primary">🔍 Найти</button>
          {(searchFrom || searchTo || searchDate) && (
            <button type="button" onClick={resetSearch} className="btn" style={{ background: '#f5f5f5' }}>Сбросить</button>
          )}
        </form>
      </div>


      <ConfirmDialog
        isOpen={!!deleteId}
        title="Удалить рейс?"
        message="Рейс и все связанные билеты будут удалены."
        onConfirm={async () => {
          if (!deleteId) return;
          const result = await deleteApi.execute(flightApi.delete(deleteId));
          if (result) { setDeleteId(null); loadFlights(); }
        }}
        onCancel={() => setDeleteId(null)}
      />

      {/* Таблица */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <table className="table">
          <thead>
            <tr>
              <th>Рейс</th>
              <th>Маршрут</th>
              <th>Вылет</th>
              <th>Прилёт</th>
              <th>Статус</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {flights.map((f) => (
              <tr key={f.id}>
                <td><strong>{f.flight_number}</strong></td>
                <td>{f.from_airport_code || f.id_from} → {f.to_airport_code || f.id_to}</td>
                <td>{new Date(f.departure_datetime).toLocaleString('ru-RU', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })}</td>
                <td>{new Date(f.arrival_datetime).toLocaleString('ru-RU', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })}</td>
                <td>
                  <span style={{
                    padding: '2px 8px', borderRadius: 12, fontSize: 12, fontWeight: 600,
                    background: f.status_name === 'Отменён' ? '#fee' : f.status_name === 'Выполняется' ? '#e8f5e9' : '#e3f2fd',
                    color: f.status_name === 'Отменён' ? '#c00' : f.status_name === 'Выполняется' ? '#2e7d32' : '#1565c0',
                  }}>
                    {f.status_name || f.id_status}
                  </span>
                </td>
                <td>
                  <Link to={`/flights/${f.id}`} className="btn" style={{ padding: '4px 12px', fontSize: 13, background: '#f5f5f5' }}>
                    Подробнее
                  </Link>
                  {isAdminUser && (
                    <button
                      onClick={() => setDeleteId(f.id)}
                      className="btn btn-danger"
                      style={{ padding: '4px 12px', fontSize: 13, marginLeft: 8 }}
                    >
                      Удалить
                    </button>
                  )}
                </td>
              </tr>
            ))}
            {flights.length === 0 && (
              <tr><td colSpan={6} style={{ textAlign: 'center', color: '#999', padding: 40 }}>Рейсы не найдены</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}