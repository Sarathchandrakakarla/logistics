from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from .models import user
# Create your views here.


def gen_password(text):
    hashed_password = make_password(text)
    return hashed_password


def signin(request):
    if request.method == "POST":
        id = request.POST['Username']
        password = request.POST['Password']
        user_list = user.objects.filter(Username=id).first()
        if user_list is None:
            return HttpResponse("<script>alert('Invalid User!!');history.back()</script>")
        else:
            Pass_Hash = user_list.Pass_Hash
            if not check_password(password, Pass_Hash):
                return HttpResponse("<script>alert('Incorrect Password!!');history.back()</script>")
            else:
                request.session['Username'] = id
                request.session['Full_Name'] = user_list.Full_Name
                request.session['Email'] = user_list.Email
                request.session['Mobile'] = user_list.Mobile
                request.session['Password'] = password
                if user_list.Role == "Admin":
                    return redirect('/admin/')
                elif user_list.Role == "User":
                    return redirect('/user/')
                elif user_list.Role == "Driver":
                    return redirect('/driver/')
                # return HttpResponse("<script>alert('Login Success!!');location.replace('/auth/login_page/');</script>")


def signup(request):
    if request.method == "POST":
        username = request.POST['Username']
        user_list = user.objects.filter(Username=username)
        if len(user_list) != 0:
            return HttpResponse("<script>alert('Username Already Exists!!');history.back()</script>")
        else:
            fullname = request.POST['Full_Name']
            password = request.POST['Password']
            email = request.POST['Email']
            mobile = request.POST['Mobile']
            pass_hash = gen_password(password)
            obj = user.objects.create(Username=username, Full_Name=fullname, Password=password,
                                      Email=email, Mobile=mobile, Role="User", Pass_Hash=pass_hash)
            return HttpResponse("<script>alert('Thanks for Signing Up!!');location.replace('/auth/login_page/');</script>")
