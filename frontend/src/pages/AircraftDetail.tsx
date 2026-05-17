import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { aircraftApi } from '../services/api';
import { useApi } from '../hooks/useApi';
import { Loading, ErrorMessage, PageHeader } from '../components/ui';
import type { Aircraft, ModelAircraft, AircraftLease } from '../types';

export function AircraftDetail() {
  const { id } = useParams<{ id: string }>();
  const aircraftId = Number(id);

  const [aircraft, setAircraft] = useState<Aircraft | null>(null);
  const [model, setModel] = useState<ModelAircraft | null>(null);
  const [leases, setLeases] = useState<AircraftLease[]>([]);

  const aircraftApiState = useApi<Aircraft>();
  const leasesApi = useApi<AircraftLease[]>();

  useEffect(() => {
    aircraftApiState.execute(aircraftApi.getById(aircraftId)).then((data) => {
      if (data) {
        setAircraft(data);
        // Загружаем модель
        aircraftApi.getModels().then(({ data: models }) => {
          const m = models.find((mdl) => mdl.id === data.id_model);
          setModel(m || null);
        });
      }
    });
    leasesApi.execute(aircraftApi.getLeases()).then((data) => {
      if (data) {
        setLeases(data.filter((l) => l.id_aircraft === aircraftId));
      }
    });
  }, [aircraftId]);

  if (aircraftApiState.loading) return <Loading />;
  if (aircraftApiState.error) return <ErrorMessage message={aircraftApiState.error} />;
  if (!aircraft) return <ErrorMessage message="Самолёт не найден" />;

  return (
    <div>
      <PageHeader
        title={`Самолёт ${aircraft.registration_number}`}
        action={
          <Link to={`/aircraft/${aircraft.id}/edit`} className="btn btn-primary">
            Редактировать
          </Link>
        }
      />

      <div className="grid-2">
        <div className="card">
          <h3 style={{ marginBottom: 12, color: '#666', fontSize: 14, textTransform: 'uppercase' }}>Основная информация</h3>
          <div style={{ display: 'grid', gap: 8 }}>
            <div><strong>Бортовой номер:</strong> {aircraft.registration_number}</div>
            <div><strong>Модель:</strong> {model?.name || aircraft.id_model}</div>
            <div><strong>Производитель:</strong> {model?.manufacturer || '—'}</div>
            <div><strong>Год выпуска:</strong> {aircraft.manufacture_year || '—'}</div>
          </div>
        </div>

        <div className="card">
          <h3 style={{ marginBottom: 12, color: '#666', fontSize: 14, textTransform: 'uppercase' }}>Техобслуживание</h3>
          <div style={{ display: 'grid', gap: 8 }}>
            <div>
              <strong>Последнее ТО:</strong>{' '}
              {aircraft.last_maintenance
                ? new Date(aircraft.last_maintenance).toLocaleDateString('ru-RU')
                : 'Не проводилось'}
            </div>
          </div>
        </div>
      </div>

      {/* Аренда */}
      <div className="card" style={{ marginTop: 16 }}>
        <h3 style={{ marginBottom: 12 }}>История аренды</h3>
        {leases.length > 0 ? (
          <table className="table">
            <thead>
              <tr><th>Авиакомпания</th><th>Начало</th><th>Окончание</th><th>Статус</th></tr>
            </thead>
            <tbody>
              {leases.map((lease) => (
                <tr key={lease.id}>
                  <td>{lease.id_airline}</td>
                  <td>{new Date(lease.start_date).toLocaleDateString('ru-RU')}</td>
                  <td>{lease.end_date ? new Date(lease.end_date).toLocaleDateString('ru-RU') : 'Бессрочно'}</td>
                  <td>
                    <span className={`badge ${lease.end_date ? 'badge-gray' : 'badge-green'}`}>
                      {lease.end_date ? 'Завершена' : 'Активна'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p style={{ color: '#999' }}>Аренда не оформлялась</p>
        )}
      </div>
    </div>
  );
}