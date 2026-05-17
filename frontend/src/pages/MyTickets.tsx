import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ticketApi } from '../services/api';
import { useAuthStore } from '../store/authStore';
import { useApi } from '../hooks/useApi';
import { Loading, ErrorMessage, PageHeader, ConfirmDialog } from '../components/ui';
import type { Ticket } from '../types';

export function MyTickets() {
  const user = useAuthStore((s) => s.user);
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const api = useApi<Ticket[]>();
  const cancelApi = useApi<Ticket>();
  const [cancelId, setCancelId] = useState<number | null>(null);

  useEffect(() => {
    if (!user) return;
    loadTickets();
  }, [user]);

  const loadTickets = () => {
    if (!user) return;
    api.execute(ticketApi.getByPassenger(user.id)).then((data) => {
      if (data) setTickets(data);
    });
  };

  const handleCancel = async () => {
    if (!cancelId) return;
    const result = await cancelApi.execute(ticketApi.cancel(cancelId));
    if (result) {
      setCancelId(null);
      loadTickets();
    }
  };

  if (!user) return <ErrorMessage message="Необходимо авторизоваться" />;
  if (api.loading) return <Loading />;
  if (api.error) return <ErrorMessage message={api.error} onRetry={loadTickets} />;

  return (
    <div>
      <PageHeader title="Мои билеты" />

      <ConfirmDialog
        isOpen={!!cancelId}
        title="Отменить билет?"
        message="Билет будет помечен как «Отменён». Вы уверены?"
        onConfirm={handleCancel}
        onCancel={() => setCancelId(null)}
      />

      {tickets.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: 40 }}>
          <p style={{ color: '#999', marginBottom: 16 }}>У вас пока нет билетов</p>
          <Link to="/flights" className="btn btn-primary">Найти рейс</Link>
        </div>
      ) : (
        <div style={{ display: 'grid', gap: 12 }}>
          {tickets.map((t) => (
            <div key={t.id} className="card" style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: 16, alignItems: 'center' }}>
              <div>
                <div style={{ fontSize: 18, fontWeight: 600, marginBottom: 4 }}>
                  Рейс {t.flight_number || t.id_flight}
                </div>
                <div style={{ color: '#666', fontSize: 14 }}>
                  Место: <strong>{t.seat_number}</strong> · Класс: {t.id_seat_class} · {t.price} ₽
                </div>
                <div style={{ marginTop: 4 }}>
                  <span style={{
                    padding: '2px 8px', borderRadius: 12, fontSize: 12, fontWeight: 600,
                    background: t.status_name === 'Отменён' ? '#fee' : '#e8f5e9',
                    color: t.status_name === 'Отменён' ? '#c00' : '#2e7d32',
                  }}>
                    {t.status_name || t.id_status}
                  </span>
                </div>
              </div>
              {t.status_name !== 'Отменён' && (
                <button onClick={() => setCancelId(t.id)} className="btn btn-danger" style={{ fontSize: 13 }}>
                  Отменить
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}