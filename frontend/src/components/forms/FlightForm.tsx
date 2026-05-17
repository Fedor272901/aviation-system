import { useEffect, useState } from 'react';
import { flightApi, aircraftApi } from '../../services/api';
import type { Flight, FlightCreate, Airport, Airline, FlightStatus, Aircraft } from '../../types';

interface FlightFormProps {
  initialData?: Flight;
  onSubmit: (data: FlightCreate) => Promise<void>;
  onCancel: () => void;
  isLoading?: boolean;
}

export function FlightForm({ initialData, onSubmit, onCancel, isLoading = false }: FlightFormProps) {
  const [formData, setFormData] = useState<FlightCreate>({
    flight_number: initialData?.flight_number || '',
    departure_datetime: initialData?.departure_datetime
      ? (() => {
          const d = new Date(initialData.departure_datetime);
          return isNaN(d.getTime()) ? '' : d.toISOString().slice(0, 16);
        })()
      : '',
    arrival_datetime: initialData?.arrival_datetime
      ? new Date(initialData.arrival_datetime).toISOString().slice(0, 16)
      : '',
    id_from: initialData?.id_from || 0,
    id_to: initialData?.id_to || 0,
    id_airline: initialData?.id_airline || 0,
    id_aircraft: initialData?.id_aircraft || 0,
    id_status: initialData?.id_status || 0,
  });

  const [airports, setAirports] = useState<Airport[]>([]);
  const [airlines, setAirlines] = useState<Airline[]>([]);
  const [statuses, setStatuses] = useState<FlightStatus[]>([]);
  const [aircraft, setAircraft] = useState<Aircraft[]>([]);
  const [loadingData, setLoadingData] = useState(true);
  const [loadError, setLoadError] = useState('');

  useEffect(() => {
    Promise.all([
      flightApi.getAirports(),
      flightApi.getAirlines(),
      flightApi.getFlightStatuses(),
      aircraftApi.getAll(0, 1000),
    ]).then(([airportsRes, airlinesRes, statusesRes, aircraftRes]) => {
      setAirports(airportsRes.data);
      setAirlines(airlinesRes.data);
      setStatuses(statusesRes.data);
      setAircraft(aircraftRes.data);
      setLoadingData(false);
    }).catch((err) => {
      setLoadError(err.response?.data?.detail || 'Не удалось загрузить справочники');
      setLoadingData(false);
    });
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  if (loadingData) {
    return <div className="card" style={{ padding: 40, textAlign: 'center' }}>Загрузка данных...</div>;
  }

  if (loadError) {
    return <div className="card" style={{ padding: 40, textAlign: 'center', color: '#c00' }}>⚠️ {loadError}</div>;
  }

  return (
    <form onSubmit={handleSubmit} className="card">
      <div className="grid-2">
        {/* Номер рейса */}
        <div className="form-group">
          <label>Номер рейса *</label>
          <input
            type="text"
            className="form-control"
            value={formData.flight_number}
            onChange={(e) => setFormData({ ...formData, flight_number: e.target.value })}
            placeholder="SU100"
            required
            maxLength={10}
          />
        </div>

        {/* Статус */}
        <div className="form-group">
          <label>Статус *</label>
          <select
            className="form-control"
            value={formData.id_status}
            onChange={(e) => setFormData({ ...formData, id_status: Number(e.target.value) })}
            required
          >
            <option value={0}>Выберите статус</option>
            {statuses.map((s) => (
              <option key={s.id} value={s.id}>{s.status_name}</option>
            ))}
          </select>
        </div>

        {/* Аэропорт вылета */}
        <div className="form-group">
          <label>Аэропорт вылета *</label>
          <select
            className="form-control"
            value={formData.id_from}
            onChange={(e) => setFormData({ ...formData, id_from: Number(e.target.value) })}
            required
          >
            <option value={0}>Выберите аэропорт</option>
            {airports.map((a) => (
              <option key={a.id} value={a.id}>{a.code} — {a.city}</option>
            ))}
          </select>
        </div>

        {/* Аэропорт прилёта */}
        <div className="form-group">
          <label>Аэропорт прилёта *</label>
          <select
            className="form-control"
            value={formData.id_to}
            onChange={(e) => setFormData({ ...formData, id_to: Number(e.target.value) })}
            required
          >
            <option value={0}>Выберите аэропорт</option>
            {airports.map((a) => (
              <option key={a.id} value={a.id}>{a.code} — {a.city}</option>
            ))}
          </select>
        </div>

        {/* Авиакомпания */}
        <div className="form-group">
          <label>Авиакомпания *</label>
          <select
            className="form-control"
            value={formData.id_airline}
            onChange={(e) => setFormData({ ...formData, id_airline: Number(e.target.value) })}
            required
          >
            <option value={0}>Выберите авиакомпанию</option>
            {airlines.map((al) => (
              <option key={al.id} value={al.id}>{al.name} ({al.code})</option>
            ))}
          </select>
        </div>

        {/* Самолёт */}
        <div className="form-group">
          <label>Самолёт *</label>
          <select
            className="form-control"
            value={formData.id_aircraft}
            onChange={(e) => setFormData({ ...formData, id_aircraft: Number(e.target.value) })}
            required
          >
            <option value={0}>Выберите самолёт</option>
            {aircraft.map((ac) => (
              <option key={ac.id} value={ac.id}>{ac.registration_number}</option>
            ))}
          </select>
        </div>

        {/* Дата вылета */}
        <div className="form-group">
          <label>Дата и время вылета *</label>
          <input
            type="datetime-local"
            className="form-control"
            value={formData.departure_datetime}
            onChange={(e) => setFormData({ ...formData, departure_datetime: e.target.value })}
            required
          />
        </div>

        {/* Дата прилёта */}
        <div className="form-group">
          <label>Дата и время прилёта *</label>
          <input
            type="datetime-local"
            className="form-control"
            value={formData.arrival_datetime}
            onChange={(e) => setFormData({ ...formData, arrival_datetime: e.target.value })}
            required
          />
        </div>
      </div>

      <div style={{ display: 'flex', gap: 12, justifyContent: 'flex-end', marginTop: 24 }}>
        <button type="button" onClick={onCancel} className="btn" style={{ background: '#f5f5f5' }}>
          Отмена
        </button>
        <button type="submit" className="btn btn-primary" disabled={isLoading}>
          {isLoading ? 'Сохранение...' : (initialData ? 'Сохранить' : 'Создать')}
        </button>
      </div>
    </form>
  );
}