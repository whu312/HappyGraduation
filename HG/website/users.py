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

def getJurisdictions(filename="page.txt"):
    fi = open(filename,"r+")
    content = fi.read()
    lines = content.split("\n")
    j = 1
    ans = {}
    for line in lines:
        ans[line] = j
        j = j << 1
    fi.close()
    return ans

def checkjurisdiction(req,page):
    thisuser = users.objects.filter(thisuser_id=req.user.id)[0]
    limits = 0
    jurisdictions = getJurisdictions()
    if page in jurisdictions:
        limits = jurisdictions[page]
    if thisuser.jurisdiction & limits:
        return True
    return False

def checkauth(func):
    def _checkauth(req,a={}):
        if req.user.is_authenticated():
            return func(req)
        return render_to_response("index.html")
    return _checkauth

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
            user = User(username = name,email = email)
            user.set_password(passwd)
            user.save()
            mylimit = 2**31-1
            oneuser = users(name=name,username=name,jurisdiction=mylimit,thisuser=user)
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


@checkauth
def userctl(req,a={}):
    a['user'] = req.user
    jur = getJurisdictions()
    jur = sorted(jur.iteritems(), key=lambda d:d[1], reverse = False)
    a["jur"] = jur
    a['users'] = users.objects.all()
    return render_to_response("userctl.html",a)

@csrf_exempt
@checkauth
def adduser(req):
    a = {'user':req.user}
    if req.method == 'POST':
        username = req.POST.get("username","")
        password = req.POST.get("password","")
        name = req.POST.get("name","")
        email = req.POST.get("email","")
        position = req.POST.get("position","")
        check_list = req.POST.getlist("jur")
        jur = 0
        for item in check_list:
            jur += int(item)
        userexist = User.objects.filter(username = username)
        if not userexist:
            user = User(username = username, email = email)
            user.set_password(password)
            user.save()
            oneuser = users(name=name,username=username,jurisdiction=jur,thisuser=user)
            oneuser.save()
            a["add_status"] = 1
        else:
            a['user_exist'] = 1
        return userctl(req,a)

@csrf_exempt
@checkauth
def deleteuser(req):
    a = {'user':req.user}
    if req.method == 'POST':
        user_id = req.POST.get("user_id","")
        thisuser = users.objects.filter(thisuser_id=int(user_id))[0]
        curuser = thisuser.thisuser
        thisuser.delete()
        curuser.delete()
        return userctl(req,a)
