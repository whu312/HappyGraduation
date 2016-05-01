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
from users import *
import json

ONE_PAGE_NUM = 5
# Create your views here.

def testhtml(req):
    return render_to_response("searchcontract.html")
    
def cleanall(req):
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
    return render_to_response("home.html",a)

@csrf_exempt
@checkauth
def newcontract(req):
    a = {'user':req.user}
    if not checkjurisdiction(req,"新增合同"):
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
                    bank=bank,bank_card=bank_card,money=money,thisproduct_id=int(product_id),startdate=startdate,
                    enddate=enddate,status=1,thismanager_id=int(manager_id),renewal_father_id=-1,
                    renewal_son_id=-1,operator_id=req.user.id)
            thiscontract.save()
            thislog = loginfo(info="new contract with id=%d" % (thiscontract.id),time=str(datetime.datetime.now()),thisuser=req.user)
            thislog.save()
        
            #CreateRepayItem(thiscontract)
            a["create_succ"] = True
            return render_to_response("newcontract.html",a)
        else:

            a["form"] = form
            return render_to_response('newcontract.html', a)

            return render_to_response('newcontract.html', RequestContext(req, a))


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




#add product control and manager
@csrf_exempt
@checkauth
def newfield(req):
    a = {'user':req.user}
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
    thisproduct = product.objects.filter(id=int(product_id))
    if thisproduct:
        thisproduct = thisproduct[0]
    a["product"] = thisproduct
    return render_to_response("product.html",a)

@checkauth
def getlog(req):
    a = {'user':req.user}
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
        print allcount
        startpos = ((thispage-1)*ONE_PAGE_NUM if (thispage-1)*ONE_PAGE_NUM<allcount else allcount)
        endpos = (thispage*ONE_PAGE_NUM if thispage*ONE_PAGE_NUM<allcount else allcount)
        logs = loginfo.objects.all()[startpos:endpos]
        print logs.count()
        a['curpage'] = thispage
        a['allpage'] = (allcount-1)/ONE_PAGE_NUM + 1
        a['logs'] = logs
        return render_to_response("log.html",a)

@csrf_exempt
@checkauth
def altercontract(req):
	a = {'user':req.user}
	a['products'] = product.objects.all()
	a['managers'] = manager.objects.all()
	if req.method == "GET":
		contractid = req.GET.get("contractid",'')
		thiscontract = contract.objects.get(id = int(contractid))
		a["contract"] = thiscontract
		return render_to_response("altercontract.html",a)
	if req.method == "POST":
		id = req.POST.get("contractid",'')
		thiscontract = contract.objects.get(id = int(id))
		thiscontract.number = req.POST.get("number",'')
		thiscontract.bank = req.POST.get("bank",'')
		thiscontract.bank_card = req.POST.get("bank_card",'')
		thiscontract.money = req.POST.get("money",'')
		thiscontract.client_name = req.POST.get("client_name",'')
		thiscontract.client_idcard = req.POST.get("client_idcard",'')
		thiscontract.product_id = req.POST.get("product_id",'')
		thiscontract.startdate = req.POST.get('startdate','')
		thiscontract.enddate = req.POST.get("enddate",'')
		thiscontract.manager_id = req.POST.get('manager_id','')
		thiscontract.save()
		
		thislog = loginfo(info="alter contract with id=%d" % (thiscontract.id),time=str(datetime.datetime.now()),thisuser=req.user)
		thislog.save()
		a = {'user':req.user}
		a["create_succ"] = True
		a["contract"] = thiscontract
		return render_to_response("altercontract.html",a)

@csrf_exempt
@checkauth
def showcontract(req,contract_id):
	a = {'user':req.user}
	if req.method == 'GET':
		contractid = contract_id
		thiscontract = contract.objects.get(id = int(contractid))
		a["contract"] = thiscontract
		return render_to_response("showcontract.html",a)

@csrf_exempt
@checkauth
def showproduct(req,product_id):
	a = {'user':req.user}
	if req.method == 'GET':
		productid = product_id
		thisproduct = product.objects.get(id = int(productid))
		a["product"] = thisproduct
		return render_to_response("showproduct.html",a)

@csrf_exempt
@checkauth
def checkcontract(req):
	a = {'user':req.user}
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
		print "id",contractid
		thiscontract = contract.objects.get(id = int(contractid))
		newstatus = int(req.POST.get('status',''))
		print newstatus
		if newstatus == 2:
			thiscontract.status = newstatus
		print thiscontract.status
		thiscontract.save()
		thislog = loginfo(info="check contract with id=%d" % (thiscontract.id),time=str(datetime.datetime.now()),thisuser=req.user)
		thislog.save()
		contracts = contract.objects.filter(status = 1)
		allcount = contracts.count()
		a = {'user':req.user}
		a['curpage'] = 1
		a['allpage'] = (allcount-1)/ONE_PAGE_NUM + 1
		a["contracts"] = contracts[0:ONE_PAGE_NUM]
		return render_to_response("checkcontracts.html",a)

@checkauth
def queryrepayitems(req,type_id):
    a = {'user':req.user}
    if not checkjurisdiction(req,"还款查询"):
        return render_to_response("jur.html",a)
    
    def item_compare(x,y):
        if y.repaydate>x.repaydate:
            return 1
        elif y.repaydate<x.repaydate:
            return -1
        return 0
    if req.method == "GET":
        fromdate = req.GET.get("fromdate",str(datetime.date.today()))
        todate = req.GET.get("todate",str(datetime.date.today()+datetime.timedelta(7))) #下一周
        contract_number = req.GET.get("contract_id","")
        
        items = [] 
        try:
            contract_id = contract.objects.filter(number=contract_number)[0].id
        except:
            contract_id = -1
        if type_id=="1" or type_id=='4':
            if contract_id != -1:
                try:
                    items = repayitem.objects.filter(repaydate__gte=fromdate,repaydate__lte=todate,
                            thiscontract_id__exact=contract_id)
                except:
                    items = []
            elif contract_number=="":
                items = repayitem.objects.filter(repaydate__gte=fromdate,repaydate__lte=todate)
        elif type_id=="2":
            if contract_id != -1:
                items = repayitem.objects.filter(repaydate__gte=fromdate,repaydate__lte=todate,
                        thiscontract_id__exact=contract_id,repaytype__gte=2,status__exact=1)
            elif contract_number=="":
                items = repayitem.objects.filter(repaydate__gte=fromdate,repaydate__lte=todate,
                        repaytype__gte=2,status__exact=1)
        elif type_id=="3":
            if contract_id != -1:
                items = list(repayitem.objects.filter(repaydate__gte=fromdate,repaydate__lte=todate,
                        thiscontract_id__exact=contract_id,status__exact=1))
                tmpitem = repayitem.objects.filter(repaydate__gte=fromdate,repaydate__lte=todate,
                        thiscontract_id__exact=contract_id,status__exact=3)
                items.extend(list(tmpitem))
            elif contract_number=="":
                items = list(repayitem.objects.filter(repaydate__gte=fromdate,repaydate__lte=todate,
                        status__exact=3))
                tmpitem = repayitem.objects.filter(repaydate__gte=fromdate,repaydate__lte=todate,status__exact=1)
                items.extend(list(tmpitem))
                
        a["repayitems"] = sorted(items,cmp=item_compare)
        a["type_id"] = type_id
        a["fromdate"] = fromdate
        a["todate"] = todate
        return render_to_response("queryrepayitems.html",a)

@checkauth
def getrepayitem(req,item_id):
    a = {'user':req.user}
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
                        thislog = loginfo(info="repay with id=%d" % (thisitem.id),time=str(datetime.datetime.now()),thisuser=req.user)
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
                            thislog = loginfo(info="renew contract %d with id=%d" % (thisitem.thiscontract.id,thisitem.thiscontract.renewal_id),time=str(datetime.datetime.now()),thisuser=req.user)
                            thislog.save()
        else:
            a["info"] = "没有该还款项"
        jsonstr = json.dumps(a,ensure_ascii=False)
        return HttpResponse(jsonstr,content_type='application/javascript')
    
@csrf_exempt
@checkauth
def checkcontracts(req):
    a = {'user':req.user}
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
        if number=="":
            allcount = 0
            for con in contract.objects.all():
                if con.status == 1:
                    allcount += 1
            print allcount
            startpos = ((thispage-1)*ONE_PAGE_NUM if (thispage-1)*ONE_PAGE_NUM<allcount else allcount)
            endpos = (thispage*ONE_PAGE_NUM if thispage*ONE_PAGE_NUM<allcount else allcount)
            contracts = contract.objects.filter(status = 1)[startpos:endpos]
            print contracts.count()
        else:
            contracts = contract.objects.filter(number=number)
        a['curpage'] = thispage
        a['allpage'] = (allcount-1)/ONE_PAGE_NUM + 1
        a['contracts'] = contracts
        return render_to_response("checkcontracts.html",a)

@csrf_exempt
@checkauth
def rollbackcontracts(req):
    a = {'user':req.user}
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
            print allcount
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
	if req.method == 'GET':
		contractid = req.GET.get("contractid",'')
		print "he",contractid
		thiscontract = contract.objects.get(id = int(contractid))
		a["contract"] = thiscontract
		return render_to_response("rollbackcontract.html",a)
	if req.method == 'POST':
		id = req.POST.get("contractid",'')
		thiscontract = contract.objects.get(id = int(id))
		thiscontract.status = 3
		thiscontract.save()
		thislog = loginfo(info="rollbackcontract with id=%d" % (thiscontract.id),time=str(datetime.datetime.now()),thisuser=req.user)
		thislog.save()
		a = {'user':req.user}
		return render_to_response("home.html",a)

@csrf_exempt
@checkauth
def querycontracts(req):
    a = {'user':req.user}
    if not checkjurisdiction(req,"合同查询"):
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
        a = {'user':req.user}
        if pagetype == 'pagedown':
            thispage += 1
        elif pagetype == 'pageup':
            thispage -= 1
        if number=="":
            allcount = contract.objects.count()
            startpos = ((thispage-1)*ONE_PAGE_NUM if (thispage-1)*ONE_PAGE_NUM<allcount else allcount)
            endpos = (thispage*ONE_PAGE_NUM if thispage*ONE_PAGE_NUM<allcount else allcount)
            contracts = contract.objects.all()[startpos:endpos]
        else:
            contracts = contract.objects.filter(number=number)
        a['curpage'] = thispage
        a['allpage'] = (allcount-1)/ONE_PAGE_NUM + 1
        a['contracts'] = contracts
        return render_to_response("querycontracts.html",a)
    if req.method == 'POST':
        a = {'user':req.user}
        contracts = []
        number = req.POST.get("number",'')
        contractbynum = contract.objects.filter(number=number)
        contractbyname = contract.objects.filter(client_name=number)
        if contractbynum.count() == 0:
            contracts = contractbyname            
        else :
            contracts = contractbynum
        a['contract_size'] = contracts.count() 
        a['contracts'] = contracts
        a['curpage'] = 1
        a['allpage'] = 1
        return render_to_response("querycontracts.html",a)

@csrf_exempt
@checkauth
def lastcheck(req):
    a = {'user':req.user}
    if not checkjurisdiction(req,"最终审核"):
        return render_to_response("jur.html",a)
    if req.method == "GET":
        fromdate = req.GET.get("fromdate",str(datetime.date.today()-datetime.timedelta(7)))
        todate = req.GET.get("todate",str(datetime.date.today())) #前一周
        cons = contract.objects.filter(startdate__gte=fromdate,startdate__lte=todate,status=2)
        a = {'user':req.user}
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
        
        cons = contract.objects.filter(startdate__gte=fromdate,startdate__lte=todate,status=2)
        #print fromdate,todate
        print status,':',fromdate,todate
        if status=='2':
            for con in cons:
                con.status = 4
                con.save()
                CreateRepayItem(con) 
        thislog = loginfo(info="lastcheck contracts from %s to %s" % (fromdate,todate),time=str(datetime.datetime.now()),thisuser=req.user)
        thislog.save()
        a = {'user':req.user}
        return render_to_response("home.html",a)
    
@checkauth
def queryproducts(req):
    a = {'user':req.user}
    if not checkjurisdiction(req,"产品管理"):
        return render_to_response("jur.html",a)
    products = product.objects.all()
    a["products"] = products
    return render_to_response("products.html",a)

@csrf_exempt
@checkauth
def renewalcontract(req,repayitem_id):
    a = {'user':req.user}
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
            client_name = req.POST.get('client_name','')
            client_idcard = req.POST.get('client_idcard','')
            bank = req.POST.get('bank','')
            bank_card = req.POST.get("bank_card",'')
            product_id = req.POST.get("product_id",'')
            money = req.POST.get('money','')
            startdate = req.POST.get('startdate','')
            enddate = req.POST.get("enddate",'')
            manager_id = req.POST.get('manager_id','')
            thisrepayitem_id = req.POST.get('repayitem_id','-1')
            if thisrepayitem_id=="-1":
                thiscontract = contract(number=number,client_name=client_name,client_idcard=client_idcard,
                        bank=bank,bank_card=bank_card,money=money,thisproduct_id=int(product_id),startdate=startdate,
                        enddate=enddate,status=1,thismanager_id=int(manager_id),renewal_father_id=-1,renewal_son_id=-1,operator_id=req.user.id)
                thiscontract.save()
                thislog = loginfo(info="new contract with id=%d" % (thiscontract.id),time=str(datetime.datetime.now()),thisuser=req.user)
                thislog.save()
            else:
                thisrepayitem = repayitem.objects.filter(id=int(thisrepayitem_id))[0]
                father_contract = thisrepayitem.thiscontract
                thiscontract = contract(number=number,client_name=client_name,client_idcard=client_idcard,
                        bank=bank,bank_card=bank_card,money=money,thisproduct_id=int(product_id),startdate=startdate,
                        enddate=enddate,status=1,thismanager_id=int(manager_id),renewal_father_id=father_contract.id,renewal_son_id=-1,
                        operator_id=req.user.id)
                thiscontract.save()
                father_contract.renewal_son_id = thiscontract.id
                thisrepayitem.status = 3
                #warnning
                if float(father_contract.money)<=float(thiscontract.money):
                    thisrepayitem.repaymoney = str(float(thisrepayitem.repaymoney) - float(father_contract.money))
                else:
                    thisrepayitem.repaymoney = str(float(thisrepayitem.repaymoney) - float(thiscontract.money))
    
                thisrepayitem.save()
                thislog = loginfo(info="renewal contract %d with id=%d" % (father_contract.id,thiscontract.id),time=str(datetime.datetime.now()),thisuser=req.user)
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
                        mlist.append(m.name)
                    plist.append((p.name,mlist))
                bplist.append((bp.name,plist))
            anslist.append((onefield.name,bplist))
        a = {'user':req.user}
        a["res"] = anslist
        return render_to_response('construct.html', a)
