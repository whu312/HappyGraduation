from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class users(models.Model):
    name = models.CharField(max_length = 128)
    jurisdiction = models.IntegerField()
    thisuser = models.ForeignKey(User)
class cycle(models.Model):
    name = models.CharField(max_length = 128)
class product(models.Model):
    name = models.CharField(max_length = 128)
    rate = models.CharField(max_length = 16)
    repaycycle = models.ForeignKey(cycle)
    closedtype = models.CharField(max_length = 16)
    closedperiod = models.IntegerField()
class field(models.Model):
    name = models.CharField(max_length = 128)
    address = models.CharField(max_length = 128)
    tel = models.CharField(max_length = 128)
class party(models.Model):
    name = models.CharField(max_length = 128)
    thisfield = models.ForeignKey(field)
class manager(models.Model):
    name = models.CharField(max_length = 128)
    tel = models.CharField(max_length = 32)
    number = models.CharField(max_length = 128)
    thisparty = models.ForeignKey(party) 
class contract(models.Model):
    number = models.CharField(max_length = 128)
    client_name = models.CharField(max_length = 128)
    client_idcard = models.CharField(max_length = 128)
    bank = models.CharField(max_length = 128)
    bank_card = models.CharField(max_length = 128)
    money = models.CharField(max_length = 128)
    thisproduct = models.ForeignKey(product)
    startdate = models.CharField(max_length = 32)
    enddate = models.CharField(max_length = 32)
    status = models.IntegerField()
    thismanager = models.ForeignKey(manager)
class loginfo(models.Model):
    info = models.CharField(max_length = 1024)
    thisuser = models.ForeignKey(User)
