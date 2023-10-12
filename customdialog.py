from tkinter import *

class _CustomDialog(Toplevel):
    def __init__(self, master, title, entry_labels: list):
        super().__init__(master=master, bg="blue")
        self.__e = entry_labels
        self.__mapped_vars = {}
        self.title(title)
        self.__comps = {}
        self.__init_comps()
        self.__bt_frame = Frame(self)
        self.__ok_bt = Button(self.__bt_frame, text="OK", command=self.__ok_bt, relief="raised")
        self.__ok_bt.pack(side=LEFT, padx=10, pady=10, fill=BOTH, ipadx=25)
        self.__cancel_bt = Button(self.__bt_frame, text="Cancel", command=self.destroy, relief="raised")
        self.__cancel_bt.pack(fill=BOTH, ipadx=25, padx=10, pady=10)
        self.__bt_frame.grid(row=len(self.__e), column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        self.values = None

    def __init_comps(self):
        for i, label in enumerate(self.__e):
            self.__mapped_vars[label] = StringVar()
            l = Label(self, text=label+":")
            l.grid(row=i, column=0)
            self.__comps[label] = Entry(self, textvariable=self.__mapped_vars[label])
            self.__comps[label].grid(row=i, column=1)

    def __ok_bt(self):
        values = {}
        for label in self.__mapped_vars:
            values[label] = self.__mapped_vars[label].get()
        self.values = values
        self.destroy()

def showdialog(master, title, entry_labels):
    c = _CustomDialog(master, title, entry_labels)
    c.wait_window()
    return c.values


