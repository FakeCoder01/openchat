from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import Profile
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
import json, PyPDF2
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from .file_handler import file_upload_handler

# Create your views here.

def home(request):
    return render(request, 'home.html')

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


def handleFileUpload(request):
    if request.method == 'POST' and request.FILES['pdf_file'] and request.POST['room_id']:
        uploaded_file = request.FILES['pdf_file']
        room_id = str(request.POST['room_id'])
        if uploaded_file.name.endswith('.pdf'):
            with uploaded_file.open('rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                num_pages = len(pdf_reader.pages)
                if num_pages > 20:
                    return JsonResponse(json.dumps({
                        "status_code" : 402,
                        "message" : "FAIL : max_size_exceeded (max 5 pages)"
                    }), safe=False)
                fs = FileSystemStorage()
                filename = fs.save(f"pdf/{room_id}.pdf", uploaded_file)
                if file_upload_handler(room_id):
                    return JsonResponse(json.dumps({
                        "status_code" : 200,
                        "message" : "File Uploaded",
                        "user_msg" : f"Your file <b>'{uploaded_file.name}'</b> has been uploaded. You can now chat with it.",
                        "redirect_url" : f"/chat?state={request.POST['room_id']}"
                    }), safe=False)
        return JsonResponse(json.dumps({
            "status_code" : 403,
            "message" : "FAIL : file_not_pdf"
        }), safe=False) 
    return JsonResponse(json.dumps({
        "status_code" : 403,
        "message" : "FAIL"
    }), safe=False) 


def login_user(request):
    if request.method == 'POST':
        username = request.POST['email']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            if not Profile.objects.filter(user=user).exists():
                messages.success(request, "Account not suitable")
                return redirect('/login')
            messages.success(request, "Login successful")
            return redirect('/')
        messages.error(request, "Invalid credentials")        
        return redirect("/login?msg=invalid credentials")    
    return render(request, 'login.html')
