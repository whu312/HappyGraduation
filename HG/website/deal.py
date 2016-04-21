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
from days import *

def CreateRepayItem(onecontract):
    thisproduct = onecontract.thisproduct
    repaycycle = thisproduct.repaycycle
    intmoney = float(onecontract.money)
    if repaycycle.cycletype == 1: #once
        if thisproduct.closedtype == 'm':
            totalmoney = intmoney + intmoney*float(thisproduct.rate)/1200*thisproduct.closedperiod
        elif thisproduct.closedtype == 'd':
            totalmoney = intmoney + intmoney*float(thisproduct.rate)/36500*thisproduct.closedperiod
        thisrepayitem = repayitem(repaydate=onecontract.enddate,repaymoney=str(totalmoney),repaytype=3,
                status=1,thiscontract=onecontract)
        thisrepayitem.save()
    elif repaycycle.cycletype == 2: #every month
        thisdate = datetime.datetime.strptime(onecontract.enddate,'%Y-%m-%d').date()
        monthmoney = intmoney + intmoney*float(thisproduct.rate)/1200
        lastrepayitem = repayitem(repaydate=onecontract.enddate,repaymoney=str(monthmoney),repaytype=2,
                status=1,thiscontract=onecontract)
        lastrepayitem.save()
        monthmoney -= intmoney
        thisdate = getPreDay(thisdate,1,0)
        startdate = datetime.datetime.strptime(onecontract.startdate,'%Y-%m-%d').date()
        tmpdate = getNextDay(startdate,1,0)
        print "tmpdate",tmpdate
        while thisdate>tmpdate:
            monthrepayitem = repayitem(repaydate=str(thisdate),repaymoney=str(monthmoney),repaytype=1,
                status=1,thiscontract=onecontract)
            monthrepayitem.save()
            thisdate = getPreDay(thisdate,1,0)
            print thisdate
        days = getDays(startdate,thisdate)
        monthrepayitem.repaymoney = str(float(monthrepayitem.repaymoney) + intmoney*float(thisproduct.rate)/36500*days)
        monthrepayitem.save()
    
