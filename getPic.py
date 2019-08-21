#!/usr/bin/env python
from __future__ import unicode_literals, print_function
# import argparse
import ffmpeg
import sys
def getinfo(in_filename):
    try:
        probe = ffmpeg.probe(in_filename)
    except ffmpeg.Error as e:
        print(e.stderr, file=sys.stderr)
#         sys.exit(1)

    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
#     print(video_stream)
    if video_stream is None:
        print('No video stream found', file=sys.stderr)
#         sys.exit(1)/
    width = int(video_stream['width'])
    height = int(video_stream['height'])
    num_frames = int(video_stream['nb_frames'])
    duration = float(video_stream['duration'])
    
    print('width: {}'.format(width))
    print('height: {}'.format(height))
    print('num_frames: {}'.format(num_frames))
    print('duration: {}'.format(duration))


def read_frame_as_jpeg(in_filename, out_filename,frame_num):
    out, err = (
        ffmpeg
        .input(in_filename)
        .filter('select', 'gte(n,{})'.format(frame_num))
#         .output('pipe:', vframes=1, format='image2', vcodec='mjpeg')
        .output(out_filename, vframes=1).overwrite_output().run(capture_stdout=True)
    )
    return out




def get_pic_frames(in_filename, out_filename, pic_nums):
    probe = ffmpeg.probe(in_filename)
    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    num_frames = int(video_stream['nb_frames'])
    
    each_frames = num_frames // pic_nums
    curr_frame = 1
    outs = []
    for i in range(pic_nums):
        tmp = read_frame_as_jpeg(in_filename, out_filename + str(i) + '.jpg',curr_frame)
        outs.append(out_filename+str(i)+'.jpg')
        curr_frame += each_frames
        if curr_frame >= num_frames:
            curr_frame = num_frames - 1
        
    return outs

def get_pic_names(in_filename, out_filename, pic_nums):
	outs = []
	for i in range(pic_nums):
		outs.append(out_filename+str(i)+'.jpg')

	return outs

if __name__ == '__main__':
	a = get_pic_frames('mc_start.mp4','rst',5)