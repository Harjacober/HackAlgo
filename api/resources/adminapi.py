
from api.resources.usersapi import UserProfile,UserUpdateProfile
from db.models import Admin








class AdminUpdateProfile(UserUpdateProfile):
    category = Admin()            

class AdminProfile(UserProfile):
    category = Admin()  
