from flask_login import LoginManager, current_user, login_user, login_required, logout_user
import datetime
from App.models import User

''' Begin Flask Login Functions '''
login_manager = LoginManager()
@login_manager.user_loader
def load_user(user_id):
    #print("\n\nuser id is ", user_id, "\n\n\n")
    return User.query.filter_by(id=int(user_id) ).first()

#N.B. Remember me cookies are for the event a user logs out accidentally

#THE URL TO REDIRECTS USER TO IF THEY ARENT LOGGED IN
login_manager.login_view = "/loginForm"
#Store the previous page that required login...and redirects user to it if true
login_manager.use_session_for_next= False

#Duration of the login_manager remember me session cookie
login_manager.REMEMBER_COOKIE_DURATION= datetime.timedelta(minutes= 10)
#Prevents client side scripts from accessing it
login_manager.REMEMBER_COOKIE_HTTPONLY= False
#Refreshes cookie on each request: if true
login_manager.REMEMBER_COOKIE_REFRESH_EACH_REQUEST= True
''' End Flask Login Functions '''