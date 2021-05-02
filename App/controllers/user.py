from flask import redirect, render_template, request, session, url_for
from flask_login import current_user, login_user, login_required, logout_user
from sqlalchemy.exc import IntegrityError
import datetime


from App.models import ( db, User, Customer, Room, Booking, Bill )
from App.login import login_manager







def create_user(data):
    try:
        user = User( email=data['email'])
        user.set_password( data['password'])
        customer= Customer(email= data['email'], firstName= data['firstName'], lastName= data['lastName'], phoneNumber= data['phoneNumber'], country=data['country'], address= data['address'])
        db.session.add(user)
        db.session.add(customer)
        db.session.commit()
        return True
    except IntegrityError:
        db.session.rollback()
        return False
    

def loginUser(data):
    user= User.query.filter_by(email=data['email']).first()
    if user != None and user.check_password(data['password']):
      login_user(user)
      #print( user.toDict())
      return True

    return False

def get_current_user():
    if current_user.is_authenticated:
        #print("User " + current_user.email + " has been logged in.")
        user= User.query.filter_by(email= current_user.email).first()
        user= user.toDict()
        return user
    return None


def log_user_out():
    logout_user()
    

def get_all_rooms():
    rooms = Room.query.all()
    
    return rooms

def get_rooms_by_type(roomType):
    rooms= Room.query.filter_by()
    return rooms


def book_a_room(data, roomType, roomNumber):


    #Get dates for calculation
    endDate = data['trip-end']
    startDate = data['trip-start']

    

    #Split Date Strings into [year, month, day]
    endDate = data['trip-end'].split('-')
    startDate = data['trip-start'].split('-')
    #Create Date object using datetime
    d1= datetime.datetime( int(endDate[0]), int(endDate[1]), int(endDate[2]) )
    d2= datetime.datetime( int(startDate[0]), int(startDate[1]), int(startDate[2])  )
    


    #Make Booking object
    booking = Booking( roomNumber = int(roomNumber) , roomType = roomType , check_in_Date= d2 , check_out_Date=d1 , userEmail= current_user.email)
    #Get room and 
    room = Room.query.filter_by(roomNumber= int(roomNumber) ).first()
    #set room.available=False
    room.book()

    try:
      db.session.add(booking)
      db.session.add(room)
      db.session.commit()

      #Create Bill - Once booking is sucessful
      room= Room.query.filter_by(roomType = roomType).first()
      roomRate = room.roomRate
      

      
      bill = Bill(roomNumber = int(roomNumber) , roomType = roomType , check_in_Date= d2 , check_out_Date=d1 , userEmail= current_user.email , roomRate = float(roomRate) )

      bill.calculateBill()
      try:
        db.session.add(bill)
        db.session.commit()
      except IntegrityError:
        db.session.rollback()
        return False
      
      #If room has been successfully booked
      return True
      
    except IntegrityError:
      db.session.rollback()
      return False

    
def get_account_details():
        return Customer.query.filter_by(email= current_user.email).first()

def get_user_booking(roomType, roomNumber):
    booking = Booking.query.filter_by(userEmail= current_user.email, roomType= roomType, roomNumber= int(roomNumber) ).first()
    if booking== None:
        return None
    return booking.toDict()

def get_user_bookings():
        user= get_current_user()
        return user['bookings']


def update_user_booking(data, roomType, roomNumber):
    
        endDate = data['trip-end']
        startDate = data['trip-start']

        booking = Booking.query.filter_by(userEmail= current_user.email, roomType= roomType, roomNumber= int(roomNumber) ).first()



        booking.check_in_Date = datetime.datetime.strptime(startDate, "%Y-%m-%d").date()
        booking.check_out_Date = datetime.datetime.strptime(endDate, "%Y-%m-%d").date()
        
        bill= Bill.query.filter_by(userEmail= current_user.email, roomType= roomType, roomNumber= int(roomNumber) ).first()

        #Create a date objects to add to bill
        bill.check_in_Date = datetime.datetime.strptime(startDate, "%Y-%m-%d").date()
        bill.check_out_Date = datetime.datetime.strptime(endDate, "%Y-%m-%d").date()

        bill.calculateBill()

        try: 
            db.session.add(booking)
            db.session.add(bill)
            db.session.commit()

            return True
            
        except: 
            db.session.rollback()
            return False

  


def delete_user_booking(roomType, roomNumber):
    
    booking = Booking.query.filter_by(userEmail= current_user.email, roomType= roomType, roomNumber= int(roomNumber) ).first()
    if booking!=None:
            

            room = Room.query.filter_by(roomNumber= int(roomNumber) ).first()
            #set room.available=False
            room.unbook()

            bill= Bill.query.filter_by(userEmail= current_user.email, roomType= roomType, roomNumber= int(roomNumber) ).first()

            try:
                db.session.delete(booking)
                db.session.delete(bill)
                #room is not deleted but updated, so we just add the update
                db.session.add(room)
                db.session.commit()
                return True
            
            except:
                db.session.rollback()
                return False



def update_user_account(data):

    user= User.query.filter_by(email= current_user.email).first()
    
    if data['firstName'] !='':
      user.customer.firstName= data['firstName']

    if data['lastName'] !='':
      user.customer.lastName= data['lastName']

    if data['password'] !='':
      user.set_password(data['password'])

    if data['country'] !='':
      user.customer.country= data['country']
    
    if data['phoneNumber'] !='':
      user.customer.phoneNumber= data['phoneNumber']

    if data['address'] !='':
      user.customer.address= data['address']

    try:
      
      db.session.add(user)
      db.session.commit()
      return True
      
    except IntegrityError:
      db.session.rollback()
      return False


def get_room_bill(roomNumber):
    return Bill.query.filter_by(roomNumber= int(roomNumber)).first() 



def pay_room_bill(roomNumber):
    bill = get_room_bill(roomNumber)

    bill.pay()
    try:
        db.session.add(bill)
        db.session.commit()
        return True

    except: 
        db.session.rollback()
        return False



def delete_acc():
    user= User.query.filter_by(email= current_user.email).first()
    customer= get_account_details()

    bookings= Booking.query.all()

  

    try:
        if bookings != None:
            for booking in bookings:
                if booking.userEmail == current_user.email:
                
                    room= Room.query.filter_by(roomNumber= booking.roomNumber).first()
                    room.unbook()
                    
                    bill= Bill.query.filter_by(roomNumber=booking.roomNumber, userEmail= current_user.email, check_in_Date= booking.check_in_Date).first()

                    
                    db.session.add(room)
                    db.session.delete(booking)
                    db.session.delete(bill)
        logout_user()
        db.session.delete(customer)
        db.session.delete(user)
        db.session.commit()
        return True
    except:
        db.session.rollback()
        login_user(user)
        return False