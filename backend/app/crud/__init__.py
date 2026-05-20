# ... существующий код ...

from app.crud.person import (
    get_person,
    get_by_email,
    get_by_passport,
    create_person,
    update_person,
    change_password,
    delete_person,
    get_all,
)

from app.crud.flight import (
    # Airport
    get_airport,
    get_airport_by_code,
    get_all_airports,
    create_airport,
    update_airport,
    delete_airport,
    # Airline
    get_airline,
    get_airline_by_code,
    get_all_airlines,
    create_airline,
    update_airline,
    delete_airline,
    # Flight Status
    get_flight_status,
    get_flight_status_by_name,
    get_all_flight_statuses,
    create_flight_status,
    delete_flight_status,
    # Flight
    get_flight,
    get_flight_by_number,
    get_all_flights,
    search_flights,
    get_upcoming_flights,
    get_flights_by_airport,
    create_flight,
    update_flight,
    delete_flight,
    # Flight Price
    get_flight_price,
    get_flight_prices_by_flight,
    get_active_flight_price,
    create_flight_price,
    update_flight_price,
    delete_flight_price,
    # Count functions
    count_departing_flights,
    count_arriving_flights,
    count_airline_flights,
    count_status_flights,
    count_flight_tickets,
    get_aircraft,
)

from app.crud.aircraft import (
    # Seat Class
    get_seat_class,
    get_seat_class_by_name,
    get_all_seat_classes,
    create_seat_class,
    update_seat_class,
    delete_seat_class,
    # Model Aircraft
    get_model_aircraft,
    get_all_model_aircraft,
    create_model_aircraft,
    update_model_aircraft,
    delete_model_aircraft,
    # Model Seats
    get_model_seat,
    get_model_seats_by_model,
    create_model_seat,
    update_model_seat,
    delete_model_seat,
    # Aircraft
    get_aircraft,
    get_aircraft_by_registration,
    get_all_aircraft,
    create_aircraft,
    update_aircraft,
    delete_aircraft,
    # Aircraft Lease
    get_aircraft_lease,
    get_all_aircraft_leases,
    get_active_lease_for_aircraft,
    create_aircraft_lease,
    update_aircraft_lease,
    delete_aircraft_lease,
    # Count functions
    count_seat_class_model_seats,
    count_model_aircraft,
    count_model_model_seats,
    count_aircraft_flights,
    count_active_aircraft_leases,
    get_airline,
)

from app.crud.crew import (
    # Flight Role
    get_flight_role,
    get_all_flight_roles,
    create_flight_role,
    get_flight_role_by_name,
    delete_flight_role,
    # Crew
    get_crew,
    get_crew_by_person,
    get_all_crew,
    create_crew,
    update_crew,
    delete_crew,
    # Crew Assignment
    get_crew_assignment,
    get_all_crew_assignments,
    get_assignments_by_flight,
    get_assignments_by_crew,
    create_crew_assignment,
    delete_crew_assignment,
)

from app.crud.ticket import (
    # Ticket Status
    get_ticket_status,
    get_ticket_status_by_name,
    get_all_ticket_statuses,
    create_ticket_status,
    delete_ticket_status,
    # Ticket
    get_ticket,
    get_all_tickets,
    search_tickets,
    get_tickets_by_passenger,
    get_tickets_by_flight,
    get_available_seats_for_flight,
    create_ticket,
    update_ticket,
    cancel_ticket,
    delete_ticket,
    get_ticket_statistics,
    # Count functions
    count_status_tickets,
    get_flight,
    get_seat_class,
    get_passenger,
    check_seat_occupied,
)