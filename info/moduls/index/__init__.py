from flask import Blueprint

index_=Blueprint('index',__name__)

from .views import *

