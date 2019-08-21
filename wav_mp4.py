import ffmpeg
import librosa
# 这个库必须管理员权限
import numpy as np
import subprocess
import os
import sys
import time


# 输入video和audio的绝对路径，以及原本视频中声音的保留比例(默认为0.2);返回融合的视频的绝对地址
def merge_mp4_mp3(path_mp4, path_mp3, retention=0.5):
    # 获取当前mp4的绝对路径，生成的文件都存储在这个绝对路径下
    tmp = path_mp4.split('/')
    path = path_mp4[:-len(tmp[-1])]
   
    # 读取video，存储为v.mp3和a.mp3
    v = ffmpeg.input(path_mp4)
    tmp_name = str(abs(hash(path_mp4)))
    ffmpeg.output(v.video, path + tmp_name + '.mp4').overwrite_output().run()
    ffmpeg.output(v.audio, path + tmp_name + '.mp3').overwrite_output().run()
    
    # 读取a.mp3和audio,将其融合，并存储为merge.mp3
    sr = 48000
    samples_raw, _ = librosa.load(path + tmp_name + '.mp3', sr=sr)
    samples_add, _ = librosa.load(path_mp3, sr=sr)
    
    len_raw = len(samples_raw)
    len_add = len(samples_add)
    if len_raw <= len_add:
        samples_add = samples_add[:len_raw]
    else:
        k = len_raw // len_add + 1
        samples_add = np.tile(samples_add, k)
        samples_add = samples[:len_raw] 
      
    # 构建渐变masks数组
    masks = np.ones(shape=np.shape(samples_add))
    gradual_len = int(sr * 0.5)
    gradual = [i for i in range(gradual_len)]
    gradual = np.asarray(gradual)
    gradual = gradual / (gradual_len)
    masks[:gradual_len] = gradual
    masks[-gradual_len:] = gradual[::-1]
    
    
    samples_merge = samples_raw * retention + samples_add * masks
    librosa.output.write_wav(path + tmp_name + 'merge.mp3', samples_merge, sr=sr)
    
    # 融合v.mp4和merge.mp3,并存储为merge.mp4
    subprocess.call('ffmpeg -i ' + path + tmp_name +'.mp4' +  ' -i ' + path + tmp_name + 'merge.mp3' + ' -strict -2 ' +  path + tmp_name + 'merge.mp4 -y', shell=True)
    
    return path + tmp_name + 'merge.mp4'

# path_mp4 = 'mc_start.mp4'    
# path_mp3 = '1.mp3'
# retention = 0.5
# merge_path = merge_mp4_mp3(path_mp4, path_mp3, retention)
# print(merge_path)

# 输入video和audio的绝对路径,剪切成的audio文件名;返回剪切的audio的绝对路径
def cut_mp3(path_mp4, path_mp3, cutted_mp3):
    # 获取当前mp4的绝对路径，生成的文件都存储在这个绝对路径下
    tmp = path_mp4.split('/')
    path = path_mp4[:-len(tmp[-1])]
   
    # 读取video，存储为a.mp3
    v = ffmpeg.input(path_mp4)
    tmp_mp3_name = str(abs(hash(path_mp4)))
    ffmpeg.output(v.audio, path + tmp_mp3_name + '.mp3').overwrite_output().run()
    
    # 读取a.mp3和audio,将audio剪切为，并存储为merge.mp3
    sr = 48000
    samples_raw, _ = librosa.load(path + tmp_mp3_name + '.mp3', sr=sr)
    samples_add, _ = librosa.load(path_mp3, sr=sr)
    samples_add = samples_add[int(sr * 0.5):]
    
    
    len_raw = len(samples_raw)
    len_add = len(samples_add)
    
    
    if len_raw <= len_add:
        samples_add = samples_add[:len_raw]
    else:
        k = len_raw // len_add + 1
        samples_add = np.tile(samples_add, k)
        samples_add = samples_add[:len_raw]
        
        
    samples_add = samples_add * 1
        
    librosa.output.write_wav(path + cutted_mp3, samples_add, sr=sr)
    return path + cutted_mp3

def cut3_mp3(path_mp4, path_mp3s, cutted_mp3_root):
    rsts = []
    for i in range(len(path_mp3s)):
        each_rst = cut_mp3(path_mp4, path_mp3s[i], cutted_mp3_root + "_" + str(time.time()) + "_" + str(i) + ".mp3")
        rsts.append(each_rst)

    return rsts

# path_mp4 = '/data/code/cjj/video2video/video.mp4'    
# path_mp3 = '/data/code/cjj/video2video/audio.mp3'
# cutted_mp3 = 'cutted_mp3.mp3'
# cutted_mp3 = cut_mp3(path_mp4, path_mp3, cutted_mp3)
# print(cutted_mp3)


def test_cut3_mp3():
    path_mp3s = os.listdir('local_test_mp3/')
    path_mp3s = ['local_test_mp3/' + x for x in path_mp3s]
    path_mp3s = path_mp3s[:3]
    rst = cut3_mp3('local_test_user/mc_start.mp4', path_mp3s, 'mc_start')
    print(rst)

def test_merge_mp4_mp3():
    path_mp4 = 'local_test_user/mc_start.mp4'
    path_mp3 = 'local_test_user/mc_start_0.mp3'
    rst = merge_mp4_mp3(path_mp4,path_mp3)
    print(rst)


if __name__ == '__main__':
    test_merge_mp4_mp3()
