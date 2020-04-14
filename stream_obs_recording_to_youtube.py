# A Python GUI for streaming to YouTube from OBS recording using ffmpeg

# 

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

# ffmpeg -re -i /Users/davidhay/Movies/2020-04-13_18-56-01.mkv -acodec copy -vcodec copy -f flv rtmp://a.rtmp.youtube.com/live2/xxxx-xxxx-xxxx-xxxx

recording_path = '/Users/davidhay/Movies/'
filename = '2020-04-13_18-56-01.mkv'
stream_key = 'xxxx-xxxx-xxxx-xxxx'
ffmpeg_path = ''
ffmpeg_command = ffmpeg_path+'ffmpeg -re -i '+recording_path+' -acodec copy -vcodec copy -f flv rtmp://a.rtmp.youtube.com/live2/'+stream_key