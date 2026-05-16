export interface Person {
  id: number;
  first_name: string;
  last_name: string;
  middle_name?: string;
  phone?: string;
  passport: string;
  email: string;
}

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
}

export interface Airport {
  id: number;
  code: string;
  name?: string;
  city: string;
}