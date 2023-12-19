from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.hashers import make_password, check_password
import pandas as pd
import os
from django.core.files.storage import FileSystemStorage
from home.models import user

# Create your views here.


def password(text):
    hashed_password = make_password(text)
    return hashed_password


def Import_Excel_pandas(request):

    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        exceldata = pd.read_excel(filename)
        dbframe = exceldata
        i = 1
        for dbframe in dbframe.itertuples():
            obj = {}
            obj['Username'] = dbframe.Username
            obj['Full_Name'] = dbframe.Full_Name
            obj['Password'] = dbframe.Password
            if dbframe.Email == "":
                obj['Email'] = None
            else:
                obj['Email'] = dbframe.Email
            if dbframe.Mobile == "":
                obj['Mobile'] = None
            else:
                obj['Mobile'] = dbframe.Mobile
            if dbframe.Role == "":
                obj['Role'] = None
            else:
                obj['Role'] = dbframe.Role
            obj['Pass_Hash'] = password(dbframe.Password)
            obj = user.objects.create(S_No = i,Username=obj['Username'],Full_Name=obj['Full_Name'], Password=obj['Password'],
                                      Email=obj['Email'], Mobile=obj['Mobile'], Role=obj['Role'], Pass_Hash=obj['Pass_Hash'])
            i += 1
        return HttpResponse("<script>alert('Successfully Imported!!')</script>")
    return render(request, 'Import_excel_db.html', {})
