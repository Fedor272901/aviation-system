import { useEffect, useState } from 'react';
import { flightApi } from '../services/api';
import type { Flight } from '../types';

export function Flights() {
  const [flights, setFlights] = useState<Flight[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    flightApi.getAll()
      .then(({ data }) => setFlights(data))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="card">Загрузка...</div>;

  return (
    <div>
      <h1 style={{ marginBottom: 16 }}>Рейсы</h1>
      <table className="table">
        <thead>
          <tr>
            <th>Номер</th>
            <th>Вылет</th>
            <th>Прилёт</th>
            <th>Самолёт</th>
            <th>Статус</th>
          </tr>
        </thead>
        <tbody>
          {flights.map((f) => (
            <tr key={f.id}>
              <td>{f.flight_number}</td>
              <td>{new Date(f.departure_datetime).toLocaleString('ru-RU')}</td>
              <td>{new Date(f.arrival_datetime).toLocaleString('ru-RU')}</td>
              <td>{f.id_aircraft}</td>
              <td>{f.id_status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}