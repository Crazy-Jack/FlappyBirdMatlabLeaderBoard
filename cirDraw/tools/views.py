import warnings
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import Http404, HttpResponse, JsonResponse
from django.template import RequestContext
from django.contrib import messages
from .forms import UploadFileForm, JsonTestFile
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.decorators import login_required
import pytz
import scipy.io
from .models import *
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Max, Min
from django.db.models import Q
import sys, datetime, time
import json
import hashlib
import csv
import numpy as np
import re
import pickle
import os


def render_login_page(request):
    logout(request)
    context = {}
    return render(request, 'tools/login.html', context)

def render_c1_page(request):
    cat = 1
    query_category = SubmissionTable.objects.filter(category__exact = cat).order_by("-best_score", "train_time")
    context = {'query': query_category, 'category': cat}
    return render(request, 'tools/index.html', context)

def render_c2_page(request):
    cat = 2
    query_category = SubmissionTable.objects.filter(category__exact = cat).order_by("-best_score", "num_nn")

    context = {'query': query_category, 'category': cat}
    return render(request, 'tools/index.html', context)

def render_c3_page(request):
    cat = 3
    query_category = SubmissionTable.objects.filter(category__exact = cat).order_by("-best_score")
    context = {'query': query_category, 'category': cat}
    return render(request, 'tools/index.html', context)


def render_upload_page(request):
    query = SubmissionTable.objects.filter(username__exact = request.user.username)
    context = {'query': query}
    return render(request, 'tools/upload.html', context)

def get_user_data(request):
    query = SubmissionTable.objects.filter(username__exact = request.user.username).order_by("-submission_time")
    l = []
    for i in query:
        obj = {'category': i.category,
               'submission_time': i.submission_time,
               'best_score': i.best_score,
               'train_time': i.train_time,
               'youtube_url': i.youtube_url,
               'num_nn': i.num_nn,
               'md5': i.md5,
               }
        l.append(obj)
    return JsonResponse(l, safe=False)



def render_index_page(request):
    # context = {'c': [query_category_1, query_category_2, query_category_3]}
    context = {}
    return render(request, 'tools/landing_page.html', context)

def render_search_page(request):
    """test_render_search_page"""
    # preload data
    prepath = "/root/e2database-release/cirDraw/tools/cache_update.pkl"
    # if not os.path.isfile(prepath):
    #     prepath = "/home/tianqinl/Code/e2database-release/cirDraw/tools/cache.pkl"
    # if not os.path.isfile(prepath):
    #     prepath = "/Users/tianqinli/Code/e2database-release/cirDraw/tools/cache.pkl"
    with open(prepath, 'rb') as f:
         all_out_data = pickle.load(f)
    all_out_data_json = json.dumps(all_out_data)
    context = {'preload': all_out_data_json}
    return render(request, 'tools/search.html', context)

@csrf_exempt
def save_to_files(request):
    if request.method == "POST":
        try:
            form = UploadFileForm(data=request.POST, files=request.FILES)
            if form.is_valid():
                # get md5 value. Note: consider (file + parameters) as a whole md5
                form_file = form.cleaned_data['file']

                str_parameters = form.cleaned_data['parameters']
               
                parameters = json.loads(str_parameters)

                b_file = form_file.read()
                
               
                file_parameters = str_parameters.encode('utf-8') + b_file
                md5 = hashlib.md5(file_parameters).hexdigest()

                sub_base = "md5_data/"
                path = sub_base + md5

                # check if the file exists
                try:
                    md5ob = SubmissionTable.objects.filter(md5__exact=md5)
                except SubmissionTable.DoesNotExist:
                    md5ob = None
                print(f"Md5 {md5} existed in DB?: ", md5ob)

                if default_storage.exists(path):
                    # over-write
                    default_storage.delete(path)

                # store md5 value and parameters into database, store file
                print(f"saving upload file {md5}...")
                path = default_storage.save(sub_base + md5, form_file) # note this path doesnot include the media root, e.g. it is actually stored in "media/data/xxxxxx"
                file_path = settings.MEDIA_ROOT + '/' + path
                print(file_path)
 
                # read nn.mat file
                # process nn.mat file

                nn_mat = scipy.io.loadmat(form_file)
                train_time = nn_mat['trainTime'][0][0]
                train_episode = nn_mat['EPISODES'][0][0]
                train_deaths = nn_mat['deaths'][0][0]
                train_highscore = nn_mat['highScore'][0][0]
                print(f"trainTime: {nn_mat['trainTime']}\nEPISODES: {nn_mat['EPISODES'][0][0]}")

                print("create model instance")
                youtube_url = parameters['youtube_url']
                print(f"parameters['category'][-1] {parameters['category'][-1]} ; parameters['num_nn'] {parameters['num_nn']}")
                category = int(parameters['category'][-1])
                num_nn = int(parameters['num_nn'])

                # time 
                timezone = pytz.timezone('US/Eastern')
                with_timezone = timezone.localize(datetime.datetime.now())

                if not md5ob:
                    new_object = SubmissionTable(
                        md5 = md5, 
                        upload_file_location = path,
                        youtube_url = youtube_url,
                        category = category,
                        best_score = int(train_highscore),
                        andrewid = request.user.email,
                        username = request.user.username,
                        submission_time = with_timezone,
                        train_time = float(train_time),
                        train_episode = int(train_episode),
                        train_deaths = int(train_deaths),
                        num_nn = int(num_nn),
                    )
                    new_object.save()
                else:
                    md5ob.update(
                        md5 = md5, 
                        upload_file_location = path,
                        youtube_url = youtube_url,
                        category = category,
                        best_score = int(train_highscore),
                        andrewid = request.user.email,
                        username = request.user.username,
                        submission_time = with_timezone,
                        train_time = float(train_time),
                        train_episode = int(train_episode),
                        train_deaths = int(train_deaths),
                        num_nn = int(num_nn)
                    )

                return_json = [{'md5': md5, 'save_status': True, 'error': ""}]
                return JsonResponse(return_json, safe=False)
            else:
                print("Form not valid")
                print("Error: ", form.errors)


        except Exception as e:
            print("Save to file Failed: ", e)
            return_json = [{'md5':"", 'save_status': False, 'error': str(e)}]
            return JsonResponse(return_json, safe=False)
        
def delete_md5(request):
    if request.method == "GET":
        flag = 1
        username = request.user.username
        md5 = request.GET['md5'] 

        # check the user own the md5
        try:
            md5ob = SubmissionTable.objects.filter(md5=md5)
            if len(md5ob) == 0:
                flag = -1
        except SubmissionTable.DoesNotExist:
            md5ob = None
            flag = -1

        if md5ob is not None:
            # check if the username matches
            target_username = md5ob[0].username
            if target_username != username:
                flag = -1

        if flag == 1:
            # delete
            md5ob.delete()
            sub_base = "md5_data/"
            path = sub_base + md5
            if default_storage.exists(path):
                default_storage.delete(path)

            # delete file
            print(f"delete {md5}")

    else:
        flag = -1

    return JsonResponse([flag], safe=False)

def create_user(request):
    # verify users
    if request.method == "POST":
        is_valid = True
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if 'andrew' not in email:
            is_valid = False 
            messages.error(request, "Must use andrew email.", extra_tags='register_user')
        
        if len(password) < 8:
            is_valid = False 
            messages.error(request, "Password must be at least 8 characters.", extra_tags='register_user')

        if User.objects.filter(Q(username=username) | Q(email=email)):
            is_valid = False 
            messages.error(request, "User already exists.", extra_tags='register_user')
        
        if is_valid:
            messages.success(request, f"Registration Complete!", extra_tags='register_user')
        
        if not is_valid:
            return redirect("/tools/user/")
        else:
            # update database
            user = User.objects.create_user(
                username = username,
                email = email,
                password = password
            )
            login(request, user)
            return redirect("/tools/upload/")
        

def loguserout(request):
    # a view that will log out a user using passward
    logout(request)
    return redirect("/tools/user/")

def loguserin(request):
    # a view that will login a user using passward
    if request.method == "POST":
        is_valid = True
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            #return render(request, 'tools/upload.html', {'user': user})
            return redirect("/tools/upload/")
        else:
            messages.error(request, "Login Failed.", extra_tags='login_user')
            return redirect("/tools/user/")
    return 

