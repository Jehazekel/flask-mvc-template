from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from App.main import app
from App.models import db
from sqlalchemy.exc import IntegrityError
import csv
import json
manager = Manager(app)
migrate = Migrate(app, db)

from App.models import User, Customer, Room

# add migrate command
manager.add_command('db', MigrateCommand)

# initDB command
@manager.command
def initDB():
    db.create_all(app=app)

    # add code to parse csv, create and save room objects
    with open("App/rooms.csv", "r") as csv_file:
        data = csv.DictReader(csv_file)

        for row in data:
            room= Room(roomType=row["type"], roomRate= row["roomRate"], roomNumber= row["roomNumber"])


            try:
                db.session.add(room)
                db.session.commit() 
            
            except IntegrityError:
                db.session.rollback()
                print("\n\nRoom Already Exists\n\n")

    make_users()  
    print("Database Initialized!")

    



# serve command
@manager.command
def serve():
    print('Application running in '+app.config['ENV']+' mode')
    app.run(host='0.0.0.0', port=8080, debug=app.config['ENV']=='development')

@manager.command
def make_users():
    print(" Creating User Bob\n\n")        
    bob = User( email='bob@gmail.com')
    bob.set_id()
    bob.set_password( 'bobpass')
    print("Bob id: " + str(bob.id) )
    print("\n\n PASSWORD: " + bob.password)
    customer1= Customer(email= 'bob@gmail.com', firstName= 'bob', lastName= 'smith', phoneNumber= 123456789, country='Trinidad', address= 'Bob Avenue')
    
    rob = User( email='rob@gmail.com')
    rob.set_id()
    rob.set_password( 'robpass')
    print("\n\nRob Password: " + rob.password)
    customer2= Customer(email= 'rob@gmail.com', firstName= 'rob', lastName= 'smith', phoneNumber= 123456789, country='Trinidad', address= 'Rob Avenue')
    #bob = User(first_name="Bob", last_name="Smith")
    #sally = User(first_name="Sally", last_name="Smith")
    #rob = User(first_name="jerry", last_name="Smith")
    
    try:
        db.session.add(bob)
        db.session.add(customer1)
        db.session.add(rob)
        db.session.add(customer2)
        db.session.commit()

    except IntegrityError:
                db.session.rollback()
                print("\n\nUser Already Exists\n\n")    
        

    print(" created users")




if __name__ == "__main__":
    manager.run()
