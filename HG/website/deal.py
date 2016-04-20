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
import days

def CreateRepayItem(onecontract):
    thisproduct = onecontract.thisproduct
    repaycycle = thisproduct.repaycycle
    if repaycycle.cycletype == 1: #once
        if thisproduct.closedtype == 'm':
            totalmoney = onecontract.money + onecontract.money*float(thisproduct.rate)/12*thisproduct.closedperiod
        elif thisproduct.closedtype == 'd':
            totalmoney = onecontract.money + onecontract.money*float(thisproduct.rate)/365*thisproduct.closedperiod
        thisrepayitem = repayitem(repaydate=onecontract.enddate,repaymoney=totalmoney,repaytype=3,
                status=1,thiscontract=onecontract)
        thisrepayitem.save()
    elif repaycycle.cycletype == 2: #every month
        thisdate = datetime.datetime.strptime(onecontract.endDate,'%Y-%m-%d').date()
        monthmoney = onecontract.money + onecontract.money*float(thisproduct.rate)/12
        lastrepayitem = repayitem(repaydate=onecontract.enddate,repaymoney=monthmoney,repaytype=2,
                status=1,thiscontract=onecontract)
        lastrepayitem.save()
        thisdate = getPreDay(thisdate,1,0)
        startdate = datetime.datetime.strptime(onecontract.startDate,'%Y-%m-%d').date()
        tmpdate = getNextDay(startdate,1,0)
        while thisdate>tmpdate:
            monthrepayitem = repayitem(repaydate=str(thisdate),repaymoney=monthmoney,repaytype=1,
                status=1,thiscontract=onecontract)
            monthrepayitem.save()
            thisdate = getPreDay(thisdate,1,0)
        days = getDays(startdate,thisdate)
        monthrepayitem.money += onecontract.money + onecontract.money*float(thisproduct.rate)/365*days
        monthrepayitem.save()
    
