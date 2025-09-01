from django.shortcuts import render
from django.http import JsonResponse
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import WordPunctTokenizer
import re
from .User_Info import *
from .Server_data import *
import random
from .training_data import TRAINING_DATA
from .FAR_Info import get_far_info,get_far_db
#import csrf_exempt
from .models import FarDetailsAll
from .forms import FarForm
import json
from django.views.decorators.csrf import csrf_exempt

nltk.data.path.append('/var/www/cgi-bin/djangovenv/venv/nltk_data')  # Update this path as needed
stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()
tokenizer = WordPunctTokenizer()



def preprocess_input(user_input):
    user_input = re.sub(r"[^\w\s]", "", user_input.lower())  # Remove punctuation
    tokens = word_tokenize(user_input)
    pos_tags=nltk.pos_tag(tokens)
    tokens=[ word for word,pos in pos_tags if pos in ('NNP','NN','NNPS','NNS')]
    return tokens

def extract_keyword(tokens):
    if len(tokens) > 0:
        return [token  for token in tokens if token.isalpha() or token.isdigit() or token.isalnum()]

    return []

def table_to_text(request,trans_details,user_message):
    if(isinstance(trans_details,list) and len(trans_details)> 0):
        request.session["details"] = trans_details
        success_or_fail=[i[0] for i in trans_details ]
        success_or_fail_code=[i[6] if i[1] == 'Y' else i[4] for i in trans_details ]
        if( '1' not in success_or_fail):
            bot_response = "transaction is successful!!!\n"
        else:
            if( len(set(success_or_fail_code)) == 1):
                bot_response = f"transaction is failed with Error Code :{ success_or_fail_code[0]} !!! \n "
            else:
                bot_response = f"transaction is failed with {success_or_fail_code} !!!"," \n "

        request.session["conversation_state"] = "awaiting_details"
        option_button="do you want more details?:\n1.YES\n2.No\n3.Back"
    else:
        bot_response = str(tables(request,user_message))+"\n\n"
        if "valid" in bot_response:
            option_button="1.main menu "
            #request.session["conversation_state"] = "awaiting_id"
            #request.session["user_selected_option"] = "2"
        else:
            option_button="1.Back\n2.main menu "
            #request.session["conversation_state"] = "awaiting_selection"
            #request.session["user_selected_option"] = None
    return (bot_response,option_button)

@csrf_exempt
def chatbot_ui(request):

    #options="1.Team Info\n2. Transaction Info\n3. Cache Info\n4. FAR Information\n5. Other"
    options="1.Team Info\n2. Transaction Info\n3. Cache Info\n4. FAR Information\n5.Server Configuration\n6.WorkLoad\nz. Other"
    #options="1. Team Info"
    conversation_state=request.session.get("conversation_state", "awaiting_selection")
    if 'chat_history' not in request.session:
        option_button=options.split("\n")
        request.session['chat_history']=[{"sender": "Bot", "message": "Hello! Please select from the following options:","options":option_button}]
    chat_history = request.session['chat_history']
    user_selected_option = request.session.get("user_selected_option", None)
    hits_choice=request.session.get("hits_choice","")
    option_button,bot_response="\n1.main menu",""
    back_option=request.session.get("back_option", [])
    back_list=request.session.get("back_list", {})
    if request.method == "POST":
        body_unicode=request.body.decode('utf-8')
        body_data=json.loads(body_unicode)
        user_m=body_data.get('message')
        #user_m = request.POST.get("message", "").strip()
        print(type(user_m))
        if(not isinstance(user_m,dict)):
            try:
                print(user_m.replace("\'", "\""))
                user_message=json.loads(user_m)
                print(user_message.values())
            except:
                user_message=str(user_m).strip().lower()
        else:
            user_message=user_m
        print(user_message)
        if conversation_state == "awaiting_selection":
            if user_message == "main menu":
                option_button=options
                request.session["conversation_state"] = "awaiting_selection"
                request.session["user_selected_option"] = None
            if  "Team Info".lower() == user_message:
                bot_response = 'Please provide the name or ID of the user.'
                request.session["conversation_state"] = "awaiting_id"
                request.session["user_selected_option"] = user_message
                back_option.append({'msg':bot_response,"state":request.session["conversation_state"],"options":option_button})
                request.session["back_option"]=back_option
            elif  "Transaction Info".lower() == user_message:
                    bot_response = 'Select from Below Options:'
                    option_button="1.Hits\n2. Transaction Flow\n3.main menu"
                    request.session["conversation_state"] ="awaiting_user_choice"
                    request.session["users_multiple_list"]=option_button
                    request.session["user_selected_option"] = user_message
                    back_option.append({'msg':bot_response,"state":request.session["conversation_state"],"options":option_button})
                    request.session["back_option"]=back_option
            elif  "Cache Info".lower() == user_message:
                bot_response = 'Select from Below Options:'
                option_button="1.Total Cache fields\n2. Cache Value\nA.Back\nB. Main Menu"
                request.session["conversation_state"] ="awaiting_user_choice"
                request.session["users_multiple_list"]=option_button
                request.session["user_selected_option"] = user_message
                back_option.append({'msg':bot_response,"state":request.session["conversation_state"],"options":option_button})
                request.session["back_option"]=back_option
            elif  "FAR Information".lower() == user_message:
                request.session["conversation_state"] = "awaiting_user_choice"
                bot_response = 'select below options:'
                #option_button="1.Enter FAR ID\n2. Have Multiple Fields\n3.Main Menu"
                option_button="1.Enter FAR ID\n3.Main Menu"
                request.session["users_multiple_list"]=option_button
                request.session["user_selected_option"] = user_message
                back_option.append({'msg':bot_response,"state":request.session["conversation_state"],"options":option_button})
                request.session["back_option"]=back_option
            elif  "Server Configuration".lower() == user_message:
                bot_response = 'Please provide the  IP of the Server.'
                request.session["conversation_state"] = "awaiting_id"
                request.session["user_selected_option"] = user_message
                back_option.append({'msg':bot_response,"state":request.session["conversation_state"],"options":option_button})
                request.session["back_option"]=back_option
            elif  "WorkLoad".lower() == user_message:
                bot_response = workload(request,user_message)
                #bot_response = workload(user_message)
                request.session["conversation_state"] = "awaiting_id"
                print("here")
                request.session["user_selected_option"] = user_message
                back_option.append({'msg':bot_response,"state":request.session["conversation_state"],"options":option_button})
                request.session["back_option"]=back_option
            elif user_message == "other":
                #bot_response = "Okay, ask whatever you want."
                bot_response = "Okay, Enter your question in chatbox"
                request.session["conversation_state"] = "awaiting_question"
                request.session["user_selected_option"] = user_message
                back_option.append({'msg':bot_response,"state":request.session["conversation_state"],"options":option_button})
                request.session["back_option"]=back_option
            else:
                bot_response = "I don't understand the question."

        elif conversation_state == "awaiting_id":
            if user_message == "main menu":
                option_button=options
                request.session["conversation_state"] = "awaiting_selection"
                request.session["user_selected_option"] = None
                back_option.clear()
                back_list.clear()
            elif user_message == "back":
                back=back_option[-1]
                bot_response=back["msg"]
                request.session["conversation_state"],option_button =back["state"],back["options"]
                back_list=back_option.pop()
                request.session["back_option"]=back_option
                request.session["back_list"]=back_list
            else:
                if user_selected_option == "Team Info".lower() :
                    bot_response,option_button = user_info(request,[user_message])
                    if(len(back_list)>0):
                        request.session["back_option"].append(back_list)
                if(request.session["user_selected_option"] == "Transaction Info".lower() ):
                    trans_details=tables(request,user_message)
                    bot_response,option_button=table_to_text(request,trans_details,user_message)
                    request.session["users_multiple_list"]=option_button
                    if(len(back_list)>0):
                        request.session["back_option"].append(back_list)
                if(request.session["user_selected_option"] == "Cache Info".lower() ):
                    bot_response=Cache_Info("Cache Info",user_message.strip())
                    option_button = "1.Back\n2.main menu"
                    if(len(back_list)>0):
                        request.session["back_option"].append(back_list)
                if(user_selected_option == "FAR Information".lower() ):
                    user_dict=request.session.get("details")
                    if user_message == "yes":
                        bot_response,option_button = get_far_info(request,user_dict)
                        option_button += "1.Back\n2.main menu"
                    elif user_message == "no":
                        option_button = "1.Back\n2.main menu"
                        bot_response="ok\n"
                        #request.session["conversation_state"] = "awaiting_selection"
                    elif(isinstance(user_message,dict)):
                        print("values:",user_message.values())
                        print("in conversion")
                        arr=len(user_message.values())
                        print(arr)
                        #all_arr_empty=all(not s for s in arr)
                        if(arr < 1 ):
                            bot_response={"Subject":"","Source":"","Requested_Destination":"","ZONE":"","Port":"","expiryoptions":["before","after"],"Expires":"date","Created":"date"}
                            option_button="y.Back\nz.Main Menu"
                        #bot_response="FORM"
                        else:
                            print("getting response from db for far")
                            if(isinstance(user_message,dict)):
                               print("this was data")
                               print(user_message)
                               bot_response=get_far_db(request,user_message)
                               print(bot_response)
                    else:
                        print("else far multiple list",type(user_message))
                        user_dict={"Far_Id":user_message}
                        bot_response,option_button = get_far_db(request,user_dict)
                    if(len(back_list)>0):
                        request.session["back_option"].append(back_list)
                if(user_selected_option == "Server Configuration".lower() ):
                    bot_response=Server_Conf(user_message)
                    option_button="y.Back\nz.Main Menu"
                    if(len(back_list)>0):
                        request.session["back_option"].append(back_list)
                if(user_selected_option == "WorkLoad".lower() ):
                    if(isinstance(user_message,dict)):
                        print(user_message)
                        bot_response=workload(request,user_message)
                        #bot_response=workload(user_message)
                        print("bot_response:",bot_response)
                    option_button="y.Back\nz.Main Menu"
                    if(len(back_list)>0):
                        request.session["back_option"].append(back_list)

        elif conversation_state == "awaiting_user_choice":
            user_choices = request.session.get("users_multiple_list", [])
            if user_message == "main menu":
                option_button=options
                request.session["conversation_state"] = "awaiting_selection"
                request.session["user_selected_option"] = None
                back_option.clear()
                back_list.clear()
            elif user_message == "back":
                back=back_option[-1]
                bot_response=back["msg"]
                request.session["conversation_state"],option_button =back["state"],back["options"]
                back_list=back_option.pop()
                request.session["back_option"]=back_option
                request.session["back_list"]=back_list

            else:
                if user_selected_option == "Team Info".lower():
                    user=[user_message.strip()]
                    bot_response,option_button = user_info(request,user)
                elif user_selected_option == "Transaction Info".lower():
                    bot_response=""
                    if user_message.strip() == "transaction flow":
                        bot_response = 'Enter REFERENCE NUMBER/URN...'
                        option_button = "1.Back\n2.main menu"
                        request.session["conversation_state"] = "awaiting_id"
                        back_option.append({'msg':bot_response,"state":request.session["conversation_state"],"options":option_button})
                        request.session["back_option"]=back_option
                        if(len(back_list)>0):
                            request.session["back_option"].append(back_list)
                    if  user_message.strip() == "hits":
                        bot_response = 'Select from Below Layers for Hits :'
                        #option_button="1.Time wise Hits\n2. Port wise Hits\n3.Service wise Hits\n4.IP wise Hits\n5.Back\n6.main menu"
                        option_button="1.EXP Hits\n2. SYS Hits\n5.Back\n6.main menu"
                        back_option.append({'msg':bot_response,"state":request.session["conversation_state"],"options":option_button})
                        request.session["back_option"]=back_option
                        if(len(back_list)>0):
                            request.session["back_option"].append(back_list)
                    elif user_message.strip() == "exp hits" or user_message.strip() == "sys hits" :
                        request.session["hits_choice"]=user_message.strip()
                        bot_response = 'Select from Below Options:'
                        option_button="1.30 Min \n2. 1 Hour\n3. Today(Till Now)\n5.Back\n6.main menu"
                        back_option.append({'msg':bot_response,"state":request.session["conversation_state"],"options":option_button})
                        request.session["back_option"]=back_option
                        if(len(back_list)>0):
                            request.session["back_option"].append(back_list)
                    elif user_message.strip() == "30 min":
                        bot_response=Hits(user_message.strip(),hits_choice)
                        option_button = "1.Back\n2.main menu"
                    elif user_message.strip() == "1 hour":
                        bot_response=Hits(user_message.strip(),hits_choice)
                        option_button = "1.Back\n2.main menu"
                    elif "today" in user_message.strip() :
                        bot_response=Hits(user_message.strip(),hits_choice)
                        option_button = "1.Back\n2.main menu"
                elif user_selected_option == "Cache Info".lower():
                    bot_response=""
                    if user_message.strip() == "cache value":
                        request.session["conversation_state"] = "awaiting_id"
                        bot_response = 'Enter Field Name...'
                        option_button = "1.Back\n2.main menu"
                        back_option.append({'msg':bot_response,"state":request.session["conversation_state"],"options":option_button})
                        request.session["back_option"]=back_option
                        if(len(back_list)>0):
                            request.session["back_option"].append(back_list)
                    else:
                        bot_response=Cache_Info(user_message)
                        option_button = "1.Back\n2.main menu"
                        if(len(back_list)>0):
                            request.session["back_option"].append(back_list)
                        '''back_option.append({'msg':bot_response,"state":request.session["conversation_state"],"options":option_button})
                        request.session["back_option"]=back_option
                        if(len(back_list)>0):
                            request.session["back_option"].append(back_list) '''
                elif user_selected_option == "FAR Information".lower():
                    bot_response=""
                    if user_message.strip() == "enter far id":
                        request.session["conversation_state"] = "awaiting_id"
                        bot_response = 'Enter FAR ID ...'
                        option_button = "1.Back\n2.main menu"
                        back_option.append({'msg':bot_response,"state":request.session["conversation_state"],"options":option_button})
                        request.session["back_option"]=back_option
                        if(len(back_list)>0):
                            request.session["back_option"].append(back_list)
                    elif "multiple fields" in user_message.strip():
                        bot_response={"Subject":"","Requested_Source":"","Requested_Destination":"","ZONE":"","Requested_Port_Translation":"","filterexpired":["before","after"],"Expires":"date","filtercreated":["before","after"],"Created":"date"}
                        #bot_response="FORM"
                        request.session["conversation_state"] = "awaiting_id"
                        option_button = "1.Back\n2.main menu"
                        back_option.append({'msg':bot_response,"state":request.session["conversation_state"],"options":option_button})
                        request.session["back_option"]=back_option
                        if(len(back_list)>0):
                            request.session["back_option"].append(back_list)
                    else:
                        print(user_message)
                        user_dict={"Far_Id":user_message.split(":")[0].strip()}
                        bot_response,option_button = get_far_db(request,user_dict)
                        if(len(back_list)>0):
                            request.session["back_option"].append(back_list)


        elif conversation_state == "awaiting_details":
            if user_message == "main menu":
                option_button=options
                request.session["conversation_state"] = "awaiting_selection"
                request.session["user_selected_option"] = None
                back_option.clear()
                back_list.clear()
            elif user_message == "back":
                back=back_option[-1]
                bot_response=back["msg"]
                request.session["conversation_state"],option_button =back["state"],back["options"]
                back_list=back_option.pop()
                request.session["back_option"]=back_option
                request.session["back_list"]=back_list

            elif(user_message == "yes" or user_message == "y"):
                if(request.session["user_selected_option"] == "Transaction Info".lower()):
                    trans_details=request.session["details"]
                    response_map={}
                    request_map={}
                    time_diff={}
                    error_codes={}
                    child_urn={}
                    if(len(trans_details) == 1):
                        request_time=trans_details[0][16]
                        response_time=trans_details[0][17]
                        Difference_in_request_response_time=time_to_string(trans_details[0][18])
                        error_code=trans_details[0][4]
                        if trans_details[0][0] != '0':
                            bot_response = f"transaction is <b>failed</b> with Error Code has <b>{error_code}</b>  \n API NAME <b> {trans_details[0][11]}</b>!!! \n backend request_time:<b> { request_time}</b> \n backend response_time:<b> { response_time}</b> \n Time difference b/n Request and Response was :<b> { Difference_in_request_response_time}</b>\n\n "
                        else:
                            bot_response = f" transaction is <b>Successful</b> \n API NAME <b>{trans_details[0][11]}</b> \n  backend request_time: <b>{request_time}</b> \n backend response_time: <b>{response_time}</b> \n Time difference b/n Request and Response was : <b>{Difference_in_request_response_time}</b> \n\n"
                    else:
                        for i in trans_details:
                            error_codes[i[11]]= i[6]
                            response_map[i[11]]= i[17]
                            request_map[i[11]]= i[16]
                            time_diff[i[11]]= i[18]
                            child_urn[i[11]]=i[3]
                        bot_string=""
                        for i in response_map.keys():
                            if not error_codes[i]:
                                bot_string+=f"\n For Child URN <b>{child_urn[i]}</b>,\n transaction is <b>Successful</b> \n API NAME <b>{i}</b> \n  backend request_time: <b>{request_map[i]}</b> \n backend response_time: <b>{response_map[i]}</b> \n Time difference b/n Request and Response was : <b>{time_to_string(time_diff[i])}</b>\n\n"
                            else:
                                bot_string+=f"\n For Child URN <b>{child_urn[i]} </b>, \n transaction is <b>failed</b> has Error Code :  <b>{error_codes[i]}</b>!!! \n API NAME <b>{i}</b> \n  backend request_time: <b>{request_map[i]}</b> \n backend response_time: <b>{response_map[i]}</b> \n Time difference b/n Request and Response was : <b>{time_to_string(time_diff[i])}</b>\n\n"
                        bot_response=bot_string
                    bot_response = f"Main URN = <b>{trans_details[0][1]}</b>\n"+bot_response
                    if(trans_details[0][2] == 'Y'):
                        bot_response="This is Orch API.\n "+bot_response+"\n"

                    else:
                        bot_response=bot_response
                elif(user_selected_option == "FAR Information".lower()):
                    details=request.session.get("details")
                    print("details",details)
                    if 'Permanent_Rule:' in details:
                        if details['Permanent_Rule:'].lower() == "yes" :
                            bot_string = "Since it is Permanent Rule ,it has no Expiry"
                        else:
                            bot_string =  f"It will Expire on {details['Expires']}"
                        bot_response=f"FAR ID <b>{details['Far_Id']}</b>  is raised for <b>{details['Subject:']} </b> which is now at <b>{details['Status:']}</b>\n with initial Requested Source <b>{details['Source']}</b> \nand initial Requested Destionation <b>{details['Destination']}</b> \nfor service/port <b>{details['Service']}</b> ."+bot_string
                        #\nIt's Dependent Department is <b>{details['Dependent Application:']}</b> and Zone <b>{details['ZONE:']}</b>\n"+bot_string
                    elif 'Permanent_Rule' in details:
                        if details['Permanent_Rule'].lower() == "yes" :
                            bot_string = "Since it is Permanent Rule ,it has no Expiry"
                        else:
                            bot_string =  f"It will Expire on {details['Expires']}"
                        bot_response=f"FAR ID <b>{details['Far_Id']}</b>  is raised for <b>{details['Subject']} </b> which is now at <b>{details['Status']}</b>\n with initial Requested Source <b>{details['Requested_Source']}</b> \nand initial Requested Destionation <b>{details['Requested_Destination']}</b> \nfor service/port <b>{details['Requested_Service']}</b> .\nIt's Dependent Department is <b>{details['Dependent_application']}</b> and Zone <b>{details['ZONE']}</b>\n"+bot_string
                option_button = "1.Back\n2.main menu "
            else:
                bot_response=f"\nFar ID for {user_m['Subject']}which is now at <b>{user_m['Status']}\n with initial Requested Source ['Requested_Source']"
                #bot_response="ok!!!"
                option_button = "1.Back\n2.main menu "
                #request.session["conversation_state"] = "awaiting_selection"
                #request.session["user_selected_option"] = None
        elif conversation_state == "awaiting_question":
            tokens = preprocess_input(user_message)
            keyword = extract_keyword(tokens)
            information,option_button=user_info(request,keyword)
            if("Sorry" in information):
                status= tables(request,user_message)
                information,option_button=table_to_text(request,status,user_message)
                if("valid" in information):
                    information="I don't have any information about what you have asked kindly contact admin..."
            bot_response = information
            if user_message.lower() == "main menu":
                bot_response=""
                option_button=options
                request.session["conversation_state"] = "awaiting_selection"
                request.session["user_selected_option"] = None

        else:
            bot_response = "An error occurred. Let's start over."
            request.session["conversation_state"] = "awaiting_selection"
            option_button = options

        print("user_message",user_message)
        print("user_selected_option",user_selected_option)
        print("conversation_state",request.session["conversation_state"])
        #print("option_button",option_button)
        print("back_option",back_option)
        print("back_list",back_list)
        print("bot response",bot_response)

        if(option_button):
            option_button=option_button.split('\n')
            if(option_button[0]==''):
                option_button=option_button[1:]
            else:
                option_button=option_button
        chat_history=request.session['chat_history']
        chat_history.append({"sender": "You", "message": user_message})
        chat_history.append({"sender": "Bot", "message": bot_response,"options":option_button})
        request.session['chat_history']=chat_history
    #return render(request, "eischatbot/chat.html", {"chat_history": request.session.get('chat_history',[])})
        print(type(request.session.get('chat_history')))
    return JsonResponse({"chat_history": request.session.get('chat_history',[])})
    return JsonResponse({"chat_history": chat_history})

#@csrf_exempt
def flush_session(request):
    if request.method == "POST":
        request.session.flush()
        return JsonResponse({'status':'session flushed'})
[root@eispr-prt1-01 EISChatBot]# ll
total 31832
-rwxr-xr-x 1 root    root        9186 Jun 13 16:21 1
-rwxr-xr-x 1 eisuser eisuser      553 Feb 27  2025 Error_Codes.py
-rwxr-xr-x 1 eisuser eisuser     2845 Jun 16 17:21 FAR.py
-rwxr-xr-x 1 eisuser eisuser    11493 Jul  7 12:55 FAR_Info.py
-rwxr-xr-x 1 root    root       11806 Jun 16 13:30 FAR_Info.py_1606
-rwxr-xr-x 1 root    root        7810 May 23 11:59 FAR_Info.py_23_05
-rwxr-xr-x 1 root    root        8095 Jun 13 15:34 FAR_Info_11062025
-rwxr-xr-x 1 root    root           0 Jun 11 17:09 FAR_Infor.py
-rwxr-xr-x 1 eisuser eisuser     3733 Apr 28 13:59 FAR_advanced.py
-rwxr-xr-x 1 eisuser eisuser 32049927 Sep  1 05:12 FarDetails.csv
-rwxr-xr-x 1 root    root        1317 May 22 17:44 PR_DPG.py
-rwxr-xr-x 1 eisuser eisuser    14345 Aug 28 18:43 Server_data.py
-rwxr-x--- 1 root    root       13856 Aug 28 17:09 Server_data.py_2
-rwxr-xr-x 1 root    root        5186 May 21 13:00 Server_data.py_21_05
-rwxr-x--- 1 root    root       12841 Aug 28 13:14 Server_data.py_28_08
-rwxr-x--- 1 root    root       13312 Aug 28 13:54 Server_data.py_28_08_1
-rwxr-xr-x 1 eisuser eisuser     2830 May 21 13:00 User_Info.py
-rwxr-xr-x 1 root    root        2696 May 21 13:00 User_Info.py_21_05
-rwxr-xr-x 1 eisuser eisuser        0 Dec  2  2024 __init__.py
drwxr-xr-x 2 eisuser eisuser     4096 Aug 28 18:43 __pycache__
-rwxr-xr-x 1 eisuser eisuser       63 Dec  2  2024 admin.py
-rwxr-xr-x 1 eisuser eisuser    29160 Apr 15 12:36 all_far.csv
-rwxr-xr-x 1 eisuser eisuser    29160 Apr 15 13:24 all_far_final.csv
-rwxr-xr-x 1 eisuser eisuser    16214 Mar 25 13:21 api_queries_test.py
-rwxr-xr-x 1 eisuser eisuser      152 Dec  2  2024 apps.py
-rwxr-xr-x 1 eisuser eisuser      827 Mar  7 12:33 chatbot_engine.py
drwxr-xr-x 2 eisuser eisuser       58 Mar 21 17:24 data
-rwxr-xr-x 1 eisuser eisuser      527 Apr  2 12:07 far_info.txt
-rwxr-xr-x 1 eisuser eisuser      497 Apr 17 13:24 forms.py
drwxr-xr-x 3 eisuser eisuser     4096 Apr 22 12:26 migrations
-rwxr-xr-x 1 eisuser eisuser     5776 Apr 22 12:26 models.py
-rwxr-xr-x 1 eisuser eisuser      493 Apr  9 12:38 payload.py
-rwxr-xr-x 1 eisuser eisuser      249 May  2 16:33 queries.py
-rwxr-xr-x 1 eisuser eisuser    29160 Apr 15 11:34 results_far.csv
-rwxr-xr-x 1 eisuser eisuser     6458 Apr 15 17:23 temp.csv
drwxr-xr-x 3 eisuser eisuser       24 Dec  2  2024 templates
drwxr-xr-x 3 eisuser eisuser       66 Feb 26  2025 templatetags
-rwxr-xr-x 1 eisuser eisuser       98 Apr  7 11:20 test_far.py
-rwxr-xr-x 1 eisuser eisuser       60 Dec  2  2024 tests.py
-rwxr-xr-x 1 eisuser eisuser      748 Mar  7 12:56 training_data.py
-rwxr-xr-x 1 eisuser eisuser      229 Feb 25  2025 urls.py
-rwxr-xr-x 1 eisuser eisuser    45080 May 13 15:03 views.bkp100525
-rwxr-xr-x 1 eisuser eisuser    28259 Aug 28 17:31 views.py
-rwxr-xr-x 1 root    root       23346 May 21 12:59 views.py_21_05
-rwxr-xr-x 1 root    root       21796 May 23 11:59 views.py_23_05
-rwxr-xr-x 1 eisuser eisuser     9415 Feb 24  2025 views.py_2402
-rwxr-xr-x 1 eisuser eisuser    19101 May 14 12:08 views.py_cp
-rwxr-xr-x 1 eisuser eisuser    15893 May 14 12:27 views.py_cp2
-rwxr-xr-x 1 root    root       21797 May 21 17:33 views.py_new
-rwxr-xr-x 1 root    root        2221 May 27 17:03 workload.py
[root@eispr-prt1-01 EISChatBot]# cd ..
[root@eispr-prt1-01 PyPortal]# ll
total 244
-rwxr-xr-x  1 eisuser eisuser    585 Feb 24  2025 0002_workloadchanges_gen_service_and_more.py
-rw-r-----  1 root    root       807 Aug 23 15:59 1
-rwxr-xr-x  1 root    root      1053 Aug 23 07:30 Alerts.txt
drwxr-xr-x 10 eisuser eisuser   4096 Aug 23 14:04 BrokerEgApi
drwxr-xr-x  7 eisuser eisuser   4096 Aug 28 23:44 EISChatBot
drwxr-xr-x  7 root    root      4096 May 27 10:03 EISChatBot_test
drwxr-xr-x  5 eisuser eisuser   4096 Sep  1 12:26 EISHome
-rwxr-xr-x  1 eisuser eisuser   2334 Jul 10 13:22 GetFarDetails.py
drwxr-xr-x  4 root    root       173 Jun  3 16:48 Grievance_data
drwxr-xr-x  5 eisuser eisuser   4096 Feb 14  2025 LaunchOps
-rwxr-xr-x  1 root    root         0 May 27 13:17 PRDRActiveSetup.txt
drwxr-xr-x  3 eisuser eisuser   4096 Aug 26 12:05 PyPortal
drwxr-xr-x  2 eisuser eisuser     71 Apr 15 17:30 __pycache__
-rw-r-----  1 root    root         0 Jul 11 19:08 aiHandler.py
drwxr-xr-x  2 eisuser eisuser      6 May 30 18:39 aiOps
drwxr-xr-x  7 eisuser eisuser    156 Aug 27 18:33 chatbot
drwxr-xr-x  7 root    root       156 Apr 30 12:49 chatbot_30042025
drwxr-xr-x  6 root    root      4096 Aug 29 22:05 curl_search
-rwxr-xr-x  1 eisuser eisuser 131072 Sep 16  2024 db.sqlite3
drwxr-xr-x  5 eisuser eisuser   4096 Aug 26 14:08 dbOpTest
drwxr-xr-x  3 eisuser eisuser    123 Dec  4  2024 dummychat
-rwxr-xr-x  1 root    root      2327 Jul  5 12:57 getIIBAlerts.py
-rwxr-xr-x  1 root    root      2490 Jul 23 19:52 getMQAlerts.py
-rwxr-xr-x  1 eisuser eisuser   1375 Nov 22  2024 manage.py
drwxr-xr-x  2 eisuser eisuser   4096 Dec 27  2024 media
-rwxr-xr-x  1 eisuser eisuser   3743 Apr 23 16:37 models.py
-rwxr-xr-x  1 root    root      4155 Jul  3 17:12 mq_data_insert.py
drwxr-xr-x  3 eisuser eisuser     18 May 23 13:07 mq_logs
-rwxr-xr-x  1 root    root      1481 May 27 13:24 prdr.py
drwxr-xr-x  5 eisuser eisuser     54 Sep 19  2024 productionfiles
-rwxr-xr-x  1 eisuser eisuser   1700 Aug 26 14:05 saveBrokerEgApi.py
-rwxr-xr-x  1 eisuser eisuser   1420 Aug 14 14:41 saveLayerBrEgApi.py
drwxr-xr-x  6 eisuser eisuser     68 Aug 28 17:08 staticfiles
-rwxr-xr-x  1 root    root      4530 Jun 24 19:34 testanalysis.py
-rwxr-xr-x  1 eisuser eisuser   4163 Jun 27 16:15 volume_analysis.py
-rwxr-xr-x  1 root    root      5211 Jul  8 13:51 volume_analysislive.py
-rwxr-xr-x  1 root    root      4094 Jun 11 12:24 volume_analysislive.py_cp
[root@eispr-prt1-01 PyPortal]# cd EISHome
[root@eispr-prt1-01 EISHome]# ll
total 188
-rw-r----- 1 root    root    47457 Aug 23 16:16  1
-rwxr-xr-x 1 root    root      433 Sep  1 15:44  Alerts.txt
-rwxr-xr-x 1 root    root        2 Sep  1 15:44  PRDRActiveSetup.txt
drwxr-xr-x 2 eisuser eisuser     6 Apr 25 13:31  Pyscripts
-rw-r----- 1 root    root    47539 Aug 23 19:01 '\'
-rwxr-xr-x 1 eisuser eisuser     0 Apr 25 12:30  __init__.py
drwxr-xr-x 2 eisuser eisuser  4096 Sep  1 12:26  __pycache__
-rwxr-xr-x 1 eisuser eisuser    63 Apr 25 12:30  admin.py
-rwxr-xr-x 1 eisuser eisuser   146 Apr 25 12:30  apps.py
-rwxr-x--- 1 eisuser root      895 Aug 23 16:17  getSwagger.py
drwxr-xr-x 3 eisuser eisuser  4096 Jun 26 12:53  migrations
-rwxr-xr-x 1 eisuser eisuser  4701 Jun 26 12:54  models.py
-rwxr-xr-x 1 eisuser eisuser    60 Apr 25 12:30  tests.py
-rwxr-xr-x 1 eisuser eisuser  2342 Aug 23 14:07  urls.py
-rwxr-xr-x 1 eisuser eisuser 47967 Sep  1 12:26  views.py
[root@eispr-prt1-01 EISHome]# cat views.py
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
