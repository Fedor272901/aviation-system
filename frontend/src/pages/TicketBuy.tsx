import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { flightApi, ticketApi, aircraftApi } from '../services/api';
import { useAuthStore } from '../store/authStore';
import { useApi } from '../hooks/useApi';
import { Loading, ErrorMessage, PageHeader } from '../components/ui';

export function TicketBuy() {
  const [searchParams] = useSearchParams();
  const flightId = Number(searchParams.get('flight'));
  const navigate = useNavigate();
  const user = useAuthStore((s) => s.user);

  const [flight, setFlight] = useState<any>(null);
  const [prices, setPrices] = useState<any[]>([]);
  const [seatClasses, setSeatClasses] = useState<any[]>([]);
  const [availableSeats, setAvailableSeats] = useState<string[]>([]);

  const [selectedClass, setSelectedClass] = useState<number>(0);
  const [selectedSeat, setSelectedSeat] = useState('');

  const flightApiState = useApi<any>();
  const pricesApi = useApi<any[]>();
  const classesApi = useApi<any[]>();
  const seatsApi = useApi<string[]>();
  const buyApi = useApi<any>();

  useEffect(() => {
    if (!flightId) return;
    flightApiState.execute(flightApi.getById(flightId)).then((d) => { if (d) setFlight(d); });
    pricesApi.execute(flightApi.getPrices(flightId)).then((d) => { if (d) setPrices(d); });
    classesApi.execute(aircraftApi.getSeatClasses()).then((d) => { if (d) setSeatClasses(d); });
  }, [flightId]);

  useEffect(() => {
    if (!flightId || !selectedClass) return;
    setSelectedSeat('');
    seatsApi.execute(ticketApi.getAvailableSeats(flightId, selectedClass)).then((d) => {
      if (d) setAvailableSeats(d);
    });
  }, [flightId, selectedClass]);

  const handleBuy = async () => {
    if (!user || !selectedSeat || !selectedClass) return;
    const price = prices.find((p) => p.id_seat_class === selectedClass)?.price || '0';
    const result = await buyApi.execute(ticketApi.create({
      seat_number: selectedSeat,
      id_seat_class: selectedClass,
      price,
      id_status: 1,
      id_flight: flightId,
      id_passenger: user.id,
    }));
    if (result) navigate('/tickets/my');
  };

  if (!user) return <ErrorMessage message="Необходимо авторизоваться" />;
  if (flightApiState.loading) return <Loading />;
  if (!flight) return <ErrorMessage message="Рейс не найден" />;

  return (
    <div>
      <PageHeader title={`Покупка билета: рейс ${flight.flight_number}`} />

      <div className="card">
        <h3 style={{ marginBottom: 12 }}>Выберите класс обслуживания</h3>
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
          {prices.map((p) => (
            <button
              key={p.id}
              onClick={() => setSelectedClass(p.id_seat_class)}
              className="btn"
              style={{
                background: selectedClass === p.id_seat_class ? '#1976d2' : '#f5f5f5',
                color: selectedClass === p.id_seat_class ? '#fff' : '#333',
              }}
            >
              {seatClasses.find((c) => c.id === p.id_seat_class)?.class_name || p.id_seat_class} — {p.price} ₽
            </button>
          ))}
          {prices.length === 0 && <p style={{ color: '#999' }}>Цены не установлены</p>}
        </div>
      </div>

      {selectedClass > 0 && (
        <div className="card">
          <h3 style={{ marginBottom: 12 }}>Выберите место</h3>
          {seatsApi.loading && <Loading text="Загрузка мест..." />}
          {seatsApi.error && <ErrorMessage message={seatsApi.error} />}
          {!seatsApi.loading && !seatsApi.error && (
            <>
              {availableSeats.length > 0 ? (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 8 }}>
                  {availableSeats.map((seat) => (
                    <button
                      key={seat}
                      onClick={() => setSelectedSeat(seat)}
                      className="btn"
                      style={{
                        padding: '8px 4px',
                        background: selectedSeat === seat ? '#1976d2' : '#f5f5f5',
                        color: selectedSeat === seat ? '#fff' : '#333',
                      }}
                    >
                      {seat}
                    </button>
                  ))}
                </div>
              ) : (
                <p style={{ color: '#999' }}>Нет свободных мест в этом классе</p>
              )}
            </>
          )}
        </div>
      )}

      {selectedSeat && (
        <div className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
          <div>
            <strong>Выбрано:</strong> рейс {flight.flight_number}, место {selectedSeat},{' '}
            {seatClasses.find((c) => c.id === selectedClass)?.class_name}
          </div>
          <button onClick={handleBuy} className="btn btn-primary" disabled={buyApi.loading}>
            {buyApi.loading ? 'Оформление...' : 'Купить билет'}
          </button>
        </div>
      )}
    </div>
  );
}