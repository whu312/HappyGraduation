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
def test(req):
    if req.method == 'GET':
        name = req.GET.get("name",'')
        email = req.GET.get("email",'')
        passwd = req.GET.get("password",'')
        userexist = User.objects.filter(username = name)
        if not userexist:
            user = User(username = name, email = email)
            user.set_password(passwd)
            user.save()
            mylimit = 2^31-1
            oneuser = users(name=name,jurisdiction=mylimit,thisuser=user)
            oneuser.save()
        return HttpResponse("add user ok")

@csrf_exempt
def login(req):
    if req.method == 'POST':
        name = req.POST.get('lname', '')
        passwd = req.POST.get('lpasswd', '')
        wizard = auth.authenticate(username = name, password = passwd)
        if wizard:
            auth.login(req, wizard)
            a = {}
            if req.user.is_authenticated():
                a['user'] = req.user
            return render_to_response("home.html",a)
        else:
            a = {}
            a['logfail'] = True
            a['lname'] = name
            a['lpasswd'] = passwd
            return render_to_response("index.html",a)
        
def logout(req):
    auth.logout(req)
    return render_to_response("index.html")
