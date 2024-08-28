from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site

from authentification import settings
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail, EmailMessage

from .token import generatorToken

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
        MyUser.is_active = False
        MyUser.save()
        messages.success(request, 'your account was create ')
        
        # Envoie de email
        subject = "Welcome in ESCANOR System"
        message = "Welcome  " + MyUser.first_name + " " + MyUser.last_name + "\n we are happy to have you among us!!! \n Thanks and have a good time!!! "
        from_email = settings.EMAIL_HOST_USER
        to_list = [MyUser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=False)
        
        #generate & confirm email
        current_site = get_current_site(request)
        email_subject = "Confirm your email in ESCANOR System"
        messageConfirm = render_to_string("emailConfirm.html", {
            'name': MyUser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(MyUser.pk)),
            'token': generatorToken.make_token(MyUser),
        })
        
        email = EmailMessage(
            email_subject,
            messageConfirm,
            settings.EMAIL_HOST_USER,
            [MyUser.email],
        )
        
        email.fail_silently = False
        email.send()
        
        return redirect('login')
    
    return render(request, 'app/register.html')

def connection(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        
        my_user = User.objects.get(username=username)
        
        if user is not None:
            login(request, user)
            firstname = user.first_name
            return render(request, 'app/index.html', {'firstname':firstname})
        
        elif my_user.is_active == False:
            messages.error(request, 'your account is not active')
            
        else:
           messages.error(request, 'Wrong authenticate ')
           return redirect('login')
    return render(request, 'app/login.html')
            

def deconnection(request):
    logout(request)
    messages.success(request, 'your are not connecte')
    return redirect('home')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and generatorToken.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your  account is now active.")
        return redirect('login')
    else:
        messages.error(request, "Your  account is not  active try later thanks")
        return redirect('home')