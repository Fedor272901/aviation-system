import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { aircraftApi } from '../services/api';
import { useApi } from '../hooks/useApi';
import { Loading, ErrorMessage, PageHeader, ConfirmDialog } from '../components/ui';
import type { Aircraft, ModelAircraft, ModelSeat, SeatClass } from '../types';

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
    // --- Распределение мест при создании модели ---
  const [newModelSeats, setNewModelSeats] = useState<{ class_id: number; count: number }[]>([]);

  // --- Редактирование мест существующей модели ---
  const [editingModelId, setEditingModelId] = useState<number | null>(null);
  const [modelSeats, setModelSeats] = useState<ModelSeat[]>([]);
  const [seatClasses, setSeatClasses] = useState<SeatClass[]>([]);
  const [newSeatClassId, setNewSeatClassId] = useState(0);
  const [newSeatCount, setNewSeatCount] = useState<number | ''>('');
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
    aircraftApi.getSeatClasses().then(({ data }) => setSeatClasses(data));
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

  const openModelSeats = async (modelId: number) => {
    setEditingModelId(modelId);
    try {
      const { data } = await aircraftApi.getModelSeats(modelId);
      setModelSeats(data);
    } catch (err: any) {
      setModelSeats([]);
      alert(err.response?.data?.detail || 'Не удалось загрузить места');
    }
  };

  const handleAddModelSeat = async () => {
    if (!editingModelId || !newSeatClassId || !newSeatCount) return;
    try {
      await aircraftApi.createModelSeat({
        id_model: editingModelId,
        id_seat_class: newSeatClassId,
        seat_count: Number(newSeatCount),
      });
      setNewSeatClassId(0);
      setNewSeatCount('');
      openModelSeats(editingModelId);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка при добавлении мест');
    }
  };

  const handleCreateModel = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newModelName.trim()) return;

    const result = await createModelApi.execute(
      aircraftApi.createModel({
        name: newModelName,
        manufacturer: newModelManufacturer || undefined,
        seats: newModelSeats.filter((s) => s.class_id > 0 && s.count > 0),
      })
    );

    if (result) {
      setNewModelName('');
      setNewModelManufacturer('');
      setNewModelSeats([]);
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

          <form onSubmit={handleCreateModel}>
            <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
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
            </div>

            {/* Блок распределения мест — теперь под инпутами, а не внутри flex-строки */}
            <div style={{ marginBottom: 16 }}>
              <strong>Распределение мест по классам:</strong>
              {newModelSeats.map((s, idx) => (
                <div key={idx} style={{ display: 'flex', gap: 8, marginTop: 8, alignItems: 'center' }}>
                  <select
                    value={s.class_id}
                    onChange={(e) => {
                      const arr = [...newModelSeats];
                      arr[idx].class_id = Number(e.target.value);
                      setNewModelSeats(arr);
                    }}
                    style={{ padding: '8px 12px', borderRadius: 6, border: '1px solid #ddd', flex: 1 }}
                  >
                    <option value={0}>Выберите класс</option>
                    {seatClasses.map((c) => (
                      <option key={c.id} value={c.id}>{c.class_name}</option>
                    ))}
                  </select>
                  <input
                    type="number"
                    placeholder="Количество"
                    value={s.count || ''}
                    onChange={(e) => {
                      const arr = [...newModelSeats];
                      arr[idx].count = Number(e.target.value);
                      setNewModelSeats(arr);
                    }}
                    min={1}
                    style={{ width: 120, padding: '8px 12px', borderRadius: 6, border: '1px solid #ddd' }}
                  />
                  <button
                    type="button"
                    onClick={() => setNewModelSeats(newModelSeats.filter((_, i) => i !== idx))}
                    className="btn btn-danger"
                    style={{ padding: '4px 12px' }}
                  >
                    ✕
                  </button>
                </div>
              ))}
              <button
                type="button"
                onClick={() => setNewModelSeats([...newModelSeats, { class_id: 0, count: 0 }])}
                className="btn"
                style={{ marginTop: 8, background: '#e3f2fd', color: '#1565c0' }}
              >
                + Добавить класс
              </button>
            </div>
          </form>

          {models.length > 0 ? (
            <>
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
                        onClick={() => openModelSeats(m.id)}
                        className="btn"
                        style={{ padding: '4px 12px', fontSize: 13, background: '#e8f5e9', color: '#2e7d32' }}
                      >
                        Места
                      </button>
                      <button
                        onClick={() => setDeleteModelId(m.id)}
                        className="btn btn-danger"
                        style={{ padding: '4px 12px', fontSize: 13, marginLeft: 8 }}
                      >
                        Удалить
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {/* ===== РЕДАКТОР МЕСТ ДЛЯ ВЫБРАННОЙ МОДЕЛИ ===== */}
            {editingModelId && (
              <div className="card" style={{ marginTop: 16, background: '#fafafa' }}>
                <h4 style={{ marginBottom: 12 }}>Распределение мест — модель #{editingModelId}</h4>

                {modelSeats.length > 0 ? (
                  <table className="table">
                    <thead>
                      <tr><th>Класс</th><th>Количество мест</th><th></th></tr>
                    </thead>
                    <tbody>
                      {modelSeats.map((ms) => (
                        <tr key={ms.id}>
                          <td>{seatClasses.find((c) => c.id === ms.id_seat_class)?.class_name || ms.id_seat_class}</td>
                          <td>
                            <input
                              type="number"
                              defaultValue={ms.seat_count}
                              onBlur={async (e) => {
                                const newCount = Number(e.target.value);
                                if (newCount > 0 && newCount !== ms.seat_count) {
                                  await aircraftApi.updateModelSeat(ms.id, newCount);
                                  openModelSeats(editingModelId);
                                }
                              }}
                              min={1}
                              style={{ width: 80, padding: '4px 8px', borderRadius: 4, border: '1px solid #ddd' }}
                            />
                          </td>
                          <td>
                            <button
                              onClick={async () => {
                                await aircraftApi.deleteModelSeat(ms.id);
                                openModelSeats(editingModelId);
                              }}
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
                  <p style={{ color: '#999' }}>Места не настроены</p>
                )}

                <div style={{ display: 'flex', gap: 8, marginTop: 12, alignItems: 'center', flexWrap: 'wrap' }}>
                  <select
                    value={newSeatClassId}
                    onChange={(e) => setNewSeatClassId(Number(e.target.value))}
                    style={{ padding: '8px 12px', borderRadius: 6, border: '1px solid #ddd' }}
                  >
                    <option value={0}>Выберите класс</option>
                    {seatClasses
                      .filter((sc) => !modelSeats.some((ms) => ms.id_seat_class === sc.id))
                      .map((c) => (
                        <option key={c.id} value={c.id}>{c.class_name}</option>
                      ))}
                  </select>
                  <input
                    type="number"
                    placeholder="Кол-во"
                    value={newSeatCount}
                    onChange={(e) => setNewSeatCount(e.target.value ? Number(e.target.value) : '')}
                    min={1}
                    style={{ width: 100, padding: '8px 12px', borderRadius: 6, border: '1px solid #ddd' }}
                  />
                  <button onClick={handleAddModelSeat} className="btn btn-primary">Добавить</button>
                  <button onClick={() => setEditingModelId(null)} className="btn" style={{ background: '#f5f5f5' }}>Закрыть</button>
                </div>
              </div>
            )}
              {/* ===== КОНЕЦ РЕДАКТОРА ===== */}
            </>
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