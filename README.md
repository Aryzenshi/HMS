# Hotel Management System v2.2025

This is the updated version of the **Hotel Management System**, a console-based Python application designed to manage hotel room bookings, check-ins, and check-outs efficiently. It integrates with an SQL database to store and manage customer and booking records.

## Features

- **Customer Management**: Stores customer details including Name, Phone Number, Address, and Government ID.
- **Booking System**: Allows customers to book rooms based on availability.
- **Check-In & Check-Out**: Manages customer arrivals and departures, ensuring accurate room status updates.
- **Room Availability**: Tracks available and occupied rooms with real-time updates.
- **Record Keeping**: Maintains past and current booking records.
- **SQL Database Integration**: Uses MySQL for persistent data storage.
- **Automatic Cleanup**: Deletes old bookings after 3 months to maintain database efficiency.

## Installation

1. Ensure you have **Python 3.x** (Recommended 3.8+) installed.
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
| Column        | Type        | Constraints |
|--------------|------------|-------------|
| CustID       | VARCHAR(5) | PRIMARY KEY |
| Name         | VARCHAR(20) | NOT NULL   |
| Phone_No     | CHAR(10)   | NOT NULL   |
| Address      | VARCHAR(50) | NOT NULL   |
| Govt_ID_Type | ENUM('UID', 'DL', 'PSP') | NOT NULL |
| Govt_ID_Number | VARCHAR(20) | UNIQUE |

### Booking Table
| Column    | Type    | Constraints |
|----------|--------|-------------|
| SrNo     | INT    | PRIMARY KEY |
| CustID   | VARCHAR(5) | FOREIGN KEY REFERENCES Customer(CustID) ON DELETE CASCADE |
| Checkin  | DATE   | NOT NULL   |
| Checkout | DATE   | NOT NULL   |
| RoomNo   | INT    | NOT NULL   |
| Status   | VARCHAR(10) | DEFAULT 'NA' |

## Changes in Version 2

- **Government ID Requirement**: Customers must provide a Govt ID (Aadhaar, Passport, or Driver's License).
- **Improved Search**: Customer lookup supports partial name matching.
- **Check-Out Enhancements**: Updates checkout date if a customer leaves early.
- **Multiple Room Bookings**: Customers can book multiple rooms, and check out from specific ones.
- **Automatic Cleanup**: Removes old bookings after 3 months.
- **Bug Fixes & Optimizations**: Improved error handling and room availability tracking.

## License

This project is licensed under the [Apache 2.0 License](./LICENSE).