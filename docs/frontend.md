# Frontend

## Стек

- React 18 + TypeScript
- Vite (сборка)
- React Router v6 (роутинг)
- Zustand (глобальный стейт)
- Axios (HTTP-клиент)

## Структура проекта

```
frontend/src/
├── components/
│   ├── ui/              # Переиспользуемые компоненты
│   │   ├── Loading.tsx
│   │   ├── ErrorMessage.tsx
│   │   ├── ConfirmDialog.tsx
│   │   └── PageHeader.tsx
│   ├── forms/           # Формы
│   │   ├── FlightForm.tsx
│   │   └── AircraftForm.tsx
│   └── Layout.tsx       # Шаблон страницы с навигацией
├── pages/               # Страницы приложения
│   ├── Home.tsx
│   ├── Flights.tsx
│   ├── FlightDetail.tsx
│   ├── FlightCreate.tsx
│   ├── Login.tsx
│   ├── Register.tsx
│   ├── Profile.tsx
│   ├── MyTickets.tsx
│   ├── TicketBuy.tsx
│   ├── Persons.tsx
│   ├── FlightStatuses.tsx
│   └── ...
├── store/
│   └── authStore.ts     # Zustand: токен, пользователь, роли
├── services/
│   └── api.ts           # Axios instance + API методы
├── hooks/
│   └── useApi.ts        # Хук для загрузки данных с состоянием
├── types/               # TypeScript интерфейсы
└── utils/
    ├── error.ts         # extractErrorMessage — обработка 422
    └── roles.ts         # isAdmin, isStaff — проверка ролей
```

## Роутинг

| Путь | Страница | Кто видит |
|------|----------|-----------|
| `/` | Home | Все |
| `/flights` | Список рейсов | Все |
| `/flights/:id` | Детали рейса | Все |
| `/login` | Вход | Только гости |
| `/register` | Регистрация | Только гости |
| `/profile` | Профиль | Авторизованные |
| `/tickets/my` | Мои билеты | Авторизованные |
| `/tickets/buy` | Покупка билета | Авторизованные |
| `/flights/new` | Создать рейс | admin |
| `/flight-statuses` | Статусы рейсов | admin |
| `/persons` | Пользователи | admin |

## Обработка ошибок

Все API-ошибки проходят через `extractErrorMessage()`:

```ts
import { extractErrorMessage } from '../utils/error';

// Pydantic 422: { detail: [{ msg: "..." }] } → строка
setError(extractErrorMessage(err, 'Ошибка по умолчанию'));
```

На уровне приложения установлен `ErrorBoundary` — при краше React покажет понятное сообщение вместо белого экрана.