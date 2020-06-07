#! /usr/bin/env python3
# A Python GUI for streaming to YouTube from OBS recording using ffmpeg

import os
import time

recording_path = '/home/misterhay/Videos/'
for root, dirs, files in os.walk(recording_path, topdown=False):
    sorted_files = sorted(files, key=os.path.getmtime)
    print(sorted_files)

    for name in files:
        filename = os.path.join(root, name)
        #print(filename)
        file_stats = os.stat(filename)
        #print(file_stats.st_mtime)

        #modification_time = time.ctime(file_stats[stat.ST_MTIME])
        #print(modification_time)

#files = sorted(recording_path, key=os.path.getmtime)
#print(files)


#fileStatsObj = os.stat ( filePath )
#modificationTime = time.ctime ( fileStatsObj [ stat.ST_MTIME ] )
#print("Last Modified Time : ", modificationTime )

'''
def start_streaming(ffmpeg_command):
    print(ffmpeg_command)

from tkinter import *
root = Tk()
display_message = StringVar()
root.title('Stream from OBS Recording to YouTube')
Label(root, text='this is a label').grid(row=0, column=0, columnspan=100)
stream_key_entry = Entry(root)
stream_key_entry.grid(row=1, column=0)

Button(root, text='Start Stream', command=lambda: start_streaming(ffmpeg_command)).grid(row=1, column=6)

root.mainloop()

# streaming_key = streaming_key_entry.get()
# ffmpeg_command = 

# ffmpeg -re -i /home/misterhay/Videos/2020-04-13_18-56-01.mkv -acodec copy -vcodec copy -f flv rtmp://a.rtmp.youtube.com/live2/xxxx-xxxx-xxxx-xxxx

recording_path = '/home/misterhay/Videos/'
filename = '2020-04-13_18-56-01.mkv'
stream_key = 'xxxx-xxxx-xxxx-xxxx'
ffmpeg_path = ''
ffmpeg_command = ffmpeg_path+'ffmpeg -re -i '+recording_path+' -acodec copy -vcodec copy -f flv rtmp://a.rtmp.youtube.com/live2/'+stream_key

start_streaming(ffmpeg_command)
'''