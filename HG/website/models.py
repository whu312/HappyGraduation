from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class users(models.Model):
    name = models.CharField(max_length = 128)
    jurisdiction = models.IntegerField()
    thisuser = models.ForeignKey(User)
