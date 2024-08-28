from authentification import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail

# Create your views here.

def home(request):
    return render(request, 'app/index.html')

def register(request):
 
    if request.method == 'POST':
        username = request.POST['username']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        password = request.POST['password']
        password1 = request.POST['password1']
        
        if User.objects.filter(username=username):
            messages.error(request,  'Username already exists')
            return redirect('register')
        
        if User.objects.filter(email=email):
            messages.error(request,  'Email already exists')
            return redirect('register')
        
        if not username.isalnum():
            messages.error(request, 'this name must be in alphanumeric')
            return redirect('register')
        
        if password != password1:
            messages.error(request, 'you need the same password')
            return redirect('register')
        
        MyUser = User.objects.create_user(username,  email, password)
        MyUser.first_name = firstname
        MyUser.last_name = lastname
        MyUser.save()
        messages.success(request, 'your account was create ')
        
        
        subject = "Welcome in ESCANOR System"
        message = "Welcome  " + MyUser.first_name + " " + MyUser.last_name + "\n we are happy to have you among us!!! \n Thanks and have a good time!!! "
        from_email = settings.EMAIL_HOST_USER
        to_list = [MyUser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=False)
        
        return redirect('login')
    
    return render(request, 'app/register.html')

def connection(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            firstname = user.first_name
            return render(request, 'app/index.html', {'firstname':firstname})
        else:
           messages.error(request, 'Wrong authenticate ')
           return redirect('login')
    return render(request, 'app/login.html')
            

def deconnection(request):
    logout(request)
    messages.success(request, 'your are not connecte')
    return redirect('home')