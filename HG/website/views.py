﻿from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render_to_response
import sys
import datetime
import copy
from website.models import *
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
import re
from django.views.decorators.csrf import csrf_exempt
from deal import *
from users import *
import json
from newadd import *
ONE_PAGE_NUM = 10
# Create your views here.

def testhtml(req):
    '''
    alllogs = loginfo.objects.all()
    for item in alllogs:
        pos = item.info.find("=")
        if pos==-1:
            continue
        cid = int(item.info[pos+1:])
        if item.info.find("repay")!=-1:
            try:
                item.info = "repay with %d of contract number=%s" % (cid,repayitem.objects.filter(id=cid)[0].thiscontract.number)
                item.save()
            except:
                print "repay log err"
            continue
        if item.info.find("renewal")!=-1:
            try:
                pos1 = item.info.find("contract ")+len("contract ")
                pos2 = item.info.find(" with")
                id1 = int(item.info[pos1:pos2])
                number1 = contract.objects.filter(id=id1)[0].number
                number2 = contract.objects.filter(id=cid)[0].number
                strline = "renewal contract %s with id=%s" % (number1,number2)
                item.info = strline
                item.save()
            except:
                print "renewal log err"
            continue
        try:
            number = contract.objects.filter(id=cid)[0].number
        except:
            print "contract not exist"
            continue
        item.info = item.info.replace("="+str(cid),"="+number)
        item.save()
    '''
    print "===== do my test" 
    ac = contract.objects.all()
    for item in ac:
        if not item.thisproduct.closedperiod == 18:
            continue
        if not item.thisproduct.closedtype == 'm':
            continue
        thisdate = datetime.datetime.strptime(item.startdate, '%Y-%m-%d').date()
        if thisdate.month < 7 :
            continue
        my_repayitems = repayitem.objects.filter(thiscontract_id = item.id)
        if not my_repayitems:
            continue
        
        intmoney = float(item.money)
        thisdate = datetime.datetime.strptime(item.enddate,'%Y-%m-%d').date()
        startdate = datetime.datetime.strptime(item.startdate,'%Y-%m-%d').date()
        totalmoney = intmoney + intmoney*float(item.thisproduct.rate)/1200*item.thisproduct.closedperiod
        leftdays = getDays(getNextDay(startdate,item.thisproduct.closedperiod,0),thisdate)
        print totalmoney
        totalmoney += intmoney*float(item.thisproduct.rate)/36500*leftdays

        my_repayitem = my_repayitems[0]
        print item.number, " ", my_repayitem.repaymoney, "==", totalmoney, "---", leftdays 
        my_repayitem.repaymoney = str(int(totalmoney+0.5))
        my_repayitem.save() 


    return render_to_response("home.html")
    
def cleanall(req):
    '''
    repayitem.objects.all().delete()
    contract.objects.all().delete()
    loginfo.objects.all().delete()
    manager.objects.all().delete()
    party.objects.all().delete()
    field.objects.all().delete()
    product.objects.all().delete()
    users.objects.all().delete()
    cycle.objects.all().delete()
    User.objects.all().delete()
    '''
    return HttpResponse("clean ok")

def addcycle(req):
    thiscycle = cycle(name=u'一次',cycletype=1)
    thiscycle.save()
    thiscycle = cycle(name=u'按月',cycletype=2)
    thiscycle.save()
    return HttpResponse("cycle ok")

@checkauth
def index(req):
    a = {'user':req.user}
    a["indexlist"] = getindexlist(req)
    return render_to_response("home.html",a)
      
def checkinput(number):
    ans = contract.objects.filter(number=number)
    if len(ans)>0:
        return False
    return True

@csrf_exempt
@checkauth
def newcontract(req):
    a = {'user':req.user}
    a["indexlist"] = getindexlist(req)
    if not checkjurisdiction(req,"新增合同"):
        return render_to_response("jur.html",a)

    a['products'] = product.objects.all()
    a['managers'] = manager.objects.raw("select * from website_manager order by convert(name USING gbk)")#order_by("name")
    form = NewContractForm()
    a["form"] = form
    if req.method == 'GET':
        return render_to_response("newcontract.html",a)
    elif req.method == 'POST':
        form = NewContractForm(req.POST)
        a["form"] = form
        if form.is_valid():
            number = req.POST.get('number','')
            if checkinput(number) == False:
                a["number_err"] = True
                return render_to_response('newcontract.html', a)
            
            client_name = req.POST.get('client_name','')
            client_idcard = req.POST.get('client_idcard','')
            address = req.POST.get('address','')
            bank = req.POST.get('bank','')
            bank_card = req.POST.get("bank_card",'')
            subbranch = req.POST.get("subbranch",'')
            province = req.POST.get("province",'')
            city = req.POST.get("city",'')
            product_id = req.POST.get("product_id",'')
            money = req.POST.get('money','')
            startdate = req.POST.get('startdate','')
            enddate = req.POST.get("enddate",'')
            manager_id = req.POST.get('manager_id','')
            factorage = req.POST.get('factorage','')
            comment = req.POST.get("comment",'')
            thiscontract = contract(number=number,client_name=client_name,client_idcard=client_idcard,address=address,
                    bank=bank,bank_card=bank_card,subbranch=subbranch,province=province,city=city,factorage=factorage,
                    comment=comment,money=money,thisproduct_id=int(product_id),startdate=startdate,enddate=enddate,status=1,
                    thismanager_id=int(manager_id),renewal_father_id=-1,renewal_son_id=-1,operator_id=req.user.id)
            thiscontract.save()
            thislog = loginfo(info="new contract with id=%s" % (thiscontract.number),time=str(datetime.datetime.now()),thisuser=req.user)
            thislog.save()
        
            #CreateRepayItem(thiscontract)
            a["create_succ"] = True
            return render_to_response("newcontract.html",a)
        else:
            a["form"] = form
            return render_to_response('newcontract.html', a)

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
        thislog = loginfo(info="change contract with id=%s from status=%s to %d" % (thiscontract.number,status,initstatus),
                time=str(datetime.datetime.now()),thisuser=req.user)
        thislog.save()
        a = {'user':req.user}
        return render_to_response("home.html",a)




#add product control and manager
@csrf_exempt
@checkauth
def newfield(req):
    a = {'user':req.user}
    a["indexlist"] = getindexlist(req)
    if not checkjurisdiction(req,"职场管理"):
        return render_to_response("jur.html",a)
    
    if req.method == "GET":
        form = NewFieldForm()
        a["form"] = form
        return render_to_response("newfield.html",a)
    elif req.method == "POST":
        form = NewFieldForm(req.POST)
        a["form"] = form
        if form.is_valid():
            name = req.POST.get("name",'')
            if len(field.objects.filter(name=name))>0:
                a["name_err"] = True
                return render_to_response('newfield.html', a)
            address = req.POST.get("address",'')
            tel = req.POST.get("tel","")
            thisfield = field(name=name,address=address,tel=tel)
            thisfield.save()
            a["create_succ"] = True
            return render_to_response("newfield.html",a)
        else:
            return render_to_response("newfield.html",a)

@csrf_exempt
@checkauth
def newbigparty(req):
    a = {'user':req.user}
    a["indexlist"] = getindexlist(req)
    if not checkjurisdiction(req,"团队管理"):
        return render_to_response("jur.html",a)
    
    a["fields"] = field.objects.all()
    if req.method == "GET":
        form = NewPartyForm()
        a["form"] = form
        return render_to_response("newbigparty.html",a)
    elif req.method == "POST":
        form = NewPartyForm(req.POST)
        a["form"] = form
        if form.is_valid():
            name = req.POST.get("name",'')
            if len(bigparty.objects.filter(name=name))>0:
                a["name_err"] = True
                return render_to_response('newbigparty.html', a)
            field_id = req.POST.get("field_id",'')
            thisparty = bigparty(name=name,thisfield_id=field_id)
            thisparty.save()
            a["create_succ"] = True
            return render_to_response("newbigparty.html",a)
        else:
            return render_to_response("newbigparty.html",a)

@csrf_exempt
@checkauth
def newparty(req):
    a = {'user':req.user}
    a["indexlist"] = getindexlist(req)
    if not checkjurisdiction(req,"团队管理"):
        return render_to_response("jur.html",a)
    
    a["bigparties"] = bigparty.objects.all()
    if req.method == "GET":
        form = NewPartyForm()
        a["form"] = form
        return render_to_response("newparty.html",a)
    elif req.method == "POST":
        form = NewPartyForm(req.POST)
        a["form"] = form
        if form.is_valid():
            name = req.POST.get("name",'')
            if len(party.objects.filter(name=name))>0:
                a["name_err"] = True
                return render_to_response('newparty.html', a)
            bigparty_id = req.POST.get("bigparty_id",'')
            thisparty = party(name=name,thisbigparty_id=bigparty_id)
            thisparty.save()
            a["create_succ"] = True
            return render_to_response("newparty.html",a)
        else:
            return render_to_response("newparty.html",a)
@csrf_exempt
@checkauth
def newmanager(req):
    a = {'user':req.user}
    a["indexlist"] = getindexlist(req)
    if not checkjurisdiction(req,"经理管理"):
        return render_to_response("jur.html",a)
    
    a["parties"] = party.objects.all()
    if req.method == "GET":
        form = NewManagerForm()
        a["form"] = form
        return render_to_response("newmanager.html",a)
    elif req.method == "POST":
        form = NewManagerForm(req.POST)
        a["form"] = form
        if form.is_valid():
            name = req.POST.get("name",'')
            tel = req.POST.get("tel",'')
            number = req.POST.get("number",'')
            if len(manager.objects.filter(number=number))>0:
                a["number_err"] = True
                return render_to_response('newmanager.html', a)
            
            party_id = req.POST.get("party_id","")
            thismanager = manager(name=name,tel=tel,number=number,thisparty_id=party_id)
            thismanager.save()
            a["create_succ"] = True
            return render_to_response("newmanager.html",a)
        else:
            return render_to_response("newmanager.html",a)
@csrf_exempt
@checkauth
def newproduct(req):
    a = {'user':req.user}
    a["indexlist"] = getindexlist(req)
    if not checkjurisdiction(req,"产品管理"):
        return render_to_response("jur.html",a)
    
    a["cycles"] = cycle.objects.all()
    if req.method == "GET":
        form = NewProductForm()
        a["form"] = form
        return render_to_response("newproduct.html",a)
    elif req.method == "POST":
        form = NewProductForm(req.POST)
        a["form"] = form
        if form.is_valid():
            name = req.POST.get("name",'')
            rate = req.POST.get("rate",'')
            repaycycle_id = req.POST.get("repaycycle_id",'')
            closedtype = req.POST.get("closedtype","")
            closedperiod = req.POST.get("closedperiod","")
            thisproduct = product(name=name,rate=rate,repaycycle_id=int(repaycycle_id),
                    closedtype=closedtype,closedperiod=int(closedperiod))
            thisproduct.save()
            a["create_succ"] = True
            return render_to_response("newproduct.html",a)
        else:
            return render_to_response("newproduct.html",a)

@checkauth
def getproduct(req,product_id):
    a = {'user':req.user}
    a["indexlist"] = getindexlist(req)
    thisproduct = product.objects.filter(id=int(product_id))
    if thisproduct:
        thisproduct = thisproduct[0]
    a["product"] = thisproduct
    return render_to_response("product.html",a)
@csrf_exempt
@checkauth
def getlog(req):
    a = {'user':req.user}
    a["indexlist"] = getindexlist(req)
    if not checkjurisdiction(req,"系统日志"):
        return render_to_response("jur.html",a)
    if req.method == "GET":
        try:
            thispage = int(req.GET.get("page",'1'))
            pagetype = str(req.GET.get("pagetype",''))
        except ValueError:
            thispage = 1
            allpage = 1
            pagetype = ''
        logs = []
        if pagetype == 'pagedown':
            thispage += 1
        elif pagetype == 'pageup':
            thispage -= 1
        allcount = 0
        for log in loginfo.objects.all():
            allcount += 1
        startpos = ((thispage-1)*ONE_PAGE_NUM if (thispage-1)*ONE_PAGE_NUM<allcount else allcount)
        endpos = (thispage*ONE_PAGE_NUM if thispage*ONE_PAGE_NUM<allcount else allcount)
        alllog = loginfo.objects.order_by("-time")
        logs = alllog[startpos:endpos]

        a['curpage'] = thispage
        a['allpage'] = (allcount-1)/ONE_PAGE_NUM + 1
        a['logs'] = logs
        return render_to_response("log.html",a)
    if req.method == 'POST':
        logs = []
        number = req.POST.get("number",'')
        alllogs = loginfo.objects.filter(info__contains=number).order_by("-time")
        a['logs'] = alllogs
        a['curpage'] = 1
        a['allpage'] = 1
        return render_to_response("log.html",a)
    
@csrf_exempt
@checkauth
def altercontract(req):
    a = {'user':req.user}
    a["indexlist"] = getindexlist(req)
    a['products'] = product.objects.all()
    a['managers'] = manager.objects.raw("select * from website_manager order by convert(name USING gbk)")#order_by("name")
    if req.method == "GET":
        contractid = req.GET.get("contractid",'')
        try:
            thiscontract = contract.objects.get(id = int(contractid))
            if thiscontract.status == 1:
                a["contract"] = thiscontract
                return render_to_response("altercontract.html",a)
            else:
                return render_to_response("home.html",a)
        except:
            return render_to_response("home.html",a)
    if req.method == "POST":
        id = req.POST.get("contractid",'')
        thiscontract = contract.objects.get(id = int(id))
        thisnumber = req.POST.get("number",'')
        isexit = contract.objects.filter(number = thisnumber)
        if thiscontract.number == thisnumber or len(isexit)==0:
            thiscontract.number = req.POST.get("number",'')
            thiscontract.bank = req.POST.get("bank",'')
            thiscontract.bank_card = req.POST.get("bank_card",'')
            thiscontract.subbranch = req.POST.get("subbranch",'')
            thiscontract.province = req.POST.get("province",'')
            thiscontract.city = req.POST.get("city",'')
            thiscontract.factorage = req.POST.get("factorage",'')  
            thiscontract.comment = req.POST.get("comment",'')  
			
            tmpmoney = req.POST.get("money",'')
            if thiscontract.money != tmpmoney and thiscontract.renewal_father_id!=-1:
                father_contract = contract.objects.get(id=int(thiscontract.renewal_father_id))
                thisrepayitem = repayitem.objects.filter(thiscontract_id=father_contract.id,repaytype__gte=2)[0]
                #warnning
                if float(father_contract.money)<=float(tmpmoney):
                    if float(father_contract.money)>float(thiscontract.money):
                        thisrepayitem.repaymoney = str(float(thisrepayitem.repaymoney) + float(thiscontract.money) - float(father_contract.money))
                else:
                    if float(father_contract.money)>float(thiscontract.money):
                        thisrepayitem.repaymoney = str(float(thisrepayitem.repaymoney) + float(thiscontract.money) - float(tmpmoney))
                    else:
                        thisrepayitem.repaymoney = str(float(thisrepayitem.repaymoney) + float(father_contract.money) - float(tmpmoney))
                        
                thisrepayitem.save()
            thiscontract.money = tmpmoney
            
            thiscontract.client_name = req.POST.get("client_name",'')
            thiscontract.client_idcard = req.POST.get("client_idcard",'')
            thiscontract.address = req.POST.get("address",'')
            thiscontract.thisproduct_id = int(req.POST.get("product_id",''))
            thiscontract.startdate = req.POST.get('startdate','')
            thiscontract.enddate = req.POST.get("enddate",'')
            thiscontract.thismanager_id = int(req.POST.get('manager_id',''))
            thiscontract.status = 1
            thiscontract.save()
            thislog = loginfo(info="alter contract with id=%s" % (thiscontract.number),time=str(datetime.datetime.now()),thisuser=req.user)
            thislog.save()
            #a = {'user':req.user}
            a["create_succ"] = True
            a["contract"] = thiscontract
            return render_to_response("altercontract.html",a)
        else:
            a["create_succ"] = False
            a["contract"] = thiscontract
            return render_to_response("altercontract.html",a)
            
        
        
@csrf_exempt
@checkauth
def showcontract(req,contract_id):
	a = {'user':req.user}
	a["indexlist"] = getindexlist(req)
	if req.method == 'GET':
		contractid = contract_id
		thiscontract = contract.objects.get(id = int(contractid))
		a["contract"] = thiscontract
		return render_to_response("showcontract.html",a)



@csrf_exempt
@checkauth
def checknumber(req):
    thiscontract = None
    result = 0
    if req.POST.has_key('number'):
        number = req.POST['number']
        thiscontract = contract.objects.filter(number = number)
    if thiscontract:
        result = 1 
        result = json.dumps(result)
    else:
        result = 0
        result = json.dumps(result)
    return HttpResponse(result, content_type='application/javascript')



@csrf_exempt
@checkauth
def showproduct(req,product_id):
	a = {'user':req.user}
	a["indexlist"] = getindexlist(req)
	if req.method == 'GET':
		productid = product_id
		thisproduct = product.objects.get(id = int(productid))
		a["product"] = thisproduct
		return render_to_response("showproduct.html",a)


@csrf_exempt
@checkauth
def terminatecon(req):
	a = {'user':req.user}
	a["indexlist"] = getindexlist(req)
	if not checkjurisdiction(req,"合同终止"):
		return render_to_response("jur.html",a)
	if req.method =='GET':
		contractid = req.GET.get("contractid",'')
		thiscontract = contract.objects.get(id = int(contractid))
		a["contract"] = thiscontract
		return render_to_response("terminatecon.html",a)
	if req.method == 'POST':
		contractid = req.POST.get("contractid",'')
		thiscomment = req.POST.get("comment",'')
		thiscontract = contract.objects.get(id = int(contractid))
		thiscontract.status = -1
		thiscontract.comment += "    "+thiscomment
		thiscontract.save()
		thislog = loginfo(info="terminate contract with id=%s" % (thiscontract.number),time=str(datetime.datetime.now()),thisuser=req.user)
		thislog.save()
        
		items = repayitem.objects.filter(thiscontract_id=thiscontract.id)
		for item in items:
			item.status = -1
			item.save()
        
        
		allcount = contract.objects.count()
		thispage = 1
		startpos = ((thispage-1)*ONE_PAGE_NUM if (thispage-1)*ONE_PAGE_NUM<allcount else allcount)
		endpos = (thispage*ONE_PAGE_NUM if thispage*ONE_PAGE_NUM<allcount else allcount)
		contracts = contract.objects.all()[startpos:endpos]
		a['curpage'] = thispage
		a['allpage'] = (allcount-1)/ONE_PAGE_NUM + 1
		a['contracts'] = contracts
		return render_to_response("querycontracts.html",a)

@csrf_exempt
@checkauth
def checkcontract(req):
	a = {'user':req.user}
	a["indexlist"] = getindexlist(req)
	if not checkjurisdiction(req,"合同审核"):
		return render_to_response("jur.html",a)
	if req.method == 'GET':
		contractid = req.GET.get("contractid",'')
        #print "he",contractid
		thiscontract = contract.objects.get(id = int(contractid))
		a["contract"] = thiscontract
		return render_to_response("checkcontract.html",a)
	if req.method == 'POST':
		contractid = req.POST.get("contractid",'')
		thiscontract = contract.objects.get(id = int(contractid))
		newstatus = int(req.POST.get('status',''))
		if newstatus == 2 and thiscontract.status == 1:
			thiscontract.status = newstatus
			thiscontract.save()
			thislog = loginfo(info="check contract with id=%s" % (thiscontract.number),time=str(datetime.datetime.now()),thisuser=req.user)
			thislog.save()
		contracts = contract.objects.filter(status = 1)
		allcount = contracts.count()
		a['curpage'] = 1
		a['allpage'] = (allcount-1)/ONE_PAGE_NUM + 1
		a["contracts"] = contracts[0:ONE_PAGE_NUM]
		return render_to_response("checkcontracts.html",a)

@checkauth
def repaytest(req):
    a = {'user':req.user}
    a["indexlist"] = getindexlist(req)
    if not checkjurisdiction(req,"还款查询"):
        return render_to_response("jur.html",a)
    
    if req.method == "GET":
        fromdate = req.GET.get("fromdate",str(datetime.date.today()))
        todate = req.GET.get("todate",str(datetime.date.today()+datetime.timedelta(7))) #下一周
        a["fromdate"] = fromdate
        a["todate"] = todate
        return render_to_response("repaytest.html",a)
    
@checkauth
def queryrepayitems(req,type_id):
    a = {'user':req.user}
    a["indexlist"] = getindexlist(req)
    print type_id
    if type_id=="1":
        if not checkjurisdiction(req,"还款查询"):
            return render_to_response("jur.html",a)
    elif type_id=="2":
        print "here"
        if not checkjurisdiction(req,"到期续单"):
            return render_to_response("jur.html",a)
    elif type_id=="3":
        if not checkjurisdiction(req,"还款确认"):
            return render_to_response("jur.html",a)
    elif type_id=="4":
        if not checkjurisdiction(req,"全部还款查询"):
            return render_to_response("jur.html",a)
        
    if req.method == "GET":
        fromdate = "1970-01-01"
        todate = "2100-01-01"
        sorteditems = []
        contract_number = req.GET.get("contract_id","")
        if type_id=="2":
            if contract_number != "":
                sorteditems = filterRepayItems(fromdate,todate,contract_number,type_id) 
        else:
            fromdate = req.GET.get("fromdate",str(datetime.date.today()))
            todate = req.GET.get("todate",str(datetime.date.today()+datetime.timedelta(7))) #下一周
            sorteditems = filterRepayItems(fromdate,todate,contract_number,type_id) 
                
        a["repayitems"] = sorteditems
        a["type_id"] = type_id
        a["fromdate"] = fromdate
        a["todate"] = todate
        a["number"] = contract_number
        return render_to_response("queryrepayitems.html",a)

@checkauth
def getrepayitem(req,item_id):
    a = {'user':req.user}
    a["indexlist"] = getindexlist(req)
    if not checkjurisdiction(req,"还款查询"):
        return render_to_response("jur.html",a)
    if req.method == "GET":
        thisitem = repayitem.objects.filter(id=int(item_id))[0]
        a["repayitem"] = thisitem
        return render_to_response("repayitem.html",a)
    
    
@csrf_exempt
@checkauth
def statusrepayitem(req,type_id):
    if req.method == "POST":
        item_id = req.POST.get("repayitem_id","")
        #status = req.POST.get("status","")
        items = repayitem.objects.filter(id=int(item_id))
        a = {"message":"false"}
        if len(items)>0:
            thisitem = items[0]
            if type_id == '1': #还款
                if not checkjurisdiction(req,"还款确认"):
                    a["info"] = "对不起您没有还款权限"
            
                elif thisitem.status==1 or thisitem.status==3:
                    a["message"] = "true"
                    a["info"] = "还款成功"
                    restitems = repayitem.objects.filter(thiscontract_id=thisitem.thiscontract.id,repaydate__lt=thisitem.repaydate)
                    for restitem in restitems:
                        if restitem.status==1:
                            a["info"] = "前期款项还未还"
                            a["message"] = "false"
                            break
                    if a["message"]=="true":
                        thisitem.status += 1
                        thisitem.save()
                        thislog = loginfo(info="repay with %d of contract number=%s" % (thisitem.id,thisitem.thiscontract.number),time=str(datetime.datetime.now()),thisuser=req.user)
                        thislog.save()
            elif type_id == '2':
                if not checkjurisdiction(req,"到期续单"):
                    a["info"] = "对不起您没有续单权限"
                elif thisitem.repaytype>1:
                    renewal_num = req.POST.get("renewal_num","-1")
                    renewal_con = contract.objects.filter(number=renewal_num)
                    a["message"] = "true"
                    a["info"] = "续签成功"
                    if not renewal_con:
                        a["message"] = "false"
                        a["info"] = "不存在该合同编号，请先添加该合同"
                    else:
                        restitems = repayitem.objects.filter(thiscontract_id=thisitem.thiscontract.id)
                        for restitem in restitems:
                            if restitem.repaytype==1 and restitem.status==1:
                                a["info"] = "还有款项没有还清"
                                a["message"] = "false"
                                break
                        if a["message"]=="true":
                            thisitem.status = 3
                            thisitem.save()
                            thisitem.thiscontract.renewal_id = renewal_con[0].id
                            thisitem.thiscontract.save()
                            thislog = loginfo(info="renew contract %s with id=%s" % (thisitem.thiscontract.number,renewal_con[0].number),time=str(datetime.datetime.now()),thisuser=req.user)
                            thislog.save()
        else:
            a["info"] = "没有该还款项"
        jsonstr = json.dumps(a,ensure_ascii=False)
        return HttpResponse(jsonstr,content_type='application/javascript')
    
@csrf_exempt
@checkauth
def checkcontracts(req):
    a = {'user':req.user}
    a["indexlist"] = getindexlist(req)
    if not checkjurisdiction(req,"合同审核"):
        return render_to_response("jur.html",a)
    
    if req.method == 'GET':
        try:
            thispage = int(req.GET.get("page",'1'))
            pagetype = str(req.GET.get("pagetype",''))
        except ValueError:
            thispage = 1
            allpage = 1
            pagetype = ''
        try:
            number = req.GET.get('number','')
        except ValueError:
            number = ""
        contracts = []
        if pagetype == 'pagedown':
            thispage += 1
        elif pagetype == 'pageup':
            thispage -= 1
        
        contracts = []
        iShowMoney = int(MinShowMoney.objects.all()[0].money)
        if number=="":
            allcount = 0
            for con in contract.objects.all():
                if con.status == 1 and float(con.money) >= iShowMoney:
                    allcount += 1
                    contracts.append(con)
            startpos = ((thispage-1)*ONE_PAGE_NUM if (thispage-1)*ONE_PAGE_NUM<allcount else allcount)
            endpos = (thispage*ONE_PAGE_NUM if thispage*ONE_PAGE_NUM<allcount else allcount)
            contracts = contracts[startpos:endpos]
        else:
            othercontracts = contract.objects.filter(number=number)
            for c in othercontracts:
                if float(c.money) >= iShowMoney:
                    contracts.append(c)
            allcount = len(contracts)
        if allcount==0:
            allcount = 1
        a['curpage'] = thispage
        a['allpage'] = (allcount-1)/ONE_PAGE_NUM + 1
        a['contracts'] = contracts
        return render_to_response("checkcontracts.html",a)

@csrf_exempt
@checkauth
def rollbackcontracts(req):
    a = {'user':req.user}
    a["indexlist"] = getindexlist(req)
    if not checkjurisdiction(req,"审核回退"):
        return render_to_response("jur.html",a)
    
    if req.method == 'GET':
        try:
            thispage = int(req.GET.get("page",'1'))
            pagetype = str(req.GET.get("pagetype",''))
        except ValueError:
            thispage = 1
            allpage = 1
            pagetype = ''
        try:
            number = req.GET.get('number','')
        except ValueError:
            number = ""
        contracts = []
        if pagetype == 'pagedown':
            thispage += 1
        elif pagetype == 'pageup':
            thispage -= 1
        if number=="":
            allcount = 0
            for con in contract.objects.all():
                if con.status == 2 :
                    allcount += 1
            startpos = ((thispage-1)*ONE_PAGE_NUM if (thispage-1)*ONE_PAGE_NUM<allcount else allcount)
            endpos = (thispage*ONE_PAGE_NUM if thispage*ONE_PAGE_NUM<allcount else allcount)
            contracts = contract.objects.filter(status = 2)[startpos:endpos]
        else:
            contracts = contract.objects.filter(number=number)
        a['curpage'] = thispage
        a['allpage'] = allcount/ONE_PAGE_NUM + 1
        a['contracts'] = contracts
        return render_to_response("rollbackcontracts.html",a)
@csrf_exempt
@checkauth
def rollbackcontract(req):
	a = {'user':req.user}
	a["indexlist"] = getindexlist(req)
	if req.method == 'GET':
		contractid = req.GET.get("contractid",'')
		thiscontract = contract.objects.get(id = int(contractid))
		a["contract"] = thiscontract
		return render_to_response("rollbackcontract.html",a)
	if req.method == 'POST':
		id = req.POST.get("contractid",'')
		thiscontract = contract.objects.get(id = int(id))
		thiscontract.status = 3
		thiscontract.save()
		thislog = loginfo(info="rollbackcontract with id=%s" % (thiscontract.number),time=str(datetime.datetime.now()),thisuser=req.user)
		thislog.save()
		a = {'user':req.user}
		return render_to_response("home.html",a)

@csrf_exempt
@checkauth
def querycontracts(req):
    a = {'user':req.user}
    a["indexlist"] = getindexlist(req)
    iShowMoney = int(MinShowMoney.objects.all()[0].money)
    if not checkjurisdiction(req,"合同查询"):
        return render_to_response("jur.html",a)
    if checkjurisdiction(req,"合同导出"):
        a["outjur"] = True
    if req.method == 'GET':
        try:
            thispage = int(req.GET.get("page",'1'))
            pagetype = str(req.GET.get("pagetype",''))
        except ValueError:
            thispage = 1
            allpage = 1
            pagetype = ''
        try:
            number = req.GET.get('number','')
        except ValueError:
            number = ""
        contracts = []
        if pagetype == 'pagedown':
            thispage += 1
        elif pagetype == 'pageup':
            thispage -= 1
        
        contracts = []
        if number=="":
            allcount = 0
            allcontract = contract.objects.all()
            for c in allcontract:
                if float(c.money) >= iShowMoney:
                    contracts.append(c)
            allcount = len(contracts)
            startpos = ((thispage-1)*ONE_PAGE_NUM if (thispage-1)*ONE_PAGE_NUM<allcount else allcount)
            endpos = (thispage*ONE_PAGE_NUM if thispage*ONE_PAGE_NUM<allcount else allcount)
            contracts = contracts[startpos:endpos]
        else:
            othercontracts = contract.objects.filter(number=number)
            for c in othercontracts:
                if float(c.money) >= iShowMoney:
                    contracts.append(c)
                    
        a['curpage'] = thispage
        a['allpage'] = (allcount-1)/ONE_PAGE_NUM + 1
        a['contracts'] = contracts
        return render_to_response("querycontracts.html",a)
    if req.method == 'POST':
        othercontracts = []
        number = req.POST.get("number",'')
        contractbynum = contract.objects.filter(number=number)
        contractbyname = contract.objects.filter(client_name=number)
        if contractbynum.count() == 0:
            othercontracts = contractbyname            
        else :
            othercontracts = contractbynum
        contracts = []
        for c in othercontracts:
            if float(c.money) >= iShowMoney:
                contracts.append(c)
                
        a['contract_size'] = len(contracts) 
        a['contracts'] = contracts
        a['curpage'] = 1
        a['allpage'] = 1
        return render_to_response("querycontracts.html",a)

@csrf_exempt
@checkauth
def lastcheck(req):
    a = {'user':req.user}
    a["indexlist"] = getindexlist(req)
    iShowMoney = int(MinShowMoney.objects.all()[0].money)
    if not checkjurisdiction(req,"最终审核"):
        return render_to_response("jur.html",a)
    if req.method == "GET":
        fromdate = req.GET.get("fromdate",str(datetime.date.today()-datetime.timedelta(7)))
        todate = req.GET.get("todate",str(datetime.date.today())) #前一周
        thiscons = contract.objects.filter(startdate__gte=fromdate,startdate__lte=todate,status=2)
        cons = []
        for c in thiscons:
            if float(c.money) >= iShowMoney:
                cons.append(c)
        totalmoney = 0.0
        for con in cons:
            addmoney = 0.0
            if con.renewal_father_id!=-1:
                father_contract = contract.objects.filter(id=int(con.renewal_father_id))[0]
                if float(con.money)>float(father_contract.money):
                    totalmoney += float(con.money) - float(father_contract.money)
            else:
                totalmoney += float(con.money)
        a["cons"] = cons
        a["totalmoney"] = totalmoney
        a["fromdate"] = fromdate
        a["todate"] = todate
        return render_to_response("lastcheck.html",a)
    if req.method == "POST":
        fromdate = req.POST.get("fromdate","")
        todate = req.POST.get("todate","")
        status = req.POST.get("status","")
        
        thiscons = contract.objects.filter(startdate__gte=fromdate,startdate__lte=todate,status=2)
        cons = []
        for c in thiscons:
            if float(c.money) >= iShowMoney:
                cons.append(c)
        #print fromdate,todate
        if status=='2':
            for con in cons:
                con.status = 4
                con.save()
                CreateRepayItem(con) 
        thislog = loginfo(info="lastcheck contracts from %s to %s" % (fromdate,todate),time=str(datetime.datetime.now()),thisuser=req.user)
        thislog.save()
        return render_to_response("home.html",a)
    
@checkauth
def queryproducts(req):
    a = {'user':req.user}
    a["indexlist"] = getindexlist(req)
    if not checkjurisdiction(req,"产品管理"):
        return render_to_response("jur.html",a)
    products = product.objects.all()
    a["products"] = products
    return render_to_response("products.html",a)

@csrf_exempt
@checkauth
def renewalcontract(req,repayitem_id):
    a = {'user':req.user}
    a["indexlist"] = getindexlist(req)
    a["repayitem_id"] = repayitem_id
    a["onecontract"] = repayitem.objects.filter(id=int(repayitem_id))[0].thiscontract
    if not checkjurisdiction(req,"到期续单"):
        return render_to_response("jur.html",a)
    a['products'] = product.objects.all()
    a['managers'] = manager.objects.all()
    form = NewContractForm()
    a["form"] = form
    if req.method == 'GET':
        return render_to_response("newcontract.html",a)
    
    elif req.method == 'POST':
        form = NewContractForm(req.POST)
        a["form"] = form
        if form.is_valid():
            number = req.POST.get('number','')
            if checkinput(number) == False:
                a["number_err"] = True
                return render_to_response('newcontract.html', a)
            
            client_name = req.POST.get('client_name','')
            client_idcard = req.POST.get('client_idcard','')
            address = req.POST.get('address','')
            bank = req.POST.get('bank','')
            bank_card = req.POST.get("bank_card",'')
            subbranch = req.POST.get("subbranch",'')
            province = req.POST.get("province",'')
            city = req.POST.get("city",'')
            product_id = req.POST.get("product_id",'')
            money = req.POST.get('money','')
            startdate = req.POST.get('startdate','')
            enddate = req.POST.get("enddate",'')
            manager_id = req.POST.get('manager_id','')
            factorage = req.POST.get('factorage','')
            comment = req.POST.get("comment",'')
            thisrepayitem_id = req.POST.get('repayitem_id','-1')
            
            if thisrepayitem_id=="-1":
                thiscontract = contract(number=number,client_name=client_name,client_idcard=client_idcard,address=address,
                    bank=bank,bank_card=bank_card,subbranch=subbranch,province=province,city=city,factorage=factorage,
                    comment=comment,money=money,thisproduct_id=int(product_id),startdate=startdate,enddate=enddate,status=1,
                    thismanager_id=int(manager_id),renewal_father_id=-1,renewal_son_id=-1,operator_id=req.user.id)
                thiscontract.save()
                thislog = loginfo(info="new contract with id=%s" % (thiscontract.number),time=str(datetime.datetime.now()),thisuser=req.user)
                thislog.save()
            else:
                thisrepayitem = repayitem.objects.filter(id=int(thisrepayitem_id))[0]
                father_contract = thisrepayitem.thiscontract
                if father_contract.renewal_son_id!=-1:
                    a["renewal_err"] = True
                    return render_to_response("newcontract.html",a)
                
                thiscontract = contract(number=number,client_name=client_name,client_idcard=client_idcard,address=address,
                    bank=bank,bank_card=bank_card,subbranch=subbranch,province=province,city=city,factorage=factorage,
                    comment=comment,money=money,thisproduct_id=int(product_id),startdate=startdate,enddate=enddate,status=1,
                    thismanager_id=int(manager_id),renewal_father_id=father_contract.id,renewal_son_id=-1,operator_id=req.user.id)
                thiscontract.save()
                father_contract.renewal_son_id = thiscontract.id
                father_contract.save()
                thisrepayitem.status = 3
                #warnning
                if float(father_contract.money)<=float(thiscontract.money):
                    thisrepayitem.repaymoney = str(float(thisrepayitem.repaymoney) - float(father_contract.money))
                else:
                    thisrepayitem.repaymoney = str(float(thisrepayitem.repaymoney) - float(thiscontract.money))
    
                thisrepayitem.save()
                thislog = loginfo(info="renewal contract %s with id=%s" % (father_contract.number,thiscontract.number),time=str(datetime.datetime.now()),thisuser=req.user)
                thislog.save()
                
                a["repayitem"] = thisrepayitem
                return render_to_response("repayitem.html",a)
                
            a["create_succ"] = True
            return render_to_response("newcontract.html",a)
        else:
            a["form"] = form
            return render_to_response('newcontract.html', a)

@checkauth
def getconstruct(req):
    a = {'user':req.user}
    a["indexlist"] = getindexlist(req)
    if not checkjurisdiction(req,"人员结构"):
        return render_to_response("jur.html",a)
    if req.method == "GET":
        fields = field.objects.all()
        anslist = []
        for onefield in fields:
            bplist = []
            bigparties = bigparty.objects.filter(thisfield_id=onefield.id)
            for bp in bigparties:
                plist = []
                parties = party.objects.filter(thisbigparty_id=bp.id)
                for p in parties:
                    mlist = []
                    managers = manager.objects.filter(thisparty_id=p.id)
                    for m in managers:
                        mlist.append(m)
                    plist.append((p.name,mlist))
                bplist.append((bp.name,plist))
            anslist.append((onefield.name,bplist))
        a["res"] = anslist
        return render_to_response('construct.html', a)

@csrf_exempt
@checkauth
def ajust(req,type_id):
    if req.method == "GET":
        a = {'user':req.user}
        a["indexlist"] = getindexlist(req)
        if type_id=="1":
            a["bps"] = bigparty.objects.all()
            a["fields"] = field.objects.all()
            return render_to_response('ajustbigparty.html', a)
        elif type_id=="2":
            a["ps"] = party.objects.all()
            a["bps"] = bigparty.objects.all()
            return render_to_response('ajustparty.html', a)
        elif type_id=="3":
            a["ps"] = party.objects.all()
            a["ms"] = manager.objects.all()
            return render_to_response('ajustmanager.html', a)
        else:
            return render_to_response('home.html', a)
    elif req.method == "POST":
        a = {}
        if type_id=="1":
            bigparty_id = req.POST.get("bigparty_id","")
            field_id = req.POST.get("field_id","")
            if bigparty_id!="" and field_id!="":
                thisbp = bigparty.objects.filter(id=int(bigparty_id))[0]
                thisbp.thisfield_id = int(field_id)
                thisbp.save()
                a["message"] = "true"
            jsonstr = json.dumps(a,ensure_ascii=False)
            return HttpResponse(jsonstr,content_type='application/javascript')
        elif type_id=="2":
            bigparty_id = req.POST.get("bigparty_id","")
            party_id = req.POST.get("party_id","")
            if bigparty_id!="" and party_id!="":
                thisp = party.objects.filter(id=int(party_id))[0]
                thisp.thisbigparty_id = int(bigparty_id)
                thisp.save()
                a["message"] = "true"
            jsonstr = json.dumps(a,ensure_ascii=False)
            return HttpResponse(jsonstr,content_type='application/javascript')
        elif type_id=="3":
            party_id = req.POST.get("party_id","")
            manager_id = req.POST.get("manager_id","")
            if party_id!="" and manager_id!="":
                thism = manager.objects.filter(id=int(manager_id))[0]
                thism.thisparty_id = int(party_id)
                thism.save()
                a["message"] = "true"
            jsonstr = json.dumps(a,ensure_ascii=False)
            return HttpResponse(jsonstr,content_type='application/javascript')
        else:
            a = {'user':req.user}
            a["indexlist"] = getindexlist(req)
            return render_to_response('home.html', a)

@csrf_exempt
@checkauth
def outcontracts(req):
    if not checkjurisdiction(req,"合同查询"):
        return render_to_response("jur.html",a)
    def file_iterator(file_name, chunk_size=512):
        with open(file_name,"rb") as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break
    def writefile(items):
        w = Workbook()
        ws = w.add_sheet('sheet1')
        titles = [u"合同编号",u"姓名",u"身份证号",u"开户行",u"银行卡号",u"产品",u"金额",u"签约日",u"到期日",u"理财顾问",u"状态",u"是否已续签",u"手续费",u"备注"]
        for i in range(0,len(titles)):
            ws.write(0,i,titles[i])
        for i in range(0,len(items)):
            ws.write(i+1,0,items[i].number)
            ws.write(i+1,1,items[i].client_name)
            ws.write(i+1,2,items[i].client_idcard)
            ws.write(i+1,3,items[i].bank)
            ws.write(i+1,4,items[i].bank_card)
            ws.write(i+1,5,items[i].thisproduct.name)
            ws.write(i+1,6,items[i].money)
            ws.write(i+1,7,items[i].startdate)
            ws.write(i+1,8,items[i].enddate)
            ws.write(i+1,9,items[i].thismanager.name)
            if items[i].status==1:
                ws.write(i+1,10,u"未审核")
            elif items[i].status==2:
                ws.write(i+1,10,u"初审通过")
            elif items[i].status==4:
                ws.write(i+1,10,u"终审通过")
            elif items[i].status==-1:
                ws.write(i+1,10,u"合同终止")
            if items[i].renewal_son_id==-1:
                ws.write(i+1,11,u"否")
            else:
                ws.write(i+1,11,u"是")
            ws.write(i+1,12,items[i].factorage)
            ws.write(i+1,13,items[i].comment)
        filename = ".//tmpfolder//" + str(datetime.datetime.now()).split(" ")[1].replace(":","").replace(".","") + ".xls"
        w.save(filename)
        return filename
    if req.method == "POST":
        thiscs = contract.objects.all()
        iShowMoney = int(MinShowMoney.objects.all()[0].money)
        cs = []
        for c in thiscs:
            if float(c.money) > iShowMoney:
                cs.append(c)
        
        the_file_name = writefile(cs)
        response = StreamingHttpResponse(file_iterator(the_file_name))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{0}"'.format("全部合同.xls")
        return response
