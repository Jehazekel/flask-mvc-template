from flask import Blueprint, redirect, render_template, request, jsonify, send_from_directory
from flask import Flask, request, flash, url_for

from flask_login import current_user, login_user, login_required, logout_user
import json
user_views = Blueprint('user_views', __name__, template_folder='../templates')

from App.login import login_manager
from App.models import User, Customer, Room , Booking , Bill
from App.controllers import (create_user, get_current_user, get_all_rooms, loginUser, log_user_out, get_rooms_by_type, book_a_room, get_account_details, delete_user_booking, get_user_bookings ) 

from App.controllers import (update_user_account, get_user_booking ,update_user_booking, get_room_bill, pay_room_bill, delete_acc )
@user_views.route('/', methods=['GET'])
def home():
    user= get_current_user()
    if current_user.is_authenticated and user !=None:
        
        return render_template('Home.html', user= user)
    return render_template('Home.html')


@user_views.route('/signupForm', methods=['GET'])
def display_signup():
  return render_template('Signup.html')



@user_views.route('/loginForm', methods=['GET'])
def loginForm():
  return render_template('Login.html')


@user_views.route('/rooms') 
def display_rooms():
  rooms= get_all_rooms()
  Currentuser= get_current_user()
  
  if Currentuser!= None:
      
      return render_template('Room.html', user= Currentuser , rooms=rooms)
  return render_template('Room.html' , rooms=rooms)


@user_views.route('/about', methods=['GET']) 
def display_about():
  user= get_current_user()
  if user!= None:
    return render_template('About.html', user = user)
  return render_template('About.html')

@user_views.route('/signup', methods=['POST'])
def sign_up():
    data= request.form      # get json data (aka submitted login_id, email & password)

    if data == None:
        flash("Invalid request.")
        return redirect("/")

    if data['password'] !=data['confirm_password']:
        flash("Passwords must match!")
        return redirect( request.referrer )

    elif data['password']=='' or data['email']=='':
        flash("Email and password fields must be filled!")
        return redirect( request.referrer )

    created= create_user(data)
    if created:
        flash("Account created")
        return redirect('/loginForm')
    else:
        flash('Sign up failed: Account could not be created.')
        return redirect( request.referrer )


@user_views.route('/login', methods=['POST'])
def login():   
  data= request.form
  
  if data['email']!='' and data['password']!='':
      login = loginUser(data)
      if login:
        flash("You have logged in successfully")
    
        return redirect( "/rooms" )

  flash("Login Failed: Invalid User email or password. ")
  return redirect( '/loginForm' )


@user_views.route("/logout", methods=["GET"])
@login_required
def logout():
  log_user_out()
  flash('Logged Out!')
  return redirect('/') 
  

@user_views.route("/book/<roomType>/<roomNumber>", methods=["GET"])
@login_required
def display_booking(roomType , roomNumber):

  user= get_current_user()
  if user!= None:
      return render_template('Book.html', user= user, roomNumber= roomNumber, roomType= roomType)
  flask("Please login before attempting the previous.")
  return redirect( "/loginForm" )



#Route for a specific room type
@user_views.route('/rooms/<roomType>')
@login_required
def display_roomType(roomType):

  rooms = get_rooms_by_type(roomType)

  roomCount=0
  for room in rooms:
    roomCount = roomCount + 1


  rooms = Room.query.filter_by(roomType = roomType , available=True).first()

  user= get_current_user()
  if user!= None:
    return render_template('Roomtype.html', user= user , roomType = roomType , rooms = rooms , roomCount = roomCount)
  
  return render_template('Roomtype.html' , roomType = roomType , rooms = rooms,roomCount = roomCount)




#Adds a booking: includes creating a bill & book room
@user_views.route("/book/<roomType>/<roomNumber>", methods=["POST"])
@login_required
def addBooking(roomType , roomNumber):  
  data= request.form
  
  #Get the current user's info: for tab bar
  user= get_current_user()
  if user!= None and data:

    booked= book_a_room(data, roomType, roomNumber)
  
    if booked:
        flash("Your room has been successfully booked.")
        return redirect("/MyBookings")

    else :
        flash("Your booking already exist.")
        return render_template('Book.html', user= user, roomNumber= roomNumber, roomType= roomType)


  flash("Invalid request.")
  return redirect("/loginForm")



@user_views.route('/MyBookings', methods=["GET"])
@login_required
def display_bookings():

  user= get_current_user()
  if user!= None :

    userbooking= user['bookings']
    
    return render_template('Userbookings.html' , user=user , bookingdetails= userbooking)
  
  flash("Only logged in users can access the previous page!")
  return redirect("/loginForm")


@user_views.route('/MyAccount', methods=["GET"])
@login_required
def display_AcountDetails():

  user= get_current_user()
  if user!= None :

    accountdetails = get_account_details()

  return render_template('Userdetails.html' , user=user , accountdetails=accountdetails)




@user_views.route('/MyBookings/updateForm/<roomType>/<roomNumber>', methods=['GET']) 
@login_required
def display_booking_updateForm(roomType, roomNumber):
  user= get_current_user()
  booking = get_user_booking(roomType, roomNumber)
  return render_template('Updateuserbookings.html', user= user, booking= booking)




#Updates a user booking and bill
@user_views.route('/MyBookings/updateForm/<roomType>/<roomNumber>', methods=['POST']) 
@login_required
def update_booking(roomType, roomNumber):
  
  data= request.form
  if roomType==None or roomNumber==None or data==None:
    flash("An invalid request was attempted.")
    return redirect("/")
  
  successful= update_user_booking(data, roomType, roomNumber)

  if successful:

    flash("Update was successful.")
    
  else:
    flash("Update failed.")

  return redirect("/MyBookings")




@user_views.route('/MyBill/<roomNumber>', methods=['GET'])
@login_required
def display_bill(roomNumber):
  
  user= get_current_user()
  if user!= None :

    bill = get_room_bill(roomNumber)

    return render_template('Userbill.html' , user = user , bill = bill)

  return redirect("/MyBookings")




@user_views.route('/MyBill/<roomNumber>/pay', methods=['POST'])
@login_required
def pay_bill(roomNumber):
  bill = get_room_bill(roomNumber)

  if bill== None:
    flash("An Invalid request was made.")
    return redirect('/MyBookings')

  if bill.paid is True:
    flash("Your bill has already been paid.")
    return redirect(request.referrer)

  successful= pay_room_bill(roomNumber)
  if successful:
    
    flash("You have successful paid your bill.")

  else: 
    
    flash("Attempt to pay bill failed.")

  return redirect(request.referrer)




#Deletes booking & unbook Room: including, booking, bill
@user_views.route("/delete/<roomType>/<roomNumber>", methods=['GET'])
@login_required
def delete_booking(roomType, roomNumber):

  user= get_current_user()
  if user!= None :
    successful= delete_user_booking(roomType, roomNumber)

    if successful:
      
      flash("Your booking has been successfully deleted.")
      
    else:
      flash("Booking failed to delete.")
    
    

    userbooking= get_user_bookings()
    
    return render_template('Userbookings.html' , user=user , bookingdetails= userbooking)

  flash("Only logged in users can access the previous page!")
  return redirect("/loginForm")




#Edit user account details
@user_views.route("/MyProfile/edit", methods=['POST'])
@login_required
def edit_account():
  data= request.form  # get json data (aka submitted login_id, email & password)
  
  if data != None:
    if data['password'] !=data['confirm_password']:
      flash("Passwords must match!")
      return redirect("/MyProfile")

    

    successful= update_user_account(data)

    
      
    if not successful:
      flash('Update failed: Account could not be updated.')
      return redirect("/MyProfile" )
    
    flash("Your account has been successfully updated.")
    
    return redirect('/MyAccount')
  
  flash("No Data has been captured.")
  return redirect('/MyProfile')






@user_views.route('/deleteUser', methods=['POST'])
@login_required
def delete_user():
  
  user= get_current_user()
  if user!= None :
    successful = delete_acc()
    

    if successful:
        
        flash("Your account has been successfully deleted.")
    else:
    
        flash("You failed to delete your account")
        return redirect (request.referrer)
  
  return redirect("/")





#Testing routes
@user_views.route('/users', methods=['GET'])
def get_user_page():
    users = User.query.all()
    users= [user.toDict() for user in users]
    return jsonify(users)
    return render_template('users.html', users=users)

@user_views.route('/r', methods=['GET'])
def all_rooms():
    rooms= get_all_rooms()
    rooms = [room.toDict() for room in rooms]
    return jsonify(rooms)




#template Routes
@user_views.route('/api/users')
def client_app():
    users = User.query.all()
    if not users:
        return jsonify([])
    
    return jsonify(users)

@user_views.route('/static/users')
def static_user_page():
  return send_from_directory('static', 'static-user.html')