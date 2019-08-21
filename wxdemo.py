
# coding=utf8
import sys
import requests
import os
import time
import random

from getPic import *
# from api import *
from wav_mp4 import *

from cv_api import *
from cv_model import *



defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)

from flask import Flask,render_template,request,json,send_from_directory
# from DB import *
app = Flask(__name__)


eng2CN = {'happy':'高兴','sad':'悲伤'}
CN2eng =  {v: k for k, v in eng2CN.items()}


@app.route('/infer-530f71ca-635b-4041-aca5-af5861f25ce7/')
def hello_world():
    return "hello world"
@app.route('/infer-530f71ca-635b-4041-aca5-af5861f25ce7/video2label',methods=['POST'])
def video2label():
    print("****************************************************")
    try:
        print(request.values)
        print(request.form)
        print(request.get_data())
        print(json.loads(request.get_data())['test'])
    except:
        pass
    try:
        # test_content = str(json.loads(request.values.get("test")))
        # print(test_content)
        print(request.values.get("test"))
    except:
        pass

    print("****************************************************")
    try:        
        video_url = str(request.values.get("video_url"))
        usr_id = str(request.values.get("user_id"))
        curr_time = str(time.time())
    except:
        pass

    try:
        video_url = str(json.loads(request.get_data())['video_url'])[1:-1]
        # 这里是为了把发过来的引号去掉
        usr_id = str(json.loads(request.get_data())['user_id'])
        curr_time = str(time.time())
        print(video_url)
        print(usr_id)
        print(curr_time)
    except Exception as e:
        print(e)
    # dir_name = usr_id + curr_time

    # print(video_url," ",dir_name)
    try:
        target_dir = 'static/user/' + str(abs(hash(usr_id)))

        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            print("mkdir : ",target_dir)

        target_file = target_dir+"/"+str(abs(hash(video_url))) + ".mp4"
    except:
        pass

    try:
        download_mp4(video_url, target_file)
        print(target_file,target_file[:-4],5)
        outs = get_pic_frames(target_file,target_file[:-4],5)
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>rst:",outs)
    except Exception as e:
        print(e)
        res = "download error"
        return json.dumps(res)



    try:
        outs_label = [recong(model,out) for out in outs]
        theme_labels = outs_label
        print(theme_labels)
        outs_label.append('deecamp_22') # 永远加个其他
        outs_label = [en2emEn[x] if x in en2emEn else 'qt' for x in outs_label]
        print(outs_label)
        # 先算出每个元素出现的次数
        tmp = {i:outs_label.count(i) for i in set(outs_label)}
        # 找出次数最大的那个
        print(tmp)
        tmp = sorted(tmp.items(),key=lambda item:item[1], reverse = True)
#         you_want = max(zip(tmp.values(), tmp.keys()))[1]
        print(tmp)
        you_wants = [x[0] for x in tmp]
        outs_label = you_wants
#         print(you_want)
    except Exception as e:
        print(e)
        you_want = "error"


    # print(in_acc_nbr)
    # input_grade1=int(json.loads(request.values.get("grade1")))
    # input_grade2 = int(json.loads(request.values.get("grade2")))
    # input_grade3 = int(json.loads(request.values.get("grade3")))
    # input_txt1=str(json.loads(request.values.get("txt1")))
    # input_txt2=str(json.loads(request.values.get("txt2")))
    # input_txt3=str(json.loads(request.values.get("txt3")))
    try:
        you_wants = list(outs_label)
    except Exception as e:
        print(e)
        you_wants = ['qt']
#     you_wants = [eng2CN[you_want] for you_want in you_wants]
    res = [str(you_want) for you_want in you_wants]
    res = {"author":"deecamp22","style_label":res}
    print(res)
    print(video_url)
    return json.dumps(res)



@app.route('/infer-530f71ca-635b-4041-aca5-af5861f25ce7/label2mp3',methods=['POST'])
def label2mp3():
    print("****************************************************")


    try:
        video_url = str(json.loads(request.get_data())['video_url'])[1:-1]
        # 这里是为了把发过来的引号去掉
        usr_id = str(json.loads(request.get_data())['user_id'])
        curr_time = str(time.time())
        print(video_url)
        print(usr_id)
        print(curr_time)
    except Exception as e:
        print(e)
        pass
    # dir_name = usr_id + curr_time

    # print(video_url," ",dir_name)
    try:
        target_dir = 'static/user/' + str(abs(hash(usr_id)))

        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            print("mkdir : ",target_dir)

        target_file = target_dir+"/"+str(abs(hash(video_url))) + ".mp4"
    except:
        pass

    try:
        download_mp4(video_url, target_file)
    except Exception as e:
        print(e)
        dir_path = 'static/' + 'happy/'




    try:        
        checks_tables = str(request.values.get("checks_tables"))
        print(checks_tables)
        curr_time = str(time.time())
#         checks_tables = CN2eng[checks_tables]
        dir_path = 'static/data/' + checks_tables + '/'
    except:
        dir_path = 'static/data/' + 'qt/' # 默认值
        # print("error: use default " + dir_path)

    try:
        checks_tables = str(json.loads(request.get_data())['checks_tables'])[1:-1]
        # 这里是为了把发过来的引号去掉
        print(checks_tables)

        dir_path = 'static/data/' + checks_tables + '/'

    except:
        dir_path = 'static/data/' + 'qt/' # 默认值
        print("error: use default " + dir_path)

    mp3s = os.listdir(dir_path)
    random.shuffle(mp3s)
    old_old_mp3s = mp3s
    mp3s = mp3s[:3]
    mp3s = [dir_path + r for r in mp3s]
    old_mp3s = mp3s

    # 剪切视频
    cutted_mp3_root = str(abs(hash(video_url)))
    mp3s = cut3_mp3(target_file, mp3s, cutted_mp3_root)
#     print('>>>old_mp3s',old_old_mp3s)

    print('>>>>>>>>>>>>>>>>>>mp3s',old_mp3s)
    res = {"voiceList":
            [{
                "src":mp3s[i],
                "name":str(i),
                "isPlayAudio": False,
                "audioTime": 0,
                "audioSeek": 0,
                "audioDuration": 0
            } for i in range(len(mp3s))]}
    
    print('>>>>>>>>>>>cutted_mp3s',mp3s)

    return json.dumps(res)


@app.route('/infer-530f71ca-635b-4041-aca5-af5861f25ce7/wav2mp4',methods=['POST'])
def wav2mp4():
    # print(request.values.get("test"))
    print("****************************************************")
    error_message = " "
    # label = str(request.values.get("label"))
    # dirpath = os.path.join(app.root_path)
    # print(label)


    try:
        video_url = str(json.loads(request.get_data())['video_url'])[1:-1]
        # 这里是为了把发过来的引号去掉
        usr_id = str(json.loads(request.get_data())['user_id'])
        mp3_url = str(json.loads(request.get_data())['mp3_url'])[1:-1]
        retention = float(json.loads(request.get_data())['retention'])

        curr_time = str(time.time())
        print(video_url)
        print(usr_id)
        print(curr_time)
    except:
        error_message = "json error"
    # dir_name = usr_id + curr_time

    # print(video_url," ",dir_name)
    try:
        target_dir = 'static/user/' + str(abs(hash(usr_id)))

        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            print("mkdir : ",target_dir)

        target_file = target_dir+"/"+str(abs(hash(video_url))) + ".mp4"
    except:
        error_message = "mkdir error"

    try:
        download_mp4(video_url, target_file)
    except Exception as e:
        print(e)
        error_message = "download error"

    try:
        print(target_file)
        res_url = merge_mp4_mp3(target_file, mp3_url, retention)
    except Exception as e:
        print(e)
        error_message = "merge error"
        res_url = 'static/mc_start.mp4'

    res = {'error_message':error_message, "res_url":res_url}
    return json.dumps(res)




def download_mp4(url, filename):
    r = requests.get(url, stream=True)
    
    if os.path.exists(filename):
        os.remove(filename)

    with open(filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)




if __name__ == '__main__':
    app.run('0.0.0.0','8080',debug=True)
    # print(app.root_path)