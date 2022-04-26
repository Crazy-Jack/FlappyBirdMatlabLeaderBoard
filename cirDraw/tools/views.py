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
    
    context = {}
    return render(request, 'tools/login.html', context)

def render_c1_page(request):
    cat = 1
    query_category = SubmissionTable.objects.filter(category__exact = cat)
    context = {'query': query_category, 'category': cat}
    return render(request, 'tools/index.html', context)

def render_c2_page(request):
    cat = 2
    query_category = SubmissionTable.objects.filter(category__exact = cat)
    context = {'query': query_category, 'category': cat}
    return render(request, 'tools/index.html', context)

def render_c3_page(request):
    cat = 3
    query_category = SubmissionTable.objects.filter(category__exact = cat)
    context = {'query': query_category, 'category': cat}
    return render(request, 'tools/index.html', context)


def render_upload_page(request):
    query = SubmissionTable.objects.filter(username__exact = request.user.username)
    context = {'query': query}
    return render(request, 'tools/upload.html', context)

def get_user_data(request):
    query = SubmissionTable.objects.filter(username__exact = request.user.username)
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


# ========================= RENDER PAGES ==============================
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

def render_stats_page(request):
    """test_render_search_page"""
    # preload data
    # with open("/home/tianqinl/mye2/cirDraw/tools/cache.pkl", 'rb') as f:
    #      all_out_data = pickle.load(f)
    # all_out_data_json = json.dumps(all_out_data)
    context = {}
    return render(request, 'tools/stats.html', context)



def render_display_page(request, md5):
    context = {"md5": md5}
    print('Render display1:',md5)
    case = UploadParametersMD5.objects.filter(md5 = md5).values('status')
    print("check:", context)
    if case.exists():
        #print("check:",case)
        code = case[0]['status']
        print('Render display2:', code, type(code))
        if code == 200:
            return render(request, 'tools/tools.html', context)
        elif code == 202:
            return render(request, 'tools/wait.html', context)
        else:
            return render(request, 'tools/HTTP404.html', context)
    else:
        print('This md5 not exist.')
        return render(request, 'tools/HTTP404.html', context)
        #raise Http404

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
                category = int(parameters['category'][-1])
                num_nn = int(parameters['num_nn'])
                if not md5ob:
                    new_object = SubmissionTable(
                        md5 = md5, 
                        upload_file_location = path,
                        youtube_url = youtube_url,
                        category = category,
                        best_score = int(train_highscore),
                        andrewid = request.user.email,
                        username = request.user.username,
                        submission_time = datetime.datetime.now(),
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
                        submission_time = datetime.datetime.now(),
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
            print(user.password)
            #return render(request, 'tools/upload.html', {'user': user})
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








# ====================================================================
@csrf_exempt
def get_meta_stats(request):
    top_percent = request.GET['top_percent']
    upordown = request.GET['upordown']
    disply_percent = request.GET['disply_percent']
    print(top_percent, upordown, disply_percent)

    top_percent = min(100, max(0, int(top_percent)))
    disply_percent = min(100, max(0, int(disply_percent)))
    
    # compute criterion
    if upordown == 'up':
        bin_clause = f"bin <= {int(top_percent)} and bin > 0"
    else:
        bin_clause = f"bin >= -{int(top_percent)} and bin < 0"
    
    limits = int(disply_percent * 141 * 0.01)
    sql_query = f'''
    select 1 as id, Gene, SUM(count_data) as sum_counts from MetaPercentData 
    where {bin_clause} group by Gene ORDER BY sum_counts DESC limit {limits};'''
    print('SQL: ', sql_query)
    data_p = SearchTableMetaData.objects.raw(sql_query)

    data_meta = []
    data_name = []
    # TODO: get the return of microarray ready
    for data_i in data_p:
        print(data_i.Gene, data_i.sum_counts)
        obj_i = {
            'Name': data_i.Gene,
            'Counts': data_i.sum_counts,
        }
        data_meta.append(obj_i)
        data_name.append(data_i.Gene)
    

    # query info based on the data_name
    dataset = []
    for gene_name in data_name:
        sql_query = f'''
        select * from MetaPercentData where Gene='{gene_name}';
        '''
        data_p = SearchTableMetaData.objects.raw(sql_query)
        upregulated = [int(i.count_data) for i in data_p[20:]]
        downregulated = [int(i.count_data) for i in data_p[:20]]
        dataset.append({'gene_name': gene_name, 'up': upregulated,
                              'down': downregulated[::-1]})
    print([data_meta, dataset])
    return JsonResponse([upordown, data_meta, dataset], safe=False)


@csrf_exempt
def get_stats(request):
    celllines = request.GET['celllines']
    if len(celllines) == 0:
        celllines = 'ALL'
    else:
        celllines = celllines[:-1].split(";")

    # duration
    durations = request.GET['durations']
    if len(durations) == 0:
        durations = 'ALL'
    else:
        print(durations[:-1])
        durations = [int(i[:-5]) for i in durations[:-1].split(";")]


    # dose
    doses = request.GET['doses']
    if len(doses) == 0:
        doses = 'ALL'
    else:
        doses = [int(i[:-3]) for i in doses[:-1].split(";")]


    # uppercent
    up_percent = request.GET['up_percent']
    down_percent = request.GET['down_percent']
    adj_p_value = request.GET['adj_p_value']
    logfc = request.GET['logfc']

    if up_percent == "-1":
        mode = "down"
        mode_sign = "<"
        logfc = str(-float(logfc))
        percent = str(float(down_percent) * 0.01)
    elif down_percent == '-1':
        mode = "up"
        mode_sign = ">"
        percent = str(float(up_percent) * 0.01)
    else:
        raise ValueError(f"up_percent {up_percent} BUT down_percent {down_percent}")

    # check sanity
    print(f"durations {durations}")
    print(f"doses {doses}")
    print(f"celllines {celllines}")

    # MicroArray
    if celllines != 'ALL' or durations != 'ALL' or doses != 'ALL':
        query = "WHERE "
        if celllines != 'ALL':
            query += "(CellLine = '" + str(celllines[0]) + "'"
            if len(celllines) > 1:
                for cell_line in celllines[1:]:
                    query += " OR CellLine = '" + str(cell_line) + "'"
            query += ")"
            

        if durations != 'ALL':
            query += " AND "
            query += "(Duration = " + str(durations[0])
            if len(durations) > 1:
                for duration in durations[1:]:
                    query += " OR Duration = " + str(duration)
            query += ")"
            

        if doses != 'ALL':
            query += " AND "
            query += "(Dose = " + str(doses[0])
            if len(doses) > 1:
                for dose in doses[1:]:
                    query += " OR Dose = " + str(dose)
            query += ")"

        print(query)
    else:
        query = ""
    sql_query = f'''
    select 1 as id, C.ins_count, C.genename, C.logfc_percent, C.log10padj_percent from (select count(A.GeneName)
    as ins_count,A.GeneName, AVG(Log2FC{mode_sign}{logfc}) as logfc_percent, AVG(minus_log10padj>{str(-np.log10(float(adj_p_value)))} OR A.minus_log10padj=0.0) as log10padj_percent from
    (select GeneName, Log2FC, minus_log10padj from MicroarrayData {query}) as A group by A.GeneName ORDER BY ins_count DESC, logfc_percent DESC) C
    where C.logfc_percent > {percent} AND C.log10padj_percent > {percent};'''
    print('SQL: ', sql_query)
    data_p = SearchTableMicroarray.objects.raw(sql_query)
    print(len(data_p))

    print(data_p.columns)
    data_microarray = []
    # TODO: get the return of microarray ready
    for data_i in data_p:
        # print(data_i.ins_count, data_i.genename)
        obj_i = {
            'ins_count': data_i.ins_count,
            'genename': data_i.genename,
            'logfc_percent': round(data_i.logfc_percent * 100, 2),
            'log10padj_percent': data_i.log10padj_percent,
        }
        data_microarray.append(obj_i)


    ## RNA-seq
    sql_query = f'''
    select 1 as id, C.ins_count, C.genename, C.logfc_percent, C.log10padj_percent from (select count(A.GeneName)
    as ins_count,A.GeneName, AVG(Log2FC{mode_sign}{logfc}) as logfc_percent, AVG(A.minus_log10padj>{str(-np.log10(float(adj_p_value)))} OR A.minus_log10padj=0.0) as log10padj_percent from
    (select GeneName, Log2FC, minus_log10padj from RNAseqData {query}) as A group by A.GeneName ORDER BY ins_count DESC, logfc_percent DESC) C
    where C.logfc_percent > {percent} AND C.log10padj_percent > {percent};'''
    print('RNAseq SQL: ', sql_query)
    data_p = SearchTableMicroarray.objects.raw(sql_query)
    print(len(data_p))

    print(data_p.columns)
    data_rnaseq = []
    # TODO: get the return of microarray ready
    for data_i in data_p:
        # print(data_i.ins_count, data_i.genename)
        obj_i = {
            'ins_count': data_i.ins_count,
            'genename': data_i.genename,
            'logfc_percent': round(data_i.logfc_percent * 100, 2),
            'log10padj_percent': data_i.log10padj_percent,
        }
        data_rnaseq.append(obj_i)




    return JsonResponse([data_microarray, data_rnaseq], safe=False)



# ====================================================================
@csrf_exempt
def search_indb(request):
    start_time = time.time()
    assert request.method == "GET", f"request.method is {request.method} not GET"

    # search for the database to get this form of data


    gene_name = request.GET['gene_name']
    print(f"gene_name {gene_name}")

    start_mr_search_time = time.time()
    data = SearchTableMicroarray.objects.filter(GeneName__exact = gene_name)
    print(f"microarray seach time {time.time() - start_mr_search_time} s")


    all_out_data = []

    out_data = {}

    # get unique duration, dose
    st_iter = time.time()
    for data_i in data:
        logfc = data_i.Log2FC
        logp = data_i.minus_log10padj # ?????
        CellLine = data_i.CellLine.replace(" ", "")
        DataSet = data_i.Source
        Dose = data_i.Dose
        Duration = data_i.Duration
        GSE = data_i.GSE

        obj = {'logfc': float(logfc),
                'logp': float(logp),
                'name': CellLine,
                'duration': convert_hour_radius(Duration),
                'dose': Dose,
                'DataSet': DataSet,
                'GSE': GSE,
            }
        if CellLine not in out_data:
            out_data[CellLine] = [obj]
        else:
            out_data[CellLine].append(obj)

        # print(f"CHECKEREERERER")

    print(f"time for object iteration {time.time() - st_iter}")
    # calculate stats
    start_calculate_stats_time = time.time()
    stats_1 = calculate_statistics(out_data, threshold_fc=0.5)
    print(f"time for calculate stats {time.time() - start_calculate_stats_time}")

    all_out_data.append(out_data)


    # RNAseq
    start_rna_search_time = time.time()
    data = SearchTableRNAseq.objects.filter(GeneName__exact = gene_name)
    print(f"RNA seach time {time.time() - start_rna_search_time} s")
    print(f"RNAseq data.objects.count() {len(data)}")
    out_data = {}
    st_iter_rna = time.time()
    for data_i in data:
        logfc = data_i.Log2FC
        logp = data_i.minus_log10padj # ???
        CellLine = data_i.CellLine.replace(" ", "")
        Dose = data_i.Dose
        Rep = data_i.Rep
        Duration = data_i.Duration
        GSE = data_i.GSE

        # print(f"data_i.filename {data_i.filename} out {out_name}: hour: {hours}; dose {dose}")
        # create object to append

        duration, multi_duration = convert_RNAseq_hour_radius(Duration)


        obj = {'logfc': float(logfc),
                'logp': float(logp),
                'name': CellLine,
                'duration': duration,
                'multi_duration': multi_duration,
                'dose': Dose,
                'GSE': GSE,
            }
        if CellLine not in out_data:
            out_data[CellLine] = [obj]
        else:
            out_data[CellLine].append(obj)
    print(f"RNA-seq iter {time.time() - st_iter_rna}")
    stats_2 = calculate_statistics(out_data, threshold_fc=2.0)
    print(f"RNA-seq processing time {time.time() - st_iter_rna}")
    all_out_data.append(out_data)

    all_out_data.append(stats_1)
    all_out_data.append(stats_2)


    # chipseq
    start_chipseq = time.time()
    print(f"---------gene_name {gene_name}")
    gene_info = SearchTableChipSeqRefData.objects.filter(gene__exact = gene_name)
    print(f"----gene_info {len(gene_info)}")
    if len(gene_info) > 0:
        chr_num = gene_info[0].chr_num
        print(f"chr_num {chr_num}")
        tss = np.mean([i.tss for i in gene_info])
        up_tss = max(0, tss - 200000)
        down_tss = tss + 200000
        print(f"tss {tss}; up_tss {up_tss}; down_tss {down_tss}")
        data_chip = SearchTableChipSeq.objects.filter(chr_num__exact = chr_num).filter(mid__gt = up_tss).filter(mid__lt=down_tss)
        # print([i.Duration for  i in data_chip])
        # print(f"chipseq time is {time.time() - start_chipseq}")

        out_data = {}
        for data_i in data_chip:
            mid = data_i.mid
            score = data_i.score # ???
            CellLine = data_i.Cellline.replace(" ", "")
            Dose = data_i.Dose
            if data_i.Duration != data_i.Duration:
                Durationn = "0"
            else:
                Duration = data_i.Duration.replace(" ", "").replace(",", "-")
            GSE = data_i.GSE

            # print(f"data_i.filename {data_i.filename} out {out_name}: hour: {hours}; dose {dose}")
            # create object to append

            duration, multi_duration = convert_RNAseq_hour_radius(Duration)
            duration = 0.56

            obj = {"log2score": np.log2(float(score)),
                    "tss": (mid - tss)/1000,
                    "name": CellLine,
                    "duration": duration,
                    "multi_duration": multi_duration,
                    "dose": Dose,
                    "GSE": GSE,
                }
            if CellLine not in out_data:
                out_data[CellLine] = [obj]
            else:
                out_data[CellLine].append(obj)
    else:
        out_data = {}
    all_out_data.append(out_data)
    end_time = time.time()
    total_time = end_time - start_time
    print(f"Total time {total_time} s")
    # print(all_out_data)
    # with open("cache_update.pkl", 'wb') as f:
    #     pickle.dump(all_out_data, f)
    return JsonResponse(all_out_data, safe=False)



def calculate_statistics(out_data, threshold_fc):
    # calculate stats for (sig_downregulated, middle, sig_upregulated)
    stats = {}
    for i in out_data:
        stats_i = [0, 0] # sig_down, sig_up
        for j in out_data[i]:
            # print(j)

            if j['logfc'] > 0 :
                if (j['logp'] == 0 and j['logfc'] > threshold_fc) or (j['logp'] >= 1.0):
                    stats_i[1] += 1
            elif j['logfc'] < 0:
                if (j['logp'] == 0 and j['logfc'] < -threshold_fc) or (j['logp'] >= 1.0):
                    stats_i[0] += 1

        i_sum = stats_i[0] + stats_i[1]

        stats_i[0], stats_i[1] = round(stats_i[0]/len(out_data[i]), 2), round(stats_i[1]/len(out_data[i]), 2)


        stats[i] = stats_i
    print(f"stats {stats}")
    return stats


def convert_RNAseq_hour_radius(hours):
    hours = hours.replace("h", "")
    if "-" in hours:
        hours = [float(i) for i in hours.split("-")]
        return convert_hour_radius(np.mean(hours)), True
    else:
        return convert_hour_radius(float(hours)), False

def convert_hour_radius(hours):
    return np.log(hours + 1)


# def meta_info_process(filename):
#     """filter the filename"""
#     filename_list = filename.split("_")
#     out_name_list = []
#     hours = 0
#     dose = 0
#     hour_string = ""
#     dose_string = ""


#     for piece in filename_list:
#         piece = piece.replace("\"", "")
#         append_switch = 1
#         if 'h' == piece.lower()[-1]:
#             try:
#                 hours = int(piece[:-1])
#                 append_switch = 0
#             except Exception as e:
#                 warnings.warn(f"Warning: Unsuccessful parsing for hours: {e}")
#         if 'nM' == piece[-2:]:
#             try:
#                 dose = int(piece[:-2])
#                 append_switch = 0
#             except Exception as e:
#                 warnings.warn(f"Warning: Unsuccessful parsing for dose: {e}")
#         # cout as part of the name if not be used as dose or hours
#         if append_switch:
#             out_name_list.append(piece)

#     M = out_name_list[0]
#     out_name_list = out_name_list[1:]
#     out_name_list = [p for p in out_name_list if not re.match(r'^\d+', p)]

#     out_name = "_".join(out_name_list)
#     return out_name, hours, dose, M








