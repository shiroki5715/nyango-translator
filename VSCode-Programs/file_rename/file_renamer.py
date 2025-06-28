import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("File Renamer")
        self.grid()
        self.create_widgets()

    def create_widgets(self):
        self.directory_label = tk.Label(self, text="Directory:")
        self.directory_label.grid(row=0, column=0)

        self.directory_entry = tk.Entry(self)
        self.directory_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.browse_button = tk.Button(self, text="Select Folder", command=self.browse)
        self.browse_button.grid(row=0, column=2, padx=10, pady=10)

        self.rename_button = tk.Button(self, text="Rename Files", command=self.rename_files)
        self.rename_button.grid(row=1, column=0, padx=10, pady=10, columnspan=3)

        self.progress = ttk.Progressbar(self, length=400, mode='determinate')
        self.progress.grid(row=2, column=0, padx=10, pady=10, columnspan=3)

    def browse(self):
        self.directory_entry.delete(0, 'end')
        self.directory_entry.insert(0, filedialog.askdirectory())

    def rename_files(self):
        directory = self.directory_entry.get()
        files = os.listdir(directory)
        files.sort()

        self.progress['maximum'] = len(files)
        self.progress['value'] = 0

        for i, filename in enumerate(files, start=1):
            base, ext = os.path.splitext(filename)
            new_name = f"{base}_{i}{ext}"
            os.rename(os.path.join(directory, filename), os.path.join(directory, new_name))
            self.progress['value'] += 1
            self.master.update()

        messagebox.showinfo("Success", "Files renamed successfully")

root = tk.Tk()
app = Application(master=root)
app.mainloop()
