import tkinter as tk
from tkinter import ttk, messagebox
import hashlib
import database as db
import customwidgets as cw
import algorithm
import re
from abc import abstractmethod

TITLE_TEXT = ("Verdana", 18, "bold")
MAIN_TEXT = ("Verdana", 10)

BLACK = "#000000"
WHITE = "#ffffff"

BG_COLOUR = "#008080"
ACCENT_COLOUR = "#828282"
TEXT_COLOUR = BLACK
HIGHLIGHT_COLOUR = "#C2620E"
ERROR_COLOUR = "#A11313"
VALID_COLOUR = "#1c9c22"
LINK_COLOUR = "#142CC7"

TTK_DEFAULT_COLOUR = "#F0F0F0"

EMAIL_REGEX = re.compile("[^@]+@[^@]+\.[^@]+")
EMAIL_SUFFIX = "@christthekingcollege.co.uk"

# Functions #
# Validation #


def standard_validation(entry):
    for char in entry:
        if char in ' !"$%^&*(),<>@:;#~-_=+{}[]':
            return False
    return True


def invalid_checker(entry):
    string_invalids = ["'", " ", '"']
    list_invalids = list(string_invalids)
    entry_list = list(entry)
    for char in entry_list:
        if char in list_invalids:
            return False
    return True


# Generic #


def hash_(string):
    # creates a hash function as an object using the md5 algorithm
    hash1 = hashlib.md5(string.encode('utf-8'))
    # returns the hashed value of the string passed in
    return hash1.hexdigest()


def reverse_map_dict(dic, value):
    for name, val in dic.items():  # for name, age in dictionary.iteritems():  (for Python 2.x)
        if val == value:
            return name


# Classes #


class AccountUser:
    """Defines how the current users data should be stored"""
    def __init__(self, id_, istn_id, email, firstname, surname, password, clearance):
        self.id = id_
        self.istn_id = istn_id
        self.email = email
        self.firstname = firstname
        self.surname = surname
        self.password = password
        self.clearance = clearance

    def __repr__(self):
        return "Username: '{}'\nFirstname: '{}'\nSurname: '{}'\nPassword: '{}'".format(
                self.email, self.firstname, self.surname, self.password)

    def update_password(self, password):
        """Updates the password for the account"""
        password = hash_(password)
        if password == self.password:
            messagebox.showerror("Message", "Unable to use old password")
            return False
        self.password = password
        a_db.update_password(self.email, self.password)

    def get_default_filepath(self):
        """Returns default filepath"""
        return a_db.get_default_filepath(self.id)

    def update_default_file(self, file_path):
        """Updates default file for the user"""
        a_db.update_default_filepath(self.id, file_path)

    def delete_default_filepath(self):
        """Updates default file for the user"""
        a_db.remove_default_filepath(self.id)


class LoginPage(cw.CentreFrame):
    """Page where the user can login with correct credentials"""
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent

        self.email = tk.StringVar()
        self.password = tk.StringVar()
        self.email_lbl = tk.Label(self, text="Email:")
        self.email_lbl.grid(row=1, column=1)
        self.email_entry = tk.Entry(self,
                                    width=25,
                                    highlightthickness=2,
                                    highlightcolor=HIGHLIGHT_COLOUR,
                                    textvariable=self.email)
        '''<------------------------- For testing purposes only ----------------------->'''
        self.email.set("admin@testing.com")
        # cw.add_placeholder_to(self.email_entry, "admin@testing.com", color=BLACK)
        '''<------------------------- For testing purposes only ----------------------->'''
        self.email_entry.grid(row=1, column=2, padx=0, pady=5)
        self.password_lbl = tk.Label(self, text="Password:")
        self.password_lbl.grid(row=2, column=1)
        self.password_entry = tk.Entry(self,
                                       width=25,
                                       highlightthickness=2,
                                       highlightcolor=HIGHLIGHT_COLOUR,
                                       textvariable=self.password,
                                       show="*")
        '''<------------------------- For testing purposes only ----------------------->'''
        self.password.set("password")
        '''<------------------------- For testing purposes only ----------------------->'''
        self.password_entry.grid(row=2, column=2, padx=0, pady=5)
        self.output_lbl = tk.Label(self, text="")
        self.output_lbl.grid(row=3, column=1)
        login_btn = ttk.Button(self, text="Login", command=self.get_login)
        login_btn.grid(row=3, column=2, pady=10)
        account_lbl = tk.Label(self,
                               text="Create Account",
                               fg=LINK_COLOUR)
        account_lbl.bind("<Button-1>", self.show_account_page)
        account_lbl.grid(row=4, column=1, columnspan=2, pady=10)

    def show_account_page(self, event):
        """Displays the account page"""
        self.parent.container.show_init_frame(self.parent.account_frame)
        self.clear()

    def clear(self):
        """Clears any data entered by the user"""
        self.email.set("")
        self.password.set("")
        self.output_lbl.config(text="")

    def get_login(self):
        """Called when the user tries to login and updates the window accordingly"""
        email = self.email.get()
        password = self.password.get()
        run = True
        if email == "" and password == "":
            self.output_lbl.config(text="No email or\n password entered")
            self.email_lbl.config(fg=ERROR_COLOUR)
            self.password_lbl.config(fg=ERROR_COLOUR)
            run = False
        else:
            self.output_lbl.config(text="")
            self.email_lbl.config(fg=BLACK)
            self.password_lbl.config(fg=BLACK)
        if run:
            if email == "":
                self.output_lbl.config(text="No email entered")
                self.email_lbl.config(fg=ERROR_COLOUR)
                run = False
            else:
                self.output_lbl.config(text="")
                self.email_lbl.config(fg=BLACK)
        if run:
            if password == "":
                self.output_lbl.config(text="No password entered")
                self.password_lbl.config(fg=ERROR_COLOUR)
                run = False
            else:
                self.output_lbl.config(text="")
                self.password_lbl.config(fg=BLACK)
        if run:
            admin_password = a_db.get_account_password(email)
            if admin_password == hash_(password):
                admin_data = a_db.get_account_details_email(email)
                self.parent.initialise_main_window(admin_data)
            else:
                self.output_lbl.config(text="Your email and\n password do not match")


class AccountPage(cw.CentreFrame):
    """Page where the user can create an account by entering credentials"""
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent

        self.nodes = []

        # creates variables for each widget
        self.first = tk.StringVar()
        self.second = tk.StringVar()
        self.code = tk.StringVar()
        self.email = tk.StringVar()
        self.pwd = tk.StringVar()
        self.r_pwd = tk.StringVar()

        # formats the page and attaches variables to the widgets
        self.first_lbl = tk.Label(self, text="Firstname:")
        self.first_lbl.grid(row=1, column=1)
        self.first_entry = tk.Entry(self,
                                    width=25,
                                    highlightthickness=2,
                                    highlightcolor=HIGHLIGHT_COLOUR,
                                    textvariable=self.first)
        self.first_entry.grid(row=1, column=2, sticky="w", padx=0, pady=5)
        self.nodes.append((self.first, self.first_lbl, self.first_entry))

        self.second_lbl = tk.Label(self, text="Surname:")
        self.second_lbl.grid(row=2, column=1)
        self.second_entry = tk.Entry(self,
                                     width=25,
                                     highlightthickness=2,
                                     highlightcolor=HIGHLIGHT_COLOUR,
                                     textvariable=self.second)
        self.second_entry.grid(row=2, column=2, sticky="w", padx=0, pady=5)
        self.nodes.append((self.second, self.second_lbl, self.second_entry))

        self.code_lbl = tk.Label(self, text="Institution Code:")
        self.code_lbl.grid(row=3, column=1)
        self.code_entry = tk.Entry(self,
                                   width=10,
                                   highlightthickness=2,
                                   highlightcolor=HIGHLIGHT_COLOUR,
                                   textvariable=self.code)
        self.code_entry.grid(row=3, column=2, sticky="w", padx=0, pady=5)
        self.nodes.append((self.code, self.code_lbl, self.code_entry))

        self.email_lbl = tk.Label(self, text="Email:")
        self.email_lbl.grid(row=4, column=1)
        self.email_entry = tk.Entry(self,
                                    width=25,
                                    highlightthickness=2,
                                    highlightcolor=HIGHLIGHT_COLOUR,
                                    textvariable=self.email)
        self.email_entry.grid(row=4, column=2, sticky="w", padx=0, pady=5)
        self.nodes.append((self.email, self.email_lbl, self.email_entry))

        self.pwd_lbl = tk.Label(self, text="Password:")
        self.pwd_lbl.grid(row=5, column=1)
        self.pwd_entry = tk.Entry(self,
                                  width=25,
                                  highlightthickness=2,
                                  highlightcolor=HIGHLIGHT_COLOUR,
                                  textvariable=self.pwd, show="*")
        self.pwd_entry.grid(row=5, column=2, sticky="w", padx=0, pady=5)
        self.nodes.append((self.pwd, self.pwd_lbl, self.pwd_entry))

        self.r_pwd_lbl = tk.Label(self, text="Repeat Password:")
        self.r_pwd_lbl.grid(row=6, column=1)
        self.r_pwd_entry = tk.Entry(self,
                                    width=25,
                                    highlightthickness=2,
                                    highlightcolor=HIGHLIGHT_COLOUR,
                                    textvariable=self.r_pwd,
                                    show="*")
        self.r_pwd_entry.grid(row=6, column=2, sticky="w", padx=0, pady=5)
        self.nodes.append((self.r_pwd, self.r_pwd_lbl, self.r_pwd_entry))

        self.output_lbl = tk.Label(self, text="")
        self.output_lbl.grid(row=7, column=1, columnspan=2, pady=3)

        login_btn = ttk.Button(self, text="Create Account", command=self.create_account_callpoint)
        login_btn.grid(row=8, column=1, columnspan=2, pady=10)

        # creates the link to the Login Page
        account_lbl = tk.Label(self,
                               text="Back",
                               fg=LINK_COLOUR)
        account_lbl.bind("<Button-1>", self.show_login_page)
        account_lbl.grid(row=9, column=1, columnspan=2, pady=10)

    def create_account_callpoint(self):
        """Callpoint of the collection of functions to create an account"""
        if self.basic_validation() and self.validate_inputs():
            self.create_account_db()

    def create_account_db(self):
        """Valid data is added into the database"""
        data = self.get_input_data()
        data[2] = a_db.get_istn_id(data[2])
        try:
            a_db.add_account(*(data[:4]+[hash_(data[-1]), 0]))
            self.show_login_page(None)
            messagebox.showinfo("TimetablePro", "Account successfully created")
            self.clear()
        except db.sql.DatabaseError:
            messagebox.showerror("TimetablePro", "Unable to create account")

    def validate_inputs(self) -> bool:
        """Validates the data inputted by the user"""
        if self.check_names():
            self.output_lbl.config(text="")
            self.first_entry.config(highlightbackground=WHITE)
            self.second_entry.config(highlightbackground=WHITE)
        else:
            self.output_lbl.config(text="Names must be in title format")
            self.first_entry.config(highlightbackground=ERROR_COLOUR)
            self.second_entry.config(highlightbackground=ERROR_COLOUR)
            return False

        if self.check_code():
            self.output_lbl.config(text="")
            self.code_entry.config(highlightbackground=WHITE)
        else:
            self.output_lbl.config(text="Not a valid institution code")
            self.code_entry.config(highlightbackground=ERROR_COLOUR)
            return False

        if self.check_email():
            self.output_lbl.config(text="")
            self.email_entry.config(highlightbackground=WHITE)
        else:
            self.output_lbl.config(text="Email is invalid or already exists")
            self.email_entry.config(highlightbackground=ERROR_COLOUR)
            return False

        if self.passwords_match():
            self.output_lbl.config(text="")
            self.pwd_entry.config(highlightbackground=WHITE)
            self.r_pwd_entry.config(highlightbackground=WHITE)
        else:
            self.output_lbl.config(text="Passwords do not match")
            self.pwd_entry.config(highlightbackground=ERROR_COLOUR)
            self.r_pwd_entry.config(highlightbackground=ERROR_COLOUR)
            return False
        return True

    def basic_validation(self):
        """Checks the inputs are not empty: returns bool"""
        valid = True
        for node in self.nodes:
            if not self.check_empty(*node):
                valid = False
        return valid

    @staticmethod
    def check_empty(var, lbl, entry):
        """checks sting is not empty and updates label"""
        string = var.get()
        if not string:
            colour = ERROR_COLOUR
        else:
            colour = WHITE
        entry.config(highlightbackground=colour)
        return string

    def check_names(self):
        """Checks names are capitalised followed by lower case letters"""
        return self.first.get().istitle() and self.second.get().istitle()

    def check_code(self):
        """Checks the institution code exists"""
        return a_db.get_istn_id(self.code.get()) is not None

    def check_email(self):
        """Checks email address is unique and correctly formatted"""
        return EMAIL_REGEX.fullmatch(self.email.get()) is not None and a_db.check_email_unique(self.email.get())

    def passwords_match(self):
        """Returns true if passwords match"""
        return self.pwd.get() == self.r_pwd.get()

    def show_login_page(self, event):
        """Displays the login page"""
        # events that is triggered pass in an event object which is not always used
        self.parent.container.show_init_frame(self.parent.login_frame)

    def clear_output(self):
        """Clears the output label"""
        self.output_lbl.config(text="")

    def clear(self):
        """Clears any data entered by the user"""
        for node in self.nodes:
            node[0].set("")
        self.clear_output()

    def get_input_data(self):
        """Fetches all of the input data from the entry boxes"""
        data = []
        for node in self.nodes:
            data.append(node[0].get())
        return data


class LoginWindow(tk.Tk):
    """Initialises account login window"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("TimetablePro")
        self.geometry("1200x600+300+200")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.resizable(width=False, height=False)

        holder = tk.Frame(self)
        holder.grid_rowconfigure(0, weight=1)
        holder.grid_columnconfigure(1, weight=1)

        image_frame = tk.Frame(self)
        try:
            gif = tk.PhotoImage(file="ExampleWordCloud.gif")
            image_lbl = tk.Label(image_frame, image=gif)
            image_lbl.image = gif
        except tk.TclError:
            image_lbl = tk.Label(image_frame, text="Could not find image")
        image_lbl.pack()
        image_frame.pack(side="left")

        self.page_ids = {}
        self.container = cw.CreateContainer(holder, self, self)
        self.login_frame = LoginPage(self)
        self.account_frame = AccountPage(self)
        self.container.add_init_page(self.login_frame)
        self.container.add_init_page(self.account_frame)
        self.container.show_init_frame(self.login_frame)
        self.container.grid(row=0, column=1, sticky="nsew")

        holder.pack(expand=True, fill="both")

    def clear_window(self):
        """Clears the window"""
        self.login_frame.clear()
        self.account_frame.clear()

    def initialise_main_window(self, admin_data):
        """Opens the MainWindow with user credentials"""
        self.withdraw()
        self.clear_window()
        app = MainWindow(self, admin_data)
        app.mainloop()

    def on_closing(self):
        """Closes connection with the database and exits"""
        a_db.close_database()
        self.destroy()


class StudentTimetable(cw.IndividualTable):
    """Implements the individual table for students"""
    def __init__(self, parent):
        cw.IndividualTable.__init__(self, parent)
        self.stdt_id = None

    def show_stdt_timetable(self, stdt_id):
        """Updates the table for a particular student"""
        if self.stdt_id == stdt_id or stdt_id is None:
            return
        self.stdt_id = stdt_id
        first, sur, yr_id = m_db.get_student_data(stdt_id)[1:4]
        yr_nm = m_db.get_year_name(yr_id)
        self.update_title(first, sur, yr_nm)
        periods = m_db.fetch_student_timetable(stdt_id)
        for cell in periods:
            self.update_cell_prd_id(*cell)


class TeacherTimetable(cw.IndividualTable):
    """Implements the individual table for teachers"""
    def __init__(self, parent):
        cw.IndividualTable.__init__(self, parent)
        self.tchr_id = None

    def show_tchr_timetable(self, tchr_id):
        """Updates the table for a particular teacher"""
        if self.tchr_id == tchr_id or tchr_id is None:
            return
        self.tchr_id = tchr_id
        tchr = m_db.get_teacher_by_id(tchr_id)
        self.update_title(tchr[3], tchr[4], tchr[1])
        periods = m_db.fetch_teacher_timetable(tchr_id)
        for cell in periods:
            self.update_cell_prd_id(*cell)


class ClassroomTimetable(cw.IndividualTable):
    """Implements the individual table for classrooms"""
    def __init__(self, parent):
        cw.IndividualTable.__init__(self, parent)
        self.clsrm_id = None

    def show_clsrm_timetable(self, clsrm_id):
        """Updates the table for a particular classroom"""
        if self.clsrm_id == clsrm_id or clsrm_id is None:
            return
        self.clsrm_id = clsrm_id
        periods = m_db.fetch_classroom_timetable(clsrm_id)
        for cell in periods:
            self.update_cell_prd_id(*cell)


class MainWindow(tk.Toplevel):
    """Creates Menubar based on the clearance of the teacher/student"""
    def __init__(self, root, admin_data, *args, **kwargs):
        super().__init__(root, *args, **kwargs)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.user = AccountUser(*admin_data)

        self.root = root
        self.minsize(width=300, height=150)
        self.title("Timetable")
        self.geometry("1400x700+200+100")
        self.protocol("WM_DELETE_WINDOW", self.logout)
        self.resizable(width=False, height=False)

        self.msg_bar = tk.Frame(self, bg=ERROR_COLOUR)
        self.msg_lbl = tk.Label(self.msg_bar,
                                text="Error: Database not connected",
                                bg=ERROR_COLOUR)
        self.msg_lbl.pack(side="left", padx=10, pady=1)
        self.msg_bar.grid(row=0, column=0, sticky="ew")

        self.container = tk.Frame(self)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid(row=1, column=0, sticky="nsew")

        file_path = self.user.get_default_filepath()
        if file_path is not None and m_db.connect_database(file_path):
            self.hide_error_bar()
        else:
            self.user.delete_default_filepath()

        self.frames = {}
        self.pages = []
        self.menubar = tk.Menu(self)
        self.config_layout()
        self.config(menu=self.menubar)

    def hide_error_bar(self):
        """Hides the error bar"""
        self.msg_bar.grid_remove()

    def show_error_bar(self):
        """Shows the error bar"""
        self.msg_bar.grid()

    def config_layout(self):
        """Configures the layout based on the clearance level"""
        if self.user.clearance in [0, 1]:
            self.config_homepage()
        elif self.user.clearance == 2:
            self.config_homepage()
            self.config_data_pages()
        self.add_pages(*self.pages)

    def config_homepage(self):
        """Adds pages and menu commands relating to the homepage"""
        account_menu = tk.Menu(self.menubar, tearoff=0)
        account_menu.add_command(label="Home", command=lambda: self.show_frames(TimetablePage))
        account_menu.add_command(label="Update Password", command=lambda: self.show_frames(ChangePasswordPage))
        account_menu.add_separator()
        account_menu.add_command(label="Logout", command=self.logout)
        self.menubar.add_cascade(label="Account", menu=account_menu)
        self.pages += [TimetablePage, ChangePasswordPage]

    def config_data_pages(self):
        file_menu = tk.Menu(self.menubar, tearoff=0)
        file_menu.add_command(label="New", command=self.create_database)
        file_menu.add_command(label="Open", command=self.open_database)
        file_menu.add_command(label="Back-Up", command=self.backup_database)
        self.menubar.add_cascade(label="File", menu=file_menu)
        edit_menu = tk.Menu(self.menubar, tearoff=0)
        edit_menu.add_command(label="Timetable", command=lambda: self.show_frames(EditTimetablePage))
        edit_menu.add_separator()
        edit_menu.add_command(label="Subjects", command=lambda: self.open_window(ImportSubjectWindow))
        edit_menu.add_command(label="Students", command=lambda: self.open_window(ImportStudentWindow))
        edit_menu.add_command(label="Teachers", command=lambda: self.open_window(ImportTeacherWindow))
        edit_menu.add_command(label="Classrooms", command=lambda: self.open_window(ImportClassroomWindow))
        edit_menu.add_separator()
        edit_menu.add_command(label="Admin",
                              command=lambda: messagebox.showinfo("Message",
                                                                  "This feature is not yet currently working"))
        edit_menu.add_separator()
        edit_menu.add_command(label="Advanced",
                              command=lambda: messagebox.showinfo("Message",
                                                                  "This feature is not yet currently working"))
        self.menubar.add_cascade(label="Edit", menu=edit_menu)
        self.pages += [EditTimetablePage]

    def create_database(self):
        """Wrapper for database module function create_database"""
        if m_db.create_database():
            self.update_filepath()
            self.hide_error_bar()
            self.refresh()

    def open_database(self):
        """Wrapper for database module function open_database"""
        if m_db.open_database():
            self.update_filepath()
            self.hide_error_bar()
            self.refresh()

    @staticmethod
    def backup_database():
        """Wrapper for database module function backup_database"""
        m_db.backup_database()

    def close_database(self):
        """Wrapper for database module function close_database"""
        m_db.close_database()
        self.show_error_bar()
        self.refresh()

    def update_filepath(self):
        """Updates the filepath"""
        if m_db.filepath is not None:
            self.user.update_default_file(m_db.filepath)

    def add_pages(self, *pages):
        """Adds classes to the container and shows the first page passed by default"""
        for F in pages:
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frames(pages[0])

    def show_frames(self, cont):
        """Displays frame relating to the parameter cont in window"""
        frame = self.frames[cont]
        try:
            frame.tkraise()
        except KeyError:
            raise KeyError("'{}' is not a page in this Window".format(frame))

    def open_window(self, window, closing_command=None):
        """Opens window with command to execute upon closing"""
        window(self, closing_command)

    def refresh(self):
        """Refreshes all pages wihtin the program"""
        for frame in self.frames.values():
            frame.refresh_all()

    def logout(self):
        """Logs user of of account and loads login screen"""
        self.destroy()
        m_db.close_database()
        bootstrapper.update()
        bootstrapper.deiconify()


class SubjectCheckButtonFrame(tk.Frame):
    """Checkbutton frame widget to select subjects"""
    def __init__(self, parent, background="white"):
        super().__init__(parent, bg=background)
        self.node_list, self.background = [], background

    def display_subjects(self, year_id=None):
        """Displays all of the subjects for a year or all if left blank"""
        if year_id is "*":
            subject_ids = m_db.get_all_subjects()
        else:
            subject_ids = m_db.get_option_subjects_by_year(year_id)
        if len(subject_ids) == 0:
            return
        subjects = list(map(m_db.get_subject_name_from_student_subjects, subject_ids))
        subjects.sort()
        for column, section in enumerate(self.layout_list(subjects)):
            for row, item in enumerate(section):
                var = tk.IntVar()
                checkbutton = tk.Checkbutton(self, bg=self.background, text=item, variable=var)
                checkbutton.grid(row=row, column=column, sticky="w")
                self.node_list.append(StudentSubjectNode(checkbutton, item, var))

    def destroy_subjects(self):
        """Clears all subjects from widget"""
        for item in self.node_list:
            item.destroy()
        self.node_list = []

    def update_subjects(self, year_id=None):
        """Updates the subjects"""
        self.destroy_subjects()
        self.display_subjects(year_id)

    def get_selected_subjects(self):
        """Returns the ids of the subjects selected"""
        subjects = []
        for item in self.node_list:
            if item.variable.get() == 1:
                subjects.append(item.subject)
        return tuple(subjects)

    def set_selected_subjects(self, subjects=None):
        """Sets the subjects that are selected"""
        if subjects is None:
            self.clear_selected_subjects()
        else:
            for item in self.node_list:
                if item.subject in subjects:
                    item.variable.set(1)
                else:
                    item.variable.set(0)

    def clear_selected_subjects(self):
        """Clears the selected subjects"""
        for item in self.node_list:
            item.variable.set(0)

    def enable_all(self):
        """Enables the widget to be interacted with"""
        for item in self.node_list:
            item.widget.config(state="active")

    def disable_all(self):
        """Disables the widget to be interacted with"""
        for item in self.node_list:
            item.widget.config(state="disabled")

    @staticmethod
    def layout_list(subjects, row_length=7):
        """Layouts the list in sections of specified length"""
        sections = len(subjects) // row_length
        segments = len(subjects) % row_length
        temp_subjects = []
        for section in range(sections):
            temp = []
            for i in range(row_length):
                temp.append(subjects[row_length * section + i])
            temp_subjects.append(temp)
        temp = []
        for end in range(1, segments + 1):
            temp.append(subjects[-end])
        if len(temp) != 0:
            temp_subjects.append(temp)
        return temp_subjects


class StudentSubjectNode:
    def __init__(self, widget, subject, variable):
        self.widget = widget
        self.subject = subject
        self.variable = variable

    def __repr__(self):
        return self.subject


class ProgressWindow(tk.Toplevel):
    """Window shown when back-ground process is going on"""
    def __init__(self, parent, title="Progress", text="Working...", process=None):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.title(title)
        self.msg_lbl = tk.Label(self, text=text)
        self.msg_lbl.grid(row=0, column=0)
        self.mainloop()
        self._start_process(process)

    def _start_process(self, process):
        """Executes the process given and passes in arguments"""
        try:
            process(self)
        except:
            pass
        finally:
            self.destroy()


class ImportSubjectWindow(tk.Toplevel):
    """Top-level window to add and edit subjects"""
    def __init__(self, parent, subject_id=None, closing_command=None):
        super().__init__(parent)
        self.subject_id = subject_id
        self.title("Subjects")
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.closing_command = closing_command

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        container = tk.Frame(self, bg=BG_COLOUR)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        container.grid(row=0, column=0, sticky="nsew")

        style = ttk.Style()
        style.configure("BW.TNotebook", background=BG_COLOUR)
        style.configure("BW.TFrame", background=BG_COLOUR)

        self.tab_controller = ttk.Notebook(container, style="BW.TNotebook")
        self.tab_controller.bind('<Button-1>', self.tab_handler)

        add_subject_tab = ttk.Frame(self.tab_controller)

        name_label_frame = ttk.LabelFrame(add_subject_tab, text="Name:")
        name_label_frame.grid_rowconfigure(0, weight=1)
        name_label_frame.grid_rowconfigure(9999, weight=1)
        name_label_frame.grid_columnconfigure(0, weight=1)
        name_label_frame.grid_columnconfigure(9999, weight=1)
        tk.Label(name_label_frame, text="Name:").grid(row=1, column=1, sticky="w")
        self.name = tk.StringVar()
        tk.Entry(name_label_frame, textvariable=self.name).grid(row=2, column=1, sticky="ew")
        tk.Label(name_label_frame, text="Code:").grid(row=3, column=1, sticky="w")
        self.code = tk.StringVar()
        tk.Entry(name_label_frame, textvariable=self.code).grid(row=4, column=1, sticky="ew")
        name_label_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.import_sbjts_tab = ttk.Frame(self.tab_controller)
        self.import_sbjts_tab.grid_rowconfigure(0, weight=1)
        self.import_sbjts_tab.grid_rowconfigure(9999, weight=1)
        self.import_sbjts_tab.grid_columnconfigure(0, weight=1)
        self.import_sbjts_tab.grid_columnconfigure(9999, weight=1)
        self.sheet = None
        self.import_button = ttk.Button(self.import_sbjts_tab, text="Select File", command=self.import_data)
        self.import_button.grid(row=1, column=1)

        self.tab_controller.add(add_subject_tab, text="Add")
        self.tab_controller.add(self.import_sbjts_tab, text="Import")
        self.tab_controller.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.bottom_bar = cw.BottomBar(self)
        self.add_btn_id = self.bottom_bar.add_button(text="Add", command=self.add_sbjt_to_db, state="active")
        self.import_btn_id = self.bottom_bar.add_button(text="Import", command=self.write_data, state="disabled")
        self.edit_btn_id = self.bottom_bar.add_button(text="Edit", command=self.edit_sbjt_in_db, state="active")
        self.bottom_bar.show_button(self.add_btn_id)
        self.bottom_bar.grid(row=1, column=0)

        if self.subject_id is not None:
            self.configure_edit()

        self.mainloop()

    @staticmethod
    def import_data():
        """direct_path = os.path.dirname(os.path.realpath(__file__))
        filename = filedialog.askopenfilename(initialdir=direct_path, title="Open",
                                              filetypes=(("All files", "*.*"),
                                                         ("SQL files", "*.sql")))
        if filename != "":
            self.import_button.grid_remove()
        self.sheet = cw.SpreadSheetFrame(self.import_sbjts_tab, rows=30, columns=5)
        self.sheet.grid(row=2, column=1)"""
        messagebox.showinfo("Message", "This feature is not yet currently working")

    def configure_edit(self, sbjt_id=None):
        if sbjt_id is not None:
            self.subject_id = sbjt_id
        sbjt_data = m_db.get_subject_data(self.subject_id)
        self.name.set(sbjt_data[2])
        self.code.set(sbjt_data[1])
        self.edit_state()

    def edit_sbjt_in_db(self):
        name = self.name.get().title()
        code = self.code.get().title()
        if self.validate_data(name, code):
            try:
                m_db.update_subject(self.subject_id, code, name)
                self.bottom_bar.configure_output(text="Subject successfully edited", fg="green")
                self.clear_widgets()
            except db.sql.OperationalError:
                self.bottom_bar.configure_output(text="Error: Unable to edit subject in database", fg=ERROR_COLOUR)

    def clear_widgets(self):
        self.name.set("")
        self.code.set("")

    def tab_handler(self, event):
        clicked_tab = self.tab_controller.tk.call(self.tab_controller._w, "identify", "tab", event.x, event.y)
        if clicked_tab is 0:
            self.add_state()
        if clicked_tab is 1:
            self.import_state()

    def add_state(self):
        self.bottom_bar.configure_output(text="")
        self.bottom_bar.hide_all_buttons()
        self.bottom_bar.show_button(self.add_btn_id)

    def import_state(self):
        self.bottom_bar.configure_output(text="")
        self.bottom_bar.hide_all_buttons()
        self.bottom_bar.show_button(self.import_btn_id)

    def edit_state(self):
        self.bottom_bar.configure_output(text="")
        self.bottom_bar.hide_all_buttons()
        self.bottom_bar.show_button(self.edit_btn_id)

    def write_data(self):
        pass

    def add_sbjt_to_db(self):
        name = self.name.get().title()
        code = self.code.get().title()
        if self.validate_data(name, code):
            try:
                m_db.add_subject(name, code)
                self.bottom_bar.configure_output(text="Subject added to database", fg="green")
                self.clear_widgets()
            except db.sql.OperationalError:
                self.bottom_bar.configure_output(text="Error: Unable to add subject to database", fg=ERROR_COLOUR)

    @staticmethod
    def validate_data(name, code):
        if name == "":
            messagebox.showerror("Error", "Subject name cannot be left blank")
            return False
        if m_db.get_subject_id_from_subjects(name) is not None:
            messagebox.showerror("Error", "Subject name must be unique")
            return False
        if code == "":
            messagebox.showerror("Error", "Subject code cannot be left blank")
            return False
        if not m_db.check_sbjt_code_unique(code):
            messagebox.showerror("Error", "Subject code must be unique")
            return False
        return True

    def on_closing(self):
        try:
            self.closing_command()
        except TypeError:
            pass
        finally:
            self.destroy()


class ImportClassroomWindow(tk.Toplevel):
    """Top-level window to add and edit classroom"""
    def __init__(self, parent, clsrm_id=None, closing_command=None):
        super().__init__(parent)
        self.clsrm_id = clsrm_id
        self.title("Classroom")
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.closing_command = closing_command

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        container = tk.Frame(self, bg=BG_COLOUR)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        container.grid(row=0, column=0, sticky="nsew")

        style = ttk.Style()
        style.configure("BW.TNotebook", background=BG_COLOUR)
        style.configure("BW.TFrame", background=BG_COLOUR)

        self.tab_controller = ttk.Notebook(container, style="BW.TNotebook")
        self.tab_controller.bind('<Button-1>', self.tab_handler)

        add_classroom_tab = ttk.Frame(self.tab_controller)

        name_label_frame = ttk.LabelFrame(add_classroom_tab, text="Classroom:")
        name_label_frame.grid_rowconfigure(0, weight=1)
        name_label_frame.grid_rowconfigure(9999, weight=1)
        name_label_frame.grid_columnconfigure(0, weight=1)
        name_label_frame.grid_columnconfigure(9999, weight=1)
        tk.Label(name_label_frame, text="Name:").grid(row=1, column=1, sticky="w")
        self.name = tk.StringVar()
        tk.Entry(name_label_frame, textvariable=self.name).grid(row=2, column=1, sticky="ew")
        tk.Label(name_label_frame, text="Size:").grid(row=3, column=1, sticky="w")
        self.size = tk.StringVar()
        tk.Entry(name_label_frame, textvariable=self.size).grid(row=4, column=1, sticky="ew")
        name_label_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        subjects_label_frame = ttk.LabelFrame(add_classroom_tab, text="Subjects:")
        self.sbjts_frame = SubjectCheckButtonFrame(subjects_label_frame, background=TTK_DEFAULT_COLOUR)
        self.sbjts_frame.display_subjects(year_id="*")
        self.sbjts_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        subjects_label_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=5, pady=5)

        self.import_clsrms_tab = ttk.Frame(self.tab_controller)
        self.import_clsrms_tab.grid_rowconfigure(0, weight=1)
        self.import_clsrms_tab.grid_rowconfigure(9999, weight=1)
        self.import_clsrms_tab.grid_columnconfigure(0, weight=1)
        self.import_clsrms_tab.grid_columnconfigure(9999, weight=1)
        self.sheet = None
        self.import_button = ttk.Button(self.import_clsrms_tab, text="Select File", command=self.import_data)
        self.import_button.grid(row=1, column=1)

        self.tab_controller.add(add_classroom_tab, text="Add")
        self.tab_controller.add(self.import_clsrms_tab, text="Import")
        self.tab_controller.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.bottom_bar = cw.BottomBar(self)
        self.add_btn_id = self.bottom_bar.add_button(text="Add", command=self.add_clsrm_to_db, state="active")
        self.import_btn_id = self.bottom_bar.add_button(text="Import", command=self.write_data, state="disabled")
        self.edit_btn_id = self.bottom_bar.add_button(text="Edit", command=self.edit_clsrm_in_db, state="active")
        self.bottom_bar.show_button(self.add_btn_id)
        self.bottom_bar.grid(row=1, column=0)

        if self.clsrm_id is not None:
            self.configure_edit()

        self.mainloop()

    @staticmethod
    def import_data():
        """direct_path = os.path.dirname(os.path.realpath(__file__))
        filename = filedialog.askopenfilename(initialdir=direct_path, title="Open",
                                              filetypes=(("All files", "*.*"),
                                                         ("SQL files", "*.sql")))
        if filename != "":
            self.import_button.grid_remove()
        self.sheet = cw.SpreadSheetFrame(self.import_clsrms_tab, rows=30, columns=5)
        self.sheet.grid(row=2, column=1)"""
        messagebox.showinfo("Message", "This feature is not yet currently working")

    def configure_edit(self, clsrm_id=None):
        if clsrm_id is not None:
            self.clsrm_id = clsrm_id
        sbjt_data = m_db.get_classroom_data(self.clsrm_id)
        self.name.set(sbjt_data[1])
        self.size.set(sbjt_data[2])
        self.edit_state()

    def edit_clsrm_in_db(self):
        name = self.name.get().title()
        size = self.size.get()
        sbjt_ids = self.sbjts_frame.get_selected_subjects()
        if self.validate_data(name, size, sbjt_ids):
            try:
                m_db.update_classroom(self.clsrm_id, name, size)
                m_db.delete_classroom_subjects(self.clsrm_id)
                m_db.add_classroom_subjects(self.clsrm_id, *sbjt_ids)
                self.bottom_bar.configure_output(text="Classroom successfully edited", fg="green")
                self.clear_widgets()
                self.on_closing()
            except db.sql.OperationalError:
                self.bottom_bar.configure_output(text="Error: Unable to edit classroom in database", fg=ERROR_COLOUR)

    def clear_widgets(self):
        self.name.set("")
        self.size.set("")
        self.sbjts_frame.clear_selected_subjects()

    def tab_handler(self, event):
        clicked_tab = self.tab_controller.tk.call(self.tab_controller._w, "identify", "tab", event.x, event.y)
        if clicked_tab is 0:
            self.add_state()
        if clicked_tab is 1:
            self.import_state()

    def add_state(self):
        self.bottom_bar.configure_output(text="")
        self.bottom_bar.hide_all_buttons()
        self.bottom_bar.show_button(self.add_btn_id)

    def import_state(self):
        self.bottom_bar.configure_output(text="")
        self.bottom_bar.hide_all_buttons()
        self.bottom_bar.show_button(self.import_btn_id)

    def edit_state(self):
        self.bottom_bar.configure_output(text="")
        self.bottom_bar.hide_all_buttons()
        self.bottom_bar.show_button(self.edit_btn_id)

    def write_data(self):
        pass

    def add_clsrm_to_db(self):
        name = self.name.get().title()
        size = self.size.get()
        sbjt_ids = self.sbjts_frame.get_selected_subjects()
        if self.validate_data(name, size, sbjt_ids):
            try:
                clsrm_id = m_db.add_classroom(name, size)
                m_db.add_classroom_subjects(clsrm_id, *sbjt_ids)
                self.bottom_bar.configure_output(text="Classroom added to database", fg="green")
                self.clear_widgets()
            except db.sql.OperationalError:
                self.bottom_bar.configure_output(text="Error: Unable to add classroom to database", fg=ERROR_COLOUR)

    @staticmethod
    def validate_data(name, size, sbjt_ids):
        if name == "":
            messagebox.showerror("Error", "Classroom name cannot be left blank")
            return False
        if not m_db.check_classroom_name_unique(name):
            messagebox.showerror("Error", "Classroom name must be unique")
            return False
        if size.isdigit():
            if int(size) <= 0:
                messagebox.showerror("Error", "Classroom size must be larger than zero")
                return False
        else:
            messagebox.showerror("Error", "Classroom size must be a number")
            return False
        if len(sbjt_ids) == 0:
            messagebox.showerror("Error", "Classroom must have at least one subject")
            return False
        return True

    def on_closing(self):
        try:
            self.closing_command()
        except TypeError:
            pass
        finally:
            self.destroy()


class ImportTeacherWindow(tk.Toplevel):
    def __init__(self, parent, teacher_id=None, closing_command=None):
        super().__init__(parent)
        self.teacher_id = teacher_id
        self.title("Teacher")
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.closing_command = closing_command

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        container = tk.Frame(self, bg=BG_COLOUR)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        container.grid(row=0, column=0, sticky="nsew")

        style = ttk.Style()
        style.configure("BW.TNotebook", background=BG_COLOUR)
        style.configure("BW.TFrame", background=BG_COLOUR)

        self.tab_controller = ttk.Notebook(container, style="BW.TNotebook")
        self.tab_controller.bind('<Button-1>', self.tab_handler)

        add_teacher_tab = ttk.Frame(self.tab_controller)
        # add_student_tab.grid_rowconfigure(0, weight=1)
        # add_student_tab.grid_columnconfigure(0, weight=1)

        name_label_frame = ttk.LabelFrame(add_teacher_tab, text="Name:")
        name_label_frame.grid_rowconfigure(0, weight=1)
        name_label_frame.grid_rowconfigure(9999, weight=1)
        name_label_frame.grid_columnconfigure(0, weight=1)
        name_label_frame.grid_columnconfigure(9999, weight=1)
        tk.Label(name_label_frame, text="Firstname:").grid(row=1, column=1, sticky="w")
        self.firstname = tk.StringVar()
        tk.Entry(name_label_frame, textvariable=self.firstname).grid(row=2, column=1, sticky="ew")
        tk.Label(name_label_frame, text="Surname:").grid(row=3, column=1, sticky="w")
        self.surname = tk.StringVar()
        tk.Entry(name_label_frame, textvariable=self.surname).grid(row=4, column=1, sticky="ew")
        name_label_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        passwords_label_frame = ttk.LabelFrame(add_teacher_tab, text="Password:")
        passwords_label_frame.grid_rowconfigure(0, weight=1)
        passwords_label_frame.grid_rowconfigure(9999, weight=1)
        passwords_label_frame.grid_columnconfigure(0, weight=1)
        passwords_label_frame.grid_columnconfigure(9999, weight=1)
        tk.Label(passwords_label_frame, text="Password:").grid(row=1, column=1, sticky="w")
        self.password = tk.StringVar()
        tk.Entry(passwords_label_frame, textvariable=self.password).grid(row=2, column=1, sticky="ew")
        tk.Label(passwords_label_frame, text="Repeat Password:").grid(row=3, column=1, sticky="w")
        self.password_repeat = tk.StringVar()
        tk.Entry(passwords_label_frame, textvariable=self.password_repeat).grid(row=4, column=1, sticky="ew")
        tk.Label(passwords_label_frame,
                 text="Note: If passwords are left\nblank then the password\nwill be set as default").grid(row=5, column=1)
        passwords_label_frame.grid(row=1, column=0, rowspan=2, sticky="nsew", padx=5, pady=5)

        subjects_label_frame = ttk.LabelFrame(add_teacher_tab, text="Subjects:")
        self.subjects_frame = SubjectCheckButtonFrame(subjects_label_frame, background=TTK_DEFAULT_COLOUR)
        self.subjects_frame.display_subjects(year_id="*")
        self.subjects_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        subjects_label_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=5, pady=5)

        code_label_frame = ttk.LabelFrame(add_teacher_tab, text="Code:")
        tk.Label(code_label_frame, text="Code:").grid(row=0, column=0, sticky="w")
        self.code = tk.StringVar()
        tk.Entry(code_label_frame, textvariable=self.code).grid(row=1, column=0, sticky="ew")
        code_label_frame.grid(row=2, column=1, sticky="nsew", padx=5, pady=5)

        email_label_frame = ttk.LabelFrame(add_teacher_tab, text="Email:")
        email_label_frame.grid_rowconfigure(0, weight=1)
        email_label_frame.grid_rowconfigure(9999, weight=1)
        email_label_frame.grid_columnconfigure(0, weight=1)
        email_label_frame.grid_columnconfigure(9999, weight=1)
        self.email = tk.StringVar()
        tk.Entry(email_label_frame, width=15, textvariable=self.email).grid(row=1, column=1, sticky="ew")
        tk.Label(email_label_frame,
                 text="Note: If the email is left blank then the teachers email will be set as default").grid(row=2, column=1)
        email_label_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

        self.import_tchrs_tab = ttk.Frame(self.tab_controller)
        self.import_tchrs_tab.grid_rowconfigure(0, weight=1)
        self.import_tchrs_tab.grid_rowconfigure(9999, weight=1)
        self.import_tchrs_tab.grid_columnconfigure(0, weight=1)
        self.import_tchrs_tab.grid_columnconfigure(9999, weight=1)
        self.sheet = None
        self.import_button = ttk.Button(self.import_tchrs_tab, text="Select File", command=self.import_data)
        self.import_button.grid(row=1, column=1)

        self.tab_controller.add(add_teacher_tab, text="Add")
        self.tab_controller.add(self.import_tchrs_tab, text="Import")
        self.tab_controller.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.bottom_bar = cw.BottomBar(self)
        self.button1_id = self.bottom_bar.add_button(text="Add", command=self.add_teacher_to_database, state="active")
        self.button2_id = self.bottom_bar.add_button(text="Import", command=self.write_data, state="disabled")
        self.bottom_bar.show_button(self.button1_id)
        self.bottom_bar.grid(row=1, column=0, sticky="ew")
        self.mainloop()

    @staticmethod
    def import_data():
        """direct_path = os.path.dirname(os.path.realpath(__file__))
        filename = filedialog.askopenfilename(initialdir=direct_path, title="Open",
                                              filetypes=(("All files", "*.*"),
                                                         ("SQL files", "*.sql")))
        if filename != "":
            self.import_button.grid_remove()
        self.sheet = cw.SpreadSheetFrame(self.import_tchrs_tab, rows=30, columns=5)
        self.sheet.grid(row=2, column=1)"""
        messagebox.showinfo("Message", "This feature is not yet currently working")

    @staticmethod
    def configure_edit():
        data = m_db.get_teacher_by_id(None)
        """Working progress"""

    def clear_widgets(self):
        self.firstname.set("")
        self.surname.set("")
        self.code.set("")
        self.password.set("")
        self.password_repeat.set("")
        self.email.set("")
        self.subjects_frame.clear_selected_subjects()

    def tab_handler(self, event):
        clicked_tab = self.tab_controller.tk.call(self.tab_controller._w, "identify", "tab", event.x, event.y)
        if clicked_tab is 0:
            self.add_state()
        if clicked_tab is 1:
            self.import_state()

    def add_state(self):
        self.bottom_bar.configure_output(text="")
        self.bottom_bar.hide_all_buttons()
        self.bottom_bar.show_button(self.button1_id)

    def import_state(self):
        self.bottom_bar.configure_output(text="")
        self.bottom_bar.hide_all_buttons()
        self.bottom_bar.show_button(self.button2_id)

    def write_data(self):
        pass

    def configure_data(self):
        data = []
        firstname, surname = self.firstname.get(), self.surname.get()
        code = self.code.get()
        if code == "":
            data.append((firstname[:1]+surname[:2]).upper())
        else:
            data.append(code)
        email = self.email.get()
        if email == "":
            suffix = m_db.get_email_suffix()
            gen_email = (surname+"."+firstname[:1]).lower()
            if m_db.check_email_unique(gen_email+suffix) is not None:
                code = 1
                while m_db.check_email_unique(gen_email+str(code)+suffix) is not None:
                    code += 1
                data.append(gen_email+str(code)+suffix)
            else:
                data.append(gen_email+suffix)
        else:
            data.append(email)
        data.append(firstname)
        data.append(surname)
        password = self.password.get()
        if password == "":
            data.append(m_db.get_default_password())
        else:
            data.append(hash_(password))
        subjects = self.subjects_frame.get_selected_subjects()
        subject_ids = []
        for subject in subjects:
            subject_ids.append(m_db.get_subject_id_from_subjects(subject))
        data.append(tuple(subject_ids))
        return tuple(data)

    def add_teacher_to_database(self):
        if self.validate_data():
            try:
                m_db.add_teacher(*self.configure_data())
                self.bottom_bar.configure_output(text="Teacher added to database", fg="green")
                self.clear_widgets()
            except db.sql.OperationalError:
                self.bottom_bar.configure_output(text="Error: Unable to add teacher to database", fg=ERROR_COLOUR)

    def validate_data(self):
        if self.firstname.get() == "" or self.surname.get() == "":
            messagebox.showerror("Error", "Firstname and Surname cannot be left blank")
            return False
        elif self.password.get() != self.password_repeat.get():
            messagebox.showerror("Error", "Passwords do not match")
            return False
        elif self.code.get() == "" and len(self.surname.get()) < 3:
            messagebox.showerror("Error", "Code required as surname to short")
            return False
        elif len(self.subjects_frame.get_selected_subjects()) == 0:
            messagebox.showerror("Error", "Teachers must be able to teach at least one subject")
            return False
        elif m_db.check_email_unique(self.email.get()) is not None:
            messagebox.showerror("Error", "Email already taken")
        return True

    def on_closing(self):
        try:
            self.closing_command()
        except TypeError:
            pass
        finally:
            self.destroy()


class ImportStudentTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(9999, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(9999, weight=1)
        self.sheet = None
        self.import_button = ttk.Button(self, text="Select File", command=self.import_data)
        self.import_button.grid(row=1, column=1)

    @staticmethod
    def import_data():
        """direct_path = os.path.dirname(os.path.realpath(__file__))
        filename = filedialog.askopenfilename(initialdir=direct_path, title="Open",
                                              filetypes=(("All files", "*.*"),
                                                         ("SQL files", "*.sql")))
        if filename != "":
            self.import_button.grid_remove()
        self.sheet = cw.SpreadSheetFrame(self.import_tchrs_tab, rows=30, columns=5)
        self.sheet.grid(row=2, column=1)"""
        messagebox.showinfo("Message", "This feature is not yet currently working")


class AddStudentTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.stdt_id = None
        name_label_frame = ttk.LabelFrame(self, text="Name:")
        name_label_frame.grid_rowconfigure(0, weight=1)
        name_label_frame.grid_rowconfigure(9999, weight=1)
        name_label_frame.grid_columnconfigure(0, weight=1)
        name_label_frame.grid_columnconfigure(9999, weight=1)
        tk.Label(name_label_frame, text="Firstname:").grid(row=1, column=1, sticky="w")
        self.firstname = tk.StringVar()
        tk.Entry(name_label_frame, textvariable=self.firstname).grid(row=2, column=1, sticky="ew")
        tk.Label(name_label_frame, text="Surname:").grid(row=3, column=1, sticky="w")
        self.surname = tk.StringVar()
        tk.Entry(name_label_frame, textvariable=self.surname).grid(row=4, column=1, sticky="ew")
        name_label_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        year_group_label_frame = ttk.LabelFrame(self, text="Year Group:")
        self.year_group = tk.StringVar()
        self.year_group.set("Select Year Group")
        year_values = []
        try:
            year_values = m_db.get_year_values_with_id()
        except AttributeError:
            pass
        self.year_id_map = {}
        for year in year_values:
            self.year_id_map[str(year[1])] = year[0]
        combobox = ttk.Combobox(year_group_label_frame,
                                textvariable=self.year_group,
                                state="readonly",
                                values=list(self.year_id_map.keys()))
        combobox.bind("<<ComboboxSelected>>", self.update_subject_frame)
        combobox.grid()
        year_group_label_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        subjects_label_frame = ttk.LabelFrame(self, text="Subjects:")
        self.subjects_frame = SubjectCheckButtonFrame(subjects_label_frame, background=TTK_DEFAULT_COLOUR)
        self.subjects_frame.disable_all()
        self.subjects_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        subjects_label_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=5, pady=5)

        email_label_frame = ttk.LabelFrame(self, text="Email:")
        email_label_frame.grid_rowconfigure(0, weight=1)
        email_label_frame.grid_rowconfigure(9999, weight=1)
        email_label_frame.grid_columnconfigure(0, weight=1)
        email_label_frame.grid_columnconfigure(9999, weight=1)
        self.email = tk.StringVar()
        tk.Entry(email_label_frame, width=15, textvariable=self.email).grid(row=1, column=1, sticky="ew")
        tk.Label(email_label_frame,
                 text="Note: If the email is left blank then the\nstudents email will set as default").grid(row=2,
                                                                                                            column=1)
        email_label_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)

    def configure_edit(self, stdt_id=None):
        if stdt_id is not None:
            self.stdt_id = stdt_id
        stdt_data = m_db.get_student_data(self.stdt_id)
        self.firstname.set(stdt_data[1])
        self.surname.set(stdt_data[2])
        self.email.set(stdt_data[4])
        self.year_group.set(reverse_map_dict(self.year_id_map, stdt_data[3]))
        self.subjects_frame.display_subjects(stdt_data[3])
        stdt_sbjts = m_db.get_student_subjects(self.stdt_id)
        self.subjects_frame.set_selected_subjects(stdt_sbjts)

    def update_subject_frame(self, event):
        year_id = self.year_id_map[self.year_group.get()]
        if m_db.check_year_option(year_id) == 1:
            self.subjects_frame.update_subjects(year_id)
            self.subjects_frame.enable_all()
        else:
            self.subjects_frame.disable_all()

    def clear_widgets(self):
        self.firstname.set("")
        self.surname.set("")
        self.year_group.set("Select Year Group")
        self.email.set("")
        self.subjects_frame.clear_selected_subjects()
        self.subjects_frame.disable_all()

    def get_widget_values(self):
        if self.year_group.get() in self.year_id_map.keys():
            year_id = self.year_id_map[self.year_group.get()]
        else:
            year_id = None
        if m_db.check_year_option(year_id) == 1:
            return self.firstname.get(),\
                   self.surname.get(),\
                   year_id,\
                   self.email.get(),\
                   self.subjects_frame.get_selected_subjects()
        return self.firstname.get(), self.surname.get(), year_id, self.email.get(), None


class ImportStudentWindow(tk.Toplevel):
    def __init__(self, parent, stdt_id=None, closing_command=None):
        super().__init__(parent)
        self.stdt_id = stdt_id
        self.title("Students")
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.closing_command = closing_command

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        container = tk.Frame(self, bg=BG_COLOUR)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        container.grid(row=0, column=0, sticky="nsew")

        style = ttk.Style()
        style.configure("BW.TNotebook", background=BG_COLOUR)
        style.configure("BW.TFrame", background=BG_COLOUR)

        self.tab_map = {}
        self.tab_controller = ttk.Notebook(container, style="BW.TNotebook")
        self.tab_controller.bind("<<NotebookTabChanged>>", self.tab_handler)

        self.add_student_tab = AddStudentTab(self.tab_controller)
        self.import_students_tab = ImportStudentTab(self.tab_controller)

        self.tab_controller.add(self.add_student_tab, text="Add")
        self.tab_map["Add"] = self.add_state
        self.tab_controller.add(self.import_students_tab, text="Import")
        self.tab_map["Import"] = self.import_state
        self.tab_controller.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.bottom_bar = cw.BottomBar(self)
        self.button1_id = self.bottom_bar.add_button(text="Add", command=self.add_stdt_to_db, state="active")
        self.button2_id = self.bottom_bar.add_button(text="Import", command=self.write_data, state="disabled")
        self.button3_id = self.bottom_bar.add_button(text="Edit", command=self.edit_stdt_in_db, state="active")
        self.bottom_bar.show_button(self.button1_id)
        self.bottom_bar.grid(row=1, column=0, sticky="ew")
        if self.stdt_id is not None:
            self.config_edit()
        self.mainloop()

    def config_edit(self, stdt_id=None):
        if stdt_id is not None:
            self.stdt_id = stdt_id
        self.add_student_tab.configure_edit(self.stdt_id)
        self.bottom_bar.hide_all_buttons()
        self.bottom_bar.show_button(self.button3_id)

    def tab_handler(self, event):
        # clicked_tab = self.tab_controller.tk.call(self.tab_controller._w, "identify", "tab", event.x, event.y)
        clicked_tab = event.widget.tab(event.widget.select(), "text")
        command = self.tab_map[clicked_tab]
        command()

    def add_state(self):
        self.bottom_bar.configure_output(text="")
        self.bottom_bar.hide_all_buttons()
        if self.stdt_id is None:
            self.bottom_bar.show_button(self.button1_id)
        else:
            self.bottom_bar.show_button(self.button3_id)

    def import_state(self):
        self.bottom_bar.configure_output(text="")
        self.bottom_bar.hide_all_buttons()
        self.bottom_bar.show_button(self.button2_id)

    def write_data(self):
        pass

    def add_stdt_to_db(self):
        firstname, surname, year_id, email, subjects = self.add_student_tab.get_widget_values()
        if self.validate_data(firstname, surname, year_id, email, subjects):
            try:
                if subjects is not None:
                    m_db.add_student(firstname, surname, year_id, email, subjects=subjects)
                else:
                    m_db.add_student(firstname, surname, year_id, email)
                self.bottom_bar.configure_output(text="Student added to database", fg="green")
                self.add_student_tab.clear_widgets()
            except db.sql.OperationalError:
                self.bottom_bar.configure_output(text="Error: Unable to add student to database", fg=ERROR_COLOUR)

    def edit_stdt_in_db(self):
        firstname, surname, year_id, email, subjects = self.add_student_tab.get_widget_values()
        if self.validate_data(firstname, surname, year_id, email, subjects):
            try:
                if subjects is not None:
                    m_db.update_student(self.stdt_id, firstname, surname, year_id, email, subjects=subjects)
                else:
                    m_db.update_student(self.stdt_id, firstname, surname, year_id, email)
                self.bottom_bar.configure_output(text="Edit successful", fg="green")
                self.on_closing()
            except db.sql.OperationalError:
                self.bottom_bar.configure_output(text="Error: Unable to edit student", fg=ERROR_COLOUR)

    def on_closing(self):
        try:
            self.closing_command()
        except TypeError:
            pass
        finally:
            self.destroy()

    @staticmethod
    def validate_data(firstname, surname, year_group, email, subjects):
        """Email validation needs to be added here as well as making sure it is unique"""
        if firstname == "" or surname == "":
            messagebox.showerror("Error", "Valid name not entered")
            return False
        elif year_group not in m_db.get_all_year_ids():
            messagebox.showerror("Error", "Year group not selected")
            return False
        elif email == "":
            messagebox.showerror("Error", "No email entered")
            return False
        else:
            if subjects is not None:
                if len(subjects) > 4:
                    messagebox.showerror("Error", "A student can not study more than 4 subjects")
                    return False
                elif len(subjects) < 3:
                    messagebox.showerror("Error", "A student must study at least 3 subjects")
                    return False
        return True


class TimetablePage(tk.Frame):
    """Displays the users timetable and leads to other areas of functionality"""
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOUR)
        self.controller = controller
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        search_frame = tk.Frame(self, borderwidth=2, relief="sunken", bg=BG_COLOUR)
        search_frame.grid_rowconfigure(1, weight=1)
        self.query = None
        self.search_var = tk.StringVar()
        self.search_box = tk.Entry(search_frame, width=40, textvariable=self.search_var)
        self.search_box.bind("<Return>", self.search)
        self.search_box.grid(row=0, column=0, columnspan=2, padx=10, pady=5)
        self.search_btn = tk.Label(search_frame, text="Search")
        self.search_btn.bind("<Button-1>", self.search)
        self.search_btn.grid(row=0, column=2, padx=10, pady=5, sticky="we")
        filters_frame = ttk.LabelFrame(search_frame, text="Filters")
        filters_frame.grid_columnconfigure(0, weight=1)
        search_frame.grid_rowconfigure(2, weight=1)

        self.radio_var = tk.IntVar(value=0)
        self.radio_btns = {}
        result_types = ["Students", "Teachers", "Classrooms"]
        for type_id, result in enumerate(result_types, 0):
            self.radio_btns[type_id] = tk.Radiobutton(filters_frame,
                                                      text=result,
                                                      variable=self.radio_var,
                                                      value=type_id,
                                                      command=self.update_filters)
            self.radio_btns[type_id].grid(row=type_id, column=0, sticky="w", pady=3)
        filters_frame.grid(row=1, column=0, sticky="nwe", padx=5, pady=5)

        table_frame = ttk.LabelFrame(search_frame, text="Results")
        table_frame.grid_rowconfigure(0, weight=1)

        self.tbl_container = cw.CreateContainer(table_frame, self, self.controller)
        self.tbl_container.grid(row=0, column=0, sticky="ns", padx=5, pady=5)

        self.tbl_val_map = {}

        self.stdt_id_map = {}
        self.stdt_tbl = cw.VerticalTable(self.tbl_container, ("Firstname", "Surname", "Year"))
        self.stdt_tbl.add_pop_up_menu(("Add", None),
                                      ("Edit", self.edit_stdt),
                                      ("Delete", self.delete_stdt))
        self.stdt_tbl.add_bind("<Button-1>", self.update_stdt_timetable)
        self.tbl_container.add_init_page(self.stdt_tbl)
        self.tbl_val_map[0] = self.stdt_tbl

        self.tchr_id_map = {}
        self.tchr_tbl = cw.VerticalTable(self.tbl_container, ("Firstname", "Surname", "Code"))
        self.tchr_tbl.add_pop_up_menu(("Add", None),
                                      ("Edit", self.edit_tchr),
                                      ("Delete", self.delete_tchr))
        self.tchr_tbl.add_bind("<Button-1>", self.update_tchr_timetable)
        self.tbl_container.add_init_page(self.tchr_tbl)
        self.tbl_val_map[1] = self.tchr_tbl

        self.clsrm_id_map = {}
        self.clsrm_tbl = cw.VerticalTable(self.tbl_container, ("Name", "Size"))
        self.clsrm_tbl.add_pop_up_menu(("Add", None),
                                       ("Edit", self.edit_clsrm),
                                       ("Delete", self.delete_clsrm))
        self.clsrm_tbl.add_bind("<Button-1>", self.update_clsrm_timetable)
        self.tbl_container.add_init_page(self.clsrm_tbl)
        self.tbl_val_map[2] = self.clsrm_tbl

        table_frame.grid(row=1, column=1, columnspan=2, rowspan=2, padx=5, pady=5, sticky="nsew")
        search_frame.grid(row=0, column=0, sticky="nsew")

        timetable_frame = cw.ScrolledFrame(self, borderwidth=2, relief="sunken")

        self.time_tbl_container = cw.CreateContainer(timetable_frame.interior, self, self.controller)
        self.time_tbl_container.grid(row=0, column=0)

        self.time_tbl_val_map = {}

        self.stdt_time_tbl = StudentTimetable(self.time_tbl_container)
        self.time_tbl_container.add_init_page(self.stdt_time_tbl)
        self.time_tbl_val_map[0] = self.stdt_time_tbl

        self.tchr_time_tbl = TeacherTimetable(self.time_tbl_container)
        self.time_tbl_container.add_init_page(self.tchr_time_tbl)
        self.time_tbl_val_map[1] = self.tchr_time_tbl

        self.clsrm_time_tbl = ClassroomTimetable(self.time_tbl_container)
        self.time_tbl_container.add_init_page(self.clsrm_time_tbl)
        self.time_tbl_val_map[2] = self.clsrm_time_tbl

        timetable_frame.grid(row=0, column=1, sticky="nsew")

        bottom_bar = cw.BottomBar(self)
        bottom_bar.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.update_filters()

    def update_filters(self):
        val = self.radio_var.get()
        tbl = self.tbl_val_map[val]
        time_tbl = self.time_tbl_val_map[val]
        self.tbl_container.show_init_frame(tbl)
        self.time_tbl_container.show_init_frame(time_tbl)

    def search(self, event):
        self.query = self.search_var.get()
        self.populate_stdt_tbl()
        self.populate_tchr_tbl()
        self.populate_clsrm_tbl()

    def get_stdt_id(self):
        try:
            return self.stdt_id_map[self.stdt_tbl.get_selected_row_id()]
        except KeyError:
            return None

    def get_tchr_id(self):
        try:
            return self.tchr_id_map[self.tchr_tbl.get_selected_row_id()]
        except KeyError:
            return None

    def get_clsrm_id(self):
        try:
            return self.clsrm_id_map[self.clsrm_tbl.get_selected_row_id()]
        except KeyError:
            return None

    def populate_stdt_tbl(self):
        self.stdt_id_map.clear()
        self.stdt_tbl.clear_table()
        data = m_db.search_students(self.query)
        if data is None:
            return
        for result in data:
            self.stdt_id_map[self.stdt_tbl.add_row(result[1], result[2], result[3])] = result[0]

    def populate_tchr_tbl(self):
        self.tchr_id_map.clear()
        self.tchr_tbl.clear_table()
        data = m_db.search_teachers(self.query)
        if data is None:
            return
        for result in data:
            self.tchr_id_map[self.tchr_tbl.add_row(result[1], result[2], result[3])] = result[0]

    def populate_clsrm_tbl(self):
        self.clsrm_id_map.clear()
        self.clsrm_tbl.clear_table()
        data = m_db.search_classrooms(self.query)
        if data is None:
            return
        for result in data:
            self.clsrm_id_map[self.clsrm_tbl.add_row(result[1], result[2])] = result[0]

    def update_stdt_timetable(self, event):
        stdt_id = self.get_stdt_id()
        self.stdt_time_tbl.show_stdt_timetable(stdt_id)

    def update_tchr_timetable(self, event):
        tchr_id = self.get_tchr_id()
        self.tchr_time_tbl.show_tchr_timetable(tchr_id)

    def update_clsrm_timetable(self, event):
        clsrm_id = self.get_clsrm_id()
        self.clsrm_time_tbl.show_clsrm_timetable(clsrm_id)

    def edit_stdt(self):
        stdt_id = self.get_stdt_id()
        ImportStudentWindow(self.controller, stdt_id=stdt_id, closing_command=self.populate_stdt_tbl)

    def edit_tchr(self):
        tchr_id = self.get_tchr_id()
        ImportTeacherWindow(self.controller, teacher_id=tchr_id, closing_command=self.populate_tchr_tbl)

    def edit_clsrm(self):
        clsrm_id = self.get_clsrm_id()
        ImportClassroomWindow(self.controller, clsrm_id=clsrm_id, closing_command=self.populate_clsrm_tbl)

    def delete_stdt(self):
        stdt_id = self.get_stdt_id()
        if stdt_id is None:
            return
        if messagebox.askokcancel("Warning", "Are you sure you want to delete this student?"):
            m_db.delete_student(stdt_id)
            self.populate_stdt_tbl()

    def delete_tchr(self):
        tchr_id = self.get_tchr_id()
        if tchr_id is None:
            return
        if messagebox.askokcancel("Warning", "Are you sure you want to delete this teacher?"):
            m_db.delete_teacher(tchr_id)
            self.populate_tchr_tbl()

    def delete_clsrm(self):
        clsrm_id = self.get_clsrm_id()
        if clsrm_id is None:
            return
        if messagebox.askokcancel("Warning", "Are you sure you want to delete this classroom?"):
            m_db.delete_classroom(clsrm_id)
            self.populate_clsrm_tbl()

    def refresh_all(self):
        """Updates the page to changes in database"""
        self.populate_stdt_tbl()
        self.populate_tchr_tbl()
        self.populate_clsrm_tbl()


class EditTimetablePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOUR)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.controller = controller

        style = ttk.Style()
        style.configure("BW.TNotebook", background=BG_COLOUR)
        style.configure("BW.TFrame", background=BG_COLOUR)

        self.tab_controller = ttk.Notebook(self, style="BW.TNotebook")
        self.tab_controller.bind('<Button-1>', self.tab_handler)

        self.cycle_tab = CycleTab(self.tab_controller, controller)
        self.model_tab = ModelTab(self.tab_controller, controller)
        self.classes_tab = ClassesTab(self.tab_controller, controller)
        self.analysis_tab = AnalysisTab(self.tab_controller, controller)
        self.timetable_tab = TimetableTab(self.tab_controller, controller)

        self.tab_controller.add(self.cycle_tab, text="Cycle")
        self.tab_controller.add(self.model_tab, text="Model")
        self.tab_controller.add(self.classes_tab, text="Classes")
        self.tab_controller.add(self.analysis_tab, text="Analysis")
        self.tab_controller.add(self.timetable_tab, text="Timetable")
        self.tab_controller.grid(row=0, sticky="nsew")

        self.bottom_bar = cw.BottomBar(self)
        self.clss_btn = self.bottom_bar.add_button(text="Create Classes",
                                                   command=self._create_class_window)
        self.timetable_btn = self.bottom_bar.add_button(text="Create Timetable",
                                                        command=None)
        self.bottom_bar.grid(row=1)

    def _create_class_window(self):
        """Needs work..."""

        def process(window):
            algorithm.Classes(m_db).create_classes()
            window.destroy()
        ProgressWindow(self.controller, title="Classes", process=process)

    def tab_handler(self, event):
        clicked_tab = self.tab_controller.tk.call(self.tab_controller._w, "identify", "tab", event.x, event.y)
        self.bottom_bar.hide_all_buttons()
        if clicked_tab is 0:
            self.cycle_tab.refresh()
        elif clicked_tab is 1:
            self.model_tab.refresh()
            self.bottom_bar.show_button(self.clss_btn)
        elif clicked_tab is 2:
            self.classes_tab.refresh()
            self.bottom_bar.show_button(self.timetable_btn)
        elif clicked_tab is 3:
            pass
            # self.analysis_tab
        elif clicked_tab is 4:
            pass
            # self.timetable_tab

    def refresh_all(self):
        self.cycle_tab.refresh()
        self.model_tab.refresh()
        self.classes_tab.refresh()
        # self.analysis_tab.refresh()
        # self.timetable_tab.refresh()


class CycleTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        side_frame = tk.Frame(self, borderwidth=2, relief="sunken")
        side_frame.grid_rowconfigure(1, weight=1)

        cycle_settings = ttk.LabelFrame(side_frame, text="Cycle Settings")
        cycle_settings.grid_columnconfigure(0, weight=1)
        cycle_settings.grid_columnconfigure(9999, weight=1)
        periods_label = tk.Label(cycle_settings, text="Number of periods:")
        periods_label.grid(row=0, column=1)
        self.periods = tk.StringVar()
        self.periods.set("5")
        periods_entry = tk.Entry(cycle_settings, textvariable=self.periods, state="disabled", width=4)
        periods_entry.grid(row=0, column=2)
        period_len_label = tk.Label(cycle_settings, text="Period length:")
        period_len_label.grid(row=1, column=1)
        self.period_len = tk.StringVar()
        self.period_len.set("60")
        period_len_entry = tk.Entry(cycle_settings, textvariable=self.period_len, state="disabled", width=4)
        period_len_entry.grid(row=1, column=2)
        cycle_len_label = tk.Label(cycle_settings, text="Weeks in Cycle:")
        cycle_len_label.grid(row=2, column=1)
        self.cycle_len = tk.StringVar()
        self.cycle_len.set("2")
        cycle_len_entry = tk.Entry(cycle_settings, textvariable=self.cycle_len, state="disabled", width=4)
        cycle_len_entry.grid(row=2, column=2)
        cycle_settings.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.stdt_id_map = {}
        self.student_table = cw.VerticalTable(side_frame, ("ID", "Firstname", "Surname", "Year"))
        self.student_table.add_pop_up_menu(("Edit", self.call_stdt_window),
                                           ("Delete", self.delete_stdt))
        self.student_table.add_bind("<Button-1>", self.update_timetable)
        self.populate_student_table()
        self.student_table.grid(row=1, column=0, padx=5, pady=5, sticky="ns")

        side_frame.grid(row=0, column=0, sticky="ns")

        timetable_frame = cw.ScrolledFrame(self, framebackground="light grey", borderwidth=2, relief="sunken")
        timetable_frame.interior.config(bg="light grey")

        self.timetable = StudentTimetable(timetable_frame.interior)
        self.timetable.grid(row=0, column=0)

        timetable_frame.grid(row=0, column=1, sticky="nsew")

    def populate_student_table(self):
        try:
            students = m_db.get_all_students()
        except AttributeError:
            return
        self.stdt_id_map.clear()
        for student in students:
            self.stdt_id_map[self.student_table.add_row(str(student[0]), student[1], student[2], m_db.get_year_name(student[3]))] = student[0]

    def update_timetable(self, event):
        stdt_id = self.stdt_id_map[self.student_table.get_selected_row_id()]
        self.timetable.show_stdt_timetable(stdt_id)

    def call_stdt_window(self):
        stdt_id = self.stdt_id_map[self.student_table.get_selected_row_id()]
        ImportStudentWindow(self.controller, stdt_id=stdt_id, closing_command=self.refresh())

    def delete_stdt(self):
        try:
            stdt_id = self.stdt_id_map[self.student_table.get_selected_row_id()]
        except KeyError:
            return
        if messagebox.askokcancel("Warning", "Are you sure you want to delete this student?"):
            m_db.delete_student(stdt_id)
            self.refresh()

    def refresh(self):
        self.student_table.clear_table()
        self.populate_student_table()
        self.timetable.clear_table()


class ModelTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.yr_id, self.sbjt_id = None, None

        left_side_frame = tk.Frame(self, borderwidth=2, relief="sunken")
        left_side_frame.grid_rowconfigure(1, weight=1)
        year_label_frame = tk.LabelFrame(left_side_frame, text="Years:")
        year_label_frame.grid_rowconfigure(0, weight=1)
        year_label_frame.grid_rowconfigure(9999, weight=1)
        year_label_frame.grid_columnconfigure(0, weight=1)
        year_label_frame.grid_columnconfigure(9999, weight=1)
        add_year_button = tk.Button(year_label_frame, text="Add")
        add_year_button.grid(row=1, column=1)
        year_label_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        self.yr_id_map = {}
        self.year_table = cw.VerticalTable(left_side_frame, ("Name", "Value", "Options"))
        self.year_table.add_bind("<Button-1>", self.update_year_subjects)
        self.populate_year_table()
        self.year_table.grid(row=1, column=0, padx=5, pady=5, sticky="ns")
        left_side_frame.grid(row=0, column=0, sticky="ns")

        middle_frame = tk.Frame(self, borderwidth=2, relief="sunken")
        middle_frame.grid_columnconfigure(0, weight=1)
        middle_frame.grid_rowconfigure(1, weight=1)
        tk.Label(middle_frame, text="Year: ").grid(row=0, column=0, sticky="w")
        self.yr_name_lbl = tk.Label(middle_frame, text="")
        self.yr_name_lbl.grid(row=0, column=1, sticky="w")
        tk.Label(middle_frame, text="Total Periods: ").grid(row=0, column=2, sticky="w")
        self.num_periods_lbl = tk.Label(middle_frame, text="")
        self.num_periods_lbl.grid(row=0, column=3, sticky="w")
        self.yr_sbjt_map = {}
        self.yr_sbjt_table = cw.VerticalTable(middle_frame, ("Code", "Name", "Option", "Periods"))
        self.yr_sbjt_table.add_pop_up_menu(("Delete", self.delete_subject_year), ("Add", self.add_subject_year))
        # self.yr_sbjt_table.configure_column_weight()
        self.yr_sbjt_table.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky="nsew")
        middle_frame.grid(row=0, column=1, sticky="nsew")

        right_side_frame = tk.Frame(self, borderwidth=2, relief="sunken")
        right_side_frame.grid_rowconfigure(1, weight=1)
        subjects_label = tk.Label(right_side_frame, text="Subjects:")
        subjects_label.grid(row=0, column=0, sticky="nw")
        self.sbjt_id_map = {}
        self.subjects_table = cw.VerticalTable(right_side_frame, ("Code", "Name"))
        self.subjects_table.add_pop_up_menu(("Add", self.add_subject),
                                            ("Edit", self.edit_subject),
                                            ("Delete", self.delete_subject))
        self.populate_subjects_table()
        self.subjects_table.grid(row=1, column=0, padx=5, pady=5, sticky="ns")
        right_side_frame.grid(row=0, column=2, sticky="ns")

    def add_subject(self):
        self.controller.open_window(ImportSubjectWindow, closing_command=self.refresh_subjects_table)

    def edit_subject(self):
        sbjt_id = reverse_map_dict(self.sbjt_id_map, self.subjects_table.get_selected_row_id())
        ImportSubjectWindow(self.controller, subject_id=sbjt_id, closing_command=self.refresh_subjects_table)

    def delete_subject(self):
        sbjt_id = reverse_map_dict(self.sbjt_id_map, self.subjects_table.get_selected_row_id())
        if messagebox.askokcancel("Warning", "Are you sure you want to delete this subject?"):
            m_db.delete_subject(sbjt_id)
            self.refresh_subjects_table()

    def add_subject_year(self):
        self.sbjt_id = reverse_map_dict(self.sbjt_id_map, self.subjects_table.get_selected_row_id())
        try:
            m_db.add_subject_to_year(self.yr_id, self.sbjt_id, 0, 0)
        except db.sql.IntegrityError:
            if m_db.check_year_option(self.yr_id) == 1:
                try:
                    m_db.add_subject_to_year(self.yr_id, self.sbjt_id, 1, 0)
                except db.sql.IntegrityError:
                    messagebox.showwarning("Warning", "Maximum number of subjects reached")
            else:
                messagebox.showwarning("Warning", "Maximum number of subjects reached as year does allow for options")
        self.refresh_yr_sbjts_table()

    def delete_subject_year(self):
        if messagebox.askokcancel("Delete Subject", "Are you sure you want to delete selected subject?"):
            key = self.yr_sbjt_map[self.yr_sbjt_table.get_selected_row_id()]
            m_db.delete_subject_from_year(key[0], key[1], key[2])
            self.refresh_yr_sbjts_table()

    def update_year_subjects(self, event):
        self.yr_id = reverse_map_dict(self.yr_id_map, self.year_table.get_selected_row_id())
        self.num_periods_lbl.config(text=str(m_db.get_periods_in_year(self.yr_id)))
        self.yr_name_lbl.config(text=str(m_db.get_year_value(self.yr_id)))
        self.yr_sbjt_table.clear_table()
        self.populate_yr_sbjts_table()

    def populate_yr_sbjts_table(self):
        try:
            subjects = m_db.get_subject_data_by_year(self.yr_id)
        except AttributeError:
            return
        self.yr_sbjt_map.clear()
        self.yr_sbjt_table.reset_row_id()
        self.yr_sbjt_table.grid_remove()
        for subject in subjects:
            self.yr_sbjt_map[self.yr_sbjt_table.add_row(*subject[1:])] = (self.yr_id, subject[0], subject[3])
        self.yr_sbjt_table.grid()

    def populate_year_table(self):
        try:
            years = m_db.get_all_year_data()
        except AttributeError:
            return
        self.yr_id_map.clear()
        self.year_table.reset_row_id()
        for year in years:
            self.yr_id_map[year[0]] = self.year_table.add_row(year[1], year[2], year[3])

    def populate_subjects_table(self):
        try:
            subjects = m_db.get_all_subject_data()
        except AttributeError:
            return
        self.sbjt_id_map.clear()
        self.subjects_table.reset_row_id()
        for subject in subjects:
            self.sbjt_id_map[subject[0]] = self.subjects_table.add_row(subject[1], subject[2])

    def refresh_yr_sbjts_table(self):
        self.yr_sbjt_table.clear_table()
        self.populate_yr_sbjts_table()

    def refresh_year_table(self):
        self.year_table.clear_table()
        self.populate_year_table()

    def refresh_subjects_table(self):
        self.subjects_table.clear_table()
        self.populate_subjects_table()

    def refresh(self):
        self.refresh_year_table()
        self.refresh_yr_sbjts_table()
        self.refresh_subjects_table()


class ClassesTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.sbjt_id = None
        self.tchr_id = None
        self.clsrm_id = None
        self.cls_id = None
        self.prd_id = None
        self.tiles = []
        self.state_colour = {1: "yellow", 2: "orange", 3: "red"}

        left_side_frame = tk.Frame(self, borderwidth=2, relief="sunken")
        left_side_frame.grid_rowconfigure(1, weight=1)
        subjects_label = tk.Label(left_side_frame, text="Subjects:")
        subjects_label.grid(row=0, column=0, sticky="nw")
        self.sbjt_id_map = {}
        self.sbjt_tbl = cw.VerticalTable(left_side_frame, ("Code", "Name"))
        self.sbjt_tbl.add_bind("<Button-1>", self.select_subject)
        self.populate_subjects_table()
        self.sbjt_tbl.grid(row=1, column=0, padx=5, pady=5, sticky="ns")
        left_side_frame.grid(row=0, column=0, sticky="ns")

        middle_frame = tk.Frame(self, borderwidth=2, relief="sunken")
        middle_frame.grid_rowconfigure(1, weight=1)
        resources_frame = ttk.LabelFrame(middle_frame, text="Resources:")
        self.radio_var = tk.IntVar()
        self.radio_var.set(1)
        tchr_rb = tk.Radiobutton(resources_frame,
                                 text="Teachers",
                                 variable=self.radio_var,
                                 value=1,
                                 command=self.radio_event)
        tchr_rb.grid(row=0, sticky="w", padx=5)
        clsrm_rb = tk.Radiobutton(resources_frame,
                                  text="Classrooms",
                                  variable=self.radio_var,
                                  value=2,
                                  command=self.radio_event)
        clsrm_rb.grid(row=1, sticky="w", padx=5)
        resources_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.container = cw.CreateContainer(middle_frame, self, controller)
        self.tchr_id_map = {}
        self.tchr_table = cw.VerticalTable(middle_frame, ("Code", "Firstname", "Surname"))
        self.tchr_table.add_bind("<Button-1>", self.select_teacher)
        self.populate_teacher_table()
        self.clsrm_id_map = {}
        self.clsrm_tbl = cw.VerticalTable(middle_frame, ("Name", "Size"))
        self.populate_classrooms_table()
        self.tchr_page_id = self.container.add_init_page(self.tchr_table)
        self.clsrm_page_id = self.container.add_init_page(self.clsrm_tbl)
        self.radio_event()
        self.container.grid(row=1, column=0, padx=5, pady=5, sticky="ns")
        middle_frame.grid(row=0, column=1, sticky="nsew")

        bottom_left_frame = tk.Frame(self, borderwidth=2, relief="sunken")
        bottom_left_frame.grid_rowconfigure(0, weight=1)
        bottom_left_frame.grid_columnconfigure(0, weight=1)
        scroll_frame = cw.ScrolledFrame(bottom_left_frame)
        scroll_frame.propagate(False)
        self.prd_id_map = {}
        self.prds_tbl = TeacherTimetable(scroll_frame.interior)
        self.prds_tbl.grid(row=0, column=0)
        self.prds_b_bar = cw.BottomBar(bottom_left_frame)
        self.undo_btn_id = self.prds_b_bar.add_button(text="Undo")
        self.prds_b_bar.show_button(self.undo_btn_id)
        self.save_btn_id = self.prds_b_bar.add_button(text="Save")
        self.prds_b_bar.show_button(self.save_btn_id)
        self.prds_b_bar.grid(row=1, column=0)
        scroll_frame.grid(row=0, column=0, sticky="nsew")
        bottom_left_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")

        right_side_frame = tk.Frame(self, borderwidth=2, relief="sunken")
        right_side_frame.grid_rowconfigure(1, weight=1)
        right_side_frame.grid_columnconfigure(0, weight=1)
        classes_label = tk.Label(right_side_frame, text="Classes:")
        classes_label.grid(row=0, column=0, sticky="nw")
        self.yr_id_map, self.cls_id_map = {}, {}
        self.clss_tbl = cw.HorizontalTable(right_side_frame)
        self.clss_tbl.add_selection_event(self.select_class)
        self.clss_tbl.add_pop_up_menu(("Add Teacher", self.add_tchr_to_cls))
        try:
            for year in m_db.get_all_year_data():
                self.yr_id_map[year[0]] = self.clss_tbl.add_row(year[1])
        except AttributeError:
            return
        self.clss_tbl.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        right_side_frame.grid(row=0, column=2, rowspan=2, sticky="nsew")

    def select_subject(self, event):
        self.sbjt_id = self.sbjt_id_map[self.sbjt_tbl.get_selected_row_id()]
        self.tchr_id, self.cls_id, self.prd_id = None, None, None
        self.populate_teacher_table()
        self.populate_classrooms_table()
        self.populate_clss_tbl()
        self.clear_prds_table()
        self.disable_bottom_bar()

    def select_teacher(self, event):
        self.tchr_id = self.tchr_id_map[self.tchr_table.get_selected_row_id()]
        self.refresh_timetable()

    def select_classroom(self, event):
        self.clsrm_id = self.clsrm_id_map[self.clsrm_tbl.get_selected_row_id()]
        pass

    def select_class(self):
        tile_id = self.clss_tbl.get_selected_tile_id()
        self.cls_id = self.cls_id_map[tile_id]
        self.refresh_timetable()

    def refresh_timetable(self):
        self.inject_tchr_timetable()
        self.inject_cls_timetable()
        if self.cls_id is None or self.tchr_id is None:
            self.disable_bottom_bar()
        else:
            self.enable_bottom_bar()

    def inject_tchr_timetable(self):
        self.prds_tbl.show_tchr_timetable(self.tchr_id)

    def inject_cls_timetable(self):
        self.clear_coloured_tiles()
        if self.cls_id is not None:
            for prd_id, result in m_db.get_cls_tchr_availability(self.cls_id, self.tchr_id):
                tile = self.prds_tbl.get_cell_prd_id(prd_id)
                self.prds_tbl.add_tile_bind((tile, ), "<Button-1>", self.select_tile)
                tile.state = self.return_state(result)
                if m_db.check_cls_tchr(prd_id, self.cls_id, self.tchr_id) == 1:
                    tile.state = 2
                tile.interphase_colour(self.state_colour[tile.state])
                self.tiles.append(tile)

    def select_tile(self, event):
        tile = self.prds_tbl.get_parent(event.widget)
        if tile.state not in [0, 3]:
            tile.state = tile.state % 2 + 1
            tile.interphase_colour(self.state_colour[tile.state])

    def clear_prds_table(self):
        self.prds_tbl.clear_table()
        self.clear_coloured_tiles()

    def clear_coloured_tiles(self):
        for tile in self.tiles:
            tile.state = 0
            tile.interphase_colour(self.prds_tbl.bg)
            self.prds_tbl.remove_tile_bind((tile, ), "<Button-1>")
        self.tiles.clear()

    def enable_bottom_bar(self):
        self.configure_buttons(state="active")

    def disable_bottom_bar(self):
        self.configure_buttons(state="disabled")

    def configure_buttons(self, **options):
        self.prds_b_bar.configure_button(self.save_btn_id, **options)
        self.prds_b_bar.configure_button(self.undo_btn_id, **options)

    def populate_clss_tbl(self):
        if self.sbjt_id is None:
            return
        self.clear_class_table()
        classes = m_db.get_classes_by_subject(self.sbjt_id)
        for cls in classes:
            title_id = self.yr_id_map[cls[3]]
            tile_id = self.clss_tbl.add_tile(title_id, cls[1], cls[2], cls[4])
            self.cls_id_map[tile_id] = cls[0]

    def clear_class_table(self):
        self.cls_id = None
        self.cls_id_map.clear()
        self.clss_tbl.reset_tile_id()
        self.clss_tbl.clear_table_contents()

    def populate_teacher_table(self):
        try:
            if self.sbjt_id is None:
                tchrs = m_db.get_all_teacher_data()
            else:
                tchrs = m_db.get_teachers_by_subject(self.sbjt_id)
        except AttributeError:
            return
        self.clear_teacher_table()
        for t in tchrs:
            self.tchr_id_map[self.tchr_table.add_row(t[1], t[3], t[4])] = t[0]

    def clear_teacher_table(self):
        self.tchr_id = None
        self.tchr_id_map.clear()
        self.tchr_table.reset_row_id()
        self.tchr_table.clear_table()

    def populate_classrooms_table(self):
        try:
            if self.sbjt_id is None:
                classrooms = m_db.get_all_classroom_data()
            else:
                classrooms = m_db.get_classrooms_by_subject(self.sbjt_id)
        except AttributeError:
            return
        self.clear_classroom_table()
        for clsrm in classrooms:
            self.clsrm_id_map[self.clsrm_tbl.add_row(clsrm[1], clsrm[2])] = clsrm[0]

    def clear_classroom_table(self):
        self.cls_id = None
        self.clsrm_id_map.clear()
        self.clsrm_tbl.reset_row_id()
        self.clsrm_tbl.clear_table()

    def populate_subjects_table(self):
        try:
            subjects = m_db.get_all_subject_data()
        except AttributeError:
            return
        self.sbjt_id_map.clear()
        self.sbjt_tbl.reset_row_id()
        self.sbjt_tbl.clear_table()
        for subject in subjects:
            self.sbjt_id_map[self.sbjt_tbl.add_row(subject[1], subject[2])] = subject[0]

    def add_tchr_to_cls(self):
        tile_id = self.clss_tbl.get_selected_tile_id()
        if tile_id is None:
            return
        self.clss_tbl.add_teacher(tile_id, 1, "AAA", 9)

    def radio_event(self):
        val = self.radio_var.get()
        if val == 1:
            self.container.show_init_frame(self.tchr_table)
        elif val == 2:
            self.container.show_init_frame(self.clsrm_tbl)

    def refresh(self):
        self.populate_subjects_table()
        self.clear_class_table()
        self.clear_teacher_table()
        self.clear_classroom_table()

    @staticmethod
    def return_state(val):
        if val is None:
            return 1
        return 3


class AnalysisTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="analysis tab").pack()


class TimetableTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="timetable tab").pack()


class ChangePasswordPage(tk.Frame):
    """Page where user can change their passord"""
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG_COLOUR)
        password_validation = parent.register(self.password_checker)
        button_validation = parent.register(self.compare_password)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(9999, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(9999, weight=1)

        label_change_password = tk.Label(self, text="Change Password", font=TITLE_TEXT, bg=BG_COLOUR)
        label_change_password.grid(row=1, column=1, columnspan=2)

        label_new_password = tk.Label(self, text="New Password:", bg=BG_COLOUR, font=MAIN_TEXT)
        label_new_password.grid(row=2, column=1)

        self.entry_new_password = tk.Entry(self, show="*", validate="key", validatecommand=(password_validation, '%P'))
        self.entry_new_password.grid(row=2, column=2)

        label_confirm_password = tk.Label(self, text="Confirm Password:", bg=BG_COLOUR, font=MAIN_TEXT)
        label_confirm_password.grid(row=3, column=1)

        self.entry_confirm_password = tk.Entry(self, show="*", validate="key", validatecommand=(button_validation, '%P'))
        self.entry_confirm_password.grid(row=3, column=2)

        self.label_output = tk.Label(self, text="", bg=BG_COLOUR, font=MAIN_TEXT)
        self.label_output.grid(row=4, column=1, columnspan=1)

        self.button_change = tk.Button(self, text="Change Password", bg=BG_COLOUR, command=lambda: self.update_page(controller))
        self.button_change.grid_configure(row=4, column=2)
        self.button_change.grid_remove()

        button_back = tk.Button(self, text="Go Back", bg=BG_COLOUR, command=lambda: self.home(controller))
        button_back.grid(row=10, column=1, columnspan=2)

    def update_page(self, controller):
        if controller.user.update_password(self.entry_new_password.get()) is not False:
            self.clear_passwords()
            self.label_output.config(text="Password Updated\n", fg="green")
        else:
            self.clear_passwords()

    def compare_password(self, *password):
        password = list(password)
        length = len(password)
        if length == 1:
            confirm_password = password[0]
            if invalid_checker(confirm_password) is False or len(confirm_password) >= 24:
                return False
            new_password = self.entry_new_password.get()
        else:
            confirm_password, new_password = password[0], password[1]
        if new_password == confirm_password and new_password != "":
            self.button_change.grid()
        else:
            self.button_change.grid_remove()
        return True

    def password_checker(self, new_password):
        character_string = "!%$^&*()_-+=/;:@#~[]{}.,<>"
        confirm_password = self.entry_confirm_password.get()
        password_points = (len(new_password)) // 2

        if invalid_checker(new_password) is False:
            return False

        self.compare_password(confirm_password, new_password)

        if password_points >= 12:
            return False
        if password_points > 8:
            password_points = 8
        elif new_password == "password":
            self.label_output.config(text="Uncrackable\n", fg="#0021ff")
            return True
        elif new_password == "":
            self.label_output.config(text="\n")
            return True

        pwd_list = list(new_password)
        for character in pwd_list:
            if character.isupper() is True:
                password_points += 5
                break
        for character in pwd_list:
            try:
                int(character)
                password_points += 5
                break
            except ValueError:
                pass
        character_list = list(character_string)
        for character in pwd_list:
            if character in character_list:
                password_points += 5
                break
        if password_points >= 20:
            self.label_output.config(text="Uncrackable\n", fg="#0021ff")
        elif password_points >= 16:
            self.label_output.config(text="Strong\n", fg="#2f8727")
        elif password_points >= 12:
            self.label_output.config(text="Medium\n", fg="#ffd000")
        elif password_points >= 6:
            self.label_output.config(text="Weak\n", fg="#ff5d00")
        else:
            self.label_output.config(text="Flimsy\n", fg="#ff0000")
        return True

    def home(self, controller):
        controller.show_frames(TimetablePage)
        self.clear_passwords()

    def clear_passwords(self):
        """Clears all the entry boxes on the ChangePasswordPage"""
        self.entry_new_password.delete(0, 'end')
        self.entry_confirm_password.delete(0, 'end')

    def refresh_all(self):
        """Updates the page to changes in database"""
        self.clear_passwords()


if __name__ == "__main__":
    a_db = db.AccountsDatabase()
    m_db = db.MainDatabase()
    bootstrapper = LoginWindow()
    bootstrapper.mainloop()
