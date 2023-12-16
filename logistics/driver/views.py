from django.http import HttpResponse
from django.shortcuts import render,redirect
from home.models import user,driver,bookings,places
from datetime import date
from django.contrib.auth.hashers import make_password, check_password

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


def driver_dashboard(request):
    sess = session_check(request)
    if sess[0]:
        username = sess[1]
        locations = places.objects.all()
        driver_obj = driver.objects.filter(Username = username)
        driver_status = 'Available'
        driver_bus_no = None
        driver_current_location = None
        if len(driver_obj) == 0:
            driver.objects.create(Username = username,Status = 'Available')
        else:
            for obj in driver_obj:
                driver_status = obj.Status
                driver_bus_no = obj.Bus_No
                driver_current_location = obj.Current_Location
                status_date = str(obj.Status_Time).split(' ')[0]
                if str(date.today()) != status_date:
                    obj.Status = 'Available'
                    obj.save()
        if var_check(request,"Action") == "Verify":
            order_id = request.POST['Order_Id']
            code = request.POST['Code']
            Orders = bookings.objects.filter(Order_Id = order_id)
            for order in Orders:
                count = 1
                for codes in order.Code.split(','):
                    verification_code,bus_no = codes.split('-')
                    if verification_code == code and bus_no == driver_bus_no:
                        count = 0
                        buses = order.Verify_Status.split(',')
                        for bus in buses:
                            if bus.find(driver_bus_no) != -1:
                                break
                            count += 1
                        buses[count] = buses[count].replace('Not_Verified','Verified',1)
                        order.Verify_Status = ','.join(buses)
                        order.save()
        if var_check(request,"Action") == "Drop":
            order_id = request.POST['Order_Id']
            Orders = bookings.objects.filter(Order_Id = order_id)
            for order in Orders:
                index = order.Completion_Status.find(driver_bus_no)
                order.Completion_Status = order.Completion_Status[0:index-14] + 'Completed' + order.Completion_Status[index-1:]
                if order.Completion_Status.find('Not_Completed') == -1:
                    order.Journey_Status = 'Completed'
                order.save()
                for bus in order.Bus_No.split(','):
                    if bus.split('-')[1] == driver_bus_no:
                        allocated_persons = bus.split('-')[0]
                bus_obj = driver.objects.get(Bus_No = driver_bus_no)
                bus_obj.Available_Seats += int(allocated_persons)
                bus_obj.save()
        if var_check(request,"Set_Status"):
            status = var_check(request,'Status')
            driver_status = status
            for obj in driver_obj:
                obj.Status = status
                if status == "Unavailable":
                    obj.Current_Location = None
                obj.save()
        if var_check(request,"Set_Bus_No"):
            bus_no = var_check(request,'Bus_No')
            if bus_no == '':
                bus_no = None
            driver_bus_no = bus_no
            for obj in driver_obj:
                obj.Bus_No = bus_no
                obj.save()
        if var_check(request,"Update_Current_Location"):
            location = var_check(request,'Current_Location')
            if location == "":
                location = None
            driver_current_location = location
            for obj in driver_obj:
                obj.Current_Location = location
                obj.save()
        if driver_bus_no != None:
            today = str(date.today())
            today_list = bookings.objects.raw('SELECT * FROM `bookings` WHERE Date = "' + today + '" AND (Journey_Status = "Ongoing" OR Journey_Status = "Completed") AND Admin_Accept_Status = 1 AND Pay_Status = 1')
            order_ids = []
            for journey in today_list:
                if journey.Bus_No != None:
                    for bus in journey.Bus_No.split(','):
                        try:
                            if bus.split('-')[1] == driver_bus_no:
                                order_ids.append(journey.Order_Id)
                                break
                        except:
                            pass
            ids = ""
            completed_ids = ""
            for id in order_ids:
                today_not_completed = bookings.objects.get(Order_Id = id)
                for bus in today_not_completed.Completion_Status.split(','):
                    if bus.split('-')[0] == "Not_Completed" and bus.split('-')[1] == driver_bus_no:
                        ids += "'" + id + "'" + ","
            for id in order_ids:
                today_completed = bookings.objects.get(Order_Id = id)
                for bus in today_completed.Completion_Status.split(','):
                    if bus.split('-')[0] == "Completed" and bus.split('-')[1] == driver_bus_no:
                        completed_ids += "'" + id + "'" + ","
            allocated_persons = {}
            if ids != "":
                ids = ids[:len(ids)-1]
                passenger_list = bookings.objects.raw("SELECT bookings.S_No,bookings.order_id AS Order_id,bookings.Username AS Username,bookings.Source AS Source,bookings.Destination AS Destination,bookings.Date AS Date,bookings.Time AS Time,bookings.Verify_Status AS Verify_Status,user.Full_Name AS Full_Name FROM bookings LEFT JOIN user ON bookings.Username = user.Username WHERE bookings.Order_Id IN (" + ids + ")")
                for passenger in passenger_list:
                    passenger.Date = format_date(passenger.Date)
                    for bus in passenger.Bus_No.split(','):
                        if bus.split('-')[1] == driver_bus_no:
                            allocated_persons[passenger.Order_Id] = bus.split('-')[0]
            if completed_ids != "":
                completed_ids = completed_ids[:len(completed_ids)-1]
                completed_list = bookings.objects.raw("SELECT bookings.S_No,bookings.order_id AS Order_id,bookings.Username AS Username,bookings.Source AS Source,bookings.Destination AS Destination,bookings.Date AS Date,bookings.Time AS Time,user.Full_Name AS Full_Name FROM bookings LEFT JOIN user ON bookings.Username = user.Username WHERE bookings.Order_Id IN (" + completed_ids + ")")
                for passenger in completed_list:
                    passenger.Date = format_date(passenger.Date)
                    for bus in passenger.Bus_No.split(','):
                        if bus.split('-')[1] == driver_bus_no:
                            allocated_persons[passenger.Order_Id] = bus.split('-')[0]
        if driver_bus_no == None:
            return render(request, 'driver_dashboard.html', {'Username': username,'Locations':locations,'Status':driver_status,'Current_Location':driver_current_location})
        else:
            try:
                return render(request, 'driver_dashboard.html', {'Username': username,'Locations':locations,'Status':driver_status,'Current_Location':driver_current_location,'Bus_No':driver_bus_no,'Passenger_List':passenger_list,'Completed_List':completed_list,'Allocated_Persons':allocated_persons})
            except:
                pass
            try:
                return render(request, 'driver_dashboard.html', {'Username': username,'Locations':locations,'Status':driver_status,'Current_Location':driver_current_location,'Bus_No':driver_bus_no,'Passenger_List':passenger_list,'Allocated_Persons':allocated_persons})
            except:
                pass
            try:
                return render(request, 'driver_dashboard.html', {'Username': username,'Locations':locations,'Status':driver_status,'Current_Location':driver_current_location,'Bus_No':driver_bus_no,'Completed_List':completed_list,'Allocated_Persons':allocated_persons})
            except:
                pass
            return render(request, 'driver_dashboard.html', {'Username': username,'Locations':locations,'Status':driver_status,'Current_Location':driver_current_location,'Bus_No':driver_bus_no})
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
        return render(request, 'driver_profile.html', {'Username': username, 'Full_Name': fullname, 'Email': email, 'Mobile': mobile,'Password':password})
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

            driver_obj = user.objects.get(Username=username)
            driver_obj.Full_Name = fullname
            driver_obj.Email = email
            driver_obj.Mobile = mobile
            driver_obj.Password = password
            driver_obj.Pass_Hash = make_password(password)
            driver_obj.save()
            request.session['Full_Name'] = fullname
            request.session['Email'] = email
            request.session['Mobile'] = mobile
            request.session['Password'] = password
        return HttpResponse('<script>alert("Profile Details Updated!");location.replace("/driver/profile/")</script>')
    else:
        return HttpResponse("<script>alert('Session Ended!Please Login Again!');location.replace('/auth/login_page/')</script>")

'''
sess = session_check(request)
    if sess[0]:
        username = sess[1]
        return render(request, 'driver_dashboard.html', {'Username': username})
    else:
        return HttpResponse("<script>alert('Session Ended!Please Login Again!');location.replace('/auth/login_page/')</script>")
'''