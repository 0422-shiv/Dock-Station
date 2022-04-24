from asyncio.windows_events import NULL
import uuid
from django.db import models
from django.contrib.auth.models import User
import uuid

class UserOTP(models.Model):
    user = models.ForeignKey(User, on_delete= models.CASCADE)
    time_st = models.DateTimeField(auto_now=True)
    otp = models.PositiveSmallIntegerField()


class BicycleData(models.Model):
    name = models.CharField(max_length=20,unique=True,null=True,blank=True)
    def __str__(self):
            return self.name

class DockStation(models.Model): 
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=200) 
    postcode = models.CharField(max_length=100) 
    landmark = models.TextField(blank=True)
    image = models.CharField(max_length=500,null=True)
    total_docks = models.IntegerField()
    bikes_availible = models.IntegerField()
    dropoff_docks = models.IntegerField()
    bicycle= models.ManyToManyField(BicycleData,related_name="dock_station_bicycle")
    latitude = models.DecimalField(max_digits=22, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=22, decimal_places=6, blank=True, null=True)

    def __str__(self):
        return self.name
    
class Booking(models.Model):
    booking_postcode = models.CharField(max_length=20)
    Charges =models.FloatField()
    booking_from=models.TextField()
    booking_to=models.TextField()
    booking_time = models.TimeField()
    leave_time=  models.TimeField()
    bicycle= models.CharField(max_length=20)
    email =  models.EmailField()
    user= models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    user_address = models.TextField()
    status = models.BooleanField(default=False)
    stripe_payment_intent =  models.CharField(max_length=255,null=True,blank=True)
    bicycle_drop_status =  models.BooleanField(default=False)
    booking_date = models.DateTimeField(auto_now_add=True, null=True)
    drop_datetime= models.DateTimeField(null=True)
    
    def __str__(self) -> str:
        return self.booking_postcode

