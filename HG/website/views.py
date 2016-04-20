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
from deal import *

ONE_PAGE_NUM = 20
# Create your views here.

def testhtml(req):
	return render_to_response("base.html")
	
def addcycle(req):
    thiscycle = cycle(name='一次',cycletype=1)
    thiscycle.save()
    thiscycle = cycle(name='按月',cycletype=2)
    thiscycle.save()
    return HttpResponse("cycle ok")

def checkauth(func):
    def _checkauth(req):
        if req.user.is_authenticated():
            return func(req)
        return render_to_response("index.html")
    return _checkauth

@checkauth
def index(req):
    a = {'user':req.user}
    return render_to_response("home.html",a)

@csrf_exempt
@checkauth
def newcontract(req):
    if req.method == 'GET':
        a = {'user':req.user}
        return render_to_response("newcontract.html")
    elif req.method == 'POST':
        number = req.POST.get('number','')
        client_name = req.POST.get('client_name','')
        client_idcard = req.POST.get('client_idcard','')
        bank = req.POST.get('bank','')
        bank_card = req.POST.get("bank_card",'')
        product_id = req.POST.get("product_id",'')
        money = req.POST.get('money','')
        startdate = req.POST.get('startdate','')
        enddate = req.POST.get("enddate",'')
        manager_id = req.POST.get('manager_id','')
        thiscontract = contract(number=number,client_name=client_name,client_idcard=client_idcard,
                bank=bank,bank_card=bank_card,money=money,thisproduct=product_id,startdate=startdate,
                enddate=enddate,status=1,thismanager=manager_id,renewal_id=-1)
        thiscontract.save()
        thislog = loginfo(info="new contract with id=%d" % (thiscontract.id),time=str(datetime.datetime.now()),thisuser=req.user)
        thislog.save()
        
        CreateRepayItem(thiscontract)
        
        a = {'user':req.user}
        return render_to_response("home.html",a)

@csrf_exempt
@checkauth
def statuscontract(req):
    if req.method == 'POST':
        contract_id = req.POST.get("contract_id",'')
        thiscontract = contract.objects.filter(id=int(contract_id))[0]
        status = req.POST.get("status",'')
        initstatus = thiscontract.status
        thiscontract.status = int(status)
        thiscontract.save()
        thislog = loginfo(info="change contract with id=%d from status=%s to %d" % (thiscontract.id,status,initstatus),
                time=str(datetime.datetime.now()),thisuser=req.user)
        thislog.save()
        a = {'user':req.user}
        return render_to_response("home.html",a)

@checkauth
def querycontracts(req):
    if req.method == 'GET':
        try:
            thispage = int(req.GET.get("page",'1'))
        except ValueError:
            thispage = 1
            allpage = 1
        try:
            number = req.GET.get('number','')
        except ValueError:
            number = ""
        contracts = []
        a = {'user':req.user}
        a['curpage'] = str(thispage)
        if number=="":
            allpage = contract.objects.count()
            startpos = ((thispage-1)*ONE_PAGE_NUM if (thispage-1)*ONE_PAGE_NUM<allpage else allpage)
            endpos = (thispage*ONE_PAGE_NUM if thispage*ONE_PAGE_NUM<allpage else allpage)
            contracts = contract.objects.all()[startpos:endpos]
        else:
            contracts = contract.objects.filter(number=number)
        a['allpage'] = str(allpage)
        a['contracts'] = contracts
        return render_to_response("querycontracts.html",a)

#add product control and manager
@csrf_exempt
@checkauth
def newfield(req):
    a = {'user':req.user}
    if req.method == "GET":
        return render_to_response("newfield.html",a)
    elif req.method == "POST":
        name = req.POST.get("name",'')
        address = req.POST.get("address",'')
        tel = req.POST.get("tel","")
        thisfield = field(name=name,address=address,tel=tel)
        thisfield.save()
        return render_to_response("home.html",a)

@csrf_exempt
@checkauth
def newparty(req):
    a = {'user':req.user}
    if req.method == "GET":
        a["fields"] = field.objects.all()
        return render_to_response("newparty.html",a)
    elif req.method == "POST":
        name = req.POST.get("name",'')
        field_id = req.POST.get("field_id",'')
        print field_id,"aaa"
        thisparty = party(name=name,thisfield_id=field_id)
        thisparty.save()
        return render_to_response("home.html",a)
@csrf_exempt
@checkauth
def newmanager(req):
    a = {'user':req.user}
    if req.method == "GET":
        a["parties"] = party.objects.all()
        return render_to_response("newmanager.html",a)
    elif req.method == "POST":
        name = req.POST.get("name",'')
        tel = req.POST.get("tel",'')
        number = req.POST.get("number",'')
        party_id = req.POST.get("party_id","")
        thismanager = manager(name=name,tel=tel,number=number,thisparty_id=party_id)
        thismanager.save()
        return render_to_response("home.html",a) 
@csrf_exempt
@checkauth
def newproduct(req):
    a = {'user':req.user}
    if req.method == "GET":
        a["mamagers"] = manager.objects.all()
        a["cycles"] = cycle.objects.all()
        return render_to_response("newproduct.html",a)
    elif req.method == "POST":
        name = req.POST.get("name",'')
        rate = req.POST.get("rate",'')
        repaycycle_id = req.POST.get("repaycycle_id",'')
        closedtype = req.POST.get("closedtype","")
        closedperiod = req.POST.get("closedperiod","")
        thisproduct = product(name=name,rate=rate,repaycycle_id=int(repaycycle_id),
                closedtype=closedtype,closedperiod=int(closedperiod))
        thisproduct.save()
        return render_to_response("home.html",a)

