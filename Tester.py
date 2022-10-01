import tkinter as tk
from tkinter import ttk
import random
import customwidgets as cw
import hashlib


def hash_(string):
    hash1 = hashlib.md5(string.encode('utf-8'))
    return hash1.hexdigest()


class TestWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.scrolled_frame = cw.ScrolledFrame(self)
        self.scrolled_frame.propagate(False)
        self.table = cw.IndividualTable(self.scrolled_frame.interior)
        self.table.enable_selection()
        self.table.add_selection_command(self.testing)
        self.table.grid(row=0, column=0)
        self.scrolled_frame.grid(row=0, column=0, sticky="nsew")

    def testing(self):
        print(self.table.get_selected_tile())


if __name__ == '__main__':
    print(hash_("94340"))
    window = TestWindow()
    window.mainloop()
