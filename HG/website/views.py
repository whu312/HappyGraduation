from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render_to_response
import sys
import datetime
from website.models import *
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
import re
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
'''
add user
'''

def testhtml(req):
	return render_to_response("base.html")
	
def index(req):
    if req.user.is_authenticated():
        a = {}
        a['user'] = req.user
        return render_to_response("home.html",a)
    else:
        return render_to_response("index.html")

