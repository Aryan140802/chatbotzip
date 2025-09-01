
from django.shortcuts import render
from django.db.models.functions import Cast
from django.db.models import IntegerField
import json
# Create your views here.
from EISHome.models import *
from BrokerEgApi.models import Usermaster
from EISChatBot.models import FarDetailsAll
from EISChatBot.Server_data import fetch_api_db
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import math
from datetime import date,timedelta,datetime
from django.db.models import Q
import json
from django.contrib.auth import authenticate, login,logout
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers import Cipher,algorithms,modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os
from dbOpTest.models import ServiceDetails
from . import getSwagger
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
            uid=data_json.get("uid")
            password=data_json.get("password")
            download=data_json.get("download")
            print(checkday)
            print("hello")
            if not authenticate(uid,password):
                return JsonResponse({"msg":"An error occured while fetching the data"},status=500,safe=False)
            portWise="declaring for safety"
            if time == "5min":
                portWise=PortWiseToday.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day__gt=datetime.now()-timedelta(minutes=5),Date_day__lt=datetime.now()).order_by('-Hits_integer').values('Port','Layer','Hits','Date_day')
                if len(portWise)==0:
                    portWise=PortWiseToday.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day__gt=datetime.now()-timedelta(minutes=10),Date_day__lt=datetime.now()).order_by('-Hits_integer').values('Port','Layer','Hits','Date_day')
                if(download):
                    portWise=portWise
                else:
                    portWise=list(portWise)[:5]

       #portWise=PortWise.objects.filter(Layer="EXP",Date_day=(checkday+" 00:00:00.000000")).order_by('-Hits').values('Port','Layer','Hits','Date_day')[:5]
            elif time=="15min":
                portWise=PortWiseToday.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day__gt=datetime.now()-timedelta(minutes=15),Date_day__lt=datetime.now()).order_by('-Hits_integer').values('Port','Layer','Hits','Date_day')
                if(download):
                    portWise=portWise
                else:
                    portWise=list(portWise)[:5]
            elif time=="30min":
                portWise=PortWiseToday.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day__gt=datetime.now()-timedelta(minutes=30),Date_day__lt=datetime.now()).order_by('-Hits_integer').values('Port','Layer','Hits','Date_day')
                if(download):
                    portWise=portWise
                else:
                    portWise=list(portWise)[:5]
            elif time=="1hour":
                portWise=PortWiseToday.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day__gt=datetime.now()-timedelta(minutes=60),Date_day__lt=datetime.now()).order_by('-Hits_integer').values('Port','Layer','Hits','Date_day')
                if(download):
                    portWise=portWise
                else:
                    portWise=list(portWise)[:5]
            elif time=="tillnow":
                portWise=PortWiseToday.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day__lt=datetime.now()).order_by('-Hits_integer').values('Port','Layer','Hits','Date_day')
                if(download):
                    portWise=portWise
                else:
                    portWise=list(portWise)[:5]
            elif time=="yesterday":
                portWise=PortWise.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day=(checkday+" 00:00:00.000000")).order_by('-Hits_integer').values('Port','Layer','Hits','Date_day')
                if(download):
                    portWise=portWise
                else:
                    portWise=list(portWise)[:5]
            elif time[0:6]=="custom":
                customDate=time[7:]
                portWise=PortWise.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day=(customDate+" 00:00:00.000000")).order_by('-Hits_integer').values('Port','Layer','Hits','Date_day')
                if(download):
                    portWise=portWise
                else:
                    portWise=list(portWise)[:5]
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
            uid=data_json.get("uid")
            password=data_json.get("password")
            download=data_json.get("download")
            if not authenticate(uid,password):
                return JsonResponse({"msg":"An error occured while fetching the data"},status=500,safe=False)
            ipWise="declaring for safety"
            if time == "5min":
                ipWise=IpWiseToday.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day__gt=datetime.now()-timedelta(minutes=5),Date_day__lt=datetime.now()).order_by('-Hits_integer').values('Ip','Layer','Hits','Date_day')
                if len(ipWise)==0:
                    ipWise=IpWiseToday.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day__gt=datetime.now()-timedelta(minutes=10),Date_day__lt=datetime.now()).order_by('-Hits_integer').values('Ip','Layer','Hits','Date_day')
                if(download):
                    ipWise=ipWise
                else:
                    ipWise=list(ipWise)[:5]
       #portWise=PortWise.objects.filter(Layer="EXP",Date_day=(checkday+" 00:00:00.000000")).order_by('-Hits').values('Port','Layer','Hits','Date_day')[:5]
            elif time=="15min":
                ipWise=IpWiseToday.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day__gt=datetime.now()-timedelta(minutes=15),Date_day__lt=datetime.now()).order_by('-Hits_integer').values('Ip','Layer','Hits','Date_day')
                if(download):
                    ipWise=ipWise
                else:
                    ipWise=list(ipWise)[:5]
            elif time=="30min":
                ipWise=IpWiseToday.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day__gt=datetime.now()-timedelta(minutes=30),Date_day__lt=datetime.now()).order_by('-Hits_integer').values('Ip','Layer','Hits','Date_day')
                if(download):
                    ipWise=ipWise
                else:
                    ipWise=ipWise[:5]
            elif time=="1hour":
                ipWise=IpWiseToday.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day__gt=datetime.now()-timedelta(minutes=60),Date_day__lt=datetime.now()).order_by('-Hits_integer').values('Ip','Layer','Hits','Date_day')
                if(download):
                    ipWise=ipWise
                else:
                    ipWise=ipWise[:5]
            elif time=="tillnow":
                ipWise=IpWiseToday.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day__lt=datetime.now()).order_by('-Hits_integer').values('Ip','Layer','Hits','Date_day')
                if(download):
                    ipWise=ipWise
                else:
                    ipWise=ipWise[:5]
            elif time=="yesterday":
                ipWise=IpWise.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day=(checkday+" 00:00:00.000000")).order_by('-Hits_integer').values('Ip','Layer','Hits','Date_day')
                if(download):
                    ipWise=ipWise
                else:
                    ipWise=ipWise[:5]
            elif time[0:6]=="custom":
                customDate=time[7:]
                ipWise=IpWise.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day=(customDate+" 00:00:00.000000")).order_by('-Hits_integer').values('Ip','Layer','Hits','Date_day')
                if(download):
                    ipWise=ipWise
                else:
                    ipWise=ipWise[:5]
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
            uid=data_json.get("uid")
            password=data_json.get("password")
            download=data_json.get("download")
            if not authenticate(uid,password):
                return JsonResponse({"msg":"An error occured while fetching the data"},status=500,safe=False)
            serviceWise="declaring for safety"
            if time == "5min":
                serviceWise=ServiceWiseToday.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day__gt=datetime.now()-timedelta(minutes=5),Date_day__lt=datetime.now()).order_by('-Hits_integer').values('Service_name','Layer','Hits','Date_day')
                if len(serviceWise)==0:
                    serviceWise=ServiceWiseToday.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day__gt=datetime.now()-timedelta(minutes=10),Date_day__lt=datetime.now()).order_by('-Hits_integer').values('Service_name','Layer','Hits','Date_day')
                if(download):
                    serviceWise=serviceWise
                else:
                    serviceWise=serviceWise[:5]

       #serviceWise=serviceWise.objects.filter(Layer="EXP",Date_day=(checkday+" 00:00:00.000000")).order_by('-Hits').values('Service_name','Layer','Hits','Date_day')[:5]
            elif time=="15min":
                serviceWise=ServiceWiseToday.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day__gt=datetime.now()-timedelta(minutes=15),Date_day__lt=datetime.now()).order_by('-Hits_integer').values('Service_name','Layer','Hits','Date_day')
                if(download):
                    serviceWise=serviceWise
                else:
                    serviceWise=serviceWise[:5]
            elif time=="30min":
                serviceWise=ServiceWiseToday.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day__gt=datetime.now()-timedelta(minutes=30),Date_day__lt=datetime.now()).order_by('-Hits_integer').values('Service_name','Layer','Hits','Date_day')
                if(download):
                    serviceWise=serviceWise
                else:
                    serviceWise=serviceWise[:5]
            elif time=="1hour":
                serviceWise=ServiceWiseToday.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day__gt=datetime.now()-timedelta(minutes=60),Date_day__lt=datetime.now()).order_by('-Hits_integer').values('Service_name','Layer','Hits','Date_day')
                if(download):
                    serviceWise=serviceWise
                else:
                    serviceWise=serviceWise[:5]
            elif time=="tillnow":
                serviceWise=ServiceWiseToday.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day__lt=datetime.now()).order_by('-Hits_integer').values('Service_name','Layer','Hits','Date_day')
                if(download):
                    serviceWise=serviceWise
                else:
                    serviceWise=serviceWise[:5]
            elif time=="yesterday":
                serviceWise=ServiceWise.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day=(checkday+" 00:00:00.000000")).order_by('-Hits_integer').values('Service_name','Layer','Hits','Date_day')
                if(download):
                    serviceWise=serviceWise
                else:
                    serviceWise=serviceWise[:5]
            elif time[0:6]=="custom":
                customDate=time[7:]
                serviceWise=ServiceWise.objects.annotate(Hits_integer=Cast('Hits', output_field=IntegerField())).filter(Layer=layer,Date_day=(customDate+" 00:00:00.000000")).order_by('-Hits_integer').values('Service_name','Layer','Hits','Date_day')
                if(download):
                    serviceWise=serviceWise
                else:
                    serviceWise=serviceWise[:5]
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



#get far details of next 12 months
def farDetailsFiveM(request):
    try:
        curMonthc=datetime.now()
        currMonth=curMonthc.month
        DetailsAll=list()
        yearcal=curMonthc.year
        j=0
        for i in range(0,12):
           if (currMonth)%12==1:
              currMonth=1
              yearcal+=1
              j=0

           Details = FarDetailsAll.objects.filter(Expires__startswith=((str(yearcal)+'-0'+str(currMonth)))).count()
           #Details = FarDetailsAll.objects.filter(Expires__startswith=((str(yearcal)+'-0'+str(currMonth)))).values()
           #Details_far=[f'{far["Far_Id"]}:{far["Subject"]}' for far in Details]
           monthName=date(yearcal,currMonth, 1).strftime('%B')
           #DetailsAll.append({monthName+"-"+str(yearcal):Details_far)})
           DetailsAll.append({monthName+"-"+str(yearcal):Details})
           currMonth+=1
        return JsonResponse({"MonthlyFarCount":DetailsAll},status=200,safe=False)

    except Exception as e:
        return JsonResponse({"An error occured while fetchit the data":e},status=500,safe=False)
    return JsonResponse({"An Error occured while fetching the data"},status=500,safe=False)




#get far details of a specific month
@csrf_exempt
def farDetailsSpecific(request):
    try:
        if request.method == 'POST':
           DetailsAll=list()
           data_json=json.loads(request.body.decode('utf-8'))
           uid = data_json.get("uid")
           password = data_json.get("password")
           try:
                decryptedPassword = decryptor(password)
           except Exception as e:
                return JsonResponse({"message": "user unauthorized"}, status=401, safe=False)

           if uid and password:
                try:
                    user = Usermaster.objects.get(uid=uid, pwd=decryptedPassword)
                except Exception as e:
                    return JsonResponse({"403 Bad Request": str(e)}, status=403, safe=False)
           filter_date=data_json.get('data_filter')
           filterArr=filter_date.split(" ")
           month=filterArr[0]
           year=filterArr[1]
           monthNum=datetime.strptime(month,"%B").month
           print(month)
           #for saftety
           Details=None
           if month == "all":
               Details = FarDetailsAll.objects.filter(Expires__startswith=((str(year)+'-0'))).values("Far_Id","Subject","Status","Created","Expires","Dependent_application","Permanent_Rule","ZONE")
           else:
               Details = FarDetailsAll.objects.filter(Expires__startswith=((str(year)+'-0'+str(monthNum)))).values("Far_Id","Subject","Status","Created","Expires","Dependent_application","Permanent_Rule","ZONE")
           #Details = FarDetailsAll.objects.filter(Expires__startswith=((str(yearcal)+'-0'+str(currMonth)))).values()
           #Details_far=[f'{far["Far_Id"]}:{far["Subject"]}' for far in Details]
           print(Details)
           return JsonResponse({"MonthlyDetails":list(Details)},status=200,safe=False)
        return JsonResponse({"got an error":"403 bad request"},status=403,safe=False)
    except Exception as e:
        return JsonResponse({"An error occured while fetchit the data":e},status=500,safe=False)
    return JsonResponse({"An Error occured while fetching the data"},status=500,safe=False)



#mq hourly details top 5 by current date api
@csrf_exempt
def mqHourlyd(request,layer):
    print("layer",layer)
    try:
       if request.method == 'POST':
            data_json = json.loads(request.body.decode('utf-8'))
            hour = data_json.get("hour")  # This should be a list
            uid = data_json.get("uid")
            password = data_json.get("password")
            download=False
            try:
               download=data_json.get("download")
            except Exception as e:
                download=False
            hourly_top5=None
            if not authenticate(uid,password):
                return JsonResponse({"msg":"An error occured while fetching the data"},status=500,safe=False)
            try:
               hourly_top5=mqHourly.objects.filter(hour__icontains=hour,date=date.today(),layer=layer).order_by('-msgCount').values()
               print(hourly_top5)
            except Exception as e:
               print(e)
            mqHourlyWiseWLog=list()
            for values in hourly_top5:
                ihit=int(values.get("msgCount",1))
                mqWLog=values.copy()
                wLog=round(math.log10(ihit)) if ihit > 0 else 0
                mqWLog["logVal"]=wLog
                mqHourlyWiseWLog.append(mqWLog)
            print(mqHourlyWiseWLog[:5])
            if download:
              return JsonResponse({"HourlyMqDetails":mqHourlyWiseWLog},status=200,safe=False)
            else:
              return JsonResponse({"HourlyMqDetails":mqHourlyWiseWLog[:5]},status=200,safe=False)

    except Exception as e:
        return JsonResponse({"An Error occured while fetching the data"},status=500,safe=False)


#mq overall hits details top 5 by current date api
@csrf_exempt
def mqOveralld(request,layer):
    try:
       if request.method == 'POST':
            data_json = json.loads(request.body.decode('utf-8'))
            uid = data_json.get("uid")
            password = data_json.get("password")
            download=False
            try:
                download=data_json.get("download")
            except Exception as e:
                download=False
            overall_top5=None
            if not authenticate(uid,password):
                return JsonResponse({"msg":"An error occured while fetching the data"},status=500,safe=False)

            overall_top5=mqOverall.objects.filter(date=date.today(),layer=layer).order_by('-msgCount').values()
            print(mqOverall)
            mqOverallWiseWLog=list()
            for values in overall_top5:
                ihit=int(values.get("msgCount",1))
                mqWLog=values.copy()
                wLog=round(math.log10(ihit)) if ihit > 0 else 0
                mqWLog["logVal"]=wLog
                mqOverallWiseWLog.append(mqWLog)
            if download:
                return JsonResponse({"mqOverallWiseWLog":mqOverallWiseWLog},status=200,safe=False)
            else:
                return JsonResponse({"mqOverallWiseWLog":mqOverallWiseWLog[:5]},status=200,safe=False)

    except Exception as e:
        return JsonResponse({"An Error occured while fetching the data"},status=500,safe=False)


#mq source hits details top 5 by current date api
@csrf_exempt
def mqSourced(request,layer):
    try:
       if request.method == 'POST':
            data_json = json.loads(request.body.decode('utf-8'))
            uid = data_json.get("uid")
            password = data_json.get("password")
            download=False
            try:
               download=data_json.get("download")
            except Exception as e:
               download=False
            source_top5=None
            if not authenticate(uid,password):
                return JsonResponse({"msg":"An error occured while fetching the data"},status=500,safe=False)

            source_top5=mqSource.objects.filter(date=date.today(),layer=layer).order_by('-msgCount').values()
            mqSourceWiseWLog=list()
            for values in source_top5:
                ihit=int(values.get("msgCount",1))
                mqWLog=values.copy()
                wLog=round(math.log10(ihit)) if ihit > 0 else 0
                mqWLog["logVal"]=wLog
                mqSourceWiseWLog.append(mqWLog)
            if download:
                return JsonResponse({"mqSourceWiseWLog":mqSourceWiseWLog},status=200,safe=False)
            else:
                return JsonResponse({"mqSourceWiseWLog":mqSourceWiseWLog[:5]},status=200,safe=False)

    except Exception as e:
        return JsonResponse({"An Error occured while fetching the data"},status=500,safe=False)







def PRDRactive(request):
    path="/var/www/cgi-bin/PyPortal/EISHome/PRDRActiveSetup.txt"
    f = open(path)
    return f.read()


@csrf_exempt
def postFavourites(request):
    try:
        if request.method == 'POST':
            data_json = json.loads(request.body.decode('utf-8'))
            favourites = data_json.get("favList")  # This should be a list
            uid = data_json.get("userId")
            password = data_json.get("password")

            try:
                decryptedPassword = decryptor(password)
            except Exception as e:
                return JsonResponse({"message": "user unauthorized"}, status=401, safe=False)

            if uid and password:
                try:
                    user = Usermaster.objects.get(uid=uid, pwd=decryptedPassword)
                except Exception as e:
                    return JsonResponse({"403 Bad Request": str(e)}, status=403, safe=False)

                # Save favorites if provided
                if favourites is not None:
                    if not isinstance(favourites, list):
                        return JsonResponse({"error": "favList must be an array"}, status=400)

                    fav_str = ",".join(favourites)  # Convert list to string

                    fav_obj, created = UserFavourites.objects.get_or_create(user=user)
                    fav_obj.favouriteOptions = fav_str
                    fav_obj.save()

                    return JsonResponse({"favourites": favourites})  # 🔁 return as list

                # Just fetch favorites
                if UserFavourites.objects.filter(user=user).exists():
                    fav_obj = UserFavourites.objects.get(user=user)
                    fav_str = fav_obj.favouriteOptions or ""
                    fav_list = [item.strip() for item in fav_str.split(',') if item.strip()]
                    return JsonResponse({"favourites": fav_list})  # ✅ return as array

                # If no UserFavourites exists
                UserFavourites.objects.create(favouriteOptions="", user=user)
                return JsonResponse({"favourites": []})

        return JsonResponse({"message": "Only POST supported"}, status=405)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



#get  the favourite of user
@csrf_exempt
def postgetFavourites(request):
    try:
        if request.method == 'POST':
           data_json=json.loads(request.body.decode('utf-8'))
           uid=request.session.get("userId")
           userSession = authenticate(username=2743582,password="password")
           print(userSession)
           if  userSession==None:
               return JsonResponse({"Invalid credentials"},status=403,safe=False)
           if  uid:
               user=UserFavourites.objects.get(uid=uid)
               if user is not None:
                  return JsonResponse({"favourites":user.favouriteOptions})
           else:
              return JsonResponse({"403 Bad Request"},status=403,safe=False)
           return JsonResponse({"message":"Data of Favourites updated"},status=200,safe=False)
    except Exception as e:
        return JsonResponse({"An error occured while saving the data"},status=500,safe=False)




#view for complince through api
@csrf_exempt
def complianceByIp(request):
    try:
        if request.method == 'POST':
           data_json=json.loads(request.body.decode('utf-8'))
           print(data_json)
           ipAddress=data_json.get("ipAddress")
           complianceIp=Compliance.objects.filter(ip_address=ipAddress).values()

           return JsonResponse({"ComplianceDetails":list(complianceIp)},status=200,safe=False)

    except Exception as e:
        print(e)
        return JsonResponse({"An error occured while fetchit the data":e},status=500,safe=False)
    return JsonResponse({"An Error occured while fetching the data"},status=500,safe=False)



#for decrypting user details
def decryptor(encryptedPass):
     try:
        encryptedData=bytes.fromhex(encryptedPass)
        key = b'Sixteen byte key'
        iv = b'Sixteen byte ivv'
        cipher=Cipher(algorithms.AES(key),modes.CBC(iv),backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_padded = decryptor.update(encryptedData) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        decrypted_data = unpadder.update(decrypted_padded) + unpadder.finalize()
        decrypted_text = decrypted_data.decode('utf-8')
        return str(decrypted_text)
     except Exception as e:
        return str(e)


#for api authentication
def authenticate(uid,password):
    try:
       decryptedPassword=decryptor(password)
    except Exception as e:
       return False
    if uid and decryptedPassword:
       try:
          user = Usermaster.objects.get(uid = uid, pwd = decryptedPassword)
       except Exception as e:
          user = None
       if user:
          return user.superlevel
       else:
          return False
    else:
       return False
    return False


@csrf_exempt
def authenticatePortal(request):
    try:
       if request.method == 'POST':
          data_json=json.loads(request.body.decode('utf-8'))
          uid=data_json.get("uid")
          password=data_json.get("password")
          if not authenticate(uid,password):
             return JsonResponse({"Response":"login Unsuccessfull","status":401},status=401,safe=False)
          return JsonResponse({"Response":"login successfull","userLevel":"L2","status":302,"uid":uid},status=200,safe=False)
    except Exception as e:
       return str(e)


@csrf_exempt
def downloadSwagger(request):
    try:
        if request.method == 'POST':
            data_json=json.loads(request.body.decode('utf-8'))
            server=data_json.get('server')
            egName=data_json.get('egName')
            apiName=data_json.get('apiName')
            #portEg=EGDetails.objects.filter(egName=egName).first()
            #port=portEg.broker.udpPort
            urlapi=fetch_api_db(request,apiName)
            if urlapi:
                apiName=urlapi
            port_dict=ServiceDetails.objects.filter(serviceName__iexact=apiName,eg__egName=egName).values('eg__broker__udpPort').first()
            port=port_dict['eg__broker__udpPort']
            print("Port",port)
            result=getSwagger.getSwaggerFile(server,port,egName,apiName)
            print(type(result))
            resultFinal=str(result.stdout)
            print(type(resultFinal))
            resultFinal=resultFinal.replace(r'"/"',"")
            print(resultFinal)
            return JsonResponse({"swaggerJson": str(resultFinal)},safe=False)
        return JsonResponse({"msg":"403 bad request"},safe=False)
    except Exception as e:
        return JsonResponse({"msg":e},safe=False)





#get the use logged in
@csrf_exempt
def Login(request):
    try:
        if request.method == 'POST':
            #return JsonResponse("")
            data_json=json.loads(request.body.decode('utf-8'))
            uid=data_json.get("uid")
            password=data_json.get("password")
            print(f"{password} this was the password")
            if not uid or not password:
                return JsonResponse({"Response":"username or password is required","status":400},status=400,safe=False)
            '''try:
               if uid == "0007" and password == "devTest":
                  #request.seesion['userId']=user.uid
                  return JsonResponse({"Response":"login successfull","userLevel":"L2","status":302},status=200,safe=False)
               else:
                  return JsonResponse({"Response":"login unsuccessfull","status":401},status=401,safe=False)
            except Exception as e:
               return JsonResponse({"Response":"login Unsuccessfull","status":401},status=401,safe=False)'''
            try:
                print("hii",password)
                print(Usermaster.objects.get(uid = uid, pwd = password))
                user = Usermaster.objects.get(uid = uid, pwd = password)
                print("hii")
            except Exception as e:
              user = None
            encrypted=None
            if user is not None and user.pwd==password:
                try:
                    request.session.set_expiry(3600)
                    request.session['username']=user.empname
                    request.session['level']=user.superlevel
                    request.session['userId']=user.uid
                    key = b'Sixteen byte key'
                    iv = b'Sixteen byte ivv'
                    cipher=Cipher(algorithms.AES(key),modes.CBC(iv),backend=default_backend())
                    encryptor = cipher.encryptor()

                    original_password=password
                    padder = padding.PKCS7(128).padder()
                    padded_data = padder.update(original_password.encode('utf-8')) + padder.finalize()

                    ciphertext = encryptor.update(padded_data)+encryptor.finalize()
                    print(ciphertext)

                    #user authentication through sessions
                    '''try:
                       userSession = authenticate(username=uid,password="password")
                    except Exception as e:
                        print(e)
                    print(userSession)
                    if userSession is not None:
                        print("executed")
                        try:
                          login(request,userSession)
                        except Exception as e:
                            print(e)'''
                except Exception as e:
                    print(e)
                if user.superlevel == 'ADMIN':
                    return JsonResponse({"Response":"login successfull","userLevel":"ADMIN","status":302,"username":request.session.get("username"),"userId":request.session.get("userId"),"password":ciphertext.hex()},status=200,safe=False)
                if user.superlevel == 'L2':
                    return JsonResponse({"Response":"login successfull","userLevel":"L2","status":302,"username":request.session.get("username"),"userId":request.session.get("userId"),"password":ciphertext.hex()},status=200,safe=False)
                return JsonResponse({"Response":"login successfull","userLevel":user.superlevel,"status":302,"username":request.session.get("username"),"userId":request.session.get("userId"),"password":ciphertext.hex()},status=200,safe=False)
            return JsonResponse({"Response":"login Unsuccessfull","status":401},status=401,safe=False)

    except Exception as e:
        return JsonResponse({"error":"An error occured while performing login ","e":str(e)},status=500,safe=False)
    return JsonResponse({"Response":"login not successfull not post method"},status=302,safe=False)

@csrf_exempt
def getannouncement(request):
    if request.method == 'POST':
        print("post")
        data_json = json.loads(request.body.decode('utf-8'))
        print(data_json)
        uid = data_json.get("uid")
        password = data_json.get("password")
        auth_user=authenticate(uid,password)
        if not auth_user:
            return JsonResponse({"msg":"An error occured while fetching the data"},status=500,safe=False)
        if "announcement" in data_json:
            announcement= data_json.get("announcement")
            time=data_json.get("time")
            level=Usermaster.objects.filter(uid=uid).first()
            print(level)
            if level.superlevel == "L2" or level.superlevel == "ADMIN":
                print("executed")
                Announcement.objects.create(Announcement=announcement,For_Time=time,updated_by=uid,Status="Approved",approved_by=uid)
            else:
                Announcement.objects.create(Announcement=announcement,For_Time=time,updated_by=uid,Status="Pending")

        last_announcement=Announcement.objects.filter(Status="Approved").last()
        print("abcd")
        try:
            if last_announcement:
                print("announcement")
                #if last_announcement.Status == "Approved":
                print(last_announcement.updated_at)
                return JsonResponse({"announcement":last_announcement.Announcement,"time":last_announcement.For_Time,"status":last_announcement.Status},status=200,safe=False)
                '''else:
                    return JsonResponse({"announcement":"Hello...!!! This is EIS-Infra Team."},status=200,safe=False)'''
            else:
                return JsonResponse({"announcement":"Hello...!!! This is EIS-Infra Team."},status=200,safe=False)
        except Exception as e:
            return JsonResponse({"An Error occured while fetching the data"},status=500,safe=False)

@csrf_exempt
def announcement_approver(request):
    try:
      if request.method == 'POST':
         data_json = json.loads(request.body.decode('utf-8'))
         uid = data_json.get("uid")
         password = data_json.get("password")
         if not authenticate(uid,password):
                print("this was the error")
                return JsonResponse({"msg":"An error occured while fetching the data"},status=500,safe=False)
    except Exception as e:
         return JsonResponse({"An Error occured while fetching the data"},status=500,safe=False)


@csrf_exempt
def getPortalAlerts(request):
    if request.method == 'POST':
        data_json = json.loads(request.body.decode('utf-8'))
        uid = data_json.get("uid")
        password = data_json.get("password")
        auth_user=authenticate(uid,password)
        print("auth_user",auth_user)
        if not auth_user:
                return JsonResponse({"msg":"An error occured while fetching the data"},status=500,safe=False)
        try:
            if auth_user == "ADMIN":
                file="/var/www/cgi-bin/PyPortal/EISHome/Alerts.txt"
                f = open(file).read()
                if f :
                    alertsPortal=[{"Alert":f}]
                else:
                    alertsPortal=[{"Alert":"No Updates"}]
            else:
                alertsPortal=logsDetails.objects.all().order_by('-persistingF').values('portal','effectedComponent','problem','persistingF')
            print(alertsPortal)
            #return  JsonResponse({"totalAlerts":list(alertsPortal)},status=200,safe=False)
            return  JsonResponse({"totalAlerts":list(alertsPortal)},status=200,safe=False)
        except Exception as e:
            return JsonResponse({"An Error occured while fetching the data"},status=500,safe=False)

@csrf_exempt
def forgotPassword(request):
    try:
      if request.method == 'POST':
         data_json = json.loads(request.body.decode('utf-8'))
         uid = data_json.get("uid")
         newpassword = data_json.get("password")
         answer = data_json.get("answer")
         securityQuestion= data_json.get("securityQuestion")
         querySet=Usermaster.objects.get(uid = uid,securityQuestion=securityQuestion)
         querySet.pwd=newpassword
         querySet.save()
         if querySet is not None:
             return JsonResponse({"msg":"Password updated successfully"},status=200,safe=False)
         return JsonResponse({"msg":"Secret question not valid "},status=403,safe=False)
    except Exception as e:
         return JsonResponse({"An Error occured while fetching the data"},status=500,safe=False)

@csrf_exempt
def getSecurityQuestion(request):
    try:
      if request.method == 'POST':
         data_json = json.loads(request.body.decode('utf-8'))
         uid = data_json.get("uid")
         querySet=Usermaster.objects.get(uid = uid)
         print(querySet.securityQuestion)
         if querySet is not None:
             return JsonResponse({"securityQuestion":querySet.securityQuestion},status=200,safe=False)
         return JsonResponse({"msg":"Emp id not valid"},status=403,safe=False)
    except Exception as e:
        print(e)
        return JsonResponse({"msg":"An Error occured while fetching the data"},status=500,safe=False)




#get the user logged out
@csrf_exempt
def logout(request):
    request.session.flush()
    return redirect('login')
