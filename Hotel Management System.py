import datetime
import time
import mysql.connector as sql
import string
import random

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
        mycur.execute("create table Customer(CustID varchar(5) primary key, Name varchar(20), Phone_No char(10) unique, Address varchar(50))")
        mycur.execute("create table Booking(SrNo int, CustID varchar(5), checkin date not null, checkout date not null, roomno int, constraint ID_Customer FOREIGN KEY (CustID) REFERENCES Customer(CustID) ON DELETE CASCADE)")
        time.sleep(1)
        print("Tables Created")
    except sql.errors.ProgrammingError:
        print("Tables Found")
        break


#id_generator
def id_gen(size = 5, chars = string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


#Global Variables
IDList = []
Name = []
temp_date1 = ''
temp_date2 = ''
roomsbooked = []
roomsavailable = []


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


#__Main__ Function
def Home():
    db.commit()
    print()
    print()
    print('\t\t\t •••••••••••••• WELCOME TO HOTEL GLIDE INN ••••••••••••••\n')
    print('\t 1 → Booking')
    print('\t 2 → Empty Rooms')
    print('\t 3 → Record')
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
            temp_name = input('Name: ')
            temp_name = temp_name.capitalize()
            temp_phno = int(input('Phone No.: '))
            temp_address = input('Address: ')
            temp_address = temp_address.capitalize()
            CID = id_gen()
            if CID in IDList:
                CID = id_gen()
                if CID not in IDList:
                    break
                else:
                    continue
            vals = (CID,temp_name,temp_phno,temp_address)
            comd = "insert into Customer values(%s,%s,%s,%s)"
            if temp_name != '' and temp_phno != '' and temp_address != '':
                mycur.execute(comd,vals)
                db.commit()
                print("CustomerID = ",CID)
                break
            else:
                raise ValueError
        except sql.errors.DataError:
            print("The entered data has some issues. Kindly review and enter again.")
        except ValueError:
            print("Wrong Input")
    return CID
  

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
    mycur.execute("select * from Customer")
    for i in mycur.fetchall():
        IDList.append(i[0])
        Name.append(i[1])
    print('\t ► ROOM BOOKING ◄ \t')
    print()
    print("CUSTOMER ID LIST: ")
    for i in range(len(IDList)):
        print(IDList[i],", ",Name[i])
    print()
    while True:
        try:
            mycur = db.cursor()
            print("DISCLAIMER: \nEnter '0' for cancelling booking.\nPress 'Enter Key' to proceed to Customer ID Generation")
            time.sleep(2)
            temp_id = input("Customer ID <Enter to proceed to record creation>\n: ")
            temp_id = temp_id.upper()
            if temp_id == '0':
                Home()
            if temp_id != '' and temp_id in IDList:
                break
            elif temp_id != '' and temp_id not in IDList:
                raise sql.errors.DataError
            else:
                print()
                print("Customer ID Generation")
                temp_id = CustID()
                break
        except sql.errors.DataError:
            print("Customer Record Not Found.")

    print("Date Format → YYYY-MM-DD")

    while True:
        while True:
            try:
                mycur = db.cursor()
                print()
                tmp1_checkin = input("Checkin Date: ")
                tmp2_checkin = tmp1_checkin.split('-')
                tmp2_checkin[0] , tmp2_checkin[1] , tmp2_checkin[2] = int(tmp2_checkin[2]) , int(tmp2_checkin[1]) , int(tmp2_checkin[0])
                
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
                tmp2_checkout[0] , tmp2_checkout[1] , tmp2_checkout[2] = int(tmp2_checkout[2]) , int(tmp2_checkout[1]) , int(tmp2_checkout[0])
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
            print(i[0].decode())

##-----------------------------------------------------------------------

    print()
    print()
    print("Room Ranges are: -\n'Suite' - [1-50]\n'Deluxe' - [51-80]\n'Luxury' - [81-100]")
    while True:
        try:
            mycur = db.cursor()
            roomNum = int(input("Alot a room number. \n"))
            if roomNum <=0 or roomNum >100:
                raise ValueError
            Checkin = []
            Checkout = []
            mycur.execute("select * from booking where roomno = %s",(roomNum,))
            for i in mycur.fetchall():
                Checkin.append(i[2])
                Checkout.append(i[3])
            for i in range(len(Checkin)):
                if tmp_date1 <= Checkout[i] and tmp_date2 >= Checkin[i]:
                    raise ValueError
            break
        except ValueError:
            print("Room not available for given range.")

    print()
    print("Saving Booking Data...")
    while True:
        try:
            mycur = db.cursor()
            name = input("Enter Name: ").capitalize()
            name +='%'
            mycur.execute("select CustID, Name, Phone_No from Customer where Name LIKE %s",(name,))
            if len(mycur.fetchall()) != 0:
                mycur = db.cursor()
                mycur.execute("select CustID, Name, Phone_No from Customer where Name LIKE %s",(name,))
                for i in mycur.fetchall():
                    print(i[0]," ",i[1]," ",i[2])
                break
            else:
                print("Customer Record not found!")
                continue
        except sql.errors.IntegrityError:
            print("Customer Record not found!")

    print()
    while True:
        try:
            mycur = db.cursor()
            CID = input("Enter Customer ID: ").upper()
            mycur.execute("select * from Booking")
            mycur.fetchall()
            srno = mycur.rowcount + 1
            vals = (srno,CID,tmp1_checkin,tmp1_checkout,roomNum)
            comd = "insert into Booking values(%s,%s,%s,%s,%s)"
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
    mycur.execute("select distinct(roomno) from booking")
    for i in mycur.fetchall():
        roomsbooked.append(i[0])
    for i in range(1,101):
        if i not in roomsbooked:
            roomsavailable.append(i)
        else:
            continue
    print("Rooms Not Booked:")
    for i in roomsavailable:
        print(i, end = ',')
    print()
    print()
    print("Rooms Booked for certain dates <Refer to Records for booking dates> : ")
    for i in roomsbooked:
        print(i, end = ',')


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
                print('|'+'%10s'%'Cust ID' + '  |  ' + '%5s'%'Name' + '\t|\t' + '%10s'%'Phone No' + '\t|\t' + '%20s'%'Address' +' \t\t|')
                print('-----------------------------------------------------------------------------------------')
                mycur.execute("select * from Customer")
                for i in mycur.fetchall():
                    print('|'+'%10s'%i[0] + '  |  ' + '%5s'%i[1] + '\t|\t' + '%10s'%str(i[2]) + '\t|\t' + '%20s'%i[3] +' \t\t|')
                break
            elif ch == 2:
                print('|'+'%5s'%'SrNo' + '\t|    ' + '%5s'%'Cust ID' + '\t|\t' + '%10s'%'Checkin' + '\t|\t' + '%10s'%'Checkout' +' \t|' + '%10s'%'RoomNo' + '\t|')
                print('-----------------------------------------------------------------------------------------')
                mycur.execute("select * from Booking")
                for i in mycur.fetchall():
                    sno = str(i[0])
                    custid = str(i[1])
                    cin = str(i[2])
                    cout = str(i[3])
                    rmno = str(i[4])
                    print('|'+'%5s'%sno + '\t|    ' + '%5s'%custid + '\t|\t' + '%10s'%cin + '\t|\t' + '%10s'%cout +' \t|' + '%10s'%rmno + '\t|\t')
                print()
                break
            elif ch == 3:
                Rooms()
                break
            else:
                raise ValueError
        except ValueError:
            print("Please Enter a Valid Choice!")

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
