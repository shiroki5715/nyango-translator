import tkinter as tk
from tkinter import filedialog, messagebox

def upload_item():
    # ここでAPIを呼び出す
    # e.g., mercari_api.upload(item_info), paypay_api.upload(item_info)
    messagebox.showinfo('Info', 'Item uploaded successfully')

root = tk.Tk()
root.title('Mercari and PayPay Uploader')

item_info_frame = tk.LabelFrame(root, text='Item Info')
item_info_frame.pack(fill='both', expand='yes')

item_name_label = tk.Label(item_info_frame, text='Item Name:')
item_name_label.pack(side='left')
item_name_entry = tk.Entry(item_info_frame)
item_name_entry.pack(side='right')

upload_button = tk.Button(root, text='Upload Item', command=upload_item)
upload_button.pack()

root.mainloop()
