from django.shortcuts import render
from django.db.models.functions import Cast
from django.db.models import IntegerField
import json
# Create your views here.
from EISHome.models import *
from BrokerEgApi.models import Usermaster
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import math
from datetime import date,timedelta,datetime
from django.db.models import Q
import json


dateToday=date.today()
yesterday=dateToday-timedelta(days=1)
checkday=str(yesterday)
def servicewise_sys(request):
    servicewise=ServiceWise.objects.filter(Layer="SYS").values()
    print(servicewise)
    return JsonResponse({"Service_wise_sys":list(servicewise)})


def ipwise_sys(request):
    ipwise=IpWise.objects.filter(Layer="SYS").values()
    return JsonResponse({"Ip_wise_sys":list(ipwise)})

def portwise_sys(request):
    portwise=PortWise.objects.filter(Layer="SYS").values()
    return JsonResponse({"Port_wise_sys":list(portwise)})

def servicewise_exp(request):
    servicewise=ServiceWise.objects.filter(Layer="EXP").values()
    print(servicewise)
    return JsonResponse({"Service_wise_exp":list(servicewise)})


def ipwise_exp(request):
    ipwise=IpWise.objects.filter(Layer="EXP").values()
    return JsonResponse({"Ip_wise_exp":list(ipwise)})

def portwise_exp(request):
    portwise=PortWise.objects.filter(Layer="EXP").values()
    return JsonResponse({"Port_wise_exp":list(portwise)})

def MonthlyFARExpiring(request):
    pass

#getting top 5 values for ip wise all
def ipwiseSorted(request):
    try:
       ipWise=IpWise.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Date_day=(checkday+" 00:00:00.000000")).order_by('-Hits_integer').values('Ip','Layer','Hits','Date_day')[:5]
       #ipWise=IpWise.objects.filter(Date_day=(checkday+" 00:00:00.000000")).order_by('-Hits').values('Ip','Layer','Hits','Date_day')[:5]
       ipWiseWLog=list()
       for values in ipWise:
           ihit=int(values.get("Hits",1))
           ipWLog=values.copy()
           wLog=round(math.log10(ihit)) if ihit > 0 else 0
           ipWLog["logVal"]=wLog
           ipWiseWLog.append(ipWLog)
    except Exception as e:
        return JsonResponse({"An error occured while fetching the data"},status=500)
    return JsonResponse({"Ip_wise_top5":ipWiseWLog},safe=False)


#getting top 5 for service wise all
def serviceWiseSorted(request):
    try:
       serviceWise=ServiceWise.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Date_day=(checkday+" 00:00:00.000000")).order_by('-Hits_integer').values('Service_name','Layer','Hits','Date_day')[:5]
       serviceWiseWLog=list()
       for values in serviceWise:
           ihit=int(values.get("Hits",1))
           serviceWLog=values.copy()
           wLog=round(math.log10(ihit)) if ihit > 0 else 0
           serviceWLog["logVal"]=wLog
           serviceWiseWLog.append(serviceWLog)
    except Exception as e:
        return JsonResponse({"An error occured while fetching the data"},status=500,safe=False)
    return JsonResponse({"service_wise_top5":serviceWiseWLog},safe=False)





#getting top 5 values for ip wise only for sys
def ipwiseSortedSys(request):
    try:
       dateToday=date.today()
       yesterday=dateToday-timedelta(days=1)
       checkday=str(yesterday)
    #   return JsonResponse({"d":(dateToday+" 00:00:00.000000")},safe=False)
       ipWise=IpWise.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer="SYS",Date_day=(checkday+" 00:00:00.000000")).order_by('-Hits_integer').values('Ip','Layer','Hits','Date_day')[:5]
       ipWiseWLog=list()
       for values in ipWise:
           ihit=int(values.get("Hits",1))
           ipWLog=values.copy()
           wLog=round(math.log10(ihit)) if ihit > 0 else 0
           ipWLog["logVal"]=wLog
           ipWiseWLog.append(ipWLog)
    except Exception as e:
        return JsonResponse({"An error occured while fetching the data"},status=500)
    return JsonResponse({"Ip_wise_top5":ipWiseWLog},safe=False)



#getting top 5 values for ip wise only for exp
def ipwiseSortedExp(request):
    try:
       ipWise=IpWise.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer="EXP",Date_day=(checkday+" 00:00:00.000000")).order_by('-Hits_integer').values('Ip','Layer','Hits','Date_day')[:5]
       #ipWise=IpWise.objects.filter(Layer="EXP",Date_day=(checkday+" 00:00:00.000000")).order_by('-Hits').values('Ip','Layer','Hits','Date_day')[:5]
       ipWiseWLog=list()
       for values in ipWise:
           ihit=int(values.get("Hits",1))
           ipWLog=values.copy()
           wLog=round(math.log10(ihit)) if ihit > 0 else 0
           ipWLog["logVal"]=wLog
           ipWiseWLog.append(ipWLog)
    except Exception as e:
        return JsonResponse({"An error occured while fetching the data"},status=500)
    return JsonResponse({"Ip_wise_top5":ipWiseWLog},safe=False)



#getting top 5 for service wise exp
def serviceWiseSortedExp(request):
    try:
       serviceWise=ServiceWise.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer="EXP",Date_day=(checkday+" 00:00:00.000000")).order_by('-Hits_integer').values('Service_name','Layer','Hits','Date_day')[:5]
       #serviceWise=ServiceWise.objects.filter(Layer="EXP",Date_day=(checkday+" 00:00:00.000000")).order_by('-Hits').values('Service_name','Layer','Hits','Date_day')[:5]
       serviceWiseWLog=list()
       for values in serviceWise:
           ihit=int(values.get("Hits",1))
           serviceWLog=values.copy()
           wLog=round(math.log10(ihit)) if ihit > 0 else 0
           serviceWLog["logVal"]=wLog
           serviceWiseWLog.append(serviceWLog)
    except Exception as e:
        return JsonResponse({"An error occured while fetching the data"},status=500,safe=False)
    return JsonResponse({"service_wise_top5":serviceWiseWLog},safe=False)




#getting top 5 for service wise sys
def serviceWiseSortedSys(request):
    try:
       serviceWise=ServiceWise.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer="SYS",Date_day=(checkday+" 00:00:00.000000")).order_by('-Hits_integer').values('Service_name','Layer','Hits','Date_day')[:5]
       #serviceWise=ServiceWise.objects.filter(Layer="SYS",Date_day=(checkday+" 00:00:00.000000")).order_by('-Hits').values('Service_name','Layer','Hits','Date_day')[:5]
       serviceWiseWLog=list()
       for values in serviceWise:
           ihit=int(values.get("Hits",1))
           serviceWLog=values.copy()
           wLog=round(math.log10(ihit)) if ihit > 0 else 0
           serviceWLog["logVal"]=wLog
           serviceWiseWLog.append(serviceWLog)
    except Exception as e:
        return JsonResponse({"An error occured while fetching the data"},status=500,safe=False)
    return JsonResponse({"service_wise_top5":serviceWiseWLog},safe=False)




#getting top 5 for port wise sys
def portWiseSortedSys(request):
    try:
       portWise=PortWise.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer="SYS",Date_day=(checkday+" 00:00:00.000000")).order_by('-Hits_integer').values('Port','Layer','Hits','Date_day')[:5]
       #portWise=PortWise.objects.filter(Layer="SYS",Date_day=(checkday+" 00:00:00.000000")).order_by('-Hits').values('Port','Layer','Hits','Date_day')[:5]
       portWiseWLog=list()
       for values in portWise:
           ihit=int(values.get("Hits",1))
           portWLog=values.copy()
           wLog=round(math.log10(ihit)) if ihit > 0 else 0
           portWLog["logVal"]=wLog
           portWiseWLog.append(portWLog)
    except Exception as e:
        return JsonResponse({"An error occured while fetching the data"},status=500,safe=False)
    return JsonResponse({"port_wise_top5":portWiseWLog},safe=False)



#getting top 5 for port wise exp
def portWiseSortedExp(request):
    try:
       portWise=PortWise.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer="EXP",Date_day=(checkday+" 00:00:00.000000")).order_by('-Hits_integer').values('Port','Layer','Hits','Date_day')[:5]
       #portWise=PortWise.objects.filter(Layer="EXP",Date_day=(checkday+" 00:00:00.000000")).order_by('-Hits').values('Port','Layer','Hits','Date_day')[:5]
       portWiseWLog=list()
       for values in portWise:
           ihit=int(values.get("Hits",1))
           portWLog=values.copy()
           wLog=round(math.log10(ihit)) if ihit > 0 else 0
           portWLog["logVal"]=wLog
           portWiseWLog.append(portWLog)
    except Exception as e:
        return JsonResponse({"An error occured while fetching the data"},status=500,safe=False)
    return JsonResponse({"port_wise_top5":portWiseWLog},safe=False)



#port wise Exp and sys with time
@csrf_exempt
def portWiseTime(request,layer):
    try:
        if layer not in ['SYS','EXP']:
           return JsonResponse({"403 Bad Request"},status=403,safe=False)
        if request.method == 'POST':
           data_json=json.loads(request.body.decode('utf-8'))
           time=data_json.get("time")
           portWise="declaring for safety"
           if time == "5min":
              portWise=PortWiseToday.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day__gt=datetime.now()-timedelta(minutes=5),Date_day__lt=datetime.now()).order_by('-Hits_integer').values('Port','Layer','Hits','Date_day')[:5]
       #portWise=PortWise.objects.filter(Layer="EXP",Date_day=(checkday+" 00:00:00.000000")).order_by('-Hits').values('Port','Layer','Hits','Date_day')[:5]
           elif time=="15min":
              portWise=PortWiseToday.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day__gt=datetime.now()-timedelta(minutes=15),Date_day__lt=datetime.now()).order_by('-Hits_integer').values('Port','Layer','Hits','Date_day')[:5]
           elif time=="30min":
              portWise=PortWiseToday.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day__gt=datetime.now()-timedelta(minutes=30),Date_day__lt=datetime.now()).order_by('-Hits_integer').values('Port','Layer','Hits','Date_day')[:5]
           elif time=="1hour":
              portWise=PortWiseToday.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day__gt=datetime.now()-timedelta(minutes=60),Date_day__lt=datetime.now()).order_by('-Hits_integer').values('Port','Layer','Hits','Date_day')[:5]
           elif time=="tillnow":
              portWise=PortWiseToday.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day__lt=datetime.now()).order_by('-Hits_integer').values('Port','Layer','Hits','Date_day')[:5]
           elif time=="yesterday":
              portWise=PortWise.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day=(checkday+" 00:00:00.000000")).order_by('-Hits_integer').values('Port','Layer','Hits','Date_day')[:5]
           elif time[0:6]=="custom":
              customDate=time[7:]
              portWise=PortWise.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day=(customDate+" 00:00:00.000000")).order_by('-Hits_integer').values('Port','Layer','Hits','Date_day')[:5]
           else:
              return JsonResponse({"403 Bad Request"},status=403,safe=False)
           portWiseWLog=list()
           for values in portWise:
               ihit=int(values.get("Hits",1))
               portWLog=values.copy()
               wLog=round(math.log10(ihit)) if ihit > 0 else 0
               portWLog["logVal"]=wLog
               portWiseWLog.append(portWLog)
           return JsonResponse({"port_wise_top5":portWiseWLog},status=200,safe=False)
    except Exception as e:
        return JsonResponse({"An error occured while fetching the data"},status=500,safe=False)
    return JsonResponse({"port_wise_top5":portWiseWLog},safe=False)


#ip wise Exp and sys with time
@csrf_exempt
def ipWiseTime(request,layer):
    try:
        if layer not in ['SYS','EXP']:
           return JsonResponse({"403 Bad Request"},status=403,safe=False)
        if request.method == 'POST':
           data_json=json.loads(request.body.decode('utf-8'))
           time=data_json.get("time")
           ipWise="declaring for safety"
           if time == "5min":
              ipWise=IpWiseToday.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day__gt=datetime.now()-timedelta(minutes=5),Date_day__lt=datetime.now()).order_by('-Hits_integer').values('Ip','Layer','Hits','Date_day')[:5]
       #portWise=PortWise.objects.filter(Layer="EXP",Date_day=(checkday+" 00:00:00.000000")).order_by('-Hits').values('Port','Layer','Hits','Date_day')[:5]
           elif time=="15min":
              ipWise=IpWiseToday.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day__gt=datetime.now()-timedelta(minutes=15),Date_day__lt=datetime.now()).order_by('-Hits_integer').values('Ip','Layer','Hits','Date_day')[:5]
           elif time=="30min":
              ipWise=IpWiseToday.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day__gt=datetime.now()-timedelta(minutes=30),Date_day__lt=datetime.now()).order_by('-Hits_integer').values('Ip','Layer','Hits','Date_day')[:5]
           elif time=="1hour":
              ipWise=IpWiseToday.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day__gt=datetime.now()-timedelta(minutes=60),Date_day__lt=datetime.now()).order_by('-Hits_integer').values('Ip','Layer','Hits','Date_day')[:5]
           elif time=="tillnow":
              ipWise=IpWiseToday.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day__lt=datetime.now()).order_by('-Hits_integer').values('Ip','Layer','Hits','Date_day')[:5]
           elif time=="yesterday":
              ipWise=IpWise.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day=(checkday+" 00:00:00.000000")).order_by('-Hits_integer').values('Ip','Layer','Hits','Date_day')[:5]
           elif time[0:6]=="custom":
              customDate=time[7:]
              ipWise=IpWise.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day=(customDate+" 00:00:00.000000")).order_by('-Hits_integer').values('Ip','Layer','Hits','Date_day')[:5]
           else:
              return JsonResponse({"403 Bad Request"},status=403,safe=False)
           ipWiseWLog=list()
           for values in ipWise:
               ihit=int(values.get("Hits",1))
               ipWLog=values.copy()
               wLog=round(math.log10(ihit)) if ihit > 0 else 0
               ipWLog["logVal"]=wLog
               ipWiseWLog.append(ipWLog)
           return JsonResponse({"Ip_wise_top5":ipWiseWLog},status=200,safe=False)
    except Exception as e:
        return JsonResponse({"An error occured while fetching the data"},status=500,safe=False)
    return JsonResponse({"Ip_wise_top5":ipWiseWLog},safe=False)



#service wise Exp and sys with time
@csrf_exempt
def serviceWiseTime(request,layer):
    try:
        if layer not in ['SYS','EXP']:
           return JsonResponse({"403 Bad Request"},status=403,safe=False)
        if request.method == 'POST':
           data_json=json.loads(request.body.decode('utf-8'))
           time=data_json.get("time")
           serviceWise="declaring for safety"
           if time == "5min":
              serviceWise=ServiceWiseToday.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day__gt=datetime.now()-timedelta(minutes=5),Date_day__lt=datetime.now()).order_by('-Hits_integer').values('Service_name','Layer','Hits','Date_day')[:5]
       #serviceWise=serviceWise.objects.filter(Layer="EXP",Date_day=(checkday+" 00:00:00.000000")).order_by('-Hits').values('Service_name','Layer','Hits','Date_day')[:5]
           elif time=="15min":
              serviceWise=ServiceWiseToday.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day__gt=datetime.now()-timedelta(minutes=15),Date_day__lt=datetime.now()).order_by('-Hits_integer').values('Service_name','Layer','Hits','Date_day')[:5]
           elif time=="30min":
              serviceWise=ServiceWiseToday.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day__gt=datetime.now()-timedelta(minutes=30),Date_day__lt=datetime.now()).order_by('-Hits_integer').values('Service_name','Layer','Hits','Date_day')[:5]
           elif time=="1hour":
              serviceWise=ServiceWiseToday.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day__gt=datetime.now()-timedelta(minutes=60),Date_day__lt=datetime.now()).order_by('-Hits_integer').values('Service_name','Layer','Hits','Date_day')[:5]
           elif time=="tillnow":
              serviceWise=ServiceWiseToday.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day__lt=datetime.now()).order_by('-Hits_integer').values('Service_name','Layer','Hits','Date_day')[:5]
           elif time=="yesterday":
              serviceWise=ServiceWise.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day=(checkday+" 00:00:00.000000")).order_by('-Hits_integer').values('Service_name','Layer','Hits','Date_day')[:5]
           elif time[0:6]=="custom":
              customDate=time[7:]
              serviceWise=ServiceWise.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day=(customDate+" 00:00:00.000000")).order_by('-Hits_integer').values('Service_name','Layer','Hits','Date_day')[:5]
           else:
              return JsonResponse({"403 Bad Request"},status=403,safe=False)
           serviceWiseWLog=list()
           for values in serviceWise:
               ihit=int(values.get("Hits",1))
               serviceWLog=values.copy()
               wLog=round(math.log10(ihit)) if ihit > 0 else 0
               serviceWLog["logVal"]=wLog
               serviceWiseWLog.append(serviceWLog)
           return JsonResponse({"service_wise_top5":serviceWiseWLog},status=200,safe=False)
    except Exception as e:
        return JsonResponse({"An error occured while fetching the data"},status=500,safe=False)
    return JsonResponse({"service_wise_top5":serviceWiseWLog},safe=False)








@csrf_exempt
def Login(request):
    try:
        if request.method == 'POST':
            #return JsonResponse("")
            data_json=json.loads(request.body.decode('utf-8'))
            uid=data_json.get("uid")
            password=data_json.get("password")
            if not uid or not password:
                return JsonResponse({"Response":"username or password is required","status":400},status=400,safe=False)
            try:
               user = Usermaster.objects.get(uid = uid, pwd = password)
               print(user.empname)
            except Exception as e:
                return JsonResponse({"Response":"login Unsuccessfull","status":401},status=401,safe=False)
            if user is not None:
                request.session.set_expiry(3600)
                request.session['username']=user.empname
                request.session['level']=user.superlevel
                if user.superlevel == 'L2':
                    return JsonResponse({"Response":"login successfull","userLevel":"L2","status":302},status=200,safe=False)
                return JsonResponse({"Response":"login successfull","userLevel":"L1","status":302},status=200,safe=False)
            return JsonResponse({"Response":"login Unsuccessfull","status":401},status=401,safe=False)

    except Exception as e:
        return JsonResponse({"error":"An error occured while performing login ","e":str(e)},status=500,safe=False)
    return JsonResponse({"Response":"login successfull"},status=302,safe=False)
