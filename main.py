import tkinter as tk
from tkinter import simpledialog
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
import customdialog
import sqlite3 as s3
import datetime
import csv
import os
#import time


_COLOR="#0071FF"
_BT_COLOR="#777799"
_ADMIN_KEY="PHY@1881@"
_con = s3.connect("ims.db")
_con.executescript("""
         CREATE TABLE IF NOT EXISTS logger (Instrument_name TEXT, Acquisition_no TEXT, date TEXT, time TEXT, user_name TEXT, user_id TEXT, action TEXT);
         CREATE TABLE IF NOT EXISTS login_info (user_id TEXT PRIMARY KEY, username TEXT, password TEXT, tag TEXT);
         CREATE TABLE IF NOT EXISTS acquisition_reg (particulars TEXT, acquisition_no TEXT PRIMARY KEY, stock_f_no TEXT, grant TEXT, supply_invoice_no TEXT, cost TEXT, cost_plus_gst TEXT, remarks TEXT,condition TEXT, description TEXT, date TEXT, time TEXT, status TEXT);
         CREATE TABLE IF NOT EXISTS student_list (student_id TEXT PRIMARY KEY, student_name TEXT);
         CREATE TABLE IF NOT EXISTS lab_log (student_id TEXT PRIMARY KEY, instruments TEXT, acquisition_nos TEXT, incharge TEXT, FOREIGN KEY (student_id) REFERENCES student_list(student_id));
         CREATE TABLE IF NOT EXISTS lab_logger (student_id TEXT, instruments TEXT, acquisition_nos TEXT, incharge TEXT, date TEXT, time TEXT);
         """)
_con.commit()

def _get_date_time():
   current_datetime = datetime.datetime.now()
   current_hour = current_datetime.hour
   current_minute = current_datetime.minute
   current_second = current_datetime.second
   current_date = current_datetime.date()
   formatted_time = f"{current_hour:02d}-{current_minute:02d}-{current_second:02d}"
   formatted_date = f"{current_date:%Y-%m-%d}"
   return formatted_time, formatted_date
   
def _on_arrow_up(master, entry_widgets, e):
   current_widget = master.focus_get()
   if current_widget in entry_widgets:
      current_index = entry_widgets.index(current_widget)
      previous_index = (current_index - 1)%len(entry_widgets)
      entry_widgets[previous_index].focus_set()
   
def _on_arrow_down(master, entry_widgets, e):
   current_widget = master.focus_get()
   if current_widget in entry_widgets:
      current_index = entry_widgets.index(current_widget)
      next_index = (current_index + 1)%len(entry_widgets)
      entry_widgets[next_index].focus_set()

class _AddInstruments(tk.Toplevel):
   def __init__(self, master, next_to):
      super().__init__(master, next_to,relief="solid", highlightbackground="#12FF00", highlightthickness=2)
      self.__master = master
      self.__next_to=next_to
      self.__fr = tk.Frame(self, bg=_COLOR, bd=3, highlightbackground="black", highlightthickness=3)
      self.__particulars=tk.StringVar()
      self.__acq_no=tk.StringVar()
      self.__stock_no=tk.StringVar()
      self.__grant=tk.StringVar()
      self.__sply=tk.StringVar()
      self.__cost=tk.StringVar()
      self.__cost_plus_gst=tk.StringVar()
      self.__remarks=tk.StringVar()
      self.__working=tk.IntVar()
      self.__not_working=tk.IntVar()
      self.__description=tk.StringVar()
      self.__condition_text=None
      self.__welcome_label = tk.Label(self, text="Add Instruments", font=("Arial", 28, "bold italic"), anchor="center", bg="black", fg="white", highlightbackground="red", highlightthickness=4, relief="raised")
      self.__welcome_label.pack(padx=2, pady=10)
      self.__particulars_label,self.__particulars_entry = self.__create_label_and_entry("Particulars", self.__particulars, 1, 0, 1, 1)
      self.__acq_no_label,self.__acq_no_entry=self.__create_label_and_entry("Acquisition No.", self.__acq_no, 2, 0, 2, 1)
      self.__stock_no_label,self.__stock_no_entry=self.__create_label_and_entry("Stock F.No.", self.__stock_no, 3, 0, 3, 1)
      self.__grant_label, self.__grant_entry=self.__create_label_and_entry("Grant", self.__grant, 4, 0, 4, 1)
      self.__sply_label, self.__sply_entry=self.__create_label_and_entry("Suppliers Invoice No.", self.__sply, 5, 0, 5, 1)
      self.__cost_label, self.__cost_entry=self.__create_label_and_entry("Cost",self.__cost, 6, 0, 6, 1)
      self.__cost_plus_gst_label, self.__cost_plus_gst_entry=self.__create_label_and_entry("Cost (+GST)",self.__cost_plus_gst, 7, 0, 7, 1)
      self.__remarks_label, self.__remarks_entry=self.__create_label_and_entry("Remarks", self.__remarks, 8, 0, 8, 1)
      self.__vars=[self.__particulars, self.__acq_no, self.__stock_no, self.__grant, self.__sply, self.__cost, self.__cost_plus_gst, self.__remarks]
      self.__instrument_condition=tk.Label(self.__fr, text="Condition", font=("Arial", 15, "bold italic"), bg=_COLOR)
      self.__instrument_condition.grid(row=9, column=0, padx=2, pady=10, sticky="e")
      self.__working_checkbox=tk.Checkbutton(self.__fr, text="working", variable=self.__working, command=self._working_checkbox_clicked)
      self.__working_checkbox.grid(row=9, column=1, padx=2)
      self.__not_working_checkbox = tk.Checkbutton(self.__fr, text="not working", variable=self.__not_working, command=self._not_working_checkbox_clicked)
      self.__not_working_checkbox.grid(row=9, column=2, padx=2)
      self.__description_label,self.__description_entry=self.__create_label_and_entry("Description", self.__description, 10, 0, 10, 1)
      self.__add_button = tk.Button(self.__fr, text="Add", font=("Arial", 15, "bold italic"), command=self._add, state="disabled")
      self.__add_button.grid(row=11, column=0,  pady=2, padx=2, columnspan=3, sticky="ew")
      self.__fr.bind("<Enter>", lambda e:self.__add_button.config(state="normal"))
      self.__fr.bind("<Leave>", lambda e:self.__add_button.config(state="disabled"))
      self.entry_widgets=[self.__particulars_entry, self.__acq_no_entry, self.__stock_no_entry, self.__grant_entry, self.__sply_entry, self.__cost_entry,self.__cost_plus_gst_entry, self.__remarks_entry]
      self.__fr.pack()
      self.bind("<Up>", lambda e:_on_arrow_up(master, self.entry_widgets, e))
      self.bind("<Down>", lambda e:_on_arrow_down(master, self.entry_widgets, e))
      self.protocol("WM_DELETE_WINDOW", self.__on_close)
      
   def _add(self):
      all_ok=False
      for i in self.__vars:
         if i.get()=="":
            all_ok=False
            break
         else:all_ok=True
         
      if all_ok and self.__working.get()==1 or self.__not_working.get()==1:
         time, date=_get_date_time()
         try:
            _con.execute("INSERT INTO acquisition_reg (particulars, acquisition_no, stock_f_no, grant, supply_invoice_no, cost, cost_plus_gst, remarks, condition, description, date, time, status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?, 'working')",(self.__particulars.get(), self.__acq_no.get(), self.__stock_no.get(), self.__grant.get(), self.__sply.get(), self.__cost.get(), self.__cost_plus_gst.get(), self.__remarks.get(), self.__condition_text, self.__description.get(), str(date), str(time)))
            _con.execute("INSERT INTO logger (Instrument_name, Acquisition_no, date, time, user_name, user_id, action) VALUES (?,?,?,?,?,?,?)", (self.__particulars.get(),self.__acq_no.get(),str(date),str(time),self.__next_to.getUser()[2],self.__next_to.getUser()[0],'added'))
            _con.commit()
            messagebox.showinfo("Action", "Successfully added")
            self.__next_to.getInstrumentsDisplay()["values"] = self.__next_to.arrange_elements()
            for entry in self.entry_widgets:
               entry.delete(0, "end")
         except sqlite3.IntegrityError:messagebox.showinfo("Insertion failed", "Data already exists!")
      elif not all_ok:messagebox.showinfo("Entry filling", "Fill all the entries")
      else:pass
      
   def _working_checkbox_clicked(self):
      if self.__working.get()==1:self.__not_working.set(0)
      self.__condition_text="working"
      self.__description_entry.config(state="disabled")
   
   def _not_working_checkbox_clicked(self):
      if self.__not_working.get()==1:self.__working.set(0)
      self.__condition_text="not working"
      self.__description_entry.config(state="normal")
   
   def __on_close(self):
      self.__next_to.rebind_events()
      self.destroy()
   
   def __create_label_and_entry(self, label_text, entry_textvariable, label_row, label_column, entry_row, entry_column):
      label = tk.Label(self.__fr, text=label_text, font=("Arial", 15, "bold italic"), bg=_COLOR, fg="black")
      label.grid(row=label_row, column=label_column, padx=2, pady=5, sticky="e")
      entry = tk.Entry(self.__fr, font=("Arial", 15), textvariable=entry_textvariable)
      entry.grid(row=entry_row, column=entry_column, padx=2, sticky="w", columnspan=2)
      return label, entry
      
class _ModifyCondition(tk.Toplevel):
   def __init__(self, master, next_to, instmt_tag, tag):
      super().__init__(master, next_to, relief="solid",highlightbackground="#12FF00", highlightthickness=2)
      self.title("Modifying window")
      self.__instmt_tag=instmt_tag
      self.__working=tk.IntVar()
      self.__not_working=tk.IntVar()
      self.__description=tk.StringVar()
      self.config(background=_COLOR)
      self.__master = master
      self.__next_to=next_to
      self.__instrument_name=None
      try:
         self.__instrument_name=_con.execute("SELECT particulars FROM acquisition_reg WHERE Acquisition_no='"+instmt_tag+"';").fetchone()[0]
      except TypeError:
         messagebox.showerror("", "Unknown instrument tag")
      self.__instrument_name_label = tk.Label(self, text="Instrument name: "+self.__instrument_name, font=("Arial", 15, "italic"), bg=_COLOR, fg="white")
      self.__instrument_name_label.grid(row=0, column=0, columnspan=3,padx=5)
      self.__instrument_tag_label = tk.Label(self, text="Acquisition no.: "+instmt_tag, font=("Arial", 15, "italic"), bg=_COLOR, fg="white")
      self.__instrument_tag_label.grid(row=1, column=0, columnspan=3, pady=2)
      self.__instrument_con_label=tk.Label(self, text="Instrument Condition: "+self.__instrument_name, font=("Arial", 15, "italic"), bg=_COLOR, fg="white")
      self.__condition_label = tk.Label(self, text="condition", font=("Arial", 15, "bold italic"), bg=_COLOR, fg="white")
      self.__condition_label.grid(row=2, column=0, padx=20, pady=40)
      self.__working_checkbox = tk.Checkbutton(self, font=("Arial Bold", 10), variable=self.__working, command=self.__working_checkbox_clicked, text="working")
      self.__working_checkbox.grid(row=2, column=1, padx=10)
      self.__not_working_checkbox = tk.Checkbutton(self, font=("Arial Bold", 10), variable=self.__not_working, command=self.__not_working_checkbox_clicked, text="not working")
      self.__not_working_checkbox.grid(row=2, column=2, padx=10)
      self.__description_label = tk.Label(self, text="description", font=("Arial", 15, "bold italic"), bg=_COLOR, fg="white")
      self.__description_label.grid(row=3, column=0, pady=10)
      self.__description_entry = tk.Entry(self, font=("Arial Bold", 10), textvariable=self.__description)
      self.__description_entry.grid(row=3, column=1, columnspan=2)
      self.__modifyBt = tk.Button(self, text="modify", command=self.__change_condition, state="disabled")
      self.__modifyBt.grid(row=4, column=0, columnspan=3, padx=20, pady=20)
      if tag=="assitant":self.__working_checkbox.config(state="disabled")
      self.bind("<Enter>", lambda e:self.__modifyBt.config(state="normal"))
      self.bind("<Leave>", lambda e:self.__modifyBt.config(state="disabled"))
      self.protocol("WM_DELETE_WINDOW", self.__on_close)

   def __change_condition(self):
      condition_text=""
      description_text=self.__description.get()
      if self.__not_working.get() or self.__working.get():
         if self.__not_working.get()==1:condition_text="not working"
         if self.__working.get()==1:condition_text="working"
         _con.execute("UPDATE acquisition_reg SET condition='"+condition_text+"', description='"+description_text+"' WHERE Acquisition_no='"+self.__instmt_tag+"';")
         _con.commit()
         self.__modifyBt.config(state="disabled")
         self.__next_to.rebind_events()
         time, date=_get_date_time()
         _con.execute("INSERT INTO logger (Instrument_name, Acquisition_no, date, time, user_name, user_id, action) VALUES ('"+self.__instrument_name+"','"+self.__instmt_tag+"','"+str(date)+"','"+str(time)+"','"+self.__next_to.getUser()[2]+"','"+self.__next_to.getUser()[0]+"','changed to "+condition_text+"');")
         _con.commit()
         messagebox.showinfo("Action", "modified successfully")
         self.destroy()
         
   def __working_checkbox_clicked(self):
      if self.__working.get()==1:self.__not_working.set(0)
      self.__description_entry.config(state="disabled")
   
   def __not_working_checkbox_clicked(self):
      if self.__not_working.get()==1:self.__working.set(0)
      self.__description_entry.config(state="normal")
    
   def __on_close(self):
      self.__next_to.rebind_events()
      self.destroy()

class _ProfileWindow(tk.Toplevel):
   def __init__(self, master, userid):
      super().__init__(master)
      self.__user = _con.execute("SELECT * FROM login_info WHERE user_id='"+userid+"';").fetchone()
      self.__usrname_lbl = tk.Label(self, text="username:", font=("Arial", 15, "bold italic"), bd=2, highlightbackground="red")
      self.__usrname_lbl.grid(row=0, column=0, pady=5, sticky="e")
      self.__usrname = tk.Label(self, text=str(self.__user[1]), font=("Arial", 15, "bold italic"), bd=2, highlightbackground="red")
      self.__usrname.grid(row=0, column=1, pady=5, sticky="w")
      self.__usrid_lbl = tk.Label(self, text="user ID: "+self.__user[0], font=("Arial", 15, "bold italic"), bd=2, highlightbackground="red")
      self.__usrid_lbl.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
      self.__pw_lbl = tk.Label(self, text="Password:", font=("Arial", 15, "bold italic"), bd=2, highlightbackground="red")
      self.__pw_lbl.grid(row=2, column=0, pady=5, sticky="e")
      self.__pw = tk.Label(self, text=str(self.__user[2]), font=("Arial", 15, "bold italic"), bd=2, highlightbackground="red")
      self.__pw.grid(row=2, column=1, pady=5, sticky="w")
      self.__chg_pass_bt = tk.Button(self, text="Change Password", font=("Arial", 15, "bold italic"), bd=2, highlightbackground="red", command=self.__chg_pw_bt)
      self.__chg_pass_bt.grid(row=3, column=0, sticky="s")
      self.__chg_username_bt = tk.Button(self, text="Change Username",font=("Arial", 15, "bold italic"), bd=2, highlightbackground="red", command=self.__chg_usrname_bt)
      self.__chg_username_bt.grid(row=3, column=1, sticky="s")
      self.mainloop()
   
   def __chg_pw_bt(self):
      result = simpledialog.askstring("Password change", "Enter the new Password")
      _con.execute("UPDATE login_info SET password='"+result+"' WHERE user_id='"+self.__user[0]+"';")
      _con.commit()
      self.__pw["text"]=_con.execute("SELECT password FROM login_info WHERE user_id='"+self.__user[0]+"';").fetchone()[0]
   
   def __chg_usrname_bt(self):
      result = simpledialog.askstring("Username change", "Enter new username")
      _con.execute("UPDATE login_info SET username='"+result+"' WHERE user_id='"+self.__user[0]+"';")
      _con.commit()
      self.__usrname["text"]=_con.execute("SELECT username FROM login_info WHERE user_id='"+self.__user[0]+"';").fetchone()[0]

class _CheckboxTreeview(ttk.Treeview):
    def __init__(self, *args, **kwargs):
        ttk.Treeview.__init__(self, *args, **kwargs)
        self.tag_configure('unchecked', image='')
        self.tag_configure('checked', image='checkmark')
        self.new_state=""
        self.__col=None
        self.__col_no=None
        self.bind('<Button-3>', self._on_checkbox_click)

    def _on_checkbox_click(self, event):
        item = self.selection()
        column = self.identify_column(event.x)
        if column == self.__col:
            try:
               current_state = self.item(item[0], 'values')[self.__col_no]
               if current_state == '\u2610':
                  self.new_state = '\u2611'  
               elif current_state == '\u2611':
                  self.new_state = '\u2610'
               elif current_state == 'issued':self.new_state = 'issued'
               elif current_state == 'returned':self.new_state='returned'
               elif current_state == '\u2612':self.new_state='\u2612'
               self.set(item, self.__col, self.new_state)
               self.item(item, tags=self.new_state)
            except IndexError:pass
            
    def setColumn(self, col):self.__col=col
    def setColumnNo(self, n):self.__col_no=n

class _ViewLabLog(tk.Toplevel):
   def __init__(self, master, std_id:str, incharge:str, *args, **kwargs):
      super().__init__(master, *args, **kwargs)
      self.__std_id=std_id
      self.__incharge=incharge
      self.title("Lab instruments log window")
      self.__fr = tk.Frame(self, bg=_COLOR, highlightbackground="black", highlightthickness=2, relief="solid")
      self.__std_id_label = tk.Label(self.__fr, bg="black", fg="white", relief="sunken", highlightthickness=2, text="Student ID:"+std_id, font=("Arial", 15, "bold italic"), highlightbackground="red")
      self.__std_id_label.grid(row=0, column=0, padx=5)
      self.__std_name_label = tk.Label(self.__fr, bg=_COLOR, fg="white",relief="sunken", highlightthickness=2,font=("Arial", 15, "bold italic"), text="Student Name:"+_con.execute("SELECT student_name FROM student_list WHERE student_id='"+std_id+"';").fetchone()[0], highlightbackground="red")
      self.__std_name_label.grid(row=0, column=1, padx=5)
      self.__instruments=_CheckboxTreeview(self.__fr, column=("sno", "inst", "acq", "slct"), show="headings")
      self.__instruments.setColumn("#4")
      self.__instruments.setColumnNo(3)
      self.__instruments.column("sno", width=30)
      self.__instruments.heading("sno", text="S.No")
      self.__instruments.column("inst", width=100)
      self.__instruments.heading("inst", text="Instrument")
      self.__instruments.column("acq", width=120)
      self.__instruments.heading("acq", text="Acquisition No.")
      self.__instruments.column("slct", width=80)
      self.__instruments.heading("slct", text="Select")
      self.__instruments.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
      self.__return_bt = tk.Button(self.__fr, text="Return", relief="solid", highlightthickness=2, font=("Helvitica", 15, "bold italic"), command=self.__return_bt_fun, bg=_BT_COLOR)
      self.__return_bt.grid(row=2, column=1, padx=5, pady=5, sticky="e")
      self.__fr.pack()
      self.__display_content()
   
   def __display_content(self):
      instmts=_con.execute("SELECT instruments, acquisition_nos FROM lab_log WHERE student_id='"+self.__std_id+"';").fetchall()
      sts = _con.execute(f"SELECT status FROM acquisition_reg WHERE Acquisition_no IN ({','.join(['?' for i in range(len(instmts[0][0].split(',')))])});", (instmts[0][1].split(","))).fetchall()
      sts = ["\u2610" for i in sts]
      for i,j,k,l in zip(range(len(sts)),instmts[0][0].split(","), instmts[0][1].split(","), sts):
         self.__instruments.insert("", "end", i, values=(str(i+1), j,k,l))
  
   def __return_bt_fun(self):
      eles = self.__instruments.get_children()
      instms = {}
      instms["instrument"] = []
      instms["acquisition_no"] = []
      instms["instrument_rem"] = _con.execute("SELECT instruments FROM lab_log WHERE student_id='"+self.__std_id+"';").fetchone()[0].split(",")
      instms["acquisition_no_rem"] = _con.execute("SELECT acquisition_nos FROM lab_log WHERE student_id='"+self.__std_id+"';").fetchone()[0].split(",")
      time, date=_get_date_time()
      for ele in eles:
         v= self.__instruments.item(ele, "values")
         if v[3] == "\u2611":
            instms["instrument"].append(v[1])
            instms["acquisition_no"].append(v[2])
            self.__instruments.new_state="returned"
            self.__instruments.set(ele, "#4", "returned")
            _con.execute("UPDATE acquisition_reg SET status=? WHERE acquisition_no=?;", ("",v[2]))
      for i,j in zip(instms["instrument"], instms["acquisition_no"]):
         instms["instrument_rem"].remove(i)
         instms["acquisition_no_rem"].remove(j)
      if len(instms["instrument_rem"])==0:_con.execute("DELETE FROM lab_log WHERE student_id=?;", (self.__std_id,))
      else:_con.execute("UPDATE lab_log SET instruments=?, acquisition_nos=? WHERE student_id=?;", (", ".join(instms["instrument_rem"]), ",".join(instms["acquisition_no_rem"]), self.__std_id))
      _con.execute("INSERT INTO lab_logger (student_id, instruments, acquisition_nos, incharge, date, time) VALUES (?,?,?,?,?,?);", (self.__std_id, ",".join(instms["instrument"]), ",".join(instms["acquisition_no"]),self.__incharge, str(date), str(time)))
      _con.commit()
      messagebox.showinfo("", "successfully returned")
      instms = None
      

class _ShowInstruments(tk.Frame):
   __CLM=["S", "dt","In","Ac", "sfn", "gr", "sin", "cst", "cpg", "con", "slc"]
   __CLM_HD=["S.No.", "Date" , "Instrument name","Acquisition no.", "Stock F.No.", "Grant", "Supply Invoice No.", "Cost", "Cost+(GST)", "Condition", "Select"]
   def __init__(self, master, user):
      super().__init__(master=master, background=_COLOR, relief="solid",highlightbackground="#12FF00", highlightthickness=2)
      self.pack(expand=True, side=tk.LEFT, padx=2, pady=2)
      self.__modify_window = None
      self.__welcome_label = tk.Label(self, text="IMS Instruments View Portal ", font=("Arial", 30, "bold italic"), anchor="center", bg="black", fg="white", highlightbackground="red", highlightthickness=4)
      self.__welcome_label.grid(row=0, column=0, columnspan=4, pady=20,  sticky="ew", padx=10)
      self.__inst = tk.StringVar()
      self.__user=user
      self.__std_id=tk.StringVar();
      self.__menubar = tk.Menu(self)
      self.__options = self.arrange_elements()
      file_menu = tk.Menu(self.__menubar, tearoff=0)
      get_acq_reg_menu=tk.Menu(file_menu, tearoff=0)
      file_menu.add_cascade(label="get acquisition reg", menu=get_acq_reg_menu)
      get_acq_reg_menu.add_command(label="Export as .csv", command=lambda:self.__export_as_csv(data_of_which="Acquisition reg"))
      get_log_menu = tk.Menu(file_menu, tearoff=0)
      file_menu.add_cascade(label="log", menu=get_log_menu)
      get_log_menu.add_command(label="Export log as .csv", command=lambda:self.__export_as_csv(data_of_which="log"))
      get_log_menu.add_command(label="Export lab log as .csv", command=lambda:self.__export_as_csv(data_of_which="lab_logger"))
      add_instrument_menu = tk.Menu(file_menu, tearoff=0)
      add_instrument_menu.add_command(label="Add Instrument data", command=self.__check_admin_key)
      file_menu.add_cascade(label="Add instrument", menu=add_instrument_menu)
      file_menu.add_command(label="Exit", command=self.__exit_fn)
      self.__menubar.add_cascade(label="File", menu=file_menu)
      profile_menu = tk.Menu(self, tearoff=0)
      profile_menu.add_command(label="view profile", command=self.__open_profile_window)
      profile_menu.add_command(label="Change Admin Key", command=self.__chg_admin_key)
      self.__menubar.add_cascade(label="profile", menu=profile_menu)
      student_menu = tk.Menu(self, tearoff=0)
      student_menu.add_command(label="Get student list", command=lambda:self.__export_as_csv(data_of_which="student_list"))
      student_menu.add_command(label="Change student name", command=lambda:self.__modify_student(action="change"))
      student_menu.add_command(label="Add student", command=lambda:self.__modify_student(action="add"))
      student_menu.add_command(label="Delete student", command=lambda:self.__modify_student(action="delete"))
      self.__menubar.add_cascade(label="Student", menu=student_menu)
      master.config(menu=self.__menubar)
      self.__stock = tk.Label(self, anchor="center", font=("Arial", 15, "bold italic"), bg=_COLOR)
      self.__stock.grid(row=3, column=3)
      self.__usr_msg = tk.Label(self, bg=_COLOR)
      self.__usr_msg.grid(row=1,column=2, rowspan=2, columnspan=2)
      self.__std_id_label = tk.Label(self, text="Student ID:", font=("Helvetica", 15, "bold italic"), bg=_COLOR)
      self.__std_id_label.grid(row=1, column=0, sticky="e")
      self.__std_id_entry = tk.Entry(self, font=("Helvetica", 10, "bold italic"), textvariable=self.__std_id)
      self.__std_id_entry.grid(row=1, column=1, sticky="w")
      self.__instrument_select_label = tk.Label(self, text="Select Instruments", font=("Helvetica", 20, "bold italic"), bg=_COLOR)
      self.__instrument_select_label.grid(row=3, column=1, padx=30, sticky="e")
      self.__instrumentsDisplay = ttk.Combobox(self, width=30, textvariable=self.__inst)
      self.__instrumentsDisplay["values"] = self.__options
      self.__instrumentsDisplay.grid(row=3, column=2, pady=20, sticky="ew")
      self.__inst.trace("w", self.__checkKey)
      self.__instruments = _CheckboxTreeview(self, columns=tuple(self.__CLM), show="headings")
      self.__instruments.setColumn("#11")
      self.__instruments.setColumnNo(10)
      self.__create_clmns(self.__CLM_HD, self.__CLM)
      self.__instruments.grid(row=4,column=0, columnspan=4)
      self.__Button = tk.Button(self, text="Log out", command=self.click, font=("Arial", 14, "bold italic"), bg=_BT_COLOR, relief="raised", highlightbackground="#888880", highlightthickness=1, bd=2, fg="white")
      self.__Button.grid(row=5, column=0, pady=30, padx=10, sticky="w")
      self.__view_issued_bt = tk.Button(self, text="issued history",  font=("Arial", 14, "bold italic"), relief="raised", highlightbackground="#888880", highlightthickness=1, bg=_BT_COLOR, bd=2, fg="white", command=self.issued_bt_fun)
      self.__view_issued_bt.grid(row=5, column=1, padx=10)
      self.__issue_bt = tk.Button(self, text="issue", font=("Arial", 14, "bold italic"), relief="raised", highlightbackground="#888880", highlightthickness=1, command=self.__issue_bt_fn, bg=_BT_COLOR, bd=2, fg="white")
      self.__issue_bt.grid(row=5, column=2, padx=10)
      self.__view_bt = tk.Button(self, text="view",  font=("Arial", 14, "bold italic"), relief="raised", highlightbackground="#888880", highlightthickness=1, command=self.__view_bt_fn, bg=_BT_COLOR, bd=2, fg="white")
      self.__view_bt.grid(row=5, column=3, padx=5)
      self.center_treeview_columns()
      self.__master = master
      self.__instrumentsDisplay.bind("<<ComboboxSelected>>",lambda e: self.on_combobox_select(e))
      self.__instruments.bind("<ButtonRelease-1>", lambda e:self.select_content(e))
      self.__master.bind("<Alt-a>", lambda e:self.__show_all(e))
      self.__list_of_instruments=self.__options
      self.__master.protocol("WM_DELETE_WINDOW", lambda:messagebox.showinfo("", "You cannot close, until you log out!"))
      self.__master.unbind("<Return>")
      self.__usr_msg_blink(0)
      
   
   class ViewIssued(tk.Toplevel):
      def __init__(self,master):
         super().__init__(master)
         self.grab_set()
         self.__lb = ttk.Treeview(self, columns=("sn", "ins", "acq", "iss"), show="headings")
         self.__lb.column("sn", width=50)
         self.__lb.heading("sn", text="S.No")
         self.__lb.column("ins", width=130)
         self.__lb.heading("ins", text="Instrument")
         self.__lb.column("acq", width=140)
         self.__lb.heading("acq", text="Acquisition No")
         self.__lb.column("iss", width=140)
         self.__lb.heading("iss", text="Issued to")
         self.__lb.pack()
         self._fill_data()
      
      def _fill_data(self):
         for i,data in enumerate(_con.execute("SELECT  acquisition_nos, instruments, student_id FROM lab_log;")):
            values=[str(i+1)]
            for column in data:
               values.append(column)
            self.__lb.insert("", "end", values=tuple(values))
            values=None
            
         
   def __modify_student(self, action=None):
      dialog=None
      try:
         if action=="change":
            dialog = customdialog.showdialog(self, "Change Student Name",["Student Id", "New name"])
            _con.execute("UPDATE student_list SET student_name=? WHERE student_id=?;", (str(dialog["Student Id"]), str(dialog["New name"]),))
         elif action=="add":
            dialog = customdialog.showdialog(self, "Add Student", ["Student Id", "Student Name"])
            _con.execute("INSERT INTO student_list (student_id, student_name) VALUES (?,?);", (str(dialog["Student Id"]), str(dialog["Student Name"])))
         elif action=="delete":
            dialog = customdialog.showdialog(self, "Delete Student", ["Student Id"])
            _con.execute("DELETE FROM student_list WHERE student_id=?;", (str(dialog["Student Id"]),))
      except s3.IntegrityError:messagebox.showerror("Error", "Student details already entered!!")
      except TypeError:pass
      finally:_con.commit()
   
   """
   For checking How many toplevel windows are opened. It will print how many windows are opened after every second
   This is commented.
   """
   #def __print_opened(self, n):
   #   self.__top = [w for w in self.__master.winfo_children() if isinstance(w, tk.Toplevel)]
   #   if n:
   #      print(self.__top)
   #      n=False
   #   else:n=True
   #   self.after(1000, lambda:self.__print_opened(True))
         
     

   def issued_bt_fun(self):
      w = self.ViewIssued(self.__master)
      
   def __exit_fn(self):
      if messagebox.askyesno("Exit Request", "Are you really want to quit?"):self.__master.destroy()
      
   def __open_profile_window(self):
      pr_win=_ProfileWindow(self.__master, self.__user[0])
   
   def __issue_bt_fn(self):
      try:
         if int(_con.execute("SELECT COUNT(*) FROM student_list WHERE student_id='"+self.__std_id.get()+"';").fetchone()[0])==1:
            eles = self.__instruments.get_children()
            instms = {}
            instms["instrument"] = []
            instms["acquisition_no"] = []
            time, date = _get_date_time()
            for ele in eles:
               v= self.__instruments.item(ele, "values")
               if v[10] == "\u2611":
                  instms["instrument"].append(v[2])
                  instms["acquisition_no"].append(v[3])
                  self.__instruments.new_state="issued"
                  self.__instruments.set(ele, "#11", "issued")
                  _con.execute("UPDATE acquisition_reg SET status=? WHERE acquisition_no=?;", ("issued",v[3]))
            _con.execute("REPLACE INTO lab_log (student_id, instruments, acquisition_nos, incharge) VALUES (?,?,?,?);", (self.__std_id.get(), ",".join(instms["instrument"]), ",".join(instms["acquisition_no"]),self.__user[1]))
            _con.execute("INSERT INTO lab_logger (student_id, instruments, acquisition_nos, incharge, date, time) VALUES (?,?,?,?,?,?);", (self.__std_id.get(), ",".join(instms["instrument"]), ",".join(instms["acquisition_no"]),self.__user[1], str(date), str(time)))
            _con.commit()
            messagebox.showinfo("Issue report", "successfully issued")
            instms = None
         else:
            messagebox.showinfo("Empty Entry", "enter the student id")
            self.__std_id_entry.focus_set()
      except TypeError:
         messagebox.showerror("invalid access", "invalid student ID or unregistered student ID")
  
   
   def __view_bt_fn(self):
      if int(_con.execute("SELECT COUNT(*) FROM student_list WHERE student_id='"+self.__std_id.get()+"';").fetchone()[0])==1:
         lab_log = _ViewLabLog(self.__master, self.__std_id.get(), self.__user[1])
          
   def __show_all(self, e):
      self.__show()
   
   def __show(self):
      self.__erase_treeview_data()
      self.__stock.config(text="total: "+str(_con.execute("SELECT COUNT(*) FROM acquisition_reg;").fetchone()[0]))
      for i,j in enumerate(_con.execute("SELECT * FROM acquisition_reg;")):
         j=list(j)
         if str(j[12])!="issued" and str(j[8])=="working":j[12]="\u2610"
         else:j[12]="\u2612"
         self.__instruments.insert("", "end", i,values=(str(i+1), j[10], j[0], j[1], j[2], j[3], j[4], j[5], j[6], j[8], j[12]))
      
   def __create_clmns(self, clmn_heading, clms):
      for i,j in zip(clms,clmn_heading):
         self.__instruments.column(i, width=len(j)*10 +10)
         self.__instruments.heading(i, text=j)
   
   def arrange_elements(self):
      original_list = _con.execute("SELECT particulars FROM acquisition_reg").fetchall()
      ordered_list=[]
      for i in original_list:
         ordered_list.append(str(i[0]))
      return tuple(set(sorted(ordered_list)))
   
   def __check_admin_key(self):
      if self.__user[3]=="admin":
         rslt = simpledialog.askstring("Admin request", "Enter Admin Key")
         if rslt==_ADMIN_KEY:
            self.__add_instrument_button_func()
      else:messagebox.showerror("Admin only access","User must be an admin")
      
   def __add_instrument_button_func(self):
      add_instruments_window=_AddInstruments(self.__master, self)
      self.__Button.config(state="disabled")
      self.__instruments.unbind("<ButtonRelease-1>")
      self.__instrumentsDisplay.unbind("<<ComboboxSelected>>")
      
      
   def click(self):
      if messagebox.askyesno("log out request", "Are you sure want to log out?"):
         self.destroy()
         lp = _LoginPage(self.__master)
         
   
   def __checkKey(self, *args):
      entered_text = self.__inst.get()
      if entered_text:
         filtered_options = [i for i in list(self.__options) if entered_text.lower() in i.lower()]
         self.__instrumentsDisplay["values"] = filtered_options
      else:
         self.__instrumentsDisplay["values"] = list(self.__options)
         
   
   def __export_as_csv(self, data_of_which=None):
      data=None
      cur = _con.cursor()
      
      try:
         if data_of_which=="Acquisition reg":
            data = cur.execute("SELECT * FROM acquisition_reg;").fetchall()
      
         elif data_of_which=="log":
            data = cur.execute("SELECT * FROM logger;").fetchall()
      
         elif data_of_which=="lab_logger":
            data = cur.execute("SELECT * FROM lab_logger;").fetchall()
      
         elif data_of_which=="student_list":
            data = cur.execute("SELECT * FROM student_list;").fetchall()
      except TypeError:
         messagebox.showerror("Invalid Type", "Must be a log or list")
      finally:pass
      
      
      result=filedialog.askdirectory()
      
      with open(result+"/"+data_of_which+".csv", "w", newline="") as f:
         csv_writer = csv.writer(f)
         csv_writer.writerow([i[0] for i in cur.description])
         for i in data:
            csv_writer.writerow(i)
         
      messagebox.showinfo("Action", data_of_which+" file saved Successfully :)")
      data=None
   
   def place_text(self):
      if self.__user is not None:
         self.__usr_msg.config(text="logged in as "+self.__user[3], font=("Helvetica", 17, "bold italic"))
   
   def center_treeview_columns(self):
      columns = self.__instruments["columns"]
    
      for col in columns:
         self.__instruments.heading(col, anchor="center")
         self.__instruments.column(col, anchor="center")
   
   def on_combobox_select(self, e):
      selected_item = self.__instrumentsDisplay.get()
      self.display_treeview_data(str(selected_item))

   
   def __chg_admin_key(self):
      global _ADMIN_KEY
      if self.__user[3]=="admin":
         rslt = simpledialog.askstring("Admin Key Change Request", "Enter the old Admin Key")
         if rslt==_ADMIN_KEY:
            _ADMIN_KEY = simpledialog.askstring("Admin Key Change Requenst", "Enter the new Admin Key")
         else:
            messagebox.showerror("Access denied", "Invalid Admin Key")
      else:messagebox.showerror("Invalid access", "User must be an admin!")
      
   def display_treeview_data(self, selected_item, stk_dsply=True):
      self.__erase_treeview_data()
      if stk_dsply:self.__stock.config(text="stock: "+str(_con.execute("SELECT COUNT(*) FROM acquisition_reg WHERE particulars=?;",(selected_item,)).fetchone()[0]))
      for i,j in enumerate(_con.execute("SELECT * FROM acquisition_reg WHERE particulars=?;", (selected_item,))):
         j=list(j)
         if j[12]!="issued":j[12]="\u2610"
         self.__instruments.insert("", "end",i , values=(str(i+1), j[10], j[0], j[1], j[2], j[3], j[4], j[5], j[6], j[8], j[12]))
      
   
   def select_content(self, e):
      try:
         selected_item = self.__instruments.selection()
         col = self.__instruments.identify_column(e.x)
         if col!="#11":
            modify_window = _ModifyCondition(self.__master, self, self.__instruments.item(selected_item[0], "values")[3], self.__user[3])
            self.__instruments.unbind("<ButtonRelease-1>")
            self.__Button.config(state="disabled")
            self.__instrumentsDisplay.unbind("<<ComboboxSelected>>")
      except IndexError:
         messagebox.showerror("Selection info", "Nothing selected!!")
   
   def rebind_events(self):
      self.__instruments.bind("<ButtonRelease-1>", lambda e: self.select_content(e))
      self.__Button.config(state="normal")
      self.__instrumentsDisplay.bind("<<ComboboxSelected>>",lambda e: self.on_combobox_select(e))
      self.__show()
   
   def __erase_treeview_data(self):
      for item in self.__instruments.get_children():
         self.__instruments.delete(item)
   
   def __usr_msg_blink(self, a):
      if a==0:
         self.__usr_msg.config(fg="black")
         a=1
      else:
         self.__usr_msg.config(fg="white")
         a=0
      self.after(1000,lambda:self.__usr_msg_blink(a))
   
   def _setUser(self, user):
      self.__user=user
   
   def getUser(self):
      return self.__user
   
   def getInstrumentsDisplay(self):
      return self.__instrumentsDisplay
   
   def getMaster(self): return self.__master

class _RegisterPortal(tk.Toplevel):
   def __init__(self, master):
      super().__init__(master, background=_COLOR)
      self.title("Registration portal")
      self.__frame = tk.Frame(self, bg=_COLOR, relief="groove",bd=2)
      self.resizable(False, False)
      self.__master=master
      self.__tag=None
      self.__admin_key=tk.StringVar()
      self.__user_id=tk.StringVar()
      self.__username=tk.StringVar()
      self.__password=tk.StringVar()
      self.__cpw=tk.StringVar()
      self.__astns=tk.IntVar()
      self.__admin=tk.IntVar()
      self.__stds=tk.IntVar()
      self.__welcome_label=tk.Label(self.__frame, text="IMS Registration Portal", font=("Arial", 20, "bold italic"), bg="black", fg="white", highlightbackground="red", highlightthickness=4)
      self.__welcome_label.grid(row=0, column=0, columnspan=4, sticky="ew", padx=10, pady=10)
      self.__admin_key_label, self.__admin_key_entry=self.__create_label_and_entry("Admin Key:", self.__admin_key, 1, 0, 1, 1)
      self.__admin_key_entry.focus_set()
      self.__user_id_label, self.__user_id_entry=self.__create_label_and_entry("user ID:", self.__user_id, 2, 0, 2, 1)
      self.__user_id_entry.config(state="disabled")
      self.__username_label, self.__username_entry=self.__create_label_and_entry("username:", self.__username, 3, 0, 3, 1)
      self.__username_entry.config(state="disabled")
      self.__password_label, self.__password_entry=self.__create_label_and_entry("password:", self.__password, 5, 0, 5, 1)
      self.__password_entry.config(state="disabled", show="*")
      self.__confirm_pw_label, self.__confirm_pw_entry=self.__create_label_and_entry("confirm password:", self.__cpw, 6, 0, 6, 1)
      self.__confirm_pw_entry.config(state="disabled", show="*")
      self.__tag_label=tk.Label(self.__frame, text="Tag:", font=("Arial", 15, "bold italic"), bg=_COLOR)
      self.__tag_label.grid(row=4, column=0, sticky="e", pady=5)
      self.__assistant_cb=tk.Checkbutton(self.__frame, text="Lab assistant", variable=self.__astns, command=self.__astnts_checkbox_clicked, state="disabled")
      self.__assistant_cb.grid(row=4, column=1)
      self.__admin_cb=tk.Checkbutton(self.__frame, text="Admin", variable=self.__admin, command=self.__admin_checkbox_clicked, state="disabled")
      self.__admin_cb.grid(row=4, column=2)
      self.__stds_cb = tk.Checkbutton(self.__frame, text="Student", variable=self.__stds, command=self.__stds_cb_clicked, state="disabled")
      self.__stds_cb.grid(row=4, column=3)
      self.__reg_Bt = tk.Button(self.__frame, text="Register", font=("Arial", 17, "bold italic"), command=self.__reg, state="disabled", bg=_BT_COLOR)
      self.__reg_Bt.grid(row=8, column=0, columnspan=4, sticky="ew", padx=5, pady=5)
      self.entry_widgets=[self.__admin_key_entry, self.__user_id_entry, self.__username_entry, self.__password_entry, self.__confirm_pw_entry]
      self.bind("<Up>", lambda e:_on_arrow_up(self, self.entry_widgets, e))
      self.bind("<Down>", lambda e:_on_arrow_down(self, self.entry_widgets, e))
      self.bind("<Return>", self.__check_admin_key)
      self.protocol("WM_DELETE_WINDOW", self.__on_close)
      self.__frame.pack(expand=True)
      self.__admin_key_lb_blink(1)
      self.mainloop()
   
   def __create_label_and_entry(self, label_text, entry_textvariable, label_row, label_column, entry_row, entry_column):
      label = tk.Label(self.__frame, text=label_text, font=("Arial", 15, "bold italic"), bg=_COLOR, fg="black", relief="groove", bd=3)
      label.grid(row=label_row, column=label_column, padx=2, pady=5, sticky="e")
      entry = tk.Entry(self.__frame, font=("Arial", 15), textvariable=entry_textvariable)
      entry.grid(row=entry_row, column=entry_column, padx=2, sticky="ew", columnspan=3)
      return label, entry
   
   def __check_admin_key(self, e):
      if self.__admin_key_entry.get()==_ADMIN_KEY:
         for i in self.winfo_children():
            for j in i.winfo_children():
               j.config(state="normal")
  
   def __admin_key_lb_blink(self, a):
      if a==1:
         self.__admin_key_label.config(fg="red")
         a=0
      else:
         self.__admin_key_label.config(fg="black")
         a=1
      self.after(1000, lambda:self.__admin_key_lb_blink(a))
      
   
   def __reg(self):
      if self.__astns.get()==1 or self.__admin.get()==1:
         if self.__password.get()!="" and self.__cpw.get()!="": 
            if self.__cpw.get()==self.__password.get() and self.__tag is not None:
               _con.execute("INSERT INTO login_info (user_id, username, password, tag) VALUES ('"+self.__user_id.get()+"', '"+self.__username.get()+"','"+self.__password.get()+"', '"+self.__tag+"')")
               self.__master.winfo_children()[0].rebind_events()
               self.destroy()	
            else:print("fill")
      if self.__stds.get()==1:
         try:_con.execute("INSERT INTO student_list (student_id, student_name) VALUES (?,?)", (self.__user_id.get(), self.__username.get()))
         except s3.IntegrityError:messagebox.showinfo("Duplicate Insertion", "Student details already entered!!")
      _con.commit()
      
      
   def __admin_checkbox_clicked(self):
      if self.__admin.get()==1:
         self.__astns.set(0)
         self.__stds.set(0)
      self.__password_entry.config(state="normal")
      self.__confirm_pw_entry.config(state="normal")
      self.__tag="admin"
   
   def __astnts_checkbox_clicked(self):
      if self.__astns.get()==1:
         self.__admin.set(0)
         self.__stds.set(0)
      self.__password_entry.config(state="normal")
      self.__confirm_pw_entry.config(state="normal")
      self.__tag="assitant"
   
   def __stds_cb_clicked(self):
      if self.__stds.get()==1:
         self.__admin.set(0)
         self.__astns.set(0)
         self.__password_entry.config(state="disabled")
         self.__confirm_pw_entry.config(state="disabled")
         self.__tag="student"
      else:
         self.__password_entry.config(state="normal")
         self.__confirm_pw_entry.config(state="normal")
         self.__tag="unassigned"
      
   
   def __on_close(self):
      self.__master.winfo_children()[0].rebind_events()
      self.destroy()

      
class _LoginPage(tk.Frame):
   __TEXT="IMS Portal"
   def __init__(self, master):
      super().__init__(master=master, bd=6, bg=_COLOR, relief="groove", highlightbackground="black", highlightthickness=2)
      self.pack(padx=10,pady=10, expand=True)
      self.__master = master
      self.__master.protocol("WM_DELETE_WINDOW", self.__master.destroy)
      self.__userID = tk.StringVar()
      self.__password = tk.StringVar()
      self.__loginlabel = tk.Label(self, fg="black",font=("Helvetica", 25, "bold italic"), highlightbackground="black", highlightthickness=2, bd=2 ,relief="raised")
      self.__loginlabel.grid(row=0, column=0, columnspan=2,padx=20, pady=40, sticky="new")
      self.__userIdlabel = tk.Label(self, text="User ID:", font=("Arial", 15, "bold italic"), bg=_COLOR)
      self.__userIdlabel.grid(row=1, column=0, padx=5, pady=20, sticky="e")
      self.__userIdEntry = tk.Entry(self, width=20, textvariable=self.__userID)
      self.__userIdEntry.grid(row=1, column=1, padx=5, pady=20, sticky="w")
      self.__PasswordLabel = tk.Label(self, text="Password:", font=("Arial", 15, "bold italic"),bg=_COLOR)
      self.__PasswordLabel.grid(row=2, column=0, padx=5, pady=20, sticky="e")
      self.__PasswordEntry = tk.Entry(self, width=20, textvariable=self.__password, show="*")
      self.__PasswordEntry.grid(row=2, column=1, padx=5, pady=20, sticky="w")
      self.__Button=tk.Button(self,text="Login", command=self.__login, background=_BT_COLOR, relief="raised", bd=2, font=("Arial", 15, "bold italic"), fg="white")
      self.__Button.grid(row=3, column=0, pady=10, padx=80)
      self.__reg_button = tk.Button(self, text="Register", command=self.__register, background=_BT_COLOR, relief="raised", bd=2, font=("Arial", 15, "bold italic"), fg="white")
      self.__reg_button.grid(row=3, column=1, padx=80, pady=30)
      self.entry_widgets=[self.__userIdEntry, self.__PasswordEntry, self.__Button]
      self.__master.bind("<Up>", lambda e:_on_arrow_up(master, self.entry_widgets, e))
      self.__master.bind("<Down>", lambda e:_on_arrow_down(master, self.entry_widgets, e))
      self.__master.bind("<Return>", lambda e:self.__userIdEntry.focus_set())
      self.__show_title("", 1)
      
   def __login(self):
      if self.__password.get() and self.__userID.get():
         user=_con.execute("SELECT * FROM login_info WHERE user_id='"+self.__userID.get()+"';").fetchone()
         try:
            if user[2]==self.__password.get() and user[3] != "student":
               self.destroy()
               nextpage = _ShowInstruments(self.__master, user)
               nextpage._setUser(user)
               nextpage.place_text()
            elif user[3] == "student":messagebox.showwarning("Access denied", "Students are not allowed to login")
            else:messagebox.showerror("Access", "Invalid Password")
         except TypeError:
             messagebox.showerror("Login Access", "User account Not registered")
   
   def __show_title(self, a, i):
      if i<=len(self.__TEXT):
         self.__loginlabel.config(text=a, fg="red")
         a+=self.__TEXT[i-1]
         self.after(350, lambda:self.__show_title(a, i+1))
      else:self.__loginlabel.config(text=self.__TEXT, fg="black")
      
   def __register(self):
      self.__reg_button.config(state="disabled")
      self.__Button.config(state="disabled")
      rg_frame=_RegisterPortal(self.__master)
      
   def rebind_events(self):
      self.__reg_button.config(state="normal")
      self.__Button.config(state="normal")
   
class _MainApp(tk.Tk):
   def __init__(self, title):
      super().__init__()
      self.title(title)
      self["bg"]="red"
      self.resizable(False, False)
      self.__l = _LoginPage(self)
      self.mainloop()
      _con.close()

if __name__=="__main__":
   _MainApp("Instrument Management System")
