from multiprocessing import context
from multiprocessing.sharedctypes import Value
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import EmailMessage, send_mail
from django.contrib.auth import authenticate, login, logout
from .models import UserProfile
from django.core.files.storage import FileSystemStorage
from framework import settings
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from . tokens import generate_token
import os
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
import time
import urllib
import json
from urllib.request import urlopen
from datetime import date
import pandas as pd
import _thread
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from app import models

# Create your views here.
def index(request):
    # return HttpResponse("this is home Page...!!!")
    return render(request, 'index.html')

def user_register(request):
    if request.method=='POST':
        fname = request.POST.get('firstname')
        lname = request.POST.get('lastname')
        uname = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')
        if pass1 != pass2:
            messages.warning(request, 'Password does not match...!')
            return redirect('register')

        elif User.objects.filter(username=uname).exists():
            messages.warning(request, 'This username already exists')
            return redirect('register')

        elif User.objects.filter(email=email).exists():
            messages.warning(request, 'This email already exists')
            return redirect('register')
        
        else:
            #print(fname,lname,uname,email,pass1,pass2)
            user = User.objects.create_user(first_name=fname, last_name=lname, username=uname, email=email, password=pass1)
            user.first_name = fname
            user.last_name = lname
            user.is_active = False
            user.save()
            messages.success(request,'You have been registered succssfully! Please check your email to confirm your email address in order to activate your account.')

            # Welcome Email
            subject = "Welcome to Opus Sock Demo website...!!!"
            message = "Hello " + user.first_name + "!! \n" + "Welcome to Opus Stock demo !! \nThank you for visiting our website\n. We have also sent you a confirmation email, please confirm your email address. \n\nThanking You\nOpus Technology Limited"        
            from_email = settings.EMAIL_HOST_USER
            to_list = [user.email]
            send_mail(subject, message, from_email, to_list, fail_silently=True)
            
            # Email Address Confirmation Email
            current_site = get_current_site(request)
            email_subject = "Confirm your Email @ Opus web demo Login!!"
            message2 = render_to_string('email_confirmation.html',{
                
                'name': user.first_name,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': generate_token.make_token(user)
            })
            email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [user.email],
            )
            email.fail_silently = True
            email.send()

            return redirect('login')
    return render(request,'register.html')


def activate(request,uidb64,token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        user = None

    if user is not None and generate_token.check_token(user,token):
        user.is_active = True
        # user.profile.signup_confirmation = True
        user.save()
        login(request,user)
        messages.success(request, "Your Account has been activated!!")
        return redirect('login')
    else:
        return render(request,'activation_failed.html')
    

def user_login(request):
    if request.method=='POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.warning(request, 'invalid value! Please register first or try again...')
            return redirect('login')
    return render(request,'login.html')

def user_logout(request):
    logout(request)
    return redirect('/')


@login_required
def user_profile(request, user_id):
	if request.method == 'POST':
		user_obj = User.objects.get(id=user_id)
		user_profile_obj = UserProfile.objects.get(id=user_id)
		# try:
		user_img = request.FILES['user_img']
		fs_handle = FileSystemStorage()
		img_name = 'images/user_{0}.png'.format(user_id)
		if fs_handle.exists(img_name):
			fs_handle.delete(img_name)
		fs_handle.save(img_name, user_img)
		user_profile_obj.profile_img = img_name
		user_profile_obj.save()
		user_profile_obj.refresh_from_db()
		# except:
		# 	messages.add_message(request, messages.ERROR, "Unable to update image..")

		return render(request, 'profile.html', {'my_profile': user_profile_obj})
	if (request.user.is_authenticated and request.user.id == user_id):
		user_obj = User.objects.get(id=user_id)
		user_profile = UserProfile.objects.get(id=user_id)

		return render(request, 'profile.html', {'my_profile': user_profile})

def functions(request):
    return render(request, 'function.html')

@login_required
def update_rank(request):
    if request.method == "POST" or request.method != "POST":
        url = "http://csprediction-env.eba-pvvpzi4d.eu-north-1.elasticbeanstalk.com/rank"
        #redirect(url)
        x = requests.get(url)
        print(x.status_code)   
    return render(request, 'update_rank.html')


def update_dataset(request):
    try:
        print("Yay! I still got executed, even though my function has already returned!...  twitter")
    finally:
        print("im in finallay")
        url = "http://csprediction-env.eba-pvvpzi4d.eu-north-1.elasticbeanstalk.com/update"
        
        #return HttpResponseRedirect(url)
        # x = requests.get(url)
        # print(x.status_code)
        redirect(url)
        
    #     x = requests.get(url, verify=False)
    #     print(x.status_code)   
    return render(request, 'update_dataset.html')

def download(request):
    if request.method == "POST":
        model = request.POST.get('dropdown')
        print(model)
        # datePicker =request.POST.get('datePicker')
        # print(datePicker)

        link = "http://csprediction-env.eba-pvvpzi4d.eu-north-1.elasticbeanstalk.com/getallfilename"
        f = urlopen(link)
        myfile = f.read()
        files=json.loads(myfile)['Name']
        #print(files)

        today = date.today()

        # dd/mm/YY
        current_date= today.strftime("%Y-%m-%d")
        print("current_date=", current_date)

        # model =""
        datePicker ="2022-04-24"

        if model=="1":
            if datePicker == "":
                filtered_lst=[]
                datelst =[]
                for element in files:
                    if current_date in element:
                        filtered_lst.append(element)
                        datelst.append(current_date)

                print(filtered_lst)
                print(datelst)
            else:
                filtered_lst=[]
                datelst =[]
                for element in files:
                    if datePicker in element:
                        filtered_lst.append(element)
                        datelst.append(datePicker)

                print(filtered_lst)
                print(datelst)

            alphalist=[]
            for  element in filtered_lst:
                if "Alpha" in element:
                    alphalist.append(element)

            print(alphalist)

            filenames=[]
            links=[]

            for file in alphalist:
                filename = file.split("/")[2]
                #print(filename) 
                filenames.append(filename)
                links.append('https://pred-model-data.s3.eu-north-1.amazonaws.com/Resources/Results/' +filename)



            print(filenames)
            print(links)

            if datePicker == "": 
                current_dates =[]
                for file in filenames:
                    if current_date in file:
                        current_dates.append(current_date)
            else:
                current_dates =[]
                for file in filenames:
                    if datePicker in file:
                        current_dates.append(datePicker)


            print(current_dates)
            
            models =['Alpha','BPC','Beta','GammaOld','GammaPrediction','Merge','NN','New','PredictionReport','Tier']
            modellst = []
            for file in filenames:
                for model in models:
                    if model in file:
                        print(file)
                        print(model)
                        if model=='PredictionReport':
                            modellst.append('All Models')
                        elif model=='GammaOld':
                            modellst.append('Gamma Old')
                        elif model=='GammaPrediction':
                            modellst.append('Gamma')
                        else:
                            modellst.append(model)
            
            print(len(modellst))

        elif model=="2":
            if datePicker == "":
                filtered_lst=[]
                datelst =[]
                for element in files:
                    if current_date in element:
                        filtered_lst.append(element)
                        datelst.append(current_date)

                print(filtered_lst)
                print(datelst)
            else:
                filtered_lst=[]
                datelst =[]
                for element in files:
                    if datePicker in element:
                        filtered_lst.append(element)
                        datelst.append(datePicker)

                print(filtered_lst)
                print(datelst)

            alphalist=[]
            for  element in filtered_lst:
                if "BPC" in element:
                    alphalist.append(element)

            print(alphalist)

            filenames=[]
            links=[]

            for file in alphalist:
                filename = file.split("/")[2]
                #print(filename) 
                filenames.append(filename)
                links.append('https://pred-model-data.s3.eu-north-1.amazonaws.com/Resources/Results/' +filename)



            print(filenames)
            print(links)

            if datePicker == "": 
                current_dates =[]
                for file in filenames:
                    if current_date in file:
                        current_dates.append(current_date)
            else:
                current_dates =[]
                for file in filenames:
                    if datePicker in file:
                        current_dates.append(datePicker)


            print(current_dates)

            models =['Alpha','BPC','Beta','GammaOld','GammaPrediction','Merge','NN','New','PredictionReport','Tier']
            modellst = []
            for file in filenames:
                for model in models:
                    if model in file:
                        print(file)
                        print(model)
                        if model=='PredictionReport':
                            modellst.append('All Models')
                        elif model=='GammaOld':
                            modellst.append('Gamma Old')
                        elif model=='GammaPrediction':
                            modellst.append('Gamma')
                        else:
                            modellst.append(model)
            
            print(len(modellst))

            models =['Alpha','BPC','Beta','GammaOld','Gamma','Merge','NN','New','PredictionReport','Tier']
            modellst = []
            for file in filenames:
                for model in models:
                    if model in file:
                        if model=='PredictionReport':
                            modellst.append('All Models')
                        else:
                            modellst.append(model)
            
            print(modellst)

        elif model=="3":
            if datePicker == "":
                filtered_lst=[]
                datelst =[]
                for element in files:
                    if current_date in element:
                        filtered_lst.append(element)
                        datelst.append(current_date)

                print(filtered_lst)
                print(datelst)
            else:
                filtered_lst=[]
                datelst =[]
                for element in files:
                    if datePicker in element:
                        filtered_lst.append(element)
                        datelst.append(datePicker)

                print(filtered_lst)
                print(datelst)

            alphalist=[]
            for  element in filtered_lst:
                if "Beta" in element:
                    alphalist.append(element)

            print(alphalist)

            filenames=[]
            links=[]

            for file in alphalist:
                filename = file.split("/")[2]
                #print(filename) 
                filenames.append(filename)
                links.append('https://pred-model-data.s3.eu-north-1.amazonaws.com/Resources/Results/' +filename)



            print(filenames)
            print(links)

            if datePicker == "": 
                current_dates =[]
                for file in filenames:
                    if current_date in file:
                        current_dates.append(current_date)
            else:
                current_dates =[]
                for file in filenames:
                    if datePicker in file:
                        current_dates.append(datePicker)


            print(current_dates)

            models =['Alpha','BPC','Beta','GammaOld','GammaPrediction','Merge','NN','New','PredictionReport','Tier']
            modellst = []
            for file in filenames:
                for model in models:
                    if model in file:
                        print(file)
                        print(model)
                        if model=='PredictionReport':
                            modellst.append('All Models')
                        elif model=='GammaOld':
                            modellst.append('Gamma Old')
                        elif model=='GammaPrediction':
                            modellst.append('Gamma')
                        else:
                            modellst.append(model)
            
            print(len(modellst))

        elif model=="4":
            if datePicker == "":
                filtered_lst=[]
                datelst =[]
                for element in files:
                    if current_date in element:
                        filtered_lst.append(element)
                        datelst.append(current_date)

                print(filtered_lst)
                print(datelst)
            else:
                filtered_lst=[]
                datelst =[]
                for element in files:
                    if datePicker in element:
                        filtered_lst.append(element)
                        datelst.append(datePicker)

                print(filtered_lst)
                print(datelst)

            alphalist=[]
            for  element in filtered_lst:
                if "GammaOld" in element:
                    alphalist.append(element)

            print(alphalist)

            filenames=[]
            links=[]

            for file in alphalist:
                filename = file.split("/")[2]
                #print(filename) 
                filenames.append(filename)
                links.append('https://pred-model-data.s3.eu-north-1.amazonaws.com/Resources/Results/' +filename)



            print(filenames)
            print(links)

            if datePicker == "": 
                current_dates =[]
                for file in filenames:
                    if current_date in file:
                        current_dates.append(current_date)
            else:
                current_dates =[]
                for file in filenames:
                    if datePicker in file:
                        current_dates.append(datePicker)


            print(current_dates)

            models =['Alpha','BPC','Beta','GammaOld','GammaPrediction','Merge','NN','New','PredictionReport','Tier']
            modellst = []
            for file in filenames:
                for model in models:
                    if model in file:
                        print(file)
                        print(model)
                        if model=='PredictionReport':
                            modellst.append('All Models')
                        elif model=='GammaOld':
                            modellst.append('Gamma Old')
                        elif model=='GammaPrediction':
                            modellst.append('Gamma')
                        else:
                            modellst.append(model)
            
            print(len(modellst))

        elif model=="5":
            if datePicker == "":
                filtered_lst=[]
                datelst =[]
                for element in files:
                    if current_date in element:
                        filtered_lst.append(element)
                        datelst.append(current_date)

                print(filtered_lst)
                print(datelst)
            else:
                filtered_lst=[]
                datelst =[]
                for element in files:
                    if datePicker in element:
                        filtered_lst.append(element)
                        datelst.append(datePicker)

                print(filtered_lst)
                print(datelst)

            alphalist=[]
            for  element in filtered_lst:
                if "GammaPrediction" in element:
                    alphalist.append(element)

            print(alphalist)

            filenames=[]
            links=[]

            for file in alphalist:
                filename = file.split("/")[2]
                #print(filename) 
                filenames.append(filename)
                links.append('https://pred-model-data.s3.eu-north-1.amazonaws.com/Resources/Results/' +filename)



            print(filenames)
            print(links)

            if datePicker == "": 
                current_dates =[]
                for file in filenames:
                    if current_date in file:
                        current_dates.append(current_date)
            else:
                current_dates =[]
                for file in filenames:
                    if datePicker in file:
                        current_dates.append(datePicker)


            print(current_dates)

            models =['Alpha','BPC','Beta','GammaOld','GammaPrediction','Merge','NN','New','PredictionReport','Tier']
            modellst = []
            for file in filenames:
                for model in models:
                    if model in file:
                        print(file)
                        print(model)
                        if model=='PredictionReport':
                            modellst.append('All Models')
                        elif model=='GammaOld':
                            modellst.append('Gamma Old')
                        elif model=='GammaPrediction':
                            modellst.append('Gamma')
                        else:
                            modellst.append(model)
            
            print(len(modellst))

        elif model=="6":
            if datePicker == "":
                filtered_lst=[]
                datelst =[]
                for element in files:
                    if current_date in element:
                        filtered_lst.append(element)
                        datelst.append(current_date)

                print(filtered_lst)
                print(datelst)
            else:
                filtered_lst=[]
                datelst =[]
                for element in files:
                    if datePicker in element:
                        filtered_lst.append(element)
                        datelst.append(datePicker)

                print(filtered_lst)
                print(datelst)

            alphalist=[]
            for  element in filtered_lst:
                if "Merge" in element:
                    alphalist.append(element)

            print(alphalist)

            filenames=[]
            links=[]

            for file in alphalist:
                filename = file.split("/")[2]
                #print(filename) 
                filenames.append(filename)
                links.append('https://pred-model-data.s3.eu-north-1.amazonaws.com/Resources/Results/' +filename)



            print(filenames)
            print(links)

            if datePicker == "": 
                current_dates =[]
                for file in filenames:
                    if current_date in file:
                        current_dates.append(current_date)
            else:
                current_dates =[]
                for file in filenames:
                    if datePicker in file:
                        current_dates.append(datePicker)


            print(current_dates)

            models =['Alpha','BPC','Beta','GammaOld','GammaPrediction','Merge','NN','New','PredictionReport','Tier']
            modellst = []
            for file in filenames:
                for model in models:
                    if model in file:
                        print(file)
                        print(model)
                        if model=='PredictionReport':
                            modellst.append('All Models')
                        elif model=='GammaOld':
                            modellst.append('Gamma Old')
                        elif model=='GammaPrediction':
                            modellst.append('Gamma')
                        else:
                            modellst.append(model)
            
            print(len(modellst))

        elif model=="7":
            if datePicker == "":
                filtered_lst=[]
                datelst =[]
                for element in files:
                    if current_date in element:
                        filtered_lst.append(element)
                        datelst.append(current_date)

                print(filtered_lst)
                print(datelst)
            else:
                filtered_lst=[]
                datelst =[]
                for element in files:
                    if datePicker in element:
                        filtered_lst.append(element)
                        datelst.append(datePicker)

                print(filtered_lst)
                print(datelst)

            alphalist=[]
            for  element in filtered_lst:
                if "NN" in element:
                    alphalist.append(element)

            print(alphalist)

            filenames=[]
            links=[]

            for file in alphalist:
                filename = file.split("/")[2]
                #print(filename) 
                filenames.append(filename)
                links.append('https://pred-model-data.s3.eu-north-1.amazonaws.com/Resources/Results/' +filename)



            print(filenames)
            print(links)

            if datePicker == "": 
                current_dates =[]
                for file in filenames:
                    if current_date in file:
                        current_dates.append(current_date)
            else:
                current_dates =[]
                for file in filenames:
                    if datePicker in file:
                        current_dates.append(datePicker)


            print(current_dates)

            models =['Alpha','BPC','Beta','GammaOld','GammaPrediction','Merge','NN','New','PredictionReport','Tier']
            modellst = []
            for file in filenames:
                for model in models:
                    if model in file:
                        print(file)
                        print(model)
                        if model=='PredictionReport':
                            modellst.append('All Models')
                        elif model=='GammaOld':
                            modellst.append('Gamma Old')
                        elif model=='GammaPrediction':
                            modellst.append('Gamma')
                        else:
                            modellst.append(model)
            
            print(len(modellst))

        elif model=="8":
            if datePicker == "":
                filtered_lst=[]
                datelst =[]
                for element in files:
                    if current_date in element:
                        filtered_lst.append(element)
                        datelst.append(current_date)

                print(filtered_lst)
                print(datelst)
            else:
                filtered_lst=[]
                datelst =[]
                for element in files:
                    if datePicker in element:
                        filtered_lst.append(element)
                        datelst.append(datePicker)

                print(filtered_lst)
                print(datelst)

            alphalist=[]
            for  element in filtered_lst:
                if "NewModel" in element:
                    alphalist.append(element)

            print(alphalist)

            filenames=[]
            links=[]

            for file in alphalist:
                filename = file.split("/")[2]
                #print(filename) 
                filenames.append(filename)
                links.append('https://pred-model-data.s3.eu-north-1.amazonaws.com/Resources/Results/' +filename)



            print(filenames)
            print(links)

            if datePicker == "": 
                current_dates =[]
                for file in filenames:
                    if current_date in file:
                        current_dates.append(current_date)
            else:
                current_dates =[]
                for file in filenames:
                    if datePicker in file:
                        current_dates.append(datePicker)


            print(current_dates)

            models =['Alpha','BPC','Beta','GammaOld','GammaPrediction','Merge','NN','New','PredictionReport','Tier']
            modellst = []
            for file in filenames:
                for model in models:
                    if model in file:
                        print(file)
                        print(model)
                        if model=='PredictionReport':
                            modellst.append('All Models')
                        elif model=='GammaOld':
                            modellst.append('Gamma Old')
                        elif model=='GammaPrediction':
                            modellst.append('Gamma')
                        else:
                            modellst.append(model)
            
            print(len(modellst))

        elif model=="9":
            if datePicker == "":
                filtered_lst=[]
                datelst =[]
                for element in files:
                    if current_date in element:
                        filtered_lst.append(element)
                        datelst.append(current_date)

                print(filtered_lst)
                print(datelst)
            else:
                filtered_lst=[]
                datelst =[]
                for element in files:
                    if datePicker in element:
                        filtered_lst.append(element)
                        datelst.append(datePicker)

                print(filtered_lst)
                print(datelst)

            alphalist=[]
            for  element in filtered_lst:
                if "PredictionReport" in element:
                    alphalist.append(element)

            print(alphalist)

            filenames=[]
            links=[]

            for file in alphalist:
                filename = file.split("/")[2]
                #print(filename) 
                filenames.append(filename)
                links.append('https://pred-model-data.s3.eu-north-1.amazonaws.com/Resources/Results/' +filename)



            print(filenames)
            print(links)

            if datePicker == "": 
                current_dates =[]
                for file in filenames:
                    if current_date in file:
                        current_dates.append(current_date)
            else:
                current_dates =[]
                for file in filenames:
                    if datePicker in file:
                        current_dates.append(datePicker)


            print(current_dates)

            models =['Alpha','BPC','Beta','GammaOld','GammaPrediction','Merge','NN','New','PredictionReport','Tier']
            modellst = []
            for file in filenames:
                for model in models:
                    if model in file:
                        print(file)
                        print(model)
                        if model=='PredictionReport':
                            modellst.append('All Models')
                        elif model=='GammaOld':
                            modellst.append('Gamma Old')
                        elif model=='GammaPrediction':
                            modellst.append('Gamma')
                        else:
                            modellst.append(model)
            
            print(len(modellst))

        elif model=="10":
            if datePicker == "":
                filtered_lst=[]
                datelst =[]
                for element in files:
                    if current_date in element:
                        filtered_lst.append(element)
                        datelst.append(current_date)

                print(filtered_lst)
                print(datelst)
            else:
                filtered_lst=[]
                datelst =[]
                for element in files:
                    if datePicker in element:
                        filtered_lst.append(element)
                        datelst.append(datePicker)

                print(filtered_lst)
                print(datelst)

            alphalist=[]
            for  element in filtered_lst:
                if "Tier" in element:
                    alphalist.append(element)

            print(alphalist)

            filenames=[]
            links=[]

            for file in alphalist:
                filename = file.split("/")[2]
                #print(filename) 
                filenames.append(filename)
                links.append('https://pred-model-data.s3.eu-north-1.amazonaws.com/Resources/Results/' +filename)



            print(filenames)
            print(links)

            if datePicker == "": 
                current_dates =[]
                for file in filenames:
                    if current_date in file:
                        current_dates.append(current_date)
            else:
                current_dates =[]
                for file in filenames:
                    if datePicker in file:
                        current_dates.append(datePicker)


            print(current_dates)

            models =['Alpha','BPC','Beta','GammaOld','GammaPrediction','Merge','NN','New','PredictionReport','Tier']
            modellst = []
            for file in filenames:
                for model in models:
                    if model in file:
                        print(file)
                        print(model)
                        if model=='PredictionReport':
                            modellst.append('All Models')
                        elif model=='GammaOld':
                            modellst.append('Gamma Old')
                        elif model=='GammaPrediction':
                            modellst.append('Gamma')
                        else:
                            modellst.append(model)
            
            print(len(modellst))

        else:
            if datePicker == "":
                filtered_lst=[]
                datelst =[]
                for element in files:
                    if current_date in element:
                        filtered_lst.append(element)
                        datelst.append(current_date)

                print(filtered_lst)
                print(datelst)
            else:
                filtered_lst=[]
                datelst =[]
                for element in files:
                    if datePicker in element:
                        filtered_lst.append(element)
                        datelst.append(datePicker)

                print(filtered_lst)
                print(datelst)


            filenames=[]
            links=[]

            for file in filtered_lst:
                filename = file.split("/")[2]
                print(filename) 
                filenames.append(filename)
                links.append('https://pred-model-data.s3.eu-north-1.amazonaws.com/Resources/Results/' +filename)



            print(filenames)
            
            if datePicker == "": 
                current_dates =[]
                for file in filenames:
                    if current_date in file:
                        current_dates.append(current_date)
            else:
                current_dates =[]
                for file in filenames:
                    if datePicker in file:
                        current_dates.append(datePicker)


            print((current_dates))

            models =['Alpha','BPC','Beta','GammaOld','GammaPrediction','Merge','NN','New','PredictionReport','Tier']
            modellst = []
            for file in filenames:
                for model in models:
                    if model in file:
                        print(file)
                        print(model)
                        if model=='PredictionReport':
                            modellst.append('All Models')
                        elif model=='GammaOld':
                            modellst.append('Gamma Old')
                        elif model=='GammaPrediction':
                            modellst.append('Gamma')
                        else:
                            modellst.append(model)
            
            print(len(modellst))

            

        sl=list(range(1,len(filenames)+1)) 
        print(sl) 

        df = pd.DataFrame(
        {'SL' : sl,
            'date' : current_dates,
            'model' : modellst,
            'filenames' : filenames,
            'link': links
        })
        print(df) 

        json_records = df.reset_index().to_json(orient ='records')

        data = []
        data= json.loads(json_records)
        context = {'f': data}
    else:
        link = "http://csprediction-env.eba-pvvpzi4d.eu-north-1.elasticbeanstalk.com/getallfilename"
        f = urlopen(link)
        myfile = f.read()
        files=json.loads(myfile)['Name']
        #print(files)

        today = date.today()

        # dd/mm/YY
        current_date= today.strftime("%Y-%m-%d")
        print("current_date=", current_date)

        # model =""
        # datePicker ="2022-04-24"

        filtered_lst=[]
        datelst =[]
        for element in files:
            if current_date in element:
                filtered_lst.append(element)
                datelst.append(current_date)

        print(filtered_lst)
        print(datelst)

        filenames=[]
        links=[]

        for file in filtered_lst:
            filename = file.split("/")[2]
            print(filename) 
            filenames.append(filename)
            links.append('https://pred-model-data.s3.eu-north-1.amazonaws.com/Resources/Results/' +filename)



        print(filenames)
            
            
        current_dates =[]
        for file in filenames:
            if current_date in file:
                current_dates.append(current_date)
           


        print(current_dates)

        models =['Alpha','BPC','Beta','GammaOld','GammaPrediction','Merge','NN','New','PredictionReport','Tier']
        modellst = []
        for file in filenames:
            for model in models:
                if model in file:
                    print(file)
                    print(model)
                    if model=='PredictionReport':
                        modellst.append('All Models')
                    elif model=='GammaOld':
                        modellst.append('Gamma Old')
                    elif model=='GammaPrediction':
                        modellst.append('Gamma')
                    else:
                        modellst.append(model)
        
        print(len(modellst))

        sl=list(range(1,len(filenames)+1)) 
        print(sl) 

        df = pd.DataFrame(
        {'SL' : sl,
            'date' : current_dates,
            'model' : modellst,
            'filenames' : filenames,
            'link': links
        })
        print(df) 

        json_records = df.reset_index().to_json(orient ='records')

        data = []
        data= json.loads(json_records)
        context = {'f': data}   
                
    return render(request, 'download.html',context)

def predictions(request):
    if request.method == "POST":
        title = request.POST.get("q")
        redio = request.POST.get("flexRadio")
        # title = title.replace(" ", "%20")
        print(title)
        print(redio)
        url = 'http://csprediction-env.eba-pvvpzi4d.eu-north-1.elasticbeanstalk.com/predict/'+ title
        #redirect(url)
        x = requests.get(url)
        print(x.status_code)
        
        if redio =="id":
            print("im here...!!")
           
            return render(request, 'short_predictions.html')  
        else:
            print("im in else part..!!")
            return render(request, 'predictions.html')
     
def test(request):
    return render(request, 'test.html',{})

def dataset_alert_notification(request):
    return render(request, 'alert_notification.html')