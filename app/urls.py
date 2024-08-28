from django.urls import path
from .views import home, register, connection, deconnection
urlpatterns = [
    path('', home, name='home'),
    path('register', register, name='register'),
    path('login', connection, name='login'),
    path('logout', deconnection, name='logout'),
]
