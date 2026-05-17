import { useEffect, useState } from 'react';
import { ticketApi } from '../services/api';
import { useAuthStore } from '../store/authStore';
import { isAdmin } from '../utils/roles';
import { useApi } from '../hooks/useApi';
import { Loading, ErrorMessage, PageHeader, ConfirmDialog } from '../components/ui';
import { Navigate } from 'react-router-dom';
import type { Ticket, TicketStatistics } from '../types';

export function Tickets() {
  const user = useAuthStore((s) => s.user);
  const isAdminUser = isAdmin(user);
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [stats, setStats] = useState<TicketStatistics | null>(null);
  const listApi = useApi<Ticket[]>();
  const statsApi = useApi<TicketStatistics>();
  const deleteApi = useApi<any>();
  const [deleteId, setDeleteId] = useState<number | null>(null);

  useEffect(() => {
    if (!isAdminUser) return;
    loadData();
  }, [isAdminUser]);

  const loadData = () => {
    listApi.execute(ticketApi.getAll()).then((data) => {
      if (data) setTickets(data);
    });
    statsApi.execute(ticketApi.getStatistics()).then((data) => {
      if (data) setStats(data);
    });
  };

  if (!isAdminUser) return <Navigate to="/" replace />;
  if (listApi.loading) return <Loading />;
  if (listApi.error) return <ErrorMessage message={listApi.error} onRetry={loadData} />;

  return (
    <div>
      <PageHeader title="Все билеты" />

      {/* Статистика */}
      {stats && (
        <div className="card" style={{ marginBottom: 16, display: 'flex', gap: 24 }}>
          <div>
            <div style={{ fontSize: 24, fontWeight: 700 }}>{stats.total_tickets}</div>
            <div style={{ fontSize: 13, color: '#666' }}>Всего билетов</div>
          </div>
          {Object.entries(stats.by_status).map(([status, count]) => (
            <div key={status}>
              <div style={{ fontSize: 24, fontWeight: 700 }}>{count}</div>
              <div style={{ fontSize: 13, color: '#666' }}>{status}</div>
            </div>
          ))}
        </div>
      )}

      <ConfirmDialog
        isOpen={!!deleteId}
        title="Удалить билет?"
        message="Билет будет удалён безвозвратно."
        onConfirm={async () => {
          if (!deleteId) return;
          const result = await deleteApi.execute(ticketApi.delete(deleteId));
          if (result) { setDeleteId(null); loadData(); }
        }}
        onCancel={() => setDeleteId(null)}
      />

      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <table className="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Рейс</th>
              <th>Пассажир</th>
              <th>Место</th>
              <th>Цена</th>
              <th>Статус</th>
              <th>Дата покупки</th>
              <th></th>
            </tr>

          </thead>
          <tbody>
            {tickets.map((t) => (
              <tr key={t.id}>
                <td>{t.id}</td>
                <td>{t.flight_number || t.id_flight}</td>
                <td>{t.passenger_email || t.id_passenger}</td>
                <td>{t.seat_number}</td>
                <td>{t.price} ₽</td>
                <td>{t.status_name || t.id_status}</td>
                <td>{new Date(t.purchase_date).toLocaleDateString('ru-RU')}</td>
                <td>
                  <button onClick={() => setDeleteId(t.id)} className="btn btn-danger" style={{ padding: '4px 8px', fontSize: 12 }}>Удалить</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}