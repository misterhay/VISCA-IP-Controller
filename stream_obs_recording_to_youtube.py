#! /usr/bin/env python3

stream_key = 'xxxx-xxxx-xxxx-xxxx'
recording_path = '/home/misterhay/Videos'
ffmpeg_path = ''

from datetime import datetime
from pathlib import Path
import os

# find the newest file in the folder
p = Path(recording_path)
time, newest_file = max((f.stat().st_mtime, f) for f in p.iterdir())

youtube_server = 'rtmp://a.rtmp.youtube.com/live2/'
command = ffmpeg_path+'ffmpeg -re -i '+str(newest_file)+' -acodec copy -vcodec copy -f flv '+youtube_server+stream_key
proceed = input('Do you want to stream'+str(newest_file)+'? (y/n)')
if proceed == 'y':
    print(command)
    os.system(command)
else:
    print('Okay, quitting.')