import base64
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import redirect, render
import requests
from home.models import user, places, bookings
import random
import string
import stripe

# Check Variables and Sessions


def session_check(request):
    if request.session.has_key('Username'):
        username = request.session['Username']
        return [True, username]
    else:
        return [False]


def var_check(request, var_name):
    try:
        request.POST[var_name]
        return request.POST[var_name]
    except:
        return False


def format_date(date):
    date = date.split('-')
    temp = date[0]
    date[0] = date[2]
    date[2] = temp
    date = '-'.join(date)
    return date


def generate_order_id(size=5, chars=string.ascii_lowercase + string.digits):
    order_id = ''.join(random.choice(chars) for _ in range(size))
    return 'hst_' + order_id

stripe.api_key = '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'
def create_checkout_session():
  session = stripe.checkout.Session.create(
    line_items=[{
      'price_data': {
        'currency': 'inr',
        'product_data': {
          'name': 'T-shirt',
        },
        'unit_amount': 3000,
      },
      'quantity': 1,
    }],
    mode='payment',
    #payment_method_types=['paypal'],
    payment_method_configuration= 'pmc_1OFJ0ASFec7g44XJ8Tm1q23W',
    success_url='http://127.0.0.1:8000/user/',
    cancel_url='https://viswatejaschools.com/',
  )

  return session.url

'''         Views       '''

'''         User       '''


def user_dashboard(request):
    sess = session_check(request)
    if sess[0]:
        username = sess[1]
        places_list = places.objects.all()
        hours = []
        for hour in range(8,24):
            if(hour < 10):
                hours.append("0"+str(hour))
            else:
                hours.append(str(hour))
        minutes = ['00','30']

        if var_check(request, "Book"):
            if not var_check(request, "Route_Type"):
                source = request.POST['From_Sel']
                destination = request.POST['To']
            else:
                source = request.POST['From']
                destination = request.POST['To_Sel']
            date = request.POST['Date']
            time = request.POST['Hours'] + ':' + request.POST['Minutes']
            no_of_persons = request.POST['No_Of_Persons']
            booking = bookings.objects.filter(
                Source=source, Destination=destination, Date=date, Username=username)
            if len(booking) != 0:
                return HttpResponse('<script>alert("Only one Booking is allowed on same day for same arrival place and destination place");history.back()</script>')
            else:
                order_id = generate_order_id()
                while len(bookings.objects.filter(Order_Id=order_id)) != 0:
                    order_id = generate_order_id()
                obj = bookings.objects.create(Order_Id=order_id, Username=username, Source=source, Destination=destination,
                                              Date=date, Time=time,No_Of_Persons = no_of_persons)
                return render(request, 'user_dashboard.html', {'Username': username, 'Colleges': places_list, 'Booked': True})
        return render(request, 'user_dashboard.html', {'Username': username, 'Colleges': places_list,'Hours':hours,'Minutes':minutes})
    else:
        return HttpResponse("<script>alert('Session Ended!Please Login Again!');location.replace('/auth/login_page/')</script>")


def logout(request):
    del request.session['Username']
    return redirect('/')


def profile(request):
    sess = session_check(request)
    if sess[0]:
        username = sess[1]
        fullname = request.session['Full_Name']
        email = request.session['Email']
        mobile = request.session['Mobile']
        password = request.session['Password']
        return render(request, 'user_profile.html', {'Username': username, 'Full_Name': fullname, 'Email': email, 'Mobile': mobile,'Password':password})
    else:
        return HttpResponse("<script>alert('Session Ended!Please Login Again!');location.replace('/auth/login_page/')</script>")


def save(request):
    sess = session_check(request)
    if sess[0]:
        username = sess[1]
        if request.method == "POST":
            fullname = request.POST['Full_Name'].strip()
            email = request.POST['Email'].strip().lower()
            mobile = request.POST['Mobile'].strip()
            password = request.POST['Password'].strip()

            user_obj = user.objects.get(Username=username)
            user_obj.Full_Name = fullname
            user_obj.Email = email
            user_obj.Mobile = mobile
            user_obj.Password = password
            user_obj.save()
            request.session['Full_Name'] = fullname
            request.session['Email'] = email
            request.session['Mobile'] = mobile
            request.session['Password'] = password
        return HttpResponse('<script>alert("Profile Details Updated!");location.replace("/user/profile/")</script>')
    else:
        return HttpResponse("<script>alert('Session Ended!Please Login Again!');location.replace('/auth/login_page/')</script>")


def journeys(request):
    sess = session_check(request)
    if sess[0]:
        username = sess[1]
        if var_check(request, "Journey_Type"):
            journey_type = var_check(request, "Journey_Type")
            if (journey_type == "Pending"):
                journey_list = bookings.objects.filter(
                    Username=username, Admin_Accept_Status=0,Journey_Status = 'Ongoing')
                print(journey_list)
            elif (journey_type == "Accepted"):
                journey_list = bookings.objects.filter(
                    Username=username, Admin_Accept_Status=1,Journey_Status = 'Ongoing')
            elif (journey_type in ['Rejected','Cancelled','Completed']):
                journey_list = bookings.objects.filter(
                    Username=username, Journey_Status=journey_type)
            for i in journey_list:
                i.Date = format_date(i.Date)
            return render(request, 'journeys.html', {'Username': username, 'Journey_List': journey_list, 'Journey_Type': journey_type})
        if var_check(request, "Cancel"):
            order_id = request.POST['Order_Id']
            booking = bookings.objects.get(Order_Id = order_id, Username=username)
            if booking.Pay_Status == 1:
                booking.Refund_Status = "To_Be_Refunded"
            booking.Journey_Status = "Cancelled"
            booking.save()
            return render(request, 'journeys.html', {'Username': username, 'Cancel_Status': True})
        return render(request, 'journeys.html', {'Username': username})
    else:
        return HttpResponse("<script>alert('Session Ended!Please Login Again!');location.replace('/auth/login_page/')</script>")


def payment(request):
    sess = session_check(request)
    if sess[0]:
        username = sess[1]
        if var_check(request,'Pay'):
            order_id = request.POST['Order_Id']
            order_details = bookings.objects.filter(Order_Id = order_id)
            for order in order_details:
                redirecturl = create_checkout_session()
                return redirect(redirecturl)
        if var_check(request, "Cancel"):
            order_id = request.POST['Order_Id']
            booking = bookings.objects.get(Order_Id = order_id, Username=username)
            booking.Journey_Status = "Cancelled"
            booking.save()
            return render(request, 'payment.html', {'Username': username, 'Cancel_Status': True})

        not_paid_list = bookings.objects.filter(
            Username=username, Pay_Status=0,Journey_Status = 'Ongoing').values()
        for order in not_paid_list:
            order['Date'] = format_date(order['Date'])
        return render(request, 'payment.html', {'Username': username, 'Orders': not_paid_list})
    else:
        return HttpResponse("<script>alert('Session Ended!Please Login Again!');location.replace('/auth/login_page/')</script>")

'''
    sess = session_check(request)
    if sess[0]:
        username = sess[1]
        return render(request, 'user_dashboard.html', {'Username': username})
    else:
        return HttpResponse("<script>alert('Session Ended!Please Login Again!');location.replace('/auth/login_page/')</script>")

'''
