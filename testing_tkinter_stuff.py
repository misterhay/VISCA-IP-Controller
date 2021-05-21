from tkinter import Tk, StringVar, Button, Label, Entry, W

def changeLabel(text):
    #label0.destroy()
    #label0.set
    label0.set('Storing')
    button1.grid_forget()
    button2.grid(row=3, column=3)

def recall(x):
    print('recalled', x)
    #button1.grid_forget()
    #button2.grid(row=3, column=3)

def store(x):
    print('stored', x)
    label0.set('')
    button2.grid_forget()
    button1.grid(row=3, column=3)

root = Tk()

#for r in range(16):
#    Label(root, text=hex(r)[-1].upper()).grid(sticky=W, row=r+2, column=1)
#    Entry(root, text='testing').grid(row=r+2, column=1)

label0 = StringVar()
label0.set('start')
Label(root, textvariable=label0).grid(row=0, column=0)
button0 = Button(root, text='Store', command=lambda: changeLabel('hello'))
button0.grid(row=0, column=7)

button1 = Button(root, text='1', command=lambda: recall(1))
button1.grid(row=3, column=3)
button2 = Button(root, text='1', bg='red', command=lambda: store(1))

root.mainloop()

#for x in range(16):
#    print('label'+str(hex(x)[-1]).upper()+'.set(entry'+str(hex(x)[-1]).upper()+'.get())')