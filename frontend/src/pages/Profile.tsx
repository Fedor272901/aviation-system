import { useState, useEffect } from 'react';
import { useAuthStore } from '../store/authStore';
import { personApi } from '../services/api';
import { useApi } from '../hooks/useApi';
import { Loading, ErrorMessage, PageHeader } from '../components/ui';
import type { PersonUpdate, PasswordChangeData } from '../types';

export function Profile() {
  const user = useAuthStore((s) => s.user);
  const checkAuth = useAuthStore((s) => s.checkAuth);
  const updateApi = useApi<any>();
  const passwordApi = useApi<any>();

  const [form, setForm] = useState<PersonUpdate>({
    first_name: '',
    last_name: '',
    middle_name: '',
    phone: '',
    passport: '',
    email: '',
  });

  useEffect(() => {
    if (user) {
      setForm({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        middle_name: user.middle_name || '',
        phone: user.phone || '',
        passport: user.passport || '',
        email: user.email || '',
      });
    }
  }, [user]);

  const [passwordForm, setPasswordForm] = useState<PasswordChangeData>({
    old_password: '',
    new_password: '',
  });

  const [showPasswordForm, setShowPasswordForm] = useState(false);

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;
    const result = await updateApi.execute(personApi.update(user.id, form));
    if (result) {
      checkAuth(); // Обновляем данные в store (теперь /auth/me отдаёт полные данные)
      alert('Профиль обновлён');
    }
  };

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;
    const result = await passwordApi.execute(personApi.changePassword(user.id, passwordForm));
    if (result) {
      setPasswordForm({ old_password: '', new_password: '' });
      setShowPasswordForm(false);
      alert('Пароль изменён');
    }
  };

  if (!user) return <ErrorMessage message="Необходимо авторизоваться" />;

  return (
    <div>
      <PageHeader title="Личный кабинет" />

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        {/* Редактирование профиля */}
        <div className="card">
          <h3 style={{ marginBottom: 16 }}>Редактировать профиль</h3>
          {updateApi.error && <ErrorMessage message={updateApi.error} />}
          <form onSubmit={handleUpdate} style={{ display: 'grid', gap: 12 }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <div>
                <label style={{ fontSize: 13, color: '#666' }}>Фамилия</label>
                <input value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} style={{ width: '100%', padding: 8, borderRadius: 6, border: '1px solid #ddd' }} />
              </div>
              <div>
                <label style={{ fontSize: 13, color: '#666' }}>Имя</label>
                <input value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} style={{ width: '100%', padding: 8, borderRadius: 6, border: '1px solid #ddd' }} />
              </div>
            </div>
            <div>
              <label style={{ fontSize: 13, color: '#666' }}>Отчество</label>
              <input value={form.middle_name} onChange={(e) => setForm({ ...form, middle_name: e.target.value })} style={{ width: '100%', padding: 8, borderRadius: 6, border: '1px solid #ddd' }} />
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <div>
                <label style={{ fontSize: 13, color: '#666' }}>Телефон</label>
                <input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} style={{ width: '100%', padding: 8, borderRadius: 6, border: '1px solid #ddd' }} />
              </div>
              <div>
                <label style={{ fontSize: 13, color: '#666' }}>Паспорт</label>
                <input value={form.passport} onChange={(e) => setForm({ ...form, passport: e.target.value })} style={{ width: '100%', padding: 8, borderRadius: 6, border: '1px solid #ddd' }} />
              </div>
            </div>
            <div>
              <label style={{ fontSize: 13, color: '#666' }}>Email</label>
              <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} style={{ width: '100%', padding: 8, borderRadius: 6, border: '1px solid #ddd' }} />
            </div>
            <button type="submit" className="btn btn-primary" disabled={updateApi.loading}>
              {updateApi.loading ? 'Сохранение...' : 'Сохранить'}
            </button>
          </form>
        </div>

        {/* Смена пароля */}
        <div className="card">
          <h3 style={{ marginBottom: 16 }}>Безопасность</h3>
          {!showPasswordForm ? (
            <button onClick={() => setShowPasswordForm(true)} className="btn" style={{ background: '#f5f5f5' }}>
              🔒 Сменить пароль
            </button>
          ) : (
            <form onSubmit={handlePasswordChange} style={{ display: 'grid', gap: 12 }}>
              {passwordApi.error && <ErrorMessage message={passwordApi.error} />}
              <div>
                <label style={{ fontSize: 13, color: '#666' }}>Текущий пароль</label>
                <input type="password" value={passwordForm.old_password} onChange={(e) => setPasswordForm({ ...passwordForm, old_password: e.target.value })} required style={{ width: '100%', padding: 8, borderRadius: 6, border: '1px solid #ddd' }} />
              </div>
              <div>
                <label style={{ fontSize: 13, color: '#666' }}>Новый пароль</label>
                <input type="password" value={passwordForm.new_password} onChange={(e) => setPasswordForm({ ...passwordForm, new_password: e.target.value })} required style={{ width: '100%', padding: 8, borderRadius: 6, border: '1px solid #ddd' }} />
              </div>
              <div style={{ display: 'flex', gap: 8 }}>
                <button type="submit" className="btn btn-primary" disabled={passwordApi.loading}>Сменить</button>
                <button type="button" onClick={() => setShowPasswordForm(false)} className="btn" style={{ background: '#f5f5f5' }}>Отмена</button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}