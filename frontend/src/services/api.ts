import axios from 'axios';
import type {
  Person,
  PersonCreate,
  PersonUpdate,
  Airport,
  Airline,
  FlightStatus,
  Flight,
  FlightCreate,
  FlightUpdate,
  FlightSearch,
  FlightPrice,
  SeatClass,
  ModelAircraft,
  Aircraft,
  AircraftLease,
  FlightRole,
  Crew,
  CrewAssignment,
  Ticket,
  TicketCreate,
  TicketUpdate,
  TicketSearch,
  TicketStatus,
  TicketStatistics,
  AuthUser,
  RegisterData,
  PasswordChangeData,
  TokenResponse, // ← добавлен
  DeleteResponse,
} from '../types';

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

// Интерцептор токена
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.set('Authorization', `Bearer ${token}`);
  }
  return config;
});

// Интерцептор 401 → редирект на логин
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const isAuthEndpoint =
      error.config?.url?.includes('/auth/login') || error.config?.url?.includes('/auth/register');
    if (error.response?.status === 401 && !isAuthEndpoint) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;

// =========================================================
// AUTH
// =========================================================

export const authApi = {
  login: (email: string, password: string) =>
    api.post<TokenResponse>('/auth/login', { email, password }),

  register: (data: RegisterData) => api.post<AuthUser>('/auth/register', data),

  me: () => api.get<AuthUser>('/auth/me'),

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },
};

// =========================================================
// PERSONS
// =========================================================

export const personApi = {
  getAll: (skip = 0, limit = 100) => api.get<Person[]>(`/persons/?skip=${skip}&limit=${limit}`),

  getById: (id: number) => api.get<Person>(`/persons/${id}`),

  create: (data: PersonCreate) => api.post<Person>('/persons/', data),

  update: (id: number, data: PersonUpdate) => api.put<Person>(`/persons/${id}`, data),

  changePassword: (id: number, data: PasswordChangeData) =>
    api.put<Person>(`/persons/${id}/password`, data),

  delete: (id: number) => api.delete<DeleteResponse>(`/persons/${id}`),
};

// =========================================================
// FLIGHTS
// =========================================================

export const flightApi = {
  // Airports
  getAirports: () => api.get<Airport[]>('/flights/airports/'),
  getAirport: (id: number) => api.get<Airport>(`/flights/airports/${id}`),
  createAirport: (data: Omit<Airport, 'id'>) => api.post<Airport>('/flights/airports/', data),
  updateAirport: (id: number, data: Omit<Airport, 'id'>) =>
    api.put<Airport>(`/flights/airports/${id}`, data),
  deleteAirport: (id: number) => api.delete<DeleteResponse>(`/flights/airports/${id}`),

  // Airlines
  getAirlines: () => api.get<Airline[]>('/flights/airlines/'),
  createAirline: (data: Omit<Airline, 'id'>) => api.post<Airline>('/flights/airlines/', data),
  deleteAirline: (id: number) => api.delete<DeleteResponse>(`/flights/airlines/${id}`),

  // Flight statuses
  getFlightStatuses: () => api.get<FlightStatus[]>('/flights/statuses/'),
  createFlightStatus: (data: { status_name: string }) =>
    api.post<FlightStatus>('/flights/statuses/', data),
  deleteFlightStatus: (id: number) => api.delete<DeleteResponse>(`/flights/statuses/${id}`),

  // Flights
  getAll: (skip = 0, limit = 100) => api.get<Flight[]>(`/flights/?skip=${skip}&limit=${limit}`),
  getUpcoming: (skip = 0, limit = 100) =>
    api.get<Flight[]>(`/flights/upcoming/?skip=${skip}&limit=${limit}`),
  getById: (id: number) => api.get<Flight>(`/flights/${id}`),
  create: (data: FlightCreate) => api.post<Flight>('/flights/', data),
  update: (id: number, data: FlightUpdate) => api.put<Flight>(`/flights/${id}`, data),
  delete: (id: number) => api.delete<DeleteResponse>(`/flights/${id}`),
  search: (criteria: FlightSearch) => api.post<Flight[]>('/flights/search/', criteria),
  getFromAirport: (airportId: number) => api.get<Flight[]>(`/flights/from-airport/${airportId}`),
  getToAirport: (airportId: number) => api.get<Flight[]>(`/flights/to-airport/${airportId}`),

  // Flight prices
  getPrices: (flightId: number) => api.get<FlightPrice[]>(`/flights/${flightId}/prices/`),
  createPrice: (data: Omit<FlightPrice, 'id'>) => api.post<FlightPrice>('/flights/prices/', data),
  updatePrice: (priceId: number, newPrice: number) =>
    api.put<FlightPrice>(`/flights/prices/${priceId}?new_price=${newPrice}`, {}),
  deletePrice: (priceId: number) => api.delete<DeleteResponse>(`/flights/prices/${priceId}`),
};

// =========================================================
// AIRCRAFT
// =========================================================

export const aircraftApi = {
  // Seat classes
  getSeatClasses: () => api.get<SeatClass[]>('/aircraft/seat-classes/'),
  createSeatClass: (data: Omit<SeatClass, 'id'>) =>
    api.post<SeatClass>('/aircraft/seat-classes/', data),
  updateSeatClass: (id: number, data: Omit<SeatClass, 'id'>) =>
    api.put<SeatClass>(`/aircraft/seat-classes/${id}`, data),
  deleteSeatClass: (id: number) => api.delete<DeleteResponse>(`/aircraft/seat-classes/${id}`),

  // Models
  getModels: () => api.get<ModelAircraft[]>('/aircraft/models/'),
  createModel: (data: {
    name: string;
    manufacturer?: string;
    seats: { class_id: number; count: number }[];
  }) => api.post<ModelAircraft>('/aircraft/models/', data),
  deleteModel: (id: number) => api.delete<DeleteResponse>(`/aircraft/models/${id}`),

  // Aircraft
  getAll: (skip = 0, limit = 100) => api.get<Aircraft[]>(`/aircraft/?skip=${skip}&limit=${limit}`),
  getById: (id: number) => api.get<Aircraft>(`/aircraft/${id}`),
  create: (data: Omit<Aircraft, 'id'>) => api.post<Aircraft>('/aircraft/', data),
  update: (id: number, data: Partial<Omit<Aircraft, 'id'>>) =>
    api.put<Aircraft>(`/aircraft/${id}`, data),
  delete: (id: number) => api.delete<DeleteResponse>(`/aircraft/${id}`),

  // Leases
  getLeases: () => api.get<AircraftLease[]>('/aircraft/leases/'),
  createLease: (data: Omit<AircraftLease, 'id'>) =>
    api.post<AircraftLease>('/aircraft/leases/', data),
  updateLease: (id: number, endDate: string) =>
    api.put<AircraftLease>(`/aircraft/leases/${id}?end_date=${endDate}`, {}),
  deleteLease: (id: number) => api.delete<DeleteResponse>(`/aircraft/leases/${id}`),
};

// =========================================================
// CREW
// =========================================================

export const crewApi = {
  // Flight roles
  getRoles: () => api.get<FlightRole[]>('/crew/roles/'),
  createRole: (data: { role_name: string }) => api.post<FlightRole>('/crew/roles/', data),
  deleteRole: (id: number) => api.delete<DeleteResponse>(`/crew/roles/${id}`),

  // Crew members
  getAll: (skip = 0, limit = 100) => api.get<Crew[]>(`/crew/?skip=${skip}&limit=${limit}`),
  getById: (id: number) => api.get<Crew>(`/crew/${id}`),
  create: (data: { person_id: number }) => api.post<Crew>('/crew/', data),
  update: (id: number, personId: number) => api.put<Crew>(`/crew/${id}`, { person_id: personId }),
  delete: (id: number) => api.delete<DeleteResponse>(`/crew/${id}`),

  // Assignments
  getAssignments: (skip = 0, limit = 100) =>
    api.get<CrewAssignment[]>(`/crew/assignments/?skip=${skip}&limit=${limit}`),
  getAssignmentsByFlight: (flightId: number) =>
    api.get<CrewAssignment[]>(`/crew/assignments/flight/${flightId}`),
  getAssignmentsByCrew: (crewId: number) =>
    api.get<CrewAssignment[]>(`/crew/assignments/crew/${crewId}`),
  createAssignment: (data: Omit<CrewAssignment, 'id'>) =>
    api.post<CrewAssignment>('/crew/assignments/', data),
  deleteAssignment: (id: number) => api.delete<DeleteResponse>(`/crew/assignments/${id}`),
};

// =========================================================
// TICKETS
// =========================================================

export const ticketApi = {
  // Ticket statuses
  getStatuses: () => api.get<TicketStatus[]>('/tickets/statuses/'),
  createStatus: (data: { status_name: string }) =>
    api.post<TicketStatus>('/tickets/statuses/', data),
  deleteStatus: (id: number) => api.delete<DeleteResponse>(`/tickets/statuses/${id}`),

  // Tickets
  getAll: (skip = 0, limit = 100) => api.get<Ticket[]>(`/tickets/?skip=${skip}&limit=${limit}`),
  getById: (id: number) => api.get<Ticket>(`/tickets/${id}`),
  create: (data: TicketCreate) => api.post<Ticket>('/tickets/', data),
  update: (id: number, data: TicketUpdate) => api.put<Ticket>(`/tickets/${id}`, data),
  delete: (id: number) => api.delete<DeleteResponse>(`/tickets/${id}`),

  // Search & filters
  search: (criteria: TicketSearch) => api.post<Ticket[]>('/tickets/search/', criteria),
  getByPassenger: (passengerId: number) => api.get<Ticket[]>(`/tickets/passenger/${passengerId}/`),
  getByFlight: (flightId: number) => api.get<Ticket[]>(`/tickets/flight/${flightId}/`),
  getAvailableSeats: (flightId: number, seatClassId: number) =>
    api.get<string[]>(`/tickets/flight/${flightId}/available/?seat_class_id=${seatClassId}`),

  // Actions
  cancel: (ticketId: number) => api.post<Ticket>(`/tickets/${ticketId}/cancel/`),

  // Statistics (admin)
  getStatistics: () => api.get<TicketStatistics>('/tickets/statistics/'),
};
