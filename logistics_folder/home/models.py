from django.db import models


class user(models.Model):
    S_No = models.IntegerField(primary_key=True)
    Username = models.CharField(max_length=50)
    Full_Name = models.CharField(max_length=100, null=True)
    Password = models.CharField(max_length=50)
    Email = models.CharField(max_length=50, null=True)
    Mobile = models.CharField(max_length=20, null=True)
    Role = models.CharField(max_length=20)
    Pass_Hash = models.CharField(max_length=256)

    class Meta:
        db_table = 'user'


class places(models.Model):
    S_No = models.IntegerField(primary_key=True)
    Name = models.CharField(max_length=100, null=True)
    Nearby = models.TextField(null=True)

    class Meta:
        db_table = 'places'


class bookings(models.Model):
    S_No = models.IntegerField(primary_key=True)
    Order_Id = models.CharField(max_length=50)
    Username = models.CharField(max_length=100)
    Source = models.CharField(max_length=100)
    Destination = models.CharField(max_length=100)
    Date = models.CharField(max_length=20)
    Time = models.CharField(max_length=20)
    No_Of_Persons = models.IntegerField(default=0)
    Allocated_Persons = models.IntegerField(default=0)
    Admin_Accept_Status = models.IntegerField(default=0)
    Pay_Status = models.IntegerField(default=0)
    Refund_Status = models.CharField(null=True,max_length=100)
    Journey_Status = models.CharField(choices=[('Ongoing','Ongoing'),('Cancelled','Cancelled'),('Completed','Completed')],default="Ongoing",max_length=50)
    Bus_No = models.CharField(max_length=20,null=True)
    Code = models.CharField(max_length=10,null=True)
    Verify_Status = models.CharField(null=True,max_length=100)
    Completion_Status = models.CharField(null=True,max_length=100)

    class Meta:
        db_table = 'bookings'


class driver(models.Model):
    S_No = models.IntegerField(primary_key=True)
    Username = models.CharField(max_length=50)
    Status = models.CharField(choices=[('Available','Available'),('On Trip','On Trip'),('Unavailable','Unavailable')],default="Available",max_length=50)
    Bus_No = models.CharField(max_length=25,null=True)
    Status_Time = models.DateField(auto_now=True)
    Current_Location = models.CharField(max_length=50,null=True)
    Available_Seats = models.IntegerField(default=12)

    class Meta:
        db_table = 'driver'

