import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { flightApi } from '../services/api';
import { useApi } from '../hooks/useApi';
import { Loading, ErrorMessage, PageHeader } from '../components/ui';
import { useAuthStore } from '../store/authStore';
import { isAdmin } from '../utils/roles';
import type { Flight, FlightPrice } from '../types';

export function FlightDetail() {
  const { id } = useParams<{ id: string }>();
  const flightId = Number(id);
  const user = useAuthStore((s) => s.user);
  const isAdminUser = isAdmin(user);

  const [flight, setFlight] = useState<Flight | null>(null);
  const [prices, setPrices] = useState<FlightPrice[]>([]);
  const flightApiState = useApi<Flight>();
  const pricesApi = useApi<FlightPrice[]>();

  useEffect(() => {
    flightApiState.execute(flightApi.getById(flightId)).then((data) => {
      if (data) setFlight(data);
    });
    pricesApi.execute(flightApi.getPrices(flightId)).then((data) => {
      if (data) setPrices(data);
    });
  }, [flightId]);

  if (flightApiState.loading) return <Loading />;
  if (flightApiState.error) return <ErrorMessage message={flightApiState.error} />;
  if (!flight) return <ErrorMessage message="Рейс не найден" />;

  return (
    <div>
      <PageHeader
        title={`Рейс ${flight.flight_number}`}
        action={
          <div style={{ display: 'flex', gap: 8 }}>
            {isAdminUser ? (
              <Link to={`/flights/${flight.id}/edit`} className="btn btn-primary">Редактировать</Link>
            ) : user ? (
              <Link to={`/tickets/buy?flight=${flight.id}`} className="btn btn-primary">Купить билет</Link>
            ) : null}
          </div>
        }
      />

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 20 }}>
        <div className="card">
          <h3 style={{ marginBottom: 12, color: '#666', fontSize: 14, textTransform: 'uppercase' }}>Информация</h3>
          <div style={{ display: 'grid', gap: 8 }}>
            <div><strong>Номер:</strong> {flight.flight_number}</div>
            <div><strong>Авиакомпания:</strong> {flight.airline_name || flight.id_airline}</div>
            <div><strong>Статус:</strong> {flight.status_name || flight.id_status}</div>
            <div><strong>Аэропорт вылета:</strong> {flight.from_airport_code || flight.id_from}</div>
            <div><strong>Аэропорт прилёта:</strong> {flight.to_airport_code || flight.id_to}</div>
          </div>
        </div>
        <div className="card">
          <h3 style={{ marginBottom: 12, color: '#666', fontSize: 14, textTransform: 'uppercase' }}>Расписание</h3>
          <div style={{ display: 'grid', gap: 8 }}>
            <div><strong>Вылет:</strong> {new Date(flight.departure_datetime).toLocaleString('ru-RU')}</div>
            <div><strong>Прилёт:</strong> {new Date(flight.arrival_datetime).toLocaleString('ru-RU')}</div>
          </div>
        </div>
      </div>

      {/* Цены */}
      <div className="card">
        <h3 style={{ marginBottom: 12 }}>Цены на билеты</h3>
        {prices.length > 0 ? (
          <table className="table">
            <thead>
              <tr><th>Класс</th><th>Цена</th></tr>
            </thead>
            <tbody>
              {prices.map((p) => (
                <tr key={p.id}><td>{p.id_seat_class}</td><td>{p.price} ₽</td></tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p style={{ color: '#999' }}>Цены не установлены</p>
        )}
      </div>
    </div>
  );
}