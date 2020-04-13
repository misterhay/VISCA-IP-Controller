# A Python GUI for streaming to YouTube from OBS recording using ffmpeg

# 

def start_streaming(ffmpeg_command):
    print(ffmpeg_command)

from tkinter import *
root = Tk()
display_message = StringVar()
root.title('Stream from OBS Recording to YouTube')
Label(root, text='this is a label').grid(row=0, column=0, columnspan=100)
streaming_key_entry = Entry(root)
streaming_key_entry.grid(row=1, column=0)

# streaming_key = streaming_key_entry.get()
# ffmpeg_command = 

Button(root, text='Start Stream', command=lambda: start_streaming(ffmpeg_command)).grid(row=1, column=6)

root.mainloop()