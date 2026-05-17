import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { flightApi } from '../services/api';
import { useApi } from '../hooks/useApi';
import { Loading, ErrorMessage, PageHeader } from '../components/ui';
import { FlightForm } from '../components/forms/FlightForm';
import type { Flight, FlightCreate } from '../types';

export function FlightEdit() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const flightId = Number(id);

  const [flight, setFlight] = useState<Flight | null>(null);
  const flightApiState = useApi<Flight>();
  const updateApi = useApi<any>();
  const [error, setError] = useState('');

  useEffect(() => {
    flightApiState.execute(flightApi.getById(flightId)).then((data) => {
      if (data) setFlight(data);
    });
  }, [flightId]);

  const handleSubmit = async (data: FlightCreate) => {
    setError('');
    const result = await updateApi.execute(flightApi.update(flightId, data));
    if (result) {
      navigate(`/flights/${flightId}`);
    } else {
      setError(updateApi.error || 'Ошибка при сохранении');
    }
  };

  if (flightApiState.loading) return <Loading />;
  if (flightApiState.error) return <ErrorMessage message={flightApiState.error} />;
  if (!flight) return <ErrorMessage message="Рейс не найден" />;

  return (
    <div>
      <PageHeader title={`Редактирование рейса ${flight.flight_number}`} action={<Link to={`/flights/${flightId}`} className="btn">Отмена</Link>} />

      {error && <ErrorMessage message={error} />}

      <FlightForm
        initialData={flight}
        onSubmit={handleSubmit}
        onCancel={() => navigate(`/flights/${flightId}`)}
        isLoading={updateApi.loading}
      />
    </div>
  );
}