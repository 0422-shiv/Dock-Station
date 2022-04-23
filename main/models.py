from asyncio.windows_events import NULL
from django.db import models
from django.contrib.auth.models import User
from geopy.geocoders import Nominatim

class UserOTP(models.Model):
    user = models.ForeignKey(User, on_delete= models.CASCADE)
    time_st = models.DateTimeField(auto_now=True)
    otp = models.PositiveSmallIntegerField()


class DockStation(models.Model): 
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=200) 
    postcode = models.CharField(max_length=100) 
    landmark = models.TextField(blank=True)
    image = models.CharField(max_length=500,null=True)
    total_docks = models.IntegerField()
    bikes_availible = models.IntegerField()
    dropoff_docks = models.IntegerField()
    latitude = models.DecimalField(max_digits=22, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=22, decimal_places=6, blank=True, null=True)



    def __str__(self):
        return self.name