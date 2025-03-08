import datetime, time, string, random, re
import mysql.connector as sql

#Server Setup
print("WELCOME TO HMS")
print()
time.sleep(0.5)
print("SERVER STARTUP")
while True:
    try:
        User = input("Enter User: ")
        Pass = input("Enter Password: ")
        db = sql.connect(host = "localhost", user = User, password = Pass)

        if db:
            print("Connection Successful \n")
            break
    except sql.errors.ProgrammingError:
        print("Connection Failed \n")
        continue

while True:
    try:
        mycur = db.cursor()
        l = []
        databs = input("Enter database to use: ")
        mycur.execute("show databases")
        for i in mycur:
            l.append(i[0])
        if databs in l:
            mycur.execute("use "+ databs)
            break
        elif databs not in l:
            create = input("Database not found\nCreate new? (y/n):")
            if create.lower() == 'y':
                mycur.execute("create database "+databs)
                mycur.execute("use "+databs)
                break
    except ValueError:
        continue
    except sql.errors.ProgrammingError:
        print("Database naming has an error")
print("NOW USING DATABASE: "+databs)
print("Creating User Tables...")
time.sleep(2)
while True:
    try:
        mycur.execute("""
                    CREATE TABLE Customer (
                        CustID VARCHAR(5) PRIMARY KEY,
                        Name VARCHAR(20),
                        Phone_No CHAR(10), 
                        Address VARCHAR(50),
                        Govt_ID_Type ENUM('UID', 'DL', 'PSP') NOT NULL,
                        Govt_ID_Number VARCHAR(20) NOT NULL,
                        CONSTRAINT unique_govt_id UNIQUE (Govt_ID_Type, Govt_ID_Number)
                    );
                    """)
        mycur.execute("""
                    CREATE TABLE Booking (
                        SrNo INT,
                        CustID VARCHAR(5),
                        checkin DATE NOT NULL,
                        checkout DATE NOT NULL,
                        roomno INT,
                        status VARCHAR(10) NOT NULL DEFAULT 'NA',
                        CONSTRAINT ID_Customer FOREIGN KEY (CustID) REFERENCES Customer(CustID) ON DELETE CASCADE
                    );
                    """)
        time.sleep(1)
        print("Tables Created")
    except sql.errors.ProgrammingError:
        print("Tables Found")
        break


#id_generator
def id_gen(size = 5, chars = string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

#phno validator
def validate_phno(phno, l=10):
    return(len(phno)==l)

#govt id validator
def validate_govt_id(govt_id_type, govt_id_number):
    patterns = {
        "UID": r"^\d{4} \d{4} \d{4}$|^\d{12}$",
        "PSP": r"^[A-Z]{1}-\d{7}$|^[A-Z]{1}\d{7}$",
        "DL": r"^[A-Z]{2}-\d{2}-(19|20)\d{2}-\d{7}$|^[A-Z]{2}\d{13}$" # make (20|21) for the next century
    }
    return bool(re.match(patterns[govt_id_type], govt_id_number))

#formatting for govt id
def format_govt_id(govt_id_type, govt_id_number):
    if govt_id_type == "UID":
        return f"{govt_id_number[:4]} {govt_id_number[4:8]} {govt_id_number[8:]}" if " " not in govt_id_number else govt_id_number
    if govt_id_type == "PSP" and "-" not in govt_id_number:
        return f"{govt_id_number[0]}-{govt_id_number[1:]}"
    if govt_id_type == "DL" and "-" not in govt_id_number:
        return f"{govt_id_number[:2]}-{govt_id_number[2:4]}-{govt_id_number[4:8]}-{govt_id_number[8:]}"
    return govt_id_number

#SQL date insertion formatter
def cdf(date_str):
    return "-".join(reversed(date_str.split("-")))

def cleanup():
    today = datetime.date.today()
    mycur.execute("DELETE FROM Booking WHERE checkout < %s", (today - datetime.timedelta(days=183),)) #6 months
    db.commit()

#Global Variables
IDList = []
Name = []
temp_date1 = ''
temp_date2 = ''
roomsbooked = []
roomsavailable = []
cleanup_ran = False

#Current Year
year = time.localtime()[0]

#Valid Date Checking Function
def date(c):
    isValidDate=True
    try:
        datetime.datetime(c[2],c[1],c[0])
    except ValueError:
        isValidDate = False
    if isValidDate:
        return True
    else:
        return False

#Check-in function for Arrival()
def CheckIn():
    mycur = db.cursor()
    print("\n\t► CUSTOMER CHECK-IN ◄\n")
    name = input("Enter Customer Name: ").strip().capitalize()
    name += "%"
    mycur.execute("SELECT CustID, Name FROM Customer WHERE Name LIKE %s", (name,))
    customers = mycur.fetchall()
    if not customers:
        print("No customer found with that name.")
        return
    print("\nMatching Customers:")
    for cid, cname in customers:
        print(f"CustID: {cid} | Name: {cname}")

    CID = input("\nEnter Customer ID for Check-In: ").strip().upper()

    mycur.execute("SELECT checkin, status FROM Booking WHERE CustID = %s", (CID,))
    result = mycur.fetchone()
    if not result:
        print("No booking found for this Customer ID.")
        return
    checkin_date, current_status = result

    if not result:
        print("No booking found for this Customer ID.")
        return
    elif current_status == "checkedin":
        print("Customer is already checked in.")
        return
    elif checkin_date > datetime.date.today():
        print("Cannot check in before the scheduled date.")
        return

    mycur.execute("UPDATE Booking SET status = 'checkedin' WHERE CustID = %s", (CID,))
    db.commit()
    print(f"Customer {CID} has been checked in successfully!")

#Check-out function for Arrival()
def CheckOut():
    global roomsbooked, roomsavailable
    mycur = db.cursor()
    print("\n\t► CUSTOMER CHECK-OUT ◄\n")

    name = input("Enter Customer Name: ").strip().capitalize()
    name += "%"
    mycur.execute("SELECT CustID, Name FROM Customer WHERE Name LIKE %s", (name,))
    customers = mycur.fetchall()

    if not customers:
        print("No customer found with that name.")
        return

    print("\nMatching Customers:")
    for cid, cname in customers:
        print(f"CustID: {cid} | Name: {cname}")

    CID = input("\nEnter Customer ID for Check-Out: ").strip().upper()

    mycur.execute("SELECT status, roomno, checkout FROM Booking WHERE CustID = %s AND status != 'checkedout'", (CID,))
    results = mycur.fetchall()

    if not results:
        print("No active bookings found for this Customer ID.")
        return

    print("\nActive Bookings:")
    print(f"{'| Room No.':<12} | {'Check-out Date':<15} | {'Status':<10} |")
    print("-" * 40)
    for status, room_no, checkout_date in results:
        print(f"| {room_no:<10} | {checkout_date:<15} | {status:<10} |")

    while True:
        try:
            room_no = int(input("\nEnter Room No. to check out: ").strip())
            if room_no not in [r[1] for r in results]:
                print("Invalid Room No. Please enter a valid booked room.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a valid room number.")

    mycur.execute("SELECT checkout FROM Booking WHERE CustID = %s AND roomno = %s", (CID, room_no))
    checkout_date = mycur.fetchone()[0]
    today_date = datetime.date.today()
    if today_date < checkout_date:
        print(f"Updating checkout date from {checkout_date} to {today_date} (early checkout).")
        mycur.execute("UPDATE Booking SET checkout = %s WHERE CustID = %s AND roomno = %s", (today_date, CID, room_no))
    mycur.execute("UPDATE Booking SET status = 'checkedout' WHERE CustID = %s AND roomno = %s", (CID, room_no))
    db.commit()
    if room_no in roomsbooked:
        roomsbooked.remove(room_no)
        roomsavailable.append(room_no)
    print(f"\nCustomer {CID} has been checked out from Room {room_no} successfully! Room is now available.")

#__Main__ Function
def Home():
    global cleanup_ran
    if not cleanup_ran:
        cleanup()
        cleanup_ran=True

    db.commit()
    print()
    print()
    print('\t\t\t •••••••••••••• WELCOME TO HOTEL GLIDE INN ••••••••••••••\n')
    print('\t 1 → Booking')
    print('\t 2 → Empty Rooms')
    print('\t 3 → Record')
    print('\t 4 → Arrival Management [Checkin/Checkout]')
    print('\t 0 → Exit')

    while True:
        try:
            choice = int(input("\t →"))
            if choice == 1:
                print()
                Book()
                time.sleep(2)
                Home()
            elif choice == 2:
                print()
                RoomsAvailable()
                time.sleep(2)
                Home()
            elif choice == 3:
                print()
                Records()
                time.sleep(2)
                Home()
            elif choice == 4:
                print()
                Arrival()
                time.sleep(2)
                Home()
            elif choice == 0:
                END()
            else:
                raise ValueError
        except ValueError:
            print("Please Enter a valid choice")

# Customer ID generator - sub-function of Book() to generate a customer profile.
def CustID():
    while True:
        try:
            mycur = db.cursor()
            temp_name = input('Name: ').strip().capitalize()
            temp_phno = input('Phone No.: ').strip()
            if not validate_phno(temp_phno):
                raise ValueError
            while True:
                temp_govt_id_type = input("Enter Govt ID Type [UID, DL, PSP]: ").strip().upper()
                if temp_govt_id_type in ['UID', 'DL', 'PSP']:
                    if temp_govt_id_type == "UID":
                        print("Expected format: 123456789012 [9263 XXXX XXXX]")
                    elif temp_govt_id_type == "PSP":
                        print("Expected format: A1234567")
                    elif temp_govt_id_type == "DL":
                        print("Expected format: AA-12-1234-1234567 or AA1212341234567")
                    break
                print("Invalid Govt ID Type. Please enter UID, DL, or PSP.")
            while True:
                temp_govt_id_number = input("ID Number: ").strip().upper()
                if temp_govt_id_type == "DL":
                    temp_govt_id_number = format_govt_id(temp_govt_id_type, temp_govt_id_number)
                if validate_govt_id(temp_govt_id_type, temp_govt_id_number):
                    break
                print("Invalid ID format. Please enter a valid ID.")
                
            mycur.execute("""
                SELECT CustID, Name, Phone_No 
                FROM Customer 
                WHERE Name = %s AND Phone_No = %s AND Govt_ID_Type = %s AND Govt_ID_Number = %s
            """, (temp_name, temp_phno, temp_govt_id_type, temp_govt_id_number))

            existing_customer = mycur.fetchone()
            if existing_customer:
                print(f"\n⚠ WARNING: Customer already exists ⚠")
                print(f"Name: {existing_customer[1]}\nCustID: {existing_customer[0]}\nPhone: {existing_customer[2]}")
                choice = input("\nDo you want to continue with this customer? (y/n): ").strip().lower()
                if choice == 'y':
                    return existing_customer[0]
                else:
                    print("\nRestarting customer entry...\n")
                    continue
            temp_address = input('Address: ').strip().capitalize()
            CID = id_gen()
            while True:
                mycur.execute("SELECT CustID FROM Customer WHERE CustID = %s", (CID,))
                if not mycur.fetchone():
                    break
                CID = id_gen()
            vals = (CID, temp_name, temp_phno, temp_address, temp_govt_id_type, temp_govt_id_number)
            comd = "INSERT INTO Customer VALUES (%s, %s, %s, %s, %s, %s)"
            mycur.execute(comd, vals)
            db.commit()
            print("New Customer Created. CustomerID =", CID)
            return CID

        except sql.errors.IntegrityError:
            print(f"Govt ID {temp_govt_id_number} is already registered.")
        except sql.errors.DataError:
            print("The entered data has some issues. Kindly review and enter again.")
        except ValueError:
            print("Incorrect Input")

# "1" Booking Function - Initiates Booking by a customer. Calls Customer ID maker if not present already.
def  Book():
    global Name
    global IDList
    global tmp_date1
    global tmp_date2
    mycur = db.cursor()
    IDList = []
    Name = []
    tmp_date1 = ''
    tmp_date2 = ''

    mycur.execute("SELECT CustID, Name, Phone_No FROM Customer")
    customer_data = {row[0]: (row[1], row[2]) for row in mycur.fetchall()}

    print("\n\t ► ROOM BOOKING ◄ \t\n")

    search_name = input("Enter Customer Name (leave blank to list all): ").strip().capitalize()
    if(search_name!=""): 
        search_phone = input("Enter Phone Number (Leave blank to search by name only): ").strip()
    else: search_phone = ""

    if search_name == "":
        print("\nAll Customers:")
        print(f"{'CustID':<10} | {'Name':<15} | {'Phone No.':<10}")
        print("-" * 40)
        for cid, (name, phone) in customer_data.items():
            print(f"{cid:<10} | {name:<15} | {phone:<10}")
        
        search_name = input("\nEnter Customer Name to continue: ").strip().capitalize()
        search_phone = input("Enter Phone Number (Leave blank to search by name only): ").strip()

    if search_phone:
        mycur.execute("SELECT CustID, Name, Phone_No FROM Customer WHERE Name LIKE %s AND Phone_No = %s", (f"%{search_name}%", search_phone))
    else:
        mycur.execute("SELECT CustID, Name, Phone_No FROM Customer WHERE Name LIKE %s", (f"%{search_name}%",))

    matching_customers = mycur.fetchall()

    if matching_customers:
        print("\nMatching Customers:")
        print(f"{'CustID':<10} | {'Name':<15} | {'Phone No.':<10}")
        print("-" * 40)
        for cid, name, phone in matching_customers:
            print(f"{cid:<10} | {name:<15} | {phone:<10}")

        while True:
            temp_id = input("\nEnter Customer ID (0 - Exit, 'Enter Key' - Generate Customer): ").strip().upper()
            if(temp_id == "0"):
                Home()

            if not temp_id:
                confirm = input("No Customer ID entered. Proceed with new Customer ID? (y/n): ").strip().lower()
                if confirm == 'y':
                    temp_id = CustID()
                    break
                else:
                    continue

            if temp_id in [cid for cid, _, _ in matching_customers]:
                break
            else:
                print("Invalid selection. Please enter a valid CustID.")
    else:
        print("\nNo matching records found. Proceeding to Customer ID generation...")
        temp_id = CustID()

    mycur.execute("SELECT Name FROM Customer WHERE CustID = %s", (temp_id,))
    customer_name = mycur.fetchone()[0]

    print(f"\nBooking for: {customer_name} (Customer ID: {temp_id})")

    print("Date Format → DD-MM-YYYY")

    while True:
        while True:
            try:
                mycur = db.cursor()

                print()
                tmp1_checkin = input("Checkin Date: ")
                if not tmp1_checkin:
                    tmp1_checkin = datetime.datetime.today().strftime("%d-%m-%Y")
                tmp2_checkin = tmp1_checkin.split('-')
                tmp2_checkin[2] , tmp2_checkin[1] , tmp2_checkin[0] = int(tmp2_checkin[2]) , int(tmp2_checkin[1]) , int(tmp2_checkin[0])
                
                print(tmp2_checkin)

                if date(tmp2_checkin):
                    break
                else:
                    raise ValueError
            except ValueError:
                print("Invalid Checkin Date!")
            except IndexError:
                print("Invalid Checkin Date")

        while True:
            try:
                mycur = db.cursor()
                tmp1_checkout = input("Checkout Date: ")
                tmp2_checkout = tmp1_checkout.split('-')
                tmp2_checkout[2] , tmp2_checkout[1] , tmp2_checkout[0] = int(tmp2_checkout[2]) , int(tmp2_checkout[1]) , int(tmp2_checkout[0])

                print(tmp2_checkout)

                if date(tmp2_checkout):
                    break
                else:
                    raise ValueError
            except ValueError:
                print("Invalid Checkout Date!")
            except IndexError:
                print("Invalid Checkout Date!")
                
        
        tmp_date1 = datetime.date(tmp2_checkin[2],tmp2_checkin[1],tmp2_checkin[0])
        tmp_date2 = datetime.date(tmp2_checkout[2],tmp2_checkout[1],tmp2_checkout[0])

        today_date = datetime.date.today()
        status = "checkedin" if tmp_date1 == today_date else "not_arrived"
        
        if tmp_date1>tmp_date2:
            print("Check-out date can't be before Check-in date")
            continue
        else:
            break
        
#Room Numbers That are Already booked code: ------------------------------
    mycur = db.cursor()
    mycur.execute("select concat('RoomNo: ',roomno,' | has been booked from - ',checkin,' to ', checkout) from booking where checkin <= %s and checkout >= %s",(tmp_date2,tmp_date1,))
    print()
    print("Rooms booked within entered range: ")
    if mycur.fetchall() == []:
        print("None")
    else:
        mycur.execute("select concat('RoomNo: ',roomno,' | has been booked from - ',checkin,' to ', checkout) from booking where checkin <= %s and checkout >= %s",(tmp_date2,tmp_date1,))
        for i in mycur.fetchall():
            print(i[0])

##-----------------------------------------------------------------------

    print()
    print()
    print("Room Ranges are: -\n'Suite' - [1-50]\n'Deluxe' - [51-80]\n'Luxury' - [81-100]")
    while True:
        try:
            mycur = db.cursor()
            roomNum = int(input("Alot a room number. \n"))
            if roomNum <= 0 or roomNum > 100:
                raise ValueError
            mycur.execute("""
                SELECT COUNT(*) FROM Booking 
                WHERE roomno = %s AND (
                    (checkin <= %s AND checkout >= %s) OR
                    (checkin >= %s AND checkin <= %s)
                )
            """, (roomNum, tmp_date2, tmp_date1, tmp_date1, tmp_date2))
            if mycur.fetchone()[0] > 0:
                print("❌ Room is already booked for these dates. Choose a different room.")
                continue
            break
        except ValueError:
            print("Invalid room number or room not available. Please enter a valid room number.")

    print()
    print("Saving Booking Data...")
    print()
    while True:
        try:
            mycur = db.cursor()
            CID = temp_id
            mycur.execute("select * from Booking")
            mycur.fetchall()
            srno = mycur.rowcount + 1
            tmp1_checkin = cdf(tmp1_checkin)
            tmp1_checkout = cdf(tmp1_checkout)
            vals = (srno,CID,tmp1_checkin,tmp1_checkout,roomNum,status)
            comd = "insert into Booking values(%s,%s,%s,%s,%s,%s)"
            mycur.execute(comd,vals)
            db.commit()
            print("Booking Successful")
            break
        except sql.IntegrityError:
            print("Wrong Customer ID!")
            print()
        except sql.ProgrammingError:
            print("Wrong Customer ID!")
            print()


# "2" > Availability function - Rooms Available for booking and Booked Room list function
def RoomsAvailable():
    global roomsbooked
    global roomsavailable
    roomsbooked = []
    roomsavailable = []
    mycur = db.cursor()
    mycur.execute("SELECT DISTINCT(roomno) FROM booking WHERE status != 'checkedout'")
    for i in mycur.fetchall():
        roomsbooked.append(i[0])
    for i in range(1, 101):
        if i not in roomsbooked:
            roomsavailable.append(i)
    print("Rooms Not Booked:")
    print(", ".join(map(str, roomsavailable)))
    
    print("\nRooms Booked for certain dates <Refer to Records for booking dates> :")
    print(", ".join(map(str, roomsbooked)))


#Room Records sub-function of Records()
def Rooms():
    mycur = db.cursor()
    mycur.execute("select roomno, checkin, checkout from booking")
    print('|'+'%5s'%'RoomNo'+'\t|\t'+'%11s'%'Checkin'+'\t|\t'+'%11s'%'Checkout'+'\t|\t')
    print('---------------------------------------------------------')
    for i in mycur.fetchall():
        print('|' + '%5s'%str(i[0]) + '\t|\t'
              +'%11s'%str(i[1]) + '\t|\t'
              +'%10s'%str(i[2]) + '\t|\t')

# "3" > Records Function - Fetches records from the sql server and displays them
def Records():
    while True:
        try:
            mycur = db.cursor()
            ch = int(input("1. Customer Records\n2. Booking Records\n3. Rooms Records\n->"))
            if ch == 1:
                print(f"{'| Cust ID':<12} | {'Name':<20} | {'Phone No.':<15} | {'Address':<30} | {'Govt ID Type':<12} | {'Govt ID Number':<20} |")
                print("-" * 126)
                mycur.execute("SELECT * FROM Customer")
                for i in mycur.fetchall():
                    print(f"| {i[0]:<10} | {i[1]:<20} | {i[2]:<15} | {i[3]:<30} | {i[4]:<12} | {i[5]:<20} |")
                break
            elif ch == 2:
                print(f"{'| SrNo':<8} | {'Cust ID':<10} | {'Check-in':<12} | {'Check-out':<12} | {'Room No.':<10} | {'Status':<10} |")
                print("-" * 80)
                mycur.execute("SELECT * FROM Booking")
                for i in mycur.fetchall():
                    sno = str(i[0])
                    custid = str(i[1])
                    cin = str(i[2])
                    cout = str(i[3])
                    rmno = str(i[4])
                    status = str(i[5])
                    print(f"| {sno:<6} | {custid:<10} | {cin:<12} | {cout:<12} | {rmno:<10} | {status:<10} |")
                print()
                break
            elif ch == 3:
                Rooms()
                break
            else:
                raise ValueError
        except ValueError:
            print("Please Enter a Valid Choice!")
        
#Function to handle check-in and check-out
def Arrival():
    while True:
        try:
            print("\n\t► ARRIVAL MANAGEMENT ◄\n")
            print("1 → Check-In")
            print("2 → Check-Out")
            print("0 → Return to Home")

            choice = int(input("\t → "))
            if choice == 1:
                CheckIn()
            elif choice == 2:
                CheckOut()
            elif choice == 0:
                Home()
            else:
                raise ValueError
        except ValueError:
            print("Invalid choice. Please enter 1, 2, or 0.")

# "0" > End of code function
def END():
    print("Thank You for using HMS")
    db.commit()
    db.close()
    print("Bye")
    time.sleep(1)
    exit()

#Driver Code
Home()