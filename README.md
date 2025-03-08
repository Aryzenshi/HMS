# Hotel Management System v1.2023

This is the first version of the **Hotel Management System**, a console-based Python application that helps manage hotel room bookings, check-ins, and check-outs. It integrates with an SQL database to store and manage customer and booking records.

## Features

- **Customer Management**: Stores customer details including Name, Phone Number, and Address.
- **Booking System**: Allows customers to book rooms based on availability.
- **Check-In & Check-Out**: Manages customer arrivals and departures.
- **Room Availability**: Tracks available and occupied rooms.
- **Record Keeping**: Maintains past and current booking records.
- **SQL Database Integration**: Uses MySQL for persistent data storage.

## Installation

1. Ensure you have **Python 3.x** installed.
2. Install MySQL and set up a database.
3. Install required dependencies:
   ```bash
   pip install mysql-connector-python
   ```
4. Clone the repository or download the script.

## Usage

1. Run the script:
   ```bash
   python "Hotel Management System.py"
   ```
2. Enter MySQL credentials when prompted.
3. Choose an option from the menu to proceed:
   - **Booking**: Book a room for a customer.
   - **Empty Rooms**: View available rooms.
   - **Records**: View customer and booking records.
   - **Arrival Management**: Handle check-ins and check-outs.
   - **Exit**: Close the application.

## Database Schema

### Customer Table
| Column    | Type        | Constraints |
|-----------|------------|-------------|
| CustID    | VARCHAR(5) | PRIMARY KEY |
| Name      | VARCHAR(20) | NOT NULL   |
| Phone_No  | CHAR(10)   | NOT NULL, UNIQUE |
| Address   | VARCHAR(50) | NOT NULL   |

### Booking Table
| Column    | Type        | Constraints |
|-----------|------------|-------------|
| SrNo      | INT        | PRIMARY KEY |
| CustID    | VARCHAR(5) | FOREIGN KEY REFERENCES Customer(CustID) ON DELETE CASCADE |
| Checkin   | DATE       | NOT NULL   |
| Checkout  | DATE       | NOT NULL   |
| RoomNo    | INT        | NOT NULL   |
| Status    | VARCHAR(10) | DEFAULT 'NA' |

## License

This project is licensed under the [Apache 2.0 License](./LICENSE).