from flask import Blueprint

passport_=Blueprint('passport',__name__,url_prefix='/passport')

from .views import *