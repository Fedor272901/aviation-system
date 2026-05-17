// =========================================================
// AUTH
// =========================================================

export interface AuthUser {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  middle_name?: string;
  phone?: string;
  passport?: string;
  roles: string[];
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  middle_name?: string;
  phone?: string;
  passport: string;
}

export interface PasswordChangeData {
  old_password: string;
  new_password: string;
}

// =========================================================
// PERSON
// =========================================================

export interface Person {
  id: number;
  first_name: string;
  last_name: string;
  middle_name?: string;
  phone?: string;
  passport: string;
  email: string;
}

export interface PersonCreate {
  first_name: string;
  last_name: string;
  middle_name?: string;
  phone?: string;
  passport: string;
  email: string;
  password: string;
}

export interface PersonUpdate {
  first_name?: string;
  last_name?: string;
  middle_name?: string;
  phone?: string;
  passport?: string;
  email?: string;
}

// =========================================================
// AIRPORT / AIRLINE / FLIGHT STATUS
// =========================================================

export interface Airport {
  id: number;
  code: string;
  name?: string;
  city: string;
}

export interface Airline {
  id: number;
  name: string;
  code: string;
  country?: string;
}

export interface FlightStatus {
  id: number;
  status_name: string;
}

// =========================================================
// FLIGHT
// =========================================================

export interface Flight {
  id: number;
  flight_number: string;
  departure_datetime: string;
  arrival_datetime: string;
  id_from: number;
  id_to: number;
  id_airline: number;
  id_aircraft: number;
  id_status: number;
  // Вложенные поля (опционально, бэкенд отдаёт при чтении)
  from_airport_code?: string;
  to_airport_code?: string;
  airline_name?: string;
  status_name?: string;
}

export interface FlightCreate {
  flight_number: string;
  departure_datetime: string;
  arrival_datetime: string;
  id_from: number;
  id_to: number;
  id_airline: number;
  id_aircraft: number;
  id_status: number;
}

export interface FlightUpdate {
  flight_number?: string;
  departure_datetime?: string;
  arrival_datetime?: string;
  id_from?: number;
  id_to?: number;
  id_airline?: number;
  id_aircraft?: number;
  id_status?: number;
}

export interface FlightSearch {
  id_from?: number;
  id_to?: number;
  date_from?: string;
  date_to?: string;
  id_airline?: number;
}

export interface FlightPrice {
  id: number;
  id_flight: number;
  id_seat_class: number;
  price: string;
  valid_from?: string;
  valid_to?: string;
}

// =========================================================
// AIRCRAFT
// =========================================================

export interface SeatClass {
  id: number;
  class_name: string;
  price_multiplier: string;
  description?: string;
}

export interface ModelAircraft {
  id: number;
  name: string;
  manufacturer?: string;
}

export interface Aircraft {
  id: number;
  registration_number: string;
  id_model: number;
  manufacture_year?: number;
  last_maintenance?: string;
}

export interface AircraftLease {
  id: number;
  id_aircraft: number;
  id_airline: number;
  start_date: string;
  end_date?: string;
}

// =========================================================
// CREW
// =========================================================

export interface FlightRole {
  id: number;
  role_name: string;
}

export interface Crew {
  id: number;
  person_id: number;
}

export interface CrewAssignment {
  id: number;
  id_flight_role: number;
  id_flight: number;
  id_crew: number;
  flight_role_name?: string;
  flight_number?: string;
  crew_person_email?: string;
}

// =========================================================
// TICKET
// =========================================================

export interface TicketStatus {
  id: number;
  status_name: string;
}

export interface Ticket {
  id: number;
  seat_number: string;
  id_seat_class: number;
  price: string;
  purchase_date: string;
  id_status: number;
  id_flight: number;
  id_passenger: number;
  // Вложенные поля
  status_name?: string;
  flight_number?: string;
  passenger_email?: string;
}

export interface TicketCreate {
  seat_number: string;
  id_seat_class: number;
  price: string;
  id_status: number;
  id_flight: number;
  id_passenger: number;
}

export interface TicketUpdate {
  seat_number?: string;
  id_seat_class?: number;
  price?: string;
  id_status?: number;
  id_flight?: number;
}

export interface TicketSearch {
  id_passenger?: number;
  id_flight?: number;
  id_status?: number;
  date_from?: string;
  date_to?: string;
}

export interface TicketStatistics {
  total_tickets: number;
  by_status: Record<string, number>;
}

// =========================================================
// API RESPONSES
// =========================================================

export interface DeleteResponse {
  message: string;
  deleted_id: number;
}

export interface ApiError {
  detail: string;
}