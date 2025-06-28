import tkinter as tk
from gui import MercariGUI

def main():
    root = tk.Tk()
    app = MercariGUI(master=root)
    app.mainloop()

if __name__ == "__main__":
    main()
