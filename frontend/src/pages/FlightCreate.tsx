import { useNavigate, Link } from 'react-router-dom';
import { useState } from 'react';
import { flightApi } from '../services/api';
import { useApi } from '../hooks/useApi';
import { PageHeader, ErrorMessage } from '../components/ui';
import { FlightForm } from '../components/forms/FlightForm';
import type { FlightCreate } from '../types';

export function FlightCreate() {
  const navigate = useNavigate();
  const createApi = useApi<any>();
  const [error, setError] = useState('');

  const handleSubmit = async (data: FlightCreate) => {
    setError('');
    const result = await createApi.execute(flightApi.create(data));
    if (result) {
      navigate('/flights');
    } else {
      setError(createApi.error || 'Ошибка при создании рейса');
    }
  };

  return (
    <div>
      <PageHeader title="Новый рейс" action={<Link to="/flights" className="btn">Отмена</Link>} />

      {error && <ErrorMessage message={error} />}

      <FlightForm onSubmit={handleSubmit} onCancel={() => navigate('/flights')} isLoading={createApi.loading} />
    </div>
  );
}