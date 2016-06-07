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
        thisdate = datetime.datetime.strptime(onecontract.enddate,'%Y-%m-%d').date()
        startdate = datetime.datetime.strptime(onecontract.startdate,'%Y-%m-%d').date()
        if thisproduct.closedtype == 'm':
            totalmoney = intmoney + intmoney*float(thisproduct.rate)/1200*thisproduct.closedperiod
            leftdays = getDays(getNextDay(startdate,thisproduct.closedperiod,0),thisdate)
            totalmoney += intmoney*float(thisproduct.rate)/36500*leftdays
        elif thisproduct.closedtype == 'd':
            totalmoney = intmoney + intmoney*float(thisproduct.rate)/36500*thisproduct.closedperiod
            leftdays = getDays(getNextDay(startdate,0,thisproduct.closedperiod),thisdate)
            totalmoney += intmoney*float(thisproduct.rate)/36500*leftdays
            
        thisrepayitem = repayitem(repaydate=onecontract.enddate,repaymoney=str(int(totalmoney+0.5)),repaytype=3,
                status=1,thiscontract=onecontract)
        thisrepayitem.save()
    elif repaycycle.cycletype == 2: #every month
        thisdate = datetime.datetime.strptime(onecontract.enddate,'%Y-%m-%d').date()
        startdate = datetime.datetime.strptime(onecontract.startdate,'%Y-%m-%d').date()
        tmpdate1 = getNextDay(startdate,1,0)
        tmpdate2 = getNextDay(tmpdate1,1,0)
        if thisdate>=tmpdate2:
            firstmoney = intmoney + intmoney*float(thisproduct.rate)/1200
            lastrepayitem = repayitem(repaydate=onecontract.enddate,repaymoney=str(int(firstmoney+0.5)),repaytype=2,
                    status=1,thiscontract=onecontract)
            lastrepayitem.save()
            thisdate = getPreDay(thisdate,1,0)
        monthmoney = intmoney*float(thisproduct.rate)/1200
        while thisdate>=tmpdate2:
            monthrepayitem = repayitem(repaydate=str(thisdate),repaymoney=str(int(monthmoney+0.5)),repaytype=1,
                status=1,thiscontract=onecontract)
            monthrepayitem.save()
            thisdate = getPreDay(thisdate,1,0)
        if tmpdate1<=thisdate:
            tmpdate3 = getPreDay(thisdate,1,0)
            days = getDays(startdate,tmpdate3)
            lastmoney = monthmoney + intmoney*float(thisproduct.rate)/36500*days
            monthrepayitem = repayitem(repaydate=str(thisdate),repaymoney=str(int(lastmoney+0.5)),repaytype=1,
                status=1,thiscontract=onecontract)
            monthrepayitem.save()
        else:
            days = getDays(startdate,thisdate)
            lastmoney = intmoney + intmoney*float(thisproduct.rate)/36500*days
            monthrepayitem = repayitem(repaydate=str(thisdate),repaymoney=str(int(lastmoney+0.5)),repaytype=2,
                status=1,thiscontract=onecontract)
            monthrepayitem.save() 
