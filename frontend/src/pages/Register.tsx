import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { extractErrorMessage } from '../utils/error';

export function Register() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    first_name: '',
    last_name: '',
    middle_name: '',
    phone: '',
    passport: '',
  });

  const [agreePD, setAgreePD] = useState(false); // ← состояние чекбокса
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const register = useAuthStore((state) => state.register);
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Пароли не совпадают');
      return;
    }

    if (formData.password.length < 8) {
      setError('Пароль должен быть не менее 8 символов');
      return;
    }

    // ← проверка согласия
    if (!agreePD) {
      setError('Необходимо согласие на обработку персональных данных');
      return;
    }

    setLoading(true);

    try {
      await register({
        email: formData.email,
        password: formData.password,
        first_name: formData.first_name,
        last_name: formData.last_name,
        middle_name: formData.middle_name || undefined,
        phone: formData.phone || undefined,
        passport: formData.passport,
      });
      navigate('/');
    } catch (err: any) {
      setError(extractErrorMessage(err, 'Ошибка регистрации'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container" style={{ maxWidth: 500, marginTop: 40 }}>
      <div className="card">
        <h1 style={{ marginBottom: 8, textAlign: 'center' }}>Регистрация</h1>
        <p style={{ color: '#666', marginBottom: 24, textAlign: 'center' }}>
          Создайте новый аккаунт
        </p>

        {error && (
          <div style={{ padding: 12, background: '#fee', color: '#c00', borderRadius: 6, marginBottom: 16 }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
            <div>
              <label style={{ display: 'block', marginBottom: 4, fontWeight: 500, fontSize: 14 }}>Имя *</label>
              <input
                type="text"
                name="first_name"
                value={formData.first_name}
                onChange={handleChange}
                required
                style={{ width: '100%', padding: '8px 12px', border: '1px solid #ddd', borderRadius: 6 }}
              />
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: 4, fontWeight: 500, fontSize: 14 }}>Фамилия *</label>
              <input
                type="text"
                name="last_name"
                value={formData.last_name}
                onChange={handleChange}
                required
                style={{ width: '100%', padding: '8px 12px', border: '1px solid #ddd', borderRadius: 6 }}
              />
            </div>
          </div>

          <div style={{ marginBottom: 16 }}>
            <label style={{ display: 'block', marginBottom: 4, fontWeight: 500, fontSize: 14 }}>Отчество</label>
            <input
              type="text"
              name="middle_name"
              value={formData.middle_name}
              onChange={handleChange}
              style={{ width: '100%', padding: '8px 12px', border: '1px solid #ddd', borderRadius: 6 }}
            />
          </div>

          <div style={{ marginBottom: 16 }}>
            <label style={{ display: 'block', marginBottom: 4, fontWeight: 500, fontSize: 14 }}>Email *</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              style={{ width: '100%', padding: '8px 12px', border: '1px solid #ddd', borderRadius: 6 }}
            />
          </div>

          <div style={{ marginBottom: 16 }}>
            <label style={{ display: 'block', marginBottom: 4, fontWeight: 500, fontSize: 14 }}>Телефон</label>
            <input
              type="tel"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              style={{ width: '100%', padding: '8px 12px', border: '1px solid #ddd', borderRadius: 6 }}
            />
          </div>

          <div style={{ marginBottom: 16 }}>
            <label style={{ display: 'block', marginBottom: 4, fontWeight: 500, fontSize: 14 }}>Паспорт *</label>
            <input
              type="text"
              name="passport"
              value={formData.passport}
              onChange={handleChange}
              required
              placeholder="1234 567890"
              style={{ width: '100%', padding: '8px 12px', border: '1px solid #ddd', borderRadius: 6 }}
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
            <div>
              <label style={{ display: 'block', marginBottom: 4, fontWeight: 500, fontSize: 14 }}>Пароль *</label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                style={{ width: '100%', padding: '8px 12px', border: '1px solid #ddd', borderRadius: 6 }}
              />
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: 4, fontWeight: 500, fontSize: 14 }}>Повторите пароль *</label>
              <input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
                style={{ width: '100%', padding: '8px 12px', border: '1px solid #ddd', borderRadius: 6 }}
              />
            </div>
          </div>

          {/* ← Чекбокс согласия на ПДн */}
          <div style={{ marginBottom: 24, display: 'flex', alignItems: 'flex-start', gap: 8 }}>
            <input
              type="checkbox"
              id="agree-pd"
              checked={agreePD}
              onChange={(e) => setAgreePD(e.target.checked)}
              style={{ marginTop: 3 }}
            />
            <label htmlFor="agree-pd" style={{ fontSize: 13, color: '#555', lineHeight: 1.4 }}>
              Я согласен на обработку персональных данных в соответствии с Федеральным законом №152-ФЗ
            </label>
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', justifyContent: 'center' }}
            disabled={loading}
          >
            {loading ? 'Регистрация...' : 'Зарегистрироваться'}
          </button>
        </form>

        <div style={{ marginTop: 24, textAlign: 'center', color: '#666' }}>
          Уже есть аккаунт?{' '}
          <Link to="/login" style={{ color: '#1976d2', textDecoration: 'underline' }}>
            Войти
          </Link>
        </div>
      </div>
    </div>
  );
}