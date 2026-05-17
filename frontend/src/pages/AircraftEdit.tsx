import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { aircraftApi } from '../services/api';
import { useApi } from '../hooks/useApi';
import { Loading, ErrorMessage, PageHeader } from '../components/ui';
import type { Aircraft } from '../types';

export function AircraftEdit() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const aircraftId = Number(id);

  const [models, setModels] = useState<any[]>([]);
  const aircraftApiState = useApi<Aircraft>();
  const updateApi = useApi<Aircraft>();
  const [error, setError] = useState('');

  const [formData, setFormData] = useState<Omit<Aircraft, 'id'>>({
    registration_number: '',
    id_model: 0,
    manufacture_year: undefined,
    last_maintenance: undefined,
  });

  useEffect(() => {
    aircraftApiState.execute(aircraftApi.getById(aircraftId)).then((data) => {
      if (data) {
        setFormData({
          registration_number: data.registration_number,
          id_model: data.id_model,
          manufacture_year: data.manufacture_year,
          last_maintenance: data.last_maintenance || undefined,
        });
      }
    });

    aircraftApi.getModels().then(({ data }) => setModels(data));
  }, [aircraftId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    const result = await updateApi.execute(aircraftApi.update(aircraftId, formData as any));
    if (result) {
      navigate(`/aircraft/${aircraftId}`);
    } else {
      setError(updateApi.error || 'Ошибка при сохранении');
    }
  };

  if (aircraftApiState.loading) return <Loading />;
  if (aircraftApiState.error) return <ErrorMessage message={aircraftApiState.error} />;

  return (
    <div>
      <PageHeader title="Редактирование самолёта" action={<Link to={`/aircraft/${aircraftId}`} className="btn">Отмена</Link>} />

      {error && <ErrorMessage message={error} />}

      <form onSubmit={handleSubmit} className="card">
        <div className="grid-2">
          <div className="form-group">
            <label>Бортовой номер *</label>
            <input
              type="text"
              className="form-control"
              value={formData.registration_number}
              onChange={(e) => setFormData({ ...formData, registration_number: e.target.value })}
              required
              maxLength={10}
            />
          </div>

          <div className="form-group">
            <label>Модель *</label>
            <select
              className="form-control"
              value={formData.id_model}
              onChange={(e) => setFormData({ ...formData, id_model: Number(e.target.value) })}
              required
            >
              <option value={0}>Выберите модель</option>
              {models.map((m) => (
                <option key={m.id} value={m.id}>{m.name}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Год выпуска</label>
            <input
              type="number"
              className="form-control"
              value={formData.manufacture_year || ''}
              onChange={(e) => setFormData({ ...formData, manufacture_year: e.target.value ? Number(e.target.value) : undefined })}
              min={1950}
              max={2030}
            />
          </div>

          <div className="form-group">
            <label>Дата последнего ТО</label>
            <input
              type="date"
              className="form-control"
              value={formData.last_maintenance || ''}
              onChange={(e) => setFormData({ ...formData, last_maintenance: e.target.value || undefined })}
            />
          </div>
        </div>

        <div style={{ display: 'flex', gap: 12, justifyContent: 'flex-end', marginTop: 24 }}>
          <Link to={`/aircraft/${aircraftId}`} className="btn" style={{ background: '#f5f5f5' }}>Отмена</Link>
          <button type="submit" className="btn btn-primary" disabled={updateApi.loading}>
            {updateApi.loading ? 'Сохранение...' : 'Сохранить'}
          </button>
        </div>
      </form>
    </div>
  );
}