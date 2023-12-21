import json
import random
import string
from django.http import HttpResponse
from django.shortcuts import render,redirect
from home.models import user,driver,bookings,places
from datetime import date
from django.contrib.auth.hashers import make_password, check_password

#Check Variables and Sessions

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


def format_date(date,reverse = False):
    date = date.split('-')
    if len(date[0]) == 1:
            if int(date[0]) < 10:
                date[0] = '0' + date[0]
    if not reverse:
        if len(date[0]) == 2:
            temp = date[0]
            date[0] = date[2]
            date[2] = temp
    else:
        if len(date[2]) == 2:
            temp = date[0]
            date[0] = date[2]
            date[2] = temp
    date = '-'.join(date)
    return date


def generate_code(size=5, chars=string.digits):
    verificationcode = ''.join(random.choice(chars) for _ in range(size))
    return verificationcode


def admin_dashboard(request):
    sess = session_check(request)
    if sess[0]:
        username = sess[1]
        today = date.today()
        pending = 0
        accepted = 0
        rejected = 0
        cancelled = 0
        completed = 0
        pending = len(bookings.objects.filter(Date = today,Admin_Accept_Status = 0,Journey_Status = 'Ongoing'))
        accepted = len(bookings.objects.filter(Date = today,Admin_Accept_Status = 1,Journey_Status = 'Ongoing'))
        rejected = len(bookings.objects.filter(Date = today,Journey_Status = 'Rejected'))
        cancelled = len(bookings.objects.filter(Date = today,Journey_Status = 'Cancelled'))
        completed = len(bookings.objects.filter(Date = today,Journey_Status = 'Completed'))
        return render(request, 'admin_dashboard.html', {'Username': username,'Pending':pending,'Accepted':accepted,'Rejected':rejected,'Cancelled':cancelled,'Completed':completed})
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
        return render(request, 'admin_profile.html', {'Username': username, 'Full_Name': fullname, 'Email': email, 'Mobile': mobile,'Password':password})
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
        return HttpResponse('<script>alert("Profile Details Updated!");location.replace("/admin/profile/")</script>')
    else:
        return HttpResponse("<script>alert('Session Ended!Please Login Again!');location.replace('/auth/login_page/')</script>")


def manage_admin(request):
    sess = session_check(request)
    if sess[0]:
        username = sess[1]
        if var_check(request,"Register"):
            admin_username = request.POST['Username']
            admin_full_name = request.POST['Full_Name']
            admin_email = request.POST['Email']
            admin_mobile = request.POST['Mobile']
            admin_password = request.POST['Password']
            admin_password_hash = make_password(admin_password)
            if len(user.objects.filter(Username = admin_username,Role = 'Admin')) != 0:
                return HttpResponse('<script>alert("Admin with this Username Already Exists!");history.back();</script>')
            if admin_email != None and admin_email != "":
                user.objects.create(Username = admin_username,Full_Name = admin_full_name,Password = admin_password,Email = admin_email,Mobile = admin_mobile,Role = 'Admin',Pass_Hash = admin_password_hash)
            else:
                user.objects.create(Username = admin_username,Full_Name = admin_full_name,Password = admin_password,Mobile = admin_mobile,Role = 'Admin',Pass_Hash = admin_password_hash)
            return render(request, 'manage_admin.html', {'Username': username,'Status':'Creation_Success'})
        elif var_check(request,"Action") == "Get_Details":
            admin_username = request.POST['Username']
            try:
                admin_obj = user.objects.get(Username = admin_username,Role = 'Admin')
                if admin_obj:
                    details = ""
                    details += admin_obj.Full_Name + ','
                    if admin_obj.Email != None:
                        details += admin_obj.Email + ','
                    else:
                        details += ','
                    details += admin_obj.Mobile + ','
                    details += admin_obj.Password
                    return HttpResponse(details)
            except:
                    return HttpResponse('')
        elif var_check(request,"Update"):
            admin_username = request.POST['Username']
            try:
                admin_obj = user.objects.get(Username = admin_username,Role = 'Admin')
                admin_obj.Full_Name = request.POST['Full_Name']
                if request.POST['Email'] != "" and request.POST['Email'] != None:
                    admin_obj.Email = request.POST['Email']
                else:
                    admin_obj.Email = None
                admin_obj.Mobile = request.POST['Mobile']
                admin_obj.Password = request.POST['Password']
                admin_obj.Pass_Hash = make_password(request.POST['Password'])
                admin_obj.save()
                return render(request, 'manage_admin.html', {'Username': username,'Status':'Updation_Success'})
            except:
                pass
            return render(request, 'manage_admin.html', {'Username': username,'Status':'Updation_Failed'})
        elif var_check(request,"Delete"):
            admin_username = request.POST['Username']
            try:
                admin_obj = user.objects.get(Username = admin_username,Role = 'Admin')
                admin_obj.delete()
            except:
                return HttpResponse("<script>alert('No Admin Found with this Username!')</script>")
            return HttpResponse("<script>alert('Admin Deleted Successfully!!');location.replace('/admin/admin_create/')</script>")
        return render(request, 'manage_admin.html', {'Username': username})
    else:
        return HttpResponse("<script>alert('Session Ended!Please Login Again!');location.replace('/auth/login_page/')</script>")


'''             Passenger Views           '''
def passenger_details(request):
    sess = session_check(request)
    if sess[0]:
        username = sess[1]
        if var_check(request,"Action") == "Fetch_List":
            search_type = request.POST['Search_Type']
            search_value = request.POST['Search_Value']
            pass_list = []
            text = ""
            if search_type == "Username":
                query = user.objects.filter(Username__icontains = search_value,Role='User')
            elif search_type == "Full_Name":
                query = user.objects.filter(Full_Name__icontains = search_value,Role='User')
            elif search_type == "Mobile":
                query = user.objects.filter(Mobile__icontains = search_value,Role='User')
            for i in query:
                pass_list.append(
                    {
                     "Username":i.Username,
                     "Full_Name":i.Full_Name,
                     "Mobile":i.Mobile,
                     "Email":i.Email,
                    }
                )
            i = 1
            for passenger in pass_list:
                text += '''<tr>
                <td>'''+str(i)+'''</td>
                <td>'''+passenger["Username"]+'''</td>
                <td>'''+passenger["Full_Name"]+'''</td>
                <td>'''+passenger["Email"]+'''</td>
                <td>'''+passenger["Mobile"]+'''</td>
                </tr>'''
                i += 1
            return HttpResponse(text)
        return render(request, 'passenger/passenger_details.html', {'Username': username})
    else:
        return HttpResponse("<script>alert('Session Ended!Please Login Again!');location.replace('/auth/login_page/')</script>")


'''             Driver Views           '''
def manage_driver(request):
    sess = session_check(request)
    if sess[0]:
        username = sess[1]
        if var_check(request,"Register"):
            driver_username = request.POST['Username']
            driver_full_name = request.POST['Full_Name']
            driver_email = request.POST['Email']
            driver_mobile = request.POST['Mobile']
            driver_password = request.POST['Password']
            driver_password_hash = make_password(driver_password)
            driver_bus_no = request.POST['Bus_No']
            if len(user.objects.filter(Username = driver_username,Role = 'Driver')) != 0:
                return HttpResponse('<script>alert("Driver with this Username Already Exists!");history.back();</script>')
            if driver_email != None and driver_email != "":
                user.objects.create(Username = driver_username,Full_Name = driver_full_name,Password = driver_password,Email = driver_email,Mobile = driver_mobile,Role = 'Driver',Pass_Hash = driver_password_hash)
            else:
                user.objects.create(Username = driver_username,Full_Name = driver_full_name,Password = driver_password,Mobile = driver_mobile,Role = 'Driver',Pass_Hash = driver_password_hash)
            if driver_bus_no != "" and driver_bus_no != None:
                driver.objects.create(Username = driver_username,Status = 'Unavailable',Bus_No = driver_bus_no)
            else:
                driver.objects.create(Username = driver_username,Status = 'Unavailable')
            return render(request, 'driver/manage_driver.html', {'Username': username,'Status':'Creation_Success'})
        elif var_check(request,"Action") == "Get_Details":
            driver_username = request.POST['Username']
            try:
                driver_obj = user.objects.get(Username = driver_username,Role = 'Driver')
                if driver_obj:
                    details = ""
                    details += driver_obj.Full_Name + ','
                    if driver_obj.Email != None:
                        details += driver_obj.Email + ','
                    else:
                        details += ','
                    details += driver_obj.Mobile + ','
                    details += driver_obj.Password + ','
                    driver_bus_obj = driver.objects.get(Username = driver_username)
                    if driver_bus_obj.Bus_No != None:
                        details += driver_bus_obj.Bus_No
                    else:
                        details += ','
                    return HttpResponse(details)
            except:
                    return HttpResponse('')
        elif var_check(request,"Update"):
            driver_username = request.POST['Username']
            try:
                driver_obj = user.objects.get(Username = driver_username,Role = 'Driver')
                driver_obj.Full_Name = request.POST['Full_Name']
                if request.POST['Email'] != "" and request.POST['Email'] != None:
                    driver_obj.Email = request.POST['Email']
                else:
                    driver_obj.Email = None
                driver_obj.Mobile = request.POST['Mobile']
                driver_obj.Password = request.POST['Password']
                driver_obj.Pass_Hash = make_password(request.POST['Password'])
                driver_obj.save()
                driver_bus_obj = driver.objects.get(Username = driver_username)
                if request.POST['Bus_No'] != "" and request.POST['Bus_No'] != None:
                    driver_bus_obj.Bus_No = request.POST['Bus_No']
                else:
                    driver_bus_obj.Bus_No = None
                driver_bus_obj.save()
                return render(request, 'driver/manage_driver.html', {'Username': username,'Status':'Updation_Success'})
            except:
                pass
            return render(request, 'driver/manage_driver.html', {'Username': username,'Status':'Updation_Failed'})
        elif var_check(request,"Delete"):
            driver_username = request.POST['Username']
            try:
                driver_obj = user.objects.get(Username = driver_username,Role = 'Driver')
                driver_obj.delete()
                driver_bus_obj = driver.objects.get(Username = driver_username)
                driver_bus_obj.delete()
            except:
                return HttpResponse("<script>alert('No Driver Found with this Username!')</script>")
            return HttpResponse("<script>alert('Driver Deleted Successfully!!');location.replace('/admin/driver/create/')</script>")
        return render(request, 'driver/manage_driver.html', {'Username': username})
    else:
        return HttpResponse("<script>alert('Session Ended!Please Login Again!');location.replace('/auth/login_page/')</script>")


def driver_details(request):
    sess = session_check(request)
    if sess[0]:
        username = sess[1]
        if var_check(request,"Action") == "Fetch_List":
            search_type = request.POST['Search_Type']
            search_value = request.POST['Search_Value']
            pass_list = []
            text = ""
            if search_type == "Username":
                query = user.objects.filter(Username__icontains = search_value,Role='Driver')
            elif search_type == "Full_Name":
                query = user.objects.filter(Full_Name__icontains = search_value,Role='Driver')
            elif search_type == "Mobile":
                query = user.objects.filter(Mobile__icontains = search_value,Role='Driver')
            for i in query:
                driver_obj = driver.objects.filter(Username = i.Username)
                for j in driver_obj:
                    pass_list.append(
                        {
                        "Username":i.Username,
                        "Full_Name":i.Full_Name,
                        "Mobile":i.Mobile,
                        "Email":i.Email,
                        "Status":j.Status,
                        "Bus_No":j.Bus_No,
                        "Current_Location":j.Current_Location,
                        }
                    )
            i = 1
            for drivers in pass_list:
                text += '''
                <tr>
                    <td>'''+str(i)+'''</td>
                    <td>'''+drivers["Username"]+'''</td>
                    <td>'''+drivers["Full_Name"]+'''</td>
                    <td>'''+drivers["Email"]+'''</td>
                    <td>'''+drivers["Mobile"]+'''</td>'''
                for j in ['Status','Bus_No','Current_Location']:
                    if drivers[j] == None:
                        text += '<td>N/A</td>'
                    else:
                        text += '<td>' + drivers[j] + '</td>'
                text += '''</tr>'''
                i += 1
            return HttpResponse(text)
        return render(request, 'driver/driver_details.html', {'Username': username})
    else:
        return HttpResponse("<script>alert('Session Ended!Please Login Again!');location.replace('/auth/login_page/')</script>")
    

'''             Request Views           '''
def request_details(request):
    sess = session_check(request)
    if sess[0]:
        username = sess[1]
        locations = places.objects.all()
        drivers = user.objects.raw('SELECT user.S_No,user.Full_Name AS Full_Name,driver.Bus_No AS Bus_No,driver.Available_Seats AS Available_Seats FROM `user` LEFT JOIN `driver` ON user.Username = driver.Username WHERE user.Role = "Driver" AND driver.Status = "Available"')
        query = "SELECT user.S_No,user.Username AS Username,user.Full_Name AS Full_Name,bookings.Order_Id AS Order_Id,bookings.Source AS Departure,bookings.Destination AS Destination,bookings.Date AS Date,bookings.Time AS Time,bookings.No_Of_Persons AS No_Of_Persons,bookings.Allocated_Persons AS Allocated_Persons,bookings.Journey_Status AS Journey_Status,bookings.Admin_Accept_Status AS Admin_Accept_Status,bookings.Pay_Status AS Pay_Status,bookings.Bus_No FROM `user` JOIN `bookings` ON user.Username = bookings.Username WHERE bookings.Date = '" + str(date.today()) + "'"
        driver_names = {}
        alloted_persons = {}
        if var_check(request,"Action") == "Filter":
            data = json.loads(request.POST['Data'])
            filters = data['Filters']
            query = "SELECT user.S_No,user.Username AS Username,user.Full_Name AS Full_Name,bookings.Order_Id AS Order_Id,bookings.Source AS Departure,bookings.Destination AS Destination,bookings.Date AS Date,bookings.Time AS Time,bookings.No_Of_Persons AS No_Of_Persons,bookings.Allocated_Persons AS Allocated_Persons,bookings.Admin_Accept_Status AS Admin_Accept_Status,bookings.Journey_Status AS Journey_Status,bookings.Pay_Status AS Pay_Status,bookings.Bus_No FROM `user` JOIN `bookings` ON user.Username = bookings.Username WHERE "
            for filter in filters:
                if filter['Name'] == "date":
                    if not filter['Type'] in ['month','range','week']:
                        query += " bookings.Date = '" + format_date(filter['Value'][0]) + "'"
                    elif filter['Type'] == "month":
                        query += " CAST(bookings.Date AS DATE) BETWEEN '" + format_date('01-' + str(filter['Value'][0]) +'-' + str(filter['Value'][1])) + "' AND '" + format_date(str(filter['Value'][2]) + '-' + str(filter['Value'][0]) + '-' + str(filter['Value'][1])) + "'"
                    else:
                        query += " CAST(bookings.Date AS DATE) BETWEEN '" + format_date(filter['Value'][0]) + "' AND '" + format_date(filter['Value'][1]) + "'"
                    if filters[-1] != filter:
                        query += " AND"
                elif filter['Name'] == "location":
                    if filter['Type'] == "Departure":
                        query += " bookings.Source = '" + str(filter['Value'][0]) + "'"
                    elif filter['Type'] == "Destination":
                        query += " bookings.Destination = '" + str(filter['Value'][0]) + "'"
                    elif filter['Type'] == "Both":
                        query += " bookings.Source = '" + str(filter['Value'][0]) + "' AND bookings.Destination = '" + str(filter['Value'][1]) + "'"
                    if filters[-1] != filter:
                        query += " AND"
                elif filter['Name'] == "bus":
                    bus_obj = bookings.objects.filter(Bus_No__icontains = str(filter['Value'][0]))
                    order_ids = ""
                    for bus in bus_obj:
                        order_ids += "'" + bus.Order_Id + "',"
                    order_ids = order_ids[:len(order_ids)-1]
                    query += " bookings.Order_Id IN (" + order_ids + ")"
                    if filters[-1] != filter:
                        query += " AND"
                elif filter['Name'] == "journey":
                    query += " bookings.Journey_Status = '" + str(filter['Value'][0]) + "'"
                    if filters[-1] != filter:
                        query += " AND"
                elif filter['Name'] == "payment":
                    if filter['Value'][0] in ["To_Be_Refunded","Refunded"]:
                        query += " bookings.Refund_Status = '" + filter['Value'][0] + "'"
                    else:
                        query += " bookings.Pay_Status = " + str(filter['Value'][0])
                    if filters[-1] != filter:
                        query += " AND"
        elif var_check(request,"Action") == "Approval":
            order_id = request.POST['Order_Id']
            status = request.POST['Status']
            booking_obj = bookings.objects.get(Order_Id = order_id)
            if status == "accept":
                booking_obj.Admin_Accept_Status = 1
            else:
                booking_obj.Journey_Status = "Rejected"
            booking_obj.save()
            if status == "accept":
                return HttpResponse('true')
            else:
                return HttpResponse('false')
        elif var_check(request,"Action") == "Allocate":
            order_id = request.POST['Order_Id']
            bus_no = request.POST['Bus_No']
            no_of_persons_to_allocate = request.POST['No_Of_Persons_To_Allocate']
            bus_obj = driver.objects.get(Bus_No = bus_no)
            bus_obj.Available_Seats -= int(no_of_persons_to_allocate)
            bus_obj.save()
            booking_obj = bookings.objects.get(Order_Id = order_id)
            booking_obj.Allocated_Persons += int(no_of_persons_to_allocate)
            if booking_obj.Bus_No == None:
                booking_obj.Bus_No = no_of_persons_to_allocate + '-' + bus_no
                booking_obj.Code = generate_code() + '-' + bus_no
                booking_obj.Verify_Status = 'Not_Verified' + '-' + bus_no
                booking_obj.Completion_Status = 'Not_Completed' + '-' + bus_no
            else:
                if booking_obj.Bus_No.find(bus_no) != -1:
                    index = booking_obj.Bus_No.find(bus_no)
                    if booking_obj.Bus_No[index-3] != ',' and index != 2:
                        booking_obj.Bus_No = booking_obj.Bus_No.replace(booking_obj.Bus_No[index-3:index-1],str(int(booking_obj.Bus_No[index-3:index-1]) + int(no_of_persons_to_allocate)),1)
                    else:
                        booking_obj.Bus_No = booking_obj.Bus_No.replace(booking_obj.Bus_No[index-2:index-1],str(int(booking_obj.Bus_No[index-2:index-1]) + int(no_of_persons_to_allocate)),1)
                else:
                    booking_obj.Bus_No += ',' + no_of_persons_to_allocate + '-' + bus_no
                

                if booking_obj.Code.find(bus_no) == -1:
                    booking_obj.Code += ',' + generate_code() + '-' + bus_no
                if booking_obj.Verify_Status.find(bus_no) == -1:
                    booking_obj.Verify_Status += ',' + 'Not_Verified' + '-' + bus_no
                    booking_obj.Completion_Status += ',' + 'Not_Completed' + '-' + bus_no
            booking_obj.save()
            bus_details = ''
            for bus in booking_obj.Bus_No.split(','):
                p_count,b_num  = bus.split('-')
                driver_obj = user.objects.raw('SELECT user.S_No,user.Full_Name AS Full_Name FROM `user` JOIN `driver` ON user.Username = driver.Username WHERE driver.Bus_No = "' + b_num + '"')
                for d in driver_obj:
                    driver_name = d.Full_Name
                bus_details += p_count + ''' person(s) - ''' + b_num + '''(''' + driver_name + ''')<br>'''
            if booking_obj.No_Of_Persons == booking_obj.Allocated_Persons:
                return HttpResponse('true,' + bus_details + ',' + str(booking_obj.Allocated_Persons))
            elif booking_obj.No_Of_Persons != booking_obj.Allocated_Persons:
                return HttpResponse('false,' + bus_details + ',' + str(booking_obj.Allocated_Persons) + ',' + str(booking_obj.No_Of_Persons - booking_obj.Allocated_Persons))

        request_list = user.objects.raw(query)
        if len(request_list) == 0:
            if var_check(request,"Action") == "Filter":
                return HttpResponse('No Data Found')
        else:
            text = ""
            count = 1
            driver_names = {}
            alloted_persons = {}
            for i in request_list:
                i.Date = format_date(i.Date,True)
                if i.Pay_Status == 1:
                    pay_status = 'Paid'
                else:
                    pay_status = 'Not Paid'
                alloted_persons[i.Order_Id] = 0
                if i.Bus_No != None:
                    buses = i.Bus_No.split(',')
                    for bus in buses:
                        try:
                            alloted_persons[i.Order_Id] += int(bus.split('-')[0].strip())
                            driver_obj = driver.objects.raw('SELECT user.S_No,user.Full_Name AS Driver_Name FROM `user` JOIN `driver` ON driver.Username = user.Username WHERE driver.Bus_No = "' + bus.split('-')[1] + '"')
                            for j in driver_obj:
                                driver_names[bus.split('-')[1]] = j.Driver_Name
                        except:
                            pass
                text += '''
                <tr>
                <td>''' + str(count) + '''</td>'''
                if i.Journey_Status == "Ongoing" and i.Admin_Accept_Status == 0:
                    text += '''
                    <td class="''' + i.Order_Id + '''-approval_status">
                        <div class="buttons">
                        <button class="btn btn-success" id="'''+ i.Order_Id + '''-accept" onclick="Approval(this)">Accept</button>
                        <button class="btn btn-danger" id="'''+ i.Order_Id + '''-reject" onclick="Approval(this)">Reject</button>
                        </div>
                    </td>
                    '''
                elif i.Journey_Status == "Ongoing" and i.Admin_Accept_Status == 1 and i.Pay_Status == 1 and i.Bus_No == None and i.No_Of_Persons != alloted_persons[i.Order_Id]:
                    unallocated_persons = i.No_Of_Persons - i.Allocated_Persons
                    text += '''
                    <td class="''' + i.Order_Id + '''-approval_status">Allocate to a Bus <br>
                        <input type="number" min="1" max="''' + str(unallocated_persons) + '''" class="form-control" id="''' + i.Order_Id + '''-no_of_persons_to_allocate" oninput="valid_max(this)" value="1">
                        <select class="form-control Bus_No" name="" id="''' + i.Order_Id + '''-bus_no">
                            <option value="">-- Select Bus --</option>
                            '''
                    for d in drivers:
                        if d.Available_Seats != 0:
                            text += '''<option value="''' + d.Bus_No + '''">''' + d.Bus_No + ''' - ''' + str(d.Available_Seats) + '''(''' + d.Full_Name + ''')</option>'''
                    text += '''</select>
                        <button class="btn btn-primary" id="''' + i.Order_Id + '''-allocate_bus" onclick="Allocate_Bus(this)">
                            Allocate Bus
                        </button>
                    </td>
                    '''
                elif i.Journey_Status == "Ongoing" and i.Admin_Accept_Status == 1 and i.Pay_Status == 0:
                    text += '''
                    <td class="''' + i.Order_Id + '''-approval_status">Waiting for Payment</td>
                    '''
                else:
                    text += '''<td class="''' + i.Order_Id + '''-approval_status">No Need for Approval</td>'''
                
                text += '''<td>''' + i.Order_Id + '''</td>
                <td>''' + i.Username + '''</td>
                <td>''' + i.Full_Name + '''</td>
                <td>''' + i.Departure + '''</td>
                <td>''' + i.Destination + '''</td>
                <td>''' + format_date(i.Date,True) + '''</td>
                <td>''' + i.Time + '''</td>
                <td>''' + str(i.No_Of_Persons) + '''</td>
                <td id="''' + i.Order_Id + '''-allocated_persons">''' + str(i.Allocated_Persons) + '''</td>
                <td id="''' + i.Order_Id + '''-journey_status">''' + i.Journey_Status + '''</td>
                <td>''' + pay_status + '''</td>
                '''
                if i.Bus_No != None and len(driver_names) != 0:
                    text += '''<td id="''' + i.Order_Id + '''-allocated_bus_no">'''
                    buses = i.Bus_No.split(',')
                    for bus in buses:
                        try:
                            text += bus.split('-')[0] + ''' person(s) - ''' + bus.split('-')[1] + '''<br>(''' + driver_names[bus.split('-')[1]] + ''')<br>'''
                        except:
                            pass
                    text += '''</td>'''
                else:
                    text += '''<td id="''' + i.Order_Id + '''-allocated_bus_no">N/A</td>'''
                count += 1
        if var_check(request,"Action") == "Filter":
            return HttpResponse(text)
        if len(driver_names) != 0:
            return render(request, 'requests/request_details.html', {'Username': username,'Locations':locations,'Drivers':drivers,'Today_Requests':request_list,'Driver_Names':driver_names,'Allocated_Persons':alloted_persons})
        else:
            return render(request, 'requests/request_details.html', {'Username': username,'Locations':locations,'Drivers':drivers,'Today_Requests':request_list,'Allocated_Persons':alloted_persons})
    else:
        return HttpResponse("<script>alert('Session Ended!Please Login Again!');location.replace('/auth/login_page/')</script>")


'''
sess = session_check(request)
    if sess[0]:
        username = sess[1]
        return render(request, 'admin_dashboard.html', {'Username': username})
    else:
        return HttpResponse("<script>alert('Session Ended!Please Login Again!');location.replace('/auth/login_page/')</script>")
'''