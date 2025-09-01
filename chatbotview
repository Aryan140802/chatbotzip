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
