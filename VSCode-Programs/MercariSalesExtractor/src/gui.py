import tkinter as tk
from scraper import scrape_mercari_sales

class MercariGUI(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.username_label = tk.Label(self, text="Username:")
        self.username_label.pack()
        self.username_entry = tk.Entry(self)
        self.username_entry.pack()

        self.password_label = tk.Label(self, text="Password:")
        self.password_label.pack()
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack()

        self.scrape_button = tk.Button(self, text="Scrape Sales", command=self.scrape_sales)
        self.scrape_button.pack()

    def scrape_sales(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        scrape_mercari_sales(username, password)
