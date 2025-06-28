import tkinter as tk
from tkinterdnd2 import TkinterDnD

def drop(event):
    filepath = event.data
    print(f"Dropped file: {filepath}")

root = TkinterDnD.Tk()
root.drop_target_register('DND_Files')
root.dnd_bind('<<Drop>>', drop)

root.mainloop()
