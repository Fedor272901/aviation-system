import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { aircraftApi } from '../services/api';
import { useApi } from '../hooks/useApi';
import { PageHeader, ErrorMessage } from '../components/ui';
import type { Aircraft } from '../types';

export function AircraftCreate() {
  const navigate = useNavigate();
  const createApi = useApi<Aircraft>();
  const [error, setError] = useState('');

  const [formData, setFormData] = useState<Omit<Aircraft, 'id'>>({
    registration_number: '',
    id_model: 0,
    manufacture_year: undefined,
    last_maintenance: undefined,
  });

  const [models, setModels] = useState<any[]>([]);
  const [loadingModels, setLoadingModels] = useState(true);

  // Загружаем модели самолётов
  useEffect(() => {
    aircraftApi.getModels().then(({ data }) => {
      setModels(data);
      setLoadingModels(false);
    });
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    const result = await createApi.execute(aircraftApi.create(formData as any));
    if (result) {
      navigate('/aircraft');
    } else {
      setError(createApi.error || 'Ошибка при создании');
    }
  };

  if (loadingModels) return <div className="card">Загрузка...</div>;

  return (
    <div>
      <PageHeader title="Новый самолёт" action={<Link to="/aircraft" className="btn">Отмена</Link>} />

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
              placeholder="RA-12345"
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
              placeholder="2020"
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

        {models.length === 0 && (
          <div style={{ color: '#c00', marginBottom: 12, fontSize: 14 }}>
            ⚠️ Нет моделей самолётов.{' '}
            <Link to="/aircraft" style={{ textDecoration: 'underline' }}>
              Перейдите к списку самолётов и создайте модель.
            </Link>
          </div>
        )}

        <div style={{ display: 'flex', gap: 12, justifyContent: 'flex-end', marginTop: 24 }}>
          <Link to="/aircraft" className="btn" style={{ background: '#f5f5f5' }}>Отмена</Link>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={createApi.loading || models.length === 0}
          >
            {createApi.loading ? 'Создание...' : 'Создать'}
          </button>
        </div>

        
      </form>
    </div>
  );
}