# import tkinter module
from tkinter import *
from tkinter import ttk

# creating main tkinter window/toplevel
root = Tk()
mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# this will create a label widget
l1 = Label(mainframe, text = "First:").grid(row = 0, column = 0, sticky = W, pady = 2)
l2 = Label(mainframe, text = "Secondjkhkjhkjh:").grid(row = 1, column = 0, sticky = W, pady = 2)

# entry widgets, used to take entry from user
e1 = Entry(mainframe).grid(row = 0, column = 1, pady = 2)
e2 = Entry(mainframe).grid(row = 1, column = 1, pady = 2)


# infinite loop which can be terminated by keyboard
# or mouse interrupt
mainloop()