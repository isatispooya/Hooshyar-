from django.db import models
from django.utils.timezone import now
from django.utils import timezone


class Auth (models.Model) :
    username = models.CharField(max_length=150)
    name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=200)
    national_code = models.CharField(max_length=200)
    mobile = models.CharField(max_length=200,unique=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    password = models.CharField(max_length=800)
    agreement = models.BooleanField(default=False)
    date_birth = models.DateField(null=True, blank=True)
    date_last_act = models.DateTimeField(default=timezone.now)
   
    def __str__(self):
        username = self.username if self.username else "NoUsername"
        national_code = self.national_code if self.national_code else "NoNationalCode"
        return f'{username} {national_code}'
    


class Otp (models.Model) :
    mobile = models.CharField(max_length=200) 
    code  = models.IntegerField ()
    date = models.DateTimeField (auto_now_add = True)



class Consultant (models.Model) :
    name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=200)
    national_code = models.CharField(max_length=200)
    phone = models.CharField(max_length=200)
    email = models.EmailField(unique=True , null=True , blank=True)
    rank = models.IntegerField()
    postion = models.CharField(max_length=100)
    profile_photo = models.ImageField(upload_to='Static/images/' , blank=True, null=True)

    def __str__(self):
        return f'{self.name} - {self.last_name}'


