import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { aircraftApi } from '../services/api';
import { useApi } from '../hooks/useApi';
import { Loading, ErrorMessage, PageHeader, ConfirmDialog } from '../components/ui';
import type { Aircraft, ModelAircraft } from '../types';

export function AircraftList() {
  const [aircraft, setAircraft] = useState<Aircraft[]>([]);
  const [models, setModels] = useState<ModelAircraft[]>([]);
  const listApi = useApi<Aircraft[]>();
  const modelsApi = useApi<ModelAircraft[]>();
  const deleteApi = useApi<any>();
  const deleteModelApi = useApi<any>();
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [deleteModelId, setDeleteModelId] = useState<number | null>(null);
  const [showModels, setShowModels] = useState(false);
  const [newModelName, setNewModelName] = useState('');
  const [newModelManufacturer, setNewModelManufacturer] = useState('');
  const createModelApi = useApi<ModelAircraft>();

  const loadData = () => {
    listApi.execute(aircraftApi.getAll(0, 1000)).then((data) => {
      if (data) setAircraft(data);
    });
    modelsApi.execute(aircraftApi.getModels()).then((data) => {
      if (data) setModels(data);
    });
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleDelete = async () => {
    if (!deleteId) return;
    const result = await deleteApi.execute(aircraftApi.delete(deleteId));
    if (result) {
      setDeleteId(null);
      loadData();
    }
  };

  const handleDeleteModel = async () => {
    if (!deleteModelId) return;
    const result = await deleteModelApi.execute(aircraftApi.deleteModel(deleteModelId));
    if (result) {
      setDeleteModelId(null);
      loadData();
    }
  };

  const handleCreateModel = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newModelName.trim()) return;
    const result = await createModelApi.execute(
      aircraftApi.createModel({
        name: newModelName,
        manufacturer: newModelManufacturer || undefined,
        seats: [],
      })
    );
    if (result) {
      setNewModelName('');
      setNewModelManufacturer('');
      loadData();
    }
  };

  const getModelName = (modelId: number) => {
    const model = models.find((m) => m.id === modelId);
    return model?.name || modelId;
  };

  if (listApi.loading && aircraft.length === 0) return <Loading />;
  if (listApi.error) return <ErrorMessage message={listApi.error} onRetry={loadData} />;



  return (
    <div>
      <PageHeader
        title="Самолёты"
        action={
          <div style={{ display: 'flex', gap: 8 }}>
            <button
              onClick={() => setShowModels(!showModels)}
              className="btn"
              style={{ background: '#e3f2fd', color: '#1565c0' }}
            >
              {showModels ? 'Скрыть модели' : 'Модели самолётов'}
            </button>
            <Link to="/aircraft/new" className="btn btn-primary">
              + Добавить самолёт
            </Link>
          </div>
        }
      />

      <ConfirmDialog
        isOpen={!!deleteId}
        title="Удалить самолёт?"
        message="Убедитесь, что самолёт не используется в рейсах и аренде."
        onConfirm={handleDelete}
        onCancel={() => setDeleteId(null)}
      />

      <ConfirmDialog
        isOpen={!!deleteModelId}
        title="Удалить модель?"
        message="Модель можно удалить только если нет самолётов этой модели."
        onConfirm={handleDeleteModel}
        onCancel={() => setDeleteModelId(null)}
      />

      {/* Секция моделей */}
      {showModels && (
        <div className="card" style={{ marginBottom: 16 }}>
          <h3 style={{ marginBottom: 12 }}>Модели самолётов</h3>

          <form onSubmit={handleCreateModel} style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
            <input
              placeholder="Название модели (например, Boeing 737)"
              value={newModelName}
              onChange={(e) => setNewModelName(e.target.value)}
              style={{ flex: 1, padding: '8px 12px', borderRadius: 6, border: '1px solid #ddd' }}
              required
            />
            <input
              placeholder="Производитель"
              value={newModelManufacturer}
              onChange={(e) => setNewModelManufacturer(e.target.value)}
              style={{ width: 180, padding: '8px 12px', borderRadius: 6, border: '1px solid #ddd' }}
            />
            <button type="submit" className="btn btn-primary" disabled={createModelApi.loading}>
              {createModelApi.loading ? '...' : 'Добавить'}
            </button>
          </form>

          {models.length > 0 ? (
            <table className="table">
              <thead>
                <tr><th>ID</th><th>Название</th><th>Производитель</th><th></th></tr>
              </thead>
              <tbody>
                {models.map((m) => (
                  <tr key={m.id}>
                    <td>{m.id}</td>
                    <td>{m.name}</td>
                    <td>{m.manufacturer || '—'}</td>
                    <td>
                      <button
                        onClick={() => setDeleteModelId(m.id)}
                        className="btn btn-danger"
                        style={{ padding: '4px 12px', fontSize: 13 }}
                      >
                        Удалить
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p style={{ color: '#999' }}>Модели не добавлены. Создайте модель перед добавлением самолёта.</p>
          )}
        </div>
      )}

      {/* Список самолётов */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <table className="table">
          <thead>
            <tr>
              <th>Бортовой номер</th>
              <th>Модель</th>
              <th>Год выпуска</th>
              <th>Последнее ТО</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {aircraft.map((ac) => (
              <tr key={ac.id}>
                <td><strong>{ac.registration_number}</strong></td>
                <td>{getModelName(ac.id_model)}</td>
                <td>{ac.manufacture_year || '—'}</td>
                <td>{ac.last_maintenance ? new Date(ac.last_maintenance).toLocaleDateString('ru-RU') : '—'}</td>
                <td>
                  <div style={{ display: 'flex', gap: 8 }}>
                    <Link to={`/aircraft/${ac.id}`} className="btn" style={{ padding: '4px 12px', fontSize: 13, background: '#f5f5f5' }}>
                      Просмотр
                    </Link>
                    <Link to={`/aircraft/${ac.id}/edit`} className="btn" style={{ padding: '4px 12px', fontSize: 13, background: '#e3f2fd', color: '#1565c0' }}>
                      Редактировать
                    </Link>
                  </div>
                </td>
              </tr>
            ))}
            {aircraft.length === 0 && (
              <tr>
                <td colSpan={5} style={{ textAlign: 'center', color: '#999', padding: 40 }}>
                  Самолёты не добавлены
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}