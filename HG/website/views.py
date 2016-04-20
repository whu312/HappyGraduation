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
        thislog = loginfo(info="new contract with id=%d" % (thiscontract.id),thisuser=req.user)
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
        thislog = loginfo(info="change contract with id=%d from status=%s to %d" % (thiscontract.id,status,initstatus),thisuser=req.user)
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

