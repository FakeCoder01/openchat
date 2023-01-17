from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import Profile
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
# Create your views here.


@login_required(login_url='/login')
def index(request):
    return render(request, 'index.html')




def signup_user(request):
    try:
        if request.method == 'POST':
            username = request.POST['email']
            password = request.POST['password']
            confirm_password = request.POST['confirm_password']

            if confirm_password != password:
                messages.error(request, "Password did not match")
                return redirect("/signup?res=Password did not match")
            user = User.objects.create_user(username, username, password)
            user.save()
            user = authenticate(request, username=username, password=password)

            if user:
                login(request, user)
                new_profile = Profile.objects.create(
                    user = user,
                    room_id = get_random_string(8)
                )
                messages.success(request, 'Account has been created')
                return redirect(f'/?res=account created successfully&perform=new')
            messages.error(request, 'User not logged in')
            return redirect("/signup?res=User not activated")
        return render(request, "signup.html")
    except Exception as err:
        print(err)
        messages.error(request, 'Account creation Failed')
        return redirect("/signup?res=Something went wrong")


def logout_user(request):
    logout(request)
    messages.success(request, 'Successfully logged out')
    return redirect('/')


def login_user(request):
    if request.method == 'POST':
        username = request.POST['email']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, "Login successful")
            return redirect('/')
        messages.error(request, "Invalid credentials")        
        return redirect("/login?msg=invalid credentials")    
    return render(request, 'login.html')
