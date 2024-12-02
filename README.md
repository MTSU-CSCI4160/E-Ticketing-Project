# Ticketwave - An E-Ticketing Platform

## Project Overview
Ticketwave is an intuitive ticket management application designed to streamline event organization and attendee engagement. Whether you're managing small gatherings or large-scale conferences, Ticketwave offers robust tools to simplify ticketing and registration processes.

## Prerequisites
- Python 3.8+
- MySQL Server
- pip (Python package manager)

## Database Schema
The application uses four tables:
- USERS
- EVENTS
- SALES
- PAYMENTS

## Installation Steps

### Create Virtual Environment
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

### Install Required Dependencies
pip install flask mysql-connector-python bcrypt

### Database Setup
-- Create Database
CREATE DATABASE Ticketwave;
USE Ticketwave;

-- Create User Table
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    dob DATE,
    role VARCHAR(50),
    created_date DATE DEFAULT CURRENT_DATE,
    update_date DATE DEFAULT NULL ON UPDATE CURRENT_DATE
);

--Create Event
CREATE TABLE events (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    location VARCHAR(255),
    event_date DATETIME NOT NULL,
    organizer_id INT NOT NULL,
    total_seats INT DEFAULT 0,
    seats_sold INT DEFAULT 0,
    seats_left INT AS (total_seats - seats_sold) STORED,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    ticket_price DECIMAL(10,2) NOT NULL
);

-- Create Sales Table
CREATE TABLE sales (
    ticket_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    event_id INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    number_of_tickets INT NOT NULL,
    purchase_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    qr_code BLOB
);

-- Create Payment Table
CREATE TABLE payment (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    event_id INT NOT NULL,
    ticket_id INT NOT NULL,
    payment_status VARCHAR(50) NOT NULL,
    payment_amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    transaction_id VARCHAR(255) UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);


### Populate Sample Data
-- Insert Sample data in the Events Table
INSERT INTO events (name, description, location, event_date, organizer_id, total_seats, seats_sold, created_date, ticket_price)
VALUES
    ('Music Festival 2024', 'An annual music festival featuring top artists.', 'Central Park, New York, NY 10024', '2024-12-10 18:00:00', 1, 500, 320, CURRENT_TIMESTAMP, 75.00),
    ('Tech Expo 2024', 'Showcasing the latest in technology and innovation.', 'Moscone Center, 747 Howard St, San Francisco, CA 94103', '2024-12-15 10:00:00', 1, 300, 152, CURRENT_TIMESTAMP, 100.00),
    ('Winter Wonderland', 'A magical winter experience with live performances.', 'Copley Square, 560 Boylston St, Boston, MA 02116', '2024-12-20 17:00:00', 1, 400, 250, CURRENT_TIMESTAMP, 50.00),
    ('Startup Pitch Night', 'Networking and pitching opportunities for startups.', 'The Collective, 400 Dexter Ave N, Seattle, WA 98109', '2024-11-25 19:00:00', 1, 200, 120, CURRENT_TIMESTAMP, 20.00),
    ('Charity Gala Dinner', 'A fundraising event for a noble cause.', 'The Drake Hotel, 140 E Walton Pl, Chicago, IL 60611', '2024-12-05 20:00:00', 1, 150, 140, CURRENT_TIMESTAMP, 150.00),
    ('Art Exhibition 2024', 'Exhibit of contemporary art from emerging artists.', 'The Broad, 221 S Grand Ave, Los Angeles, CA 90012', '2024-12-18 16:00:00', 1, 250, 100, CURRENT_TIMESTAMP, 30.00),
    ('Comedy Night Special', 'A night of laughter with top comedians.', 'The Comedy Inn, 14501 S Dixie Hwy, Miami, FL 33176', '2024-12-22 21:00:00', 1, 180, 180, CURRENT_TIMESTAMP, 40.00),
    ('Science Fair 2024', 'Interactive science exhibits and demos for all ages.', 'Thinkery, 1830 Simond Ave, Austin, TX 78723', '2024-11-30 09:00:00', 1, 350, 200, CURRENT_TIMESTAMP, 25.00),
    ('Fashion Week 2024', 'Showcasing the latest fashion trends.', 'Kay Bailey Hutchison Convention Center, 650 S Griffin St, Dallas, TX 75202', '2024-12-14 15:00:00', 1, 400, 350, CURRENT_TIMESTAMP, 120.00),
    ('Food Truck Festival', 'A celebration of culinary diversity with top food trucks.', 'Discovery Green, 1500 McKinney St, Houston, TX 77010', '2024-12-08 12:00:00', 1, 300, 250, CURRENT_TIMESTAMP, 10.00),
    ('Film Premiere Night', 'Exclusive premiere screening of a highly anticipated film.', 'TCL Chinese Theatre, 6925 Hollywood Blvd, Los Angeles, CA 90028', '2024-12-21 19:30:00', 1, 600, 450, CURRENT_TIMESTAMP, 60.00),
    ('Book Fair 2024', 'A gathering for book lovers and literary enthusiasts.', 'Jacob K. Javits Convention Center, 429 11th Ave, New York, NY 10001', '2024-12-02 10:00:00', 1, 700, 500, CURRENT_TIMESTAMP, 15.00),
    ('MTIA Bollywood Night', 'Bollywood Night for MTIA Students', 'Student Union Ball Room', '2024-11-21 00:00:00', 3, 50, 3, CURRENT_TIMESTAMP, 5.00),
    ('DBMS Project Expo', 'Test', 'Student Union Ball Room', '2025-01-01 00:00:00', 1, 50, 1, CURRENT_TIMESTAMP, 0.00);


### Configure Database Connection

This need to be updated in the app.py file.


db_config = {
    'host': 'your_host_name',
    'user': 'user_name',
    'password': 'secret/password',
    'database': 'Ticketwave'
}

### Running the Application
python app.py

Once the application loads up navigate to Signup page from there and sign up as a Organize Events and Buy Tickets.

## Project Structure
supplier-shipment-app/
│
├── app.py               # Main Flask application
├── templates/
│   ├── All Templates fles
├── static/
|   ├── Images
└──README.md            # This file


1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/e-ticketing-project.git
