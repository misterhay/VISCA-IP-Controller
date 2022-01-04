#!/usr/bin/env python
# sudo apt install python3-tk

from camera import *

try:
    with open('config.txt', 'r') as f:
        ip_and_port = f.read().splitlines()
        ip = ip_and_port[0]
        port = int(ip_and_port[1])
    f.close()
except:
    ip = '192.168.1.100'
    port = 52381
c = Camera(ip, port)

def save_preset_labels():
    with open('preset_labels.txt', 'w') as f:
        for entry in entry_boxes:
            f.write(entry.get())
            f.write('\n')
    f.close()

def save_ip_and_port():
    with open('config.txt', 'w') as f:
        f.write(ip_entry.get())
        f.write('\n')
        f.write(port_entry.get())
    f.close()

# GUI
from tkinter import Tk, StringVar, Button, Label, Scale, Entry, W
root = Tk()
#display_message = StringVar()
root.title('VISCA IP Camera Controller')
root['background'] = 'white'
#Label(root, text='VISCA IP Camera Controller').grid(row=0, column=0, columnspan=100)

store_column = 0
label_column = 1
recall_column = 2
pan_tilt_column = 5
pan_tilt_row = 1
zoom_column = 3
zoom_row = 1
focus_column = 3
focus_row = 5
on_off_column = 3
on_off_row = 13
button_width = 8
store_color = 'red'
recall_color = 'light grey'
pan_tilt_color = 'white'
zoom_color = 'cyan'
focus_color = 'light blue'
on_off_color = 'violet'

# Preset store buttons
Label(root, text='Store', bg=store_color).grid(row=1, column=store_column)
Button(root, text=0, width=3, bg=store_color, command=lambda: c.memory_set(0)).grid(row=2, column=store_column)
Button(root, text=1, width=3, bg=store_color, command=lambda: c.memory_set(1)).grid(row=3, column=store_column)
Button(root, text=2, width=3, bg=store_color, command=lambda: c.memory_set(2)).grid(row=4, column=store_column)
Button(root, text=3, width=3, bg=store_color, command=lambda: c.memory_set(3)).grid(row=5, column=store_column)
Button(root, text=4, width=3, bg=store_color, command=lambda: c.memory_set(4)).grid(row=6, column=store_column)
Button(root, text=5, width=3, bg=store_color, command=lambda: c.memory_set(5)).grid(row=7, column=store_column)
Button(root, text=6, width=3, bg=store_color, command=lambda: c.memory_set(6)).grid(row=8, column=store_column)
Button(root, text=7, width=3, bg=store_color, command=lambda: c.memory_set(7)).grid(row=9, column=store_column)
Button(root, text=8, width=3, bg=store_color, command=lambda: c.memory_set(8)).grid(row=10, column=store_column)
Button(root, text=9, width=3, bg=store_color, command=lambda: c.memory_set(9)).grid(row=11, column=store_column)
Button(root, text='A', width=3, bg=store_color, command=lambda: c.memory_set(10)).grid(row=12, column=store_column)
Button(root, text='B', width=3, bg=store_color, command=lambda: c.memory_set(11)).grid(row=13, column=store_column)
Button(root, text='C', width=3, bg=store_color, command=lambda: c.memory_set(12)).grid(row=14, column=store_column)
Button(root, text='D', width=3, bg=store_color, command=lambda: c.memory_set(13)).grid(row=15, column=store_column)
Button(root, text='E', width=3, bg=store_color, command=lambda: c.memory_set(14)).grid(row=16, column=store_column)
Button(root, text='F', width=3, bg=store_color, command=lambda: c.memory_set(15)).grid(row=17, column=store_column)

# Recall buttons and entries (as labels)
Label(root, text='Recall', bg=recall_color).grid(row=1, column=recall_column)
Button(root, text=0, width=5, bg=recall_color, command=lambda: c.memory_recall(0)).grid(row=2, column=recall_column)
Button(root, text=1, width=5, bg=recall_color, command=lambda: c.memory_recall(1)).grid(row=3, column=recall_column)
Button(root, text=2, width=5, bg=recall_color, command=lambda: c.memory_recall(2)).grid(row=4, column=recall_column)
Button(root, text=3, width=5, bg=recall_color, command=lambda: c.memory_recall(3)).grid(row=5, column=recall_column)
Button(root, text=4, width=5, bg=recall_color, command=lambda: c.memory_recall(4)).grid(row=6, column=recall_column)
Button(root, text=5, width=5, bg=recall_color, command=lambda: c.memory_recall(5)).grid(row=7, column=recall_column)
Button(root, text=6, width=5, bg=recall_color, command=lambda: c.memory_recall(6)).grid(row=8, column=recall_column)
Button(root, text=7, width=5, bg=recall_color, command=lambda: c.memory_recall(7)).grid(row=9, column=recall_column)
Button(root, text=8, width=5, bg=recall_color, command=lambda: c.memory_recall(8)).grid(row=10, column=recall_column)
Button(root, text=9, width=5, bg=recall_color, command=lambda: c.memory_recall(9)).grid(row=11, column=recall_column)
Button(root, text='A', width=5, bg=recall_color, command=lambda: c.memory_recall(10)).grid(row=12, column=recall_column)
Button(root, text='B', width=5, bg=recall_color, command=lambda: c.memory_recall(11)).grid(row=13, column=recall_column)
Button(root, text='C', width=5, bg=recall_color, command=lambda: c.memory_recall(12)).grid(row=14, column=recall_column)
Button(root, text='D', width=5, bg=recall_color, command=lambda: c.memory_recall(13)).grid(row=15, column=recall_column)
Button(root, text='E', width=5, bg=recall_color, command=lambda: c.memory_recall(14)).grid(row=16, column=recall_column)
Button(root, text='F', width=5, bg=recall_color, command=lambda: c.memory_recall(15)).grid(row=17, column=recall_column)
try:
    with open('preset_labels.txt', 'r') as f:
        labels = f.read().splitlines()
    f.close()
except:
    pass
entry_boxes = []
for e in range(16):
    box = Entry(root, justify='right')
    try:
        box.insert(-1, labels[e])
    except:
        pass
    box.grid(row=e+2, column=label_column)
    entry_boxes.append(box)
Button(root, text='Save preset labels', bg=store_color, command=lambda: save_preset_labels()).grid(row=1, column=label_column)

# Pan speed and Tilt speed sliders
Label(root, text='Pan Speed', bg=pan_tilt_color).grid(row=pan_tilt_row, column=pan_tilt_column)
pan_speed_slider = Scale(root, from_=24, to=0, bg=pan_tilt_color)
pan_speed_slider.set(7)
pan_speed_slider.grid(row=pan_tilt_row+1, column=pan_tilt_column, rowspan=4)
Label(root, text='Tilt Speed', bg=pan_tilt_color).grid(row=pan_tilt_row, column=pan_tilt_column+1)
tilt_speed_slider = Scale(root, from_=24, to=0, bg=pan_tilt_color)
tilt_speed_slider.set(7)
tilt_speed_slider.grid(row=pan_tilt_row+1, column=pan_tilt_column+1, rowspan=4)
#Button(root, text='test', command=lambda: print(pan_speed_slider.get(), tilt_speed_slider.get())).grid(row=0,column=0)

# Pan and tilt buttons
Button(root, text='↑', width=3, bg=pan_tilt_color, command=lambda: c.pantilt('up', pan_speed_slider.get(), tilt_speed_slider.get())).grid(row=pan_tilt_row, column=pan_tilt_column+3)
Button(root, text='←', width=3, bg=pan_tilt_color, command=lambda: c.pantilt('left', pan_speed_slider.get(), tilt_speed_slider.get())).grid(row=pan_tilt_row+1, column=pan_tilt_column+2)
Button(root, text='→', width=3, bg=pan_tilt_color, command=lambda: c.pantilt('right', pan_speed_slider.get(), tilt_speed_slider.get())).grid(row=pan_tilt_row+1, column=pan_tilt_column+4)
Button(root, text='↓', width=3, bg=pan_tilt_color, command=lambda: c.pantilt('down', pan_speed_slider.get(), tilt_speed_slider.get())).grid(row=pan_tilt_row+2, column=pan_tilt_column+3)
Button(root, text='↖', width=3, bg=pan_tilt_color, command=lambda: c.pantilt('upleft', pan_speed_slider.get(), tilt_speed_slider.get())).grid(row=pan_tilt_row, column=pan_tilt_column+2)
Button(root, text='↗', width=3, bg=pan_tilt_color, command=lambda: c.pantilt('upright', pan_speed_slider.get(), tilt_speed_slider.get())).grid(row=pan_tilt_row, column=pan_tilt_column+4)
Button(root, text='↙', width=3, bg=pan_tilt_color, command=lambda: c.pantilt('downleft', pan_speed_slider.get(), tilt_speed_slider.get())).grid(row=pan_tilt_row+2, column=pan_tilt_column+2)
Button(root, text='↘', width=3, bg=pan_tilt_color, command=lambda: c.pantilt('downright', pan_speed_slider.get(), tilt_speed_slider.get())).grid(row=pan_tilt_row+2, column=pan_tilt_column+4)
Button(root, text='■', width=3, bg=pan_tilt_color, command=lambda: c.pantilt_stop()).grid(row=pan_tilt_row+1, column=pan_tilt_column+3)
#Button(root, text='Home', command=lambda: send_message(pan_home)).grid(row=pan_tilt_row+2, column=pan_tilt_column+1)

# Zoom buttons
Label(root, text='Zoom', bg=zoom_color, width=button_width).grid(row=zoom_row, column=zoom_column)
Button(root, text='In', bg=zoom_color, width=button_width, command=lambda: c.zoom_in()).grid(row=zoom_row+1, column=zoom_column)
Button(root, text='Stop', bg=zoom_color, width=button_width, command=lambda: c.zoom_stop()).grid(row=zoom_row+2, column=zoom_column)
Button(root, text='Out', bg=zoom_color, width=button_width, command=lambda: c.zoom_out()).grid(row=zoom_row+3, column=zoom_column)

# Focus buttons
Label(root, text='Focus', bg=focus_color, width=button_width).grid(row=focus_row, column=focus_column)
Button(root, text='Far', bg=focus_color, width=button_width, command=lambda: c.focus_far()).grid(row=focus_row+1, column=focus_column)
Button(root, text='Stop', bg=focus_color, width=button_width, command=lambda: c.focus_stop()).grid(row=focus_row+2, column=focus_column)
Button(root, text='Near', bg=focus_color, width=button_width, command=lambda: c.focus_near()).grid(row=focus_row+3, column=focus_column)
Button(root, text='Manual', bg=focus_color, width=button_width, command=lambda: c.focus_manual()).grid(row=focus_row+4, column=focus_column)
Button(root, text='One Push', bg=focus_color, width=button_width, command=lambda: c.focus_one_push()).grid(row=focus_row+5, column=focus_column)
Button(root, text='Auto', bg=focus_color, width=button_width, command=lambda: c.focus_auto()).grid(row=focus_row+6, column=focus_column)

# On off connect buttons
Label(root, text='Camera', bg=on_off_color, width=button_width).grid(row=on_off_row, column=on_off_column)
Button(root, text='On', bg=on_off_color, width=button_width, command=lambda: c.on()).grid(row=on_off_row+1, column=on_off_column)
Button(root, text='Connect', bg=on_off_color, width=button_width, command=lambda: c.connect()).grid(row=on_off_row+2, column=on_off_column)
Button(root, text='Off', bg=on_off_color, width=button_width, command=lambda: c.off()).grid(row=on_off_row+3, column=on_off_column)
Button(root, text='Info Off', bg=on_off_color, width=button_width, command=lambda: c.info_display_off()).grid(row=on_off_row+4, column=on_off_column)

# IP and Port entry
Label(root, text='Camera IP', width=button_width).grid(row=18, column=label_column-1)
ip_entry = Entry(root, textvariable=ip)
ip_entry.grid(row=18, column=label_column)
ip_entry.insert(0, ip)
Button(root, text='Save', command=lambda: save_ip_and_port()).grid(row=18, column=label_column+1)
Label(root, text='Port', width=button_width).grid(row=19, column=label_column-1)
port_entry = Entry(root, textvariable=port)
port_entry.grid(row=19, column=label_column)
port_entry.insert(0, port)
Button(root, text='Save', command=lambda: save_ip_and_port()).grid(row=19, column=label_column+1)

# IP Label
#Label(root, text=camera_ip+':'+str(camera_port)).grid(row=6, column=0, columnspan=3)
# Connection Label
#Label(root, textvariable=display_message).grid(row=6, column=4, columnspan=3)

root.mainloop()
#'''
