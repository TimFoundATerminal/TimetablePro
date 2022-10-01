import os
import sqlite3 as sql
from tkinter import messagebox, filedialog
from shutil import copyfile


class AccountsDatabase:
    def __init__(self):
        try:
            self.connection = sql.connect("Accounts")
            self.cursor = self.connection.cursor()
        except FileNotFoundError:
            messagebox.showerror("Error", "Unable to find file 'Accounts' file")
            self.connection = None
            self.cursor = None

    def close_database(self):
        try:
            self.connection.close()
        except AttributeError:
            pass
        finally:
            self.connection = None
            self.cursor = None

    def create_admin_table(self):
        self.cursor.executescript("""
        CREATE TABLE institutions (Institution_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                    Institution_Code TEXT NOT NULL,
                                    Institution_Name TEXT NOT NULL,
                                    Institution_Address TEXT,
                                    CONSTRAINT UQ_code UNIQUE (Institution_Code),
                                    CONSTRAINT UQ_adrs UNIQUE (Institution_Address));
                                    
        INSERT INTO institutions (Institution_ID, 
                                  Institution_Code, 
                                  Institution_Name, 
                                  Institution_Address) VALUES ('1', 
                                                               'CTK', 
                                                               'Christ the King College', 
                                                               'PO35 WQX');

        CREATE TABLE accounts (Account_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                    Institution_ID INTEGER NOT NULL,
                                    Account_Email TEXT NOT NULL,
                                    Account_Forename TEXT NOT NULL,
                                    Account_Surname TEXT NOT NULL,
                                    Account_Password TEXT NOT NULL,
                                    Account_Clearance INTEGER NOT NULL,
                                    CONSTRAINT UQ_email UNIQUE (Account_Email)
                                    CONSTRAINT FK_istn_id 
                                       FOREIGN KEY (Institution_ID) REFERENCES institutions(Institution_ID));

        CREATE TABLE preferences (Account_ID INTEGER NOT NULL,
                                    File_Path TEXT,
                                    CONSTRAINT FK_acnt_id 
                                       FOREIGN KEY (Account_ID) REFERENCES accounts(Account_ID));""")

    def get_default_filepath(self, acnt_id):
        self.cursor.execute("""SELECT File_Path 
                               FROM preferences
                               WHERE Account_ID = (:id)""",
                            {"id": acnt_id})
        return self.unpack_tuple(self.cursor.fetchone())

    def remove_default_filepath(self, acnt_id):
        with self.connection:
            self.cursor.execute("""DELETE FROM preferences
                                   WHERE Account_ID = (:id)""",
                                {"id": acnt_id})

    def update_default_filepath(self, acnt_id, filepath):
        self.remove_default_filepath(acnt_id)
        with self.connection:
            self.cursor.execute("""INSERT INTO preferences (Account_ID, File_Path)
                                   VALUES (:id, :path)""",
                                {"id": acnt_id, "path": filepath})

    def update_password(self, email, password):
        with self.connection:
            self.cursor.execute("UPDATE accounts SET Account_Password = (:password) WHERE Account_Email = (:email)",
                                {"password": password, "email": email})

    def get_account_password(self, email):
        self.cursor.execute("SELECT Account_Password FROM accounts WHERE Account_Email = (:email)",
                            {"email": email})
        return self.unpack_tuple(self.cursor.fetchone())

    def get_account_details_email(self, email):
        self.cursor.execute("""SELECT * 
                            FROM accounts 
                            WHERE Account_Email = (:email)""",
                            {"email": email})
        return self.cursor.fetchone()

    def get_account_details_id(self, acnt_id):
        self.cursor.execute("""SELECT * 
                            FROM accounts 
                            WHERE Account_ID = (:account_id)""",
                            {"account_id": acnt_id})
        return self.cursor.fetchone()

    def check_email_unique(self, email):
        self.cursor.execute("SELECT Account_ID FROM accounts WHERE Account_Email = (:email)",
                            {"email": email})
        return self.cursor.fetchone() is None

    def add_account(self, firstname, secondname, institution_id, email, password, clearance):
        with self.connection:
            self.cursor.execute("""INSERT INTO accounts (Account_Email,
                                                        Institution_ID, 
                                                        Account_Forename, 
                                                        Account_Surname, 
                                                        Account_Password, 
                                                        Account_Clearance) 
                                VALUES (:email, :institution, :firstname, :lastname, :password, :clearance)""",
                                {"firstname": firstname,
                                 "lastname": secondname,
                                 "institution": institution_id,
                                 "password": password,
                                 "email": email,
                                 "clearance": clearance})

    def get_istn_id(self, code):
        self.cursor.execute("""SELECT Institution_ID FROM institutions WHERE Institution_Code = (:code)""",
                            {"code": code})
        return self.unpack_tuple(self.cursor.fetchone())

    @staticmethod
    def unpack_tuple(single_tuple):
        if single_tuple is None:
            return single_tuple
        return single_tuple[0]


class MainDatabase:

    connection = None
    cursor = None
    filepath = None

    def __init__(self, default_db=None):
        if default_db is None:
            return
        self.connect_database(filepath=default_db)

    @staticmethod
    def uri_filepath(filepath):
        """Converts filedialog filepath into an uri"""
        filepath = filepath.replace("\\", "/")
        filepath = filepath.replace(" ", "%20")
        return "file://localhost/" + filepath

    @staticmethod
    def os_filepath(filepath):
        """Converts filedialog filepath into an uri"""
        filepath = filepath[17:]
        filepath = filepath.replace("%20", " ")
        return filepath

    def connect_database(self, filepath):
        """Creates the connection object to the database"""
        query = "?mode=rw"
        # exception is to ensure the path is valid
        try:
            connection = sql.connect(filepath+query, uri=True)
            cursor = connection.cursor()
        except sql.DatabaseError:
            messagebox.showerror("Error", "Invalid filepath\n(%s)" % filepath)
            return False
        # connection object will connect to files that are not databases
        try:
            # makes sure the database file contains a students table
            cursor.execute("SELECT * FROM students")
        except sql.DatabaseError:
            messagebox.showerror("Error", "Unable to open files of this type\n(%s)" % filepath)
            connection.close()
            return False
        # upon connection, objects are assigned as attributes
        self.connection = connection
        self.cursor = cursor
        self.filepath = filepath
        return True

    def backup_database(self):
        """Backs up the Database"""
        # opens the destination folder in 'write bits' mode
        dst = filedialog.asksaveasfile(mode="wb",
                                       title="Back-Up Database",
                                       defaultextension=".db",
                                       filetypes=(("All files", "*.*"), ))
        if dst is None:
            return
        self.os_filepath(self.filepath)
        # opens the database in 'read bits' mode and reads contents
        db_to_save = open(self.os_filepath(self.filepath), "rb").read()
        # writes the data to the file
        dst.write(db_to_save)
        dst.close()

    def close_database(self):
        """Closes connection with Database"""
        # closes the connection within the database
        try:
            self.connection.close()
        except AttributeError:
            pass
        finally:
            self.connection = None
            self.cursor = None
            self.filepath = None

    def open_database(self):
        """Opens an already existing database"""
        # relative path of the program to open file explorer
        direct_path = os.path.dirname(os.path.realpath(__file__))
        filepath = filedialog.askopenfilename(initialdir=direct_path, title="Open",
                                              filetypes=(("All files", "*.*"),
                                                         ("SQL files", "*.sql")))
        # converts into uri format and connects
        return self.connect_database(self.uri_filepath(filepath))

    def create_database(self):
        """Creates a new database """
        direct_path = os.path.dirname(os.path.realpath(__file__))
        filepath = filedialog.asksaveasfilename(initialdir=direct_path, title="Save as",
                                                filetypes=(("All files", "*.*"), ("SQL files", "*.sql")))
        try:
            connection = sql.connect(filepath)
            cursor = connection.cursor()
            cursor.executescript("""
            CREATE TABLE storage (Field TEXT PRIMARY KEY NOT NULL,
                                  Text TEXT,
                                  Value INTEGER);
                                  
            INSERT INTO storage ("Field", "Text", "Value") 
            VALUES ('option_periods', '', '0');
            INSERT INTO storage ("Field", "Text", "Value") 
            VALUES ('num_options', '', '0');
            INSERT INTO storage ("Field", "Text", "Value") 
            VALUES ('email_suffix', '@example.email.co.uk', '');
            INSERT INTO storage ("Field", "Text", "Value") 
            VALUES ('default_password', '5f4dcc3b5aa765d61d8327deb882cf99', '');
            
            CREATE TABLE subjects (Subject_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                   Subject_Code TEXT NOT NULL,
                                   Subject_Name TEXT NOT NULL,
                                   CONSTRAINT UQ_sbjt_code
                                      UNIQUE (Subject_Code),
                                   CONSTRAINT UQ_sbjt_name
                                      UNIQUE (Subject_Name));
            
            CREATE TABLE years (Year_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                Year_Name TEXT NOT NULL,
                                Year_Value INTEGER NOT NULL,
                                Year_Options INTEGER NOT NULL);
                                   
            CREATE TABLE year_subjects (Year_ID INTEGER NOT NULL,
                                         Subject_ID INTEGER NOT NULL,
                                         Subject_Option INTEGER DEFAULT 0,
                                         Subject_Periods INTEGER DEFAULT 0,
                                         PRIMARY KEY (Year_ID, Subject_ID, Subject_Option),
                                         CONSTRAINT FK_yr_id
                                            FOREIGN KEY (Year_ID) REFERENCES years(Year_ID)
                                            ON DELETE CASCADE,
                                         CONSTRAINT FK_sbjt_id
                                            FOREIGN KEY (Subject_ID) REFERENCES subjects(Subject_ID)
                                            ON DELETE CASCADE);

            CREATE TABLE teachers (Teacher_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                   Teacher_Code TEXT NOT NULL,
                                   Teacher_Email TEXT NOT NULL,
                                   Teacher_Forename TEXT NOT NULL,
                                   Teacher_Surname TEXT NOT NULL,
                                   Teacher_Password TEXT NOT NULL,
                                   CONSTRAINT UQ_tchr_email
                                      UNIQUE (Teacher_Email));

            CREATE TABLE teacher_subjects (Teacher_ID INTEGER NOT NULL,
                                         Subject_ID INTEGER NOT NULL,
                                         PRIMARY KEY (Teacher_ID, Subject_ID),
                                         CONSTRAINT FK_tchr_id
                                            FOREIGN KEY (Teacher_ID) REFERENCES teachers(Teacher_ID)
                                            ON DELETE CASCADE,
                                         CONSTRAINT FK_sbjt_id
                                            FOREIGN KEY (Subject_ID) REFERENCES subjects(Subject_ID)
                                            ON DELETE CASCADE);

            CREATE TABLE students (Student_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                     Student_Forename TEXT NOT NULL,
                                     Student_Surname TEXT NOT NULL,
                                     Student_Year INTEGER NOT NULL,
                                     Student_Email TEXT NOT NULL,
                                     CONSTRAINT UQ_stdt_email
                                        UNIQUE (Student_Email),
                                     CONSTRAINT FK_stdt_yr
                                        FOREIGN KEY (Student_Year) REFERENCES years(Year_ID)
                                        ON DELETE CASCADE);

            CREATE TABLE student_subjects (Student_ID INTEGER NOT NULL,
                                         Subject_ID INTEGER NOT NULL,
                                         PRIMARY KEY (Student_ID, Subject_ID),
                                         CONSTRAINT FK_stdt_id
                                            FOREIGN KEY (Student_ID) REFERENCES students(Student_ID)
                                            ON DELETE CASCADE,
                                         CONSTRAINT FK_sbjt_id
                                            FOREIGN KEY (Subject_ID) REFERENCES subjects(Subject_ID)
                                            ON DELETE CASCADE);

            CREATE TABLE classrooms (Classroom_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                       Classroom_Name TEXT NOT NULL,
                                       MaxNoStudents INTEGER NOT NULL);

            CREATE TABLE classroom_subjects (Classroom_ID INTEGER NOT NULL,
                                               Subject_ID INTEGER NOT NULL,
                                               PRIMARY KEY (Classroom_ID, Subject_ID),
                                               CONSTRAINT FK_clrm_id
                                                FOREIGN KEY (Classroom_ID) REFERENCES classrooms(Classroom_ID)
                                                ON DELETE CASCADE,
                                               CONSTRAINT FK_sbjt_id
                                                FOREIGN KEY (Subject_ID) REFERENCES subjects(Subject_ID)
                                                ON DELETE CASCADE);

            CREATE TABLE classes (Class_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                    Class_Name TEXT NOT NULL,
                                    Class_Number INTEGER NOT NULL,
                                    Class_Year INTEGER NOT NULL,
                                    Class_Subject INTEGER NOT NULL,
                                    Class_Type INTEGER NOT NULL,
                                    CONSTRAINT FK_sbjt_id
                                        FOREIGN KEY (Class_Subject) REFERENCES subjects(Subject_ID)
                                        ON DELETE CASCADE,
                                    CONSTRAINT FK_clss_yr
                                        FOREIGN KEY (Class_Year) REFERENCES years(Year_ID)
                                        ON DELETE CASCADE);

            CREATE TABLE class_students (Class_ID INTEGER NOT NULL,
                                           Student_ID INTEGER NOT NULL,
                                           PRIMARY KEY (Class_ID, Student_ID),
                                           CONSTRAINT FK_class_id
                                            FOREIGN KEY (Class_ID) REFERENCES classes(Class_ID)
                                            ON DELETE CASCADE,
                                           CONSTRAINT FK_stdt_id
                                            FOREIGN KEY (Student_ID) REFERENCES students(Student_ID)
                                            ON DELETE CASCADE);

            CREATE TABLE sets (Set_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                                          Subject_ID INTEGER NOT NULL,
                                                          Set_Year INTEGER NOT NULL,
                                                          Set_Number INTEGER NOT NULL,
                                                          Set_Type INTEGER NOT NULL,
                                                          CONSTRAINT UQ_set_id 
                                                            UNIQUE (Subject_ID, Set_Year, Set_Number, Set_Type),
                                                          CONSTRAINT FK_subject_id
                                                            FOREIGN KEY (Subject_ID) REFERENCES subjects(Subject_ID)
                                                            ON DELETE CASCADE,
                                                          CONSTRAINT FK_set_yr
                                                            FOREIGN KEY (Set_Year) REFERENCES years(Year_ID)
                                                            ON DELETE CASCADE);

            CREATE TABLE set_classes (Set_ID INTEGER NOT NULL,
                                        Class_ID INTEGER NOT NULL,
                                        PRIMARY KEY (Set_ID, Class_ID),
                                        CONSTRAINT FK_set_id
                                            FOREIGN KEY (Set_ID) REFERENCES sets(Set_ID)
                                            ON DELETE CASCADE,
                                        CONSTRAINT FK_class_id
                                            FOREIGN KEY (Class_ID) REFERENCES class(Class_ID)
                                            ON DELETE CASCADE);
                                            
            CREATE TABLE blocks (Block_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                    Block_Name TEXT NOT NULL, 
                                    Block_Year INTEGER NOT NULL,
                                    Block_Number INTEGER NOT NULL,
                                    CONSTRAINT UQ_block_id 
                                     UNIQUE (Block_Name, Block_Year),
                                    CONSTRAINT FK_block_yr
                                     FOREIGN KEY (Block_Year) REFERENCES years(Year_ID)
                                     ON DELETE CASCADE);
                                                            
            CREATE TABLE block_sets (Block_ID INTEGER NOT NULL,
                                        Set_ID INTEGER NOT NULL,
                                        PRIMARY KEY (Block_ID, Set_ID),
                                        CONSTRAINT FK_block_id
                                            FOREIGN KEY (Block_ID) REFERENCES blocks(Block_ID)
                                            ON DELETE CASCADE,
                                        CONSTRAINT FK_set_id
                                            FOREIGN KEY (Set_ID) REFERENCES sets(Set_ID)
                                            ON DELETE CASCADE);

            CREATE TABLE periods (Period_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                                    Period_Number INTEGER NOT NULL,
                                    Period_Day INTEGER NOT NULL,
                                    Period_Week INTEGER NOT NULL);
                                                    
            CREATE TABLE period_students (Period_ID INTEGER NOT NULL,
                                          Student_ID INTEGER NOT NULL,
                                          PRIMARY KEY (Period_ID, Student_ID),
                                          CONSTRAINT FK_period_id
                                           FOREIGN KEY (Period_ID) REFERENCES periods(Period_ID)
                                           ON DELETE CASCADE,
                                          CONSTRAINT FK_stdt_id
                                           FOREIGN KEY (Student_ID) REFERENCES students(Student_ID)
                                           ON DELETE CASCADE);

            CREATE TABLE class_placement (Period_ID INTEGER NOT NULL,
                                            Class_ID INTEGER NOT NULL,
                                            Teacher_ID INTEGER NULL,
                                            Classroom_ID INTEGER NULL,
                                            PRIMARY KEY (Period_ID, Class_ID),
                                            CONSTRAINT UQ_period_teacher 
                                                UNIQUE (Period_ID, Teacher_ID),
                                            CONSTRAINT UQ_period_classroom 
                                                UNIQUE (Period_ID, Classroom_ID),
                                            CONSTRAINT FK_period_id
                                                FOREIGN KEY (Period_ID) REFERENCES periods(Period_ID)
                                                ON DELETE CASCADE,
                                            CONSTRAINT FK_class_id
                                                FOREIGN KEY (Class_ID) REFERENCES classes(Class_ID)
                                                ON DELETE CASCADE,
                                            CONSTRAINT FK_teacher_id
                                                FOREIGN KEY (Teacher_ID) REFERENCES teachers(Teacher_ID)
                                                ON DELETE CASCADE,
                                            CONSTRAINT FK_classroom_id
                                                FOREIGN KEY (Classroom_ID) REFERENCES classrooms(Classroom_ID)
                                                ON DELETE CASCADE);
            """)
            self.connection = connection
            self.cursor = cursor
            self.filepath = self.uri_filepath(filepath)
            return True

        except ValueError:
            messagebox.showerror("Error", "Unable to create file\n(%s)" % filepath)
            return False
        except sql.OperationalError:
            messagebox.showerror("Error", "Unable to open file\n(%s)" % filepath)
            return False

    def get_email_suffix(self):
        self.cursor.execute("""SELECT Text FROM storage WHERE Field = 'email_suffix'""")
        return self.unpack_tuple(self.cursor.fetchone())

    def get_option_periods(self):
        self.cursor.execute("""SELECT Value FROM storage WHERE Field = 'option_periods'""")
        return self.unpack_tuple(self.cursor.fetchone())

    def get_default_password(self):
        self.cursor.execute("""SELECT Text FROM storage WHERE Field = 'default_password'""")
        return self.unpack_tuple(self.cursor.fetchone())

    def check_email_unique(self, email):
        self.cursor.execute("""SELECT Teacher_Email FROM teachers WHERE Teacher_Email = (:email)""",
                            {"email": email})
        return self.unpack_tuple(self.cursor.fetchone())

    def update_password(self, email, password):
        with self.connection:
            self.cursor.execute("UPDATE teachers SET Teacher_Password = (:password) WHERE Teacher_Email = (:email)",
                                {"password": password, "email": email})

    def add_year(self, name, value, option):
        with self.connection:
            self.cursor.execute("""INSERT INTO years (Year_Name, Year_Value, Year_Options)
                                   VALUES (:name, :value, :option)""",
                                {"name": name, "value": value, "option": option})
        return self.get_last_insert_rowid()

    def update_year(self, year_id, name, value, option):
        with self.connection:
            self.cursor.execute("""UPDATE years
                                   SET Year_Name = (:name),
                                       Year_Value = (:value),
                                       Year_Option = (:option)
                                   WHERE Year_ID = (:id)""",
                                {"name": name, "value": value, "option": option, "id": year_id})

    def delete_year(self, year_id):
        with self.connection:
            self.cursor.execute("""DELETE FROM years WHERE Year_ID = (:year_id)""",
                                {"year_id": year_id})

    def get_all_year_data(self):
        self.cursor.execute("""SELECT * FROM years""")
        return self.cursor.fetchall()

    def get_all_year_ids(self):
        self.cursor.execute("""SELECT Year_ID FROM years""")
        return self.tuples_to_list(self.cursor.fetchall())

    def get_year_values(self):
        self.cursor.execute("""SELECT Year_Value FROM years""")
        return self.tuples_to_list(self.cursor.fetchall())

    def get_year_values_with_id(self):
        self.cursor.execute("""SELECT Year_ID, Year_Value FROM years""")
        return self.cursor.fetchall()

    def get_year_value(self, year_id):
        self.cursor.execute("""SELECT Year_Value FROM years WHERE Year_ID = (:year)""",
                            {"year": year_id})
        return self.unpack_tuple(self.cursor.fetchone())

    def get_year_name(self, year_id):
        self.cursor.execute("""SELECT Year_Name FROM years WHERE Year_ID = (:year)""",
                            {"year": year_id})
        return self.unpack_tuple(self.cursor.fetchone())

    def check_year_option(self, year_id):
        self.cursor.execute("""SELECT Year_Options FROM years WHERE Year_ID = (:id)""",
                            {"id": year_id})
        return self.unpack_tuple(self.cursor.fetchone())

    def get_teacher_by_id(self, tchr_id):
        self.cursor.execute("SELECT * FROM teachers WHERE Teacher_ID = (:id)", {"id": tchr_id})
        return self.cursor.fetchone()

    def get_teacher_by_email(self, email):
        self.cursor.execute("SELECT * FROM teachers WHERE Teacher_Email = (:email)", {"email": email})
        return self.cursor.fetchone()

    def get_all_teachers(self):
        self.cursor.execute("""SELECT Teacher_ID FROM teachers""")
        return self.tuples_to_list(self.cursor.fetchall())

    def get_teachers_by_subject(self, sbjt_id):
        self.cursor.execute("""SELECT teachers.Teacher_ID, Teacher_Code, Teacher_Email, Teacher_Forename, Teacher_Surname
                                FROM teacher_subjects
                                INNER JOIN teachers
                                ON teacher_subjects.Teacher_ID = teachers.Teacher_ID
                                WHERE Subject_ID = (:sbjt_id)""",
                            {"sbjt_id": sbjt_id})
        return self.cursor.fetchall()

    def get_all_teacher_data(self):
        self.cursor.execute("""SELECT * FROM teachers""")
        return self.cursor.fetchall()

    def get_classroom_data(self, classroom_id):
        self.cursor.execute("""SELECT Classroom_ID, 
                                      Classroom_Name, 
                                      MaxNoStudents FROM classrooms WHERE Classroom_ID = (:class_id)""",
                            {"class_id": classroom_id})
        return self.unpack_tuple(self.cursor.fetchall())

    def get_classrooms_by_subject(self, sbjt_id):
        self.cursor.execute("""SELECT classrooms.Classroom_ID, Classroom_Name, MaxNoStudents
                                FROM classroom_subjects
                                INNER JOIN classrooms
                                ON classroom_subjects.Classroom_ID = classrooms.Classroom_ID
                                WHERE Subject_ID = (:sbjt_id)""",
                            {"sbjt_id": sbjt_id})
        return self.cursor.fetchall()

    def get_all_classrooms(self):
        self.cursor.execute("""SELECT Classroom_ID FROM classrooms""")
        return self.tuples_to_list(self.cursor.fetchall())

    def get_all_classroom_data(self):
        self.cursor.execute("SELECT * FROM classrooms")
        return self.cursor.fetchall()

    def check_classroom_name_unique(self, name):
        self.cursor.execute("""SELECT Classroom_ID 
                               FROM classrooms 
                               WHERE Classroom_Name = (:clsrm_name)""",
                            {"clsrm_name": name})
        return self.cursor.fetchone() is None

    def add_classroom(self, name, size):
        """Returns the id of the new classroom added into database"""
        with self.connection:
            self.cursor.execute("""INSERT INTO classrooms (Classroom_Name, MaxNoStudents)
                                   VALUES (:clsrm_name, :clsrm_size)""",
                                {"clsrm_name": name, "clsrm_size": size})
        return self.get_last_insert_rowid()

    def update_classroom(self, clsrm_id, name, size):
        with self.connection:
            self.cursor.execute("""UPDATE classrooms 
                                   SET Classroom_Name = (:clsrm_name),
                                       MaxNoStudents = (:clsrm_size)
                                   WHERE Classroom_ID = (:clsrm_id)""",
                                {"clsrm_name": name, "clsrm_size": size, "clsrm_id": clsrm_id})

    def delete_classroom(self, clsrm_id):
        with self.connection:
            self.cursor.execute("""DELETE FROM classrooms
                                   WHERE Classroom_ID = (:clsrm_id)""",
                                {"clsrm_id": clsrm_id})
        self.delete_classroom_subjects(clsrm_id)

    def delete_classroom_subjects(self, clsrm_id):
        with self.connection:
            self.cursor.execute("""DELETE FROM classroom_subjects
                                   WHERE Classroom_ID = (:clsrm_id)""",
                                {"clsrm_id": clsrm_id})

    def add_classroom_subject(self, clsrm_id, sbjt_id):
        print(sbjt_id)
        with self.connection:
            self.cursor.execute("""INSERT INTO classroom_subjects (Classroom_ID, Subject_ID)
                                   VALUES (:clsrm_id, :sbjt_id)""",
                                {"clsrm_id": clsrm_id, "sbjt_id": sbjt_id})

    def add_classroom_subjects(self, clsrm_id, *sbjt_ids):
        for sbjt_id in sbjt_ids:
            self.add_classroom_subject(clsrm_id, sbjt_id)

    def get_student_data(self, stdt_id):
        self.cursor.execute("SELECT * FROM students WHERE Student_ID = (:stdt_id)",
                            {"stdt_id": stdt_id})
        return self.cursor.fetchone()

    def get_all_students(self):
        self.cursor.execute("SELECT * FROM students")
        return self.cursor.fetchall()

    def get_num_students_yr(self, year):
        self.cursor.execute("""SELECT count(Student_ID) AS Num_Students
                                FROM students
                                WHERE Student_YearGroup = (:year)""",
                            {"year": year})
        return self.unpack_tuple(self.cursor.fetchone())

    def max_id_students(self):
        self.cursor.execute("SELECT MAX(Student_ID) from students")
        return self.unpack_tuple(self.cursor.fetchone())

    def add_student(self, firstname, lastname, year_id, email, subjects=None):
        with self.connection:
            self.cursor.execute(
                """INSERT INTO students (Student_Forename, Student_Surname, Student_Year, Student_Email)
                VALUES (:firstname, :lastname, :year_id, :email)""",
                {"firstname": firstname, "lastname": lastname, "year_id": year_id, "email": email})
        self.connection.commit()
        if subjects is not None:
            for subject in subjects:
                with self.connection:
                    self.cursor.execute("INSERT INTO student_subjects VALUES (:student_id, :subject_id)",
                                        {"student_id": self.max_id_students(),
                                         "subject_id": self.get_subject_id_from_subjects(subject)})
                    self.connection.commit()

    def update_student(self, student_id, firstname, lastname, year_id, email, subjects=None):
        with self.connection:
            self.cursor.execute(
                """UPDATE students SET Student_Forename = (:firstname),
                                       Student_Surname = (:lastname),
                                       Student_Year = (:year_id),
                                       Student_Email = (:email)
                WHERE Student_ID = (:student_id)""",
                {"firstname": firstname,
                 "lastname": lastname,
                 "year_id": year_id,
                 "email": email,
                 "student_id": student_id})
        self.connection.commit()
        self.delete_student_subjects(student_id)
        if subjects is not None:
            for subject in subjects:
                with self.connection:
                    self.cursor.execute("INSERT INTO student_subjects VALUES (:student_id, :subject_id)",
                                        {"student_id": student_id,
                                         "subject_id": self.get_subject_id_from_subjects(subject)})
                    self.connection.commit()

    def delete_student(self, student_id):
        with self.connection:
            self.cursor.execute("""DELETE FROM students WHERE Student_ID = (:stdt_id)""",
                                {"stdt_id": student_id})
        self.connection.commit()
        self.delete_student_subjects(student_id)

    def delete_student_subjects(self, student_id):
        with self.connection:
            self.cursor.execute("DELETE FROM student_subjects WHERE Student_ID = (:student_id)",
                                {"student_id": student_id})

    def add_teacher(self, code, email, firstname, surname, password, subject_ids):
        with self.connection:
            self.cursor.execute("""INSERT INTO teachers (Teacher_Code, Teacher_Email, Teacher_Forename, Teacher_Surname, Teacher_Password)
                                VALUES (:code, :email, :firstname, :surname, :password)""",
                                {"code": code, "email": email, "firstname": firstname, "surname": surname, "password": password})
            self.cursor.execute("""SELECT last_insert_rowid()""")
        insert_id = self.get_last_insert_rowid()
        for subject_id in subject_ids:
            self.add_teacher_subject(insert_id, subject_id)

    def add_teacher_subject(self, tchr_id, sbjt_id):
        with self.connection:
            self.cursor.execute("""INSERT INTO teacher_subjects (Teacher_ID, Subject_ID)
                                   VALUES (:insert_id, :subject_id)""",
                                {"insert_id": tchr_id, "subject_id": sbjt_id})

    def update_teacher(self, tchr_id, code, email, firstname, surname, password):
        with self.connection:
            self.cursor.execute("""UPDATE teachers 
                                   SET Teacher_Code = (:code), 
                                       Teacher_Email = (:email), 
                                       Teacher_Forename = (:firstname), 
                                       Teacher_Surname = (:surname), 
                                       Teacher_Password = (:password),
                                   WHERE Teacher_ID = (:tchr_id)""",
                                {"tchr_id": tchr_id,
                                 "code": code,
                                 "email": email,
                                 "firstname": firstname,
                                 "surname": surname,
                                 "password": password})

    def update_teacher_subjects(self, tchr_id, *sbjt_ids):
        self.delete_teacher_subjects(tchr_id)
        with self.connection:
            for sbjt_id in sbjt_ids:
                self.add_teacher_subject(tchr_id, sbjt_id)

    def delete_teacher(self, tchr_id):
        with self.connection:
            self.cursor.execute("""DELETE FROM teachers WHERE Teacher_ID = (:tchr_id)""",
                                {"tchr_id": tchr_id})
        self.delete_teacher_subjects(tchr_id)

    def delete_teacher_subjects(self, tchr_id):
        with self.connection:
            self.cursor.execute("""DELETE FROM teachers_subjects WHERE Teacher_ID = (:tchr_id)""",
                                {"tchr_id": tchr_id})

    def delete_subject(self, subject_id):
        with self.connection:
            self.cursor.execute("""DELETE FROM subjects WHERE Subject_ID = (:subject_id)""",
                                {"subject_id": subject_id})

    def update_subject(self, id_, code, name):
        with self.connection:
            self.cursor.execute("""UPDATE subjects
                                   SET Subject_Code = (:code),
                                       Subject_Name = (:name),
                                   WHERE Subject_ID = (:subject_id)""",
                                {"subject_id": id_,
                                 "code": code,
                                 "name": name})

    def add_subject(self, name, code):
        with self.connection:
            self.cursor.execute("""INSERT INTO subjects (Subject_Code, Subject_Name)
                                   VALUES (:code, :name)""",
                                {"code": code,
                                 "name": name})

    def check_sbjt_code_unique(self, code):
        self.cursor.execute("SELECT Subject_ID from subjects WHERE Subject_Code = (:subject_code)",
                            {"subject_code": code})
        return self.cursor.fetchone() is None

    def get_subject_data(self, sbjt_id):
        self.cursor.execute("""SELECT * FROM subjects WHERE Subject_ID = (:sbjt_id)""",
                            {"sbjt_id": sbjt_id})
        return self.cursor.fetchone()

    def get_subject_id_from_subjects(self, subject_name):
        self.cursor.execute("SELECT Subject_ID from subjects WHERE Subject_Name = (:subject_name)",
                            {"subject_name": subject_name})
        return self.unpack_tuple(self.cursor.fetchone())

    def get_subject_name_from_student_subjects(self, subject_id):
        self.cursor.execute("SELECT Subject_Name from subjects WHERE Subject_ID = (:subject_id)",
                            {"subject_id": subject_id})
        return self.unpack_tuple(self.cursor.fetchone())

    def get_all_subjects(self):
        self.cursor.execute("SELECT Subject_ID FROM subjects")
        return self.tuples_to_list(self.cursor.fetchall())

    def get_all_subject_data(self):
        self.cursor.execute("""SELECT * FROM subjects ORDER BY Subject_Code""")
        return self.cursor.fetchall()

    def get_core_subjects(self, year_id):
        self.cursor.execute("""SELECT subjects.Subject_ID
                                FROM subjects
                                INNER JOIN year_subjects
                                ON subjects.Subject_ID = year_subjects.Subject_ID
                                WHERE Year_ID = (:year) AND Subject_Option = '0'""",
                            {"year": year_id})
        return self.tuples_to_list(self.cursor.fetchall())

    def add_subject_to_year(self, year_id, subject_id, option, periods):
        with self.connection:
            self.cursor.execute("""INSERT INTO year_subjects
                                    VALUES (:year, :subject, :option, :periods)""",
                                {"year": year_id, "subject": subject_id, "option": option, "periods": periods})
        return self.get_last_insert_rowid()

    def delete_subject_from_year(self, year_id, subject_id, option):
        with self.connection:
            self.cursor.execute("""DELETE FROM year_subjects
                                    WHERE Year_ID = (:year)
                                    AND Subject_ID = (:subject)
                                    AND Subject_Option = (:option)""",
                                {"year": year_id, "subject": subject_id, "option": option})

    def get_option_subjects_by_year(self, year_id):
        self.cursor.execute("""SELECT subjects.Subject_ID
                                FROM subjects
                                INNER JOIN year_subjects
                                ON subjects.Subject_ID = year_subjects.Subject_ID
                                WHERE Year_ID = (:year) AND Subject_Option = '1'""",
                            {"year": year_id})
        return self.tuples_to_list(self.cursor.fetchall())

    def get_subject_data_by_year(self, year_id):
        self.cursor.execute("""SELECT subjects.Subject_ID, Subject_Code, Subject_Name, Subject_Option, Subject_Periods
                                FROM subjects
                                INNER JOIN year_subjects
                                ON subjects.Subject_ID = year_subjects.Subject_ID
                                WHERE Year_ID = (:year)
                                ORDER BY Subject_Code""",
                            {"year": year_id})
        return self.cursor.fetchall()

    def get_periods_in_year(self, year_id):
        self.cursor.execute("""SELECT COALESCE(sum(Subject_Periods),0)
                                FROM subjects
                                INNER JOIN year_subjects
                                ON subjects.Subject_ID = year_subjects.Subject_ID
                                WHERE Year_ID = (:year)""",
                            {"year": year_id})
        return self.unpack_tuple(self.cursor.fetchone())

    def get_all_option_subjects(self):
        self.cursor.execute("""SELECT subjects.Subject_ID
                                FROM subjects
                                INNER JOIN year_subjects
                                ON subjects.Subject_ID = year_subjects.Subject_ID
                                WHERE Subject_Option = '1'""")
        return self.tuples_to_list(self.cursor.fetchall())

    def get_students_in_year(self, year_id):
        self.cursor.execute("""SELECT Student_ID FROM students WHERE Student_Year=(:year)""",
                            {"year": year_id})
        return self.tuples_to_list(self.cursor.fetchall())

    def get_subject_code(self, subject_id):
        self.cursor.execute("""SELECT Subject_Code FROM subjects WHERE Subject_ID=(:subject_id)""",
                            {"subject_id": subject_id})
        return self.unpack_tuple(self.cursor.fetchone())

    def get_all_classes(self):
        self.cursor.execute("SELECT Class_ID FROM classes")
        return self.tuples_to_list(self.cursor.fetchall())

    def get_classes_in_set(self, set_id):
        self.cursor.execute("""SELECT Class_ID FROM set_classes WHERE Set_ID = (:set_id)""",
                            {"set_id": set_id})
        return self.tuples_to_list(self.cursor.fetchall())

    def get_subject_periods_of_set(self, set_id):
        self.cursor.execute("""SELECT Subject_ID, Set_Type FROM sets WHERE Set_ID = (:set_id)""",
                            {"set_id": set_id})
        data = self.cursor.fetchone()
        if data[1] == 1:
            return data[0], self.get_option_periods()
        self.cursor.execute("""SELECT Subject_Periods FROM subjects WHERE Subject_ID = (:subject_id)""",
                            {"subject_id": data[0]})
        return data[0], self.unpack_tuple(self.cursor.fetchone())

    def get_class_type(self, class_id):
        self.cursor.execute("""SELECT Class_Type FROM classes WHERE Class_ID = (:class_id)""",
                            {"class_id": class_id})
        return self.unpack_tuple(self.cursor.fetchone())

    def get_classes(self, year, subject_id, type_):
        self.cursor.execute("""SELECT Class_ID
                               FROM classes
                               WHERE Class_Year = (:year)
                                AND Class_Subject = (:subject)
                                AND Class_Type = (:type)""",
                            {"year": year, "subject": subject_id, "type": type_})
        return self.tuples_to_list(self.cursor.fetchall())

    def check_cls_tchr(self, prd_id, cls_id, tchr_id):
        self.cursor.execute("""SELECT count(Period_ID)
                                FROM class_placement
                                WHERE Period_ID = (:prd_id) AND Class_ID = (:cls_id) AND Teacher_ID = (:tchr_id)""",
                            {"prd_id": prd_id, "cls_id": cls_id, "tchr_id": tchr_id})
        return self.cursor.fetchall()[0]

    def get_cls_tchr_availability(self, cls_id, tchr_id):
        self.cursor.execute("""SELECT class_placement.Period_ID, tchr_prds.Period_ID
                                FROM class_placement
                                LEFT JOIN (SELECT Period_ID
                                FROM class_placement
                                WHERE Teacher_ID = (:tchr_id)) AS tchr_prds
                                ON class_placement.Period_ID = tchr_prds.Period_ID
                                WHERE class_placement.Class_ID = (:cls_id)
                                ORDER BY class_placement.Period_ID""",
                            {"tchr_id": tchr_id, "cls_id": cls_id})
        return self.cursor.fetchall()

    def get_cls_clsrm_availability(self, cls_id, clsrm_id):
        self.cursor.execute("""SELECT class_placement.Period_ID, clsrm_prds.Classroom_ID
                                FROM class_placement
                                LEFT JOIN (SELECT Classroom_ID
                                FROM class_placement
                                WHERE Classroom_ID = (:clsrm_id)) AS clsrm_prds
                                ON class_placement.Classroom_ID = clsrm_prds.Classroom_ID
                                WHERE class_placement.Class_ID = (:cls_id)""",
                            {"clsrm_id": clsrm_id, "cls_id": cls_id})
        return self.cursor.fetchall()

    def get_classes_by_subject(self, subject_id):
        """Fetches all of the classes that take a particular subject regardless of options"""
        self.cursor.execute("""SELECT classes.Class_ID, Block_Name, Class_Name, Year_ID, Subject_Periods
                                FROM classes
                                INNER JOIN set_classes
                                ON classes.Class_ID = set_classes.Class_ID
                                INNER JOIN block_sets
                                ON set_classes.Set_ID = block_sets.Set_ID
                                INNER JOIN blocks
                                ON block_sets.Block_ID = blocks.Block_ID
                                INNER JOIN year_subjects
                                ON classes.Class_Year = year_subjects.Year_ID 
                                   AND classes.Class_Subject = year_subjects.Subject_ID
                                WHERE Class_Subject = (:sbjt_id)""",
                            {"sbjt_id": subject_id})
        return self.cursor.fetchall()

    def get_subject_teachers(self, year_id):
        self.cursor.execute("""SELECT teacher_subjects.Subject_ID, Subject_Option, count(Teacher_ID) AS Num_Teachers
                                FROM teacher_subjects
                                INNER JOIN year_subjects
                                ON teacher_subjects.Subject_ID = year_subjects.Subject_ID
                                WHERE Subject_Periods != 0 AND Year_ID = (:year_id)
                                GROUP BY teacher_subjects.Subject_ID
                                ORDER BY Num_Teachers DESC""",
                            {"year_id": year_id})
        return self.cursor.fetchall()

    def get_subjects_of_student(self, student_id):
        self.cursor.execute("""SELECT subjects.Subject_Name
                               FROM subjects
                               INNER JOIN student_subjects
                                ON subjects.Subject_ID=student_subjects.Subject_ID
                               WHERE student_subjects.Student_ID = (:student_id)
                               ORDER BY subjects.Subject_Name""",
                            {"student_id": student_id})
        return self.tuples_to_list(self.cursor.fetchall())

    def get_student_subjects(self, student_id):
        self.cursor.execute("""SELECT subjects.Subject_ID
                               FROM subjects
                               INNER JOIN student_subjects
                                ON subjects.Subject_ID = student_subjects.Subject_ID
                               WHERE student_subjects.Student_ID = (:student_id)
                               ORDER BY subjects.Subject_Name""",
                            {"student_id": student_id})
        return self.tuples_to_list(self.cursor.fetchall())

    def get_required_periods_of_class(self, class_id):
        self.cursor.execute("""SELECT subjects.Subject_Periods
                               FROM classes
                               INNER JOIN subjects
                                ON classes.Class_Subject=subjects.Subject_ID
                               WHERE classes.Class_ID = (:class_id)""",
                            {"class_id": class_id})
        return self.unpack_tuple(self.cursor.fetchone())

    def get_students_by_subject(self, subject, year):
        self.cursor.execute("""SELECT student_subjects.Student_ID
                               FROM student_subjects
                               INNER JOIN subjects
                                ON student_subjects.Subject_ID=subjects.Subject_ID
                               INNER JOIN students
                                ON student_subjects.Student_ID=students.Student_ID
                               WHERE subjects.Subject_ID=(:subject_id)
                                AND students.Student_YearGroup=(:year)
                               ORDER BY student_subjects.Student_ID""",
                            {"subject_id": subject, "year": year})
        return self.tuples_to_list(self.cursor.fetchall())

    def get_period_availability(self, subject):
        self.cursor.execute("""SELECT results.Period_ID, count(results.Teacher_ID) AS Teacher_ID, results.Classroom_ID
                                FROM (SELECT unique_results.Period_ID, unique_results.Teacher_ID, count(unique_results.Classroom_ID) AS Classroom_ID
                                    FROM (SELECT DISTINCT periods.Period_ID, teacher_subjects.Teacher_ID, classroom_subjects.Classroom_ID
                                        FROM periods
                                        LEFT JOIN class_placement 
                                        ON periods.Period_ID=class_placement.Period_ID
                                        CROSS JOIN teacher_subjects
                                        CROSS JOIN classroom_subjects
                                        WHERE (teacher_subjects.Subject_ID = (:subject) AND classroom_subjects.Subject_ID = (:subject))
                                        AND classroom_subjects.Classroom_ID NOT IN (SELECT Classroom_ID FROM class_placement WHERE Period_ID = periods.Period_ID)
                                        AND (teacher_subjects.Teacher_ID NOT IN (SELECT Teacher_ID FROM class_placement WHERE Period_ID = periods.Period_ID)))
                                    AS unique_results
                                    GROUP BY unique_results.Period_ID, unique_results.Teacher_ID)
                                AS results
                                GROUP BY results.Period_ID""",
                            {"subject": subject})
        return self.cursor.fetchall()

    def get_num_sbjt_clss_prd(self, subject_id):
        """For a particular subject, it returns the num class for that subject already timetabled"""
        self.cursor.execute("""SELECT periods.Period_ID, COALESCE(sum(table1.num_sbjt_clss),0) AS Num_Subject_Classes
                                FROM periods
                                LEFT JOIN (SELECT periods.Period_ID, count(classes.Class_Subject) AS num_sbjt_clss
                                FROM periods
                                INNER JOIN class_placement
                                ON periods.Period_ID = class_placement.Period_ID
                                INNER JOIN classes 
                                ON class_placement.Class_ID = classes.Class_ID
                                WHERE classes.Class_Subject = (:subject_id)
                                GROUP BY periods.Period_ID) AS table1
                                ON periods.Period_ID = table1.Period_ID
                                GROUP BY periods.Period_ID""",
                            {"subject_id": subject_id})
        return self.cursor.fetchall()

    def get_num_yr_clss_prd(self, year_id):
        self.cursor.execute("""SELECT periods.Period_ID, COALESCE(sum(table2.num_yr_clss),0) AS Num_Year_Classes
                                FROM periods
                                LEFT JOIN (SELECT periods.Period_ID, count(class_placement.Period_ID) AS num_yr_clss
                                FROM periods
                                LEFT JOIN class_placement
                                ON periods.Period_ID = class_placement.Period_ID
                                INNER JOIN classes
                                ON class_placement.Class_ID = classes.Class_ID
                                WHERE classes.Class_Year = (:year_id)
                                GROUP BY periods.Period_ID
                                ORDER BY num_yr_clss) AS table2
                                ON periods.Period_ID = table2.Period_ID
                                GROUP BY periods.Period_ID""",
                            {"year_id": year_id})
        return self.cursor.fetchall()

    def get_existing_set_classes(self, subject_id, year_id):
        self.cursor.execute("""SELECT count(Class_ID) as Num_Classes
                                FROM sets
                                INNER JOIN set_classes
                                ON sets.Set_ID = set_classes.Set_ID
                                WHERE Subject_ID = (:subject_id) 
                                AND Set_Year = (:year_id)
                                GROUP BY sets.Set_ID
                                ORDER BY Num_Classes DESC""",
                            {"subject_id": subject_id, "year_id": year_id})
        return self.tuples_to_list(self.cursor.fetchall())

    def get_teacher_availability(self, period_id, subject_id):
        self.cursor.execute("""SELECT T.Teacher_ID, 
                                (SELECT count(CP.Teacher_ID) FROM class_placement CP WHERE T.Teacher_ID = CP.Teacher_ID) AS Contact_Periods
                                FROM (SELECT Teacher_ID
                                FROM teacher_subjects
                                WHERE Subject_ID = (:subject_id)) AS T
                                WHERE T.Teacher_ID NOT IN (SELECT Teacher_ID 
                                FROM class_placement 
                                WHERE Period_ID = (:period_id))""",
                            {"subject_id": subject_id, "period_id": period_id})
        return self.cursor.fetchall()

    def get_classroom_availability(self, period, subject_id):
        self.cursor.execute("""SELECT C.Classroom_ID
                                FROM (SELECT Classroom_ID
                                FROM classroom_subjects
                                WHERE Subject_ID = (:subject_id)) AS C
                                WHERE C.Classroom_ID NOT IN (SELECT Classroom_ID
                                FROM class_placement 
                                WHERE Period_ID = (:period_id))""",
                            {"subject_id": subject_id, "period_id": period})
        return self.tuples_to_list(self.cursor.fetchall())

    def get_classroom_sizes(self):
        self.cursor.execute("""SELECT MaxNoStudents FROM classrooms""")
        return self.tuples_to_list(self.cursor.fetchall())

    def insert_class_placement(self, period, class_id, teacher_id, classroom_id):
        with self.connection:
            self.cursor.execute("""INSERT INTO class_placement
                                    VALUES (:period, :class, :teacher, :classroom)""",
                                {"period": period,
                                 "class": class_id,
                                 "teacher": teacher_id,
                                 "classroom": classroom_id})

    def create_empty_class(self, name, number, year, subject, cls_type):
        with self.connection:
            self.cursor.execute("""INSERT INTO classes (Class_Name,
                                                        Class_Number,
                                                        Class_Year,
                                                        Class_Subject,
                                                        Class_Type)
                                   VALUES (:name, :number, :year, :subject, :type)""",
                                {"name": name,
                                 "number": number,
                                 "year": year,
                                 "subject": subject,
                                 "type": cls_type})

    def create_class(self, name, number, year, students, subject, cls_type):
        self.cursor.execute("SELECT MAX(Class_ID) FROM classes")
        value = self.unpack_tuple(self.cursor.fetchone())
        if value is None:
            value = 1
        else:
            value += 1
        with self.connection:
            self.cursor.execute("""INSERT INTO classes (Class_ID,
                                                        Class_Name,
                                                        Class_Number,
                                                        Class_Year,
                                                        Class_Subject,
                                                        Class_Type)
                                   VALUES (:class_id, :name, :number, :year, :subject, :type)""",
                                {"class_id": value,
                                 "name": name,
                                 "number": number,
                                 "year": year,
                                 "subject": subject,
                                 "type": cls_type})
            for student in students:
                self.cursor.execute("""INSERT INTO class_students (Class_ID, Student_ID)
                                       VALUES (:class_id, :student_id)""",
                                    {"class_id": value, "student_id": student})

    def fetch_student_timetable(self, student_id):
        self.cursor.execute("""SELECT periods.Period_ID, Subject_Code, Teacher_Code, Classroom_Name
                                FROM periods
                                LEFT JOIN (SELECT Period_ID, Subject_Code, Teacher_Code, Classroom_Name
                                FROM class_placement
                                INNER JOIN (SELECT Class_ID
                                FROM class_students
                                WHERE Student_ID = (:student_id)) AS stdt_clss
                                ON class_placement.Class_ID = stdt_clss.Class_ID
                                LEFT JOIN classes
                                ON class_placement.Class_ID = classes.Class_ID
                                LEFT JOIN classrooms
                                ON class_placement.Classroom_ID = classrooms.Classroom_ID
                                LEFT JOIN teachers
                                ON class_placement.Teacher_ID = teachers.Teacher_ID
                                LEFT JOIN subjects
                                ON classes.Class_Subject = subjects.Subject_ID) AS period_data
                                ON periods.Period_ID = period_data.Period_ID""",
                            {"student_id": student_id})
        return self.cursor.fetchall()

    def fetch_teacher_timetable(self, teacher_id):
        self.cursor.execute("""SELECT periods.Period_ID, Subject_Code, Class_Name, Classroom_Name
                                FROM periods
                                LEFT JOIN (SELECT Period_ID, Subject_Code, Class_Name, Classroom_Name
                                FROM class_placement
                                LEFT JOIN classes
                                ON class_placement.Class_ID = classes.Class_ID
                                LEFT JOIN classrooms
                                ON class_placement.Classroom_ID = classrooms.Classroom_ID
                                LEFT JOIN subjects
                                ON classes.Class_Subject = subjects.Subject_ID
                                WHERE Teacher_ID = (:teacher_id)) AS period_data
                                ON periods.Period_ID = period_data.Period_ID""",
                            {"teacher_id": teacher_id})
        return self.cursor.fetchall()

    def fetch_classroom_timetable(self, classroom_id):
        self.cursor.execute("""SELECT periods.Period_ID, Subject_Code, Teacher_Code, Class_Name
                                FROM periods
                                LEFT JOIN (SELECT class_placement.Period_ID, Subject_Code, Teacher_Code, Class_Name
                                FROM class_placement
                                LEFT JOIN classes
                                ON class_placement.Class_ID = classes.Class_ID
                                LEFT JOIN teachers
                                ON class_placement.Teacher_ID = teachers.Teacher_ID
                                LEFT JOIN subjects
                                ON classes.Class_Subject = subjects.Subject_ID
                                WHERE Classroom_ID = (:classroom_id)) AS period_data
                                ON periods.Period_ID = period_data.Period_ID""",
                            {"classroom_id": classroom_id})
        return self.cursor.fetchall()

    def add_all_subjects_to_classrooms(self):
        subject_ids = self.get_all_subjects()
        classrooms = self.get_all_classrooms()
        with self.connection:
            for classroom in classrooms:
                for subject_id in subject_ids:
                    self.cursor.execute("""INSERT INTO classroom_subjects (Classroom_ID, Subject_ID)
                                           VALUES (:classroom_id, :subject_id)""",
                                        {"classroom_id": classroom, "subject_id": subject_id})

    def add_all_subjects_to_teachers(self):
        subject_ids = self.get_all_subjects()
        teachers = self.get_all_teachers()
        with self.connection:
            for teacher in teachers:
                for subject_id in subject_ids:
                    self.cursor.execute("""INSERT INTO teacher_subjects (Teacher_ID, Subject_ID)
                                           VALUES (:teacher_id, :subject_id)""",
                                        {"teacher_id": teacher, "subject_id": subject_id})

    def create_periods(self):
        with self.connection:
            for week in range(1, 3):
                for day in range(1, 6):
                    for period in range(1, 6):
                        self.cursor.execute("""INSERT INTO periods (Period_Number, Period_Day, Period_Week)
                                               VALUES (:number, :day, :week)""",
                                            {"number": period, "day": day, "week": week})

    def get_all_sets(self):
        self.cursor.execute("""SELECT Set_ID FROM sets""")
        return self.tuples_to_list(self.cursor.fetchall())

    def create_set(self, subject, year, number, type_):
        with self.connection:
            self.cursor.execute("""INSERT INTO sets (Subject_ID, Set_Year, Set_Number, Set_Type) 
                                   VALUES (:subject, :year, :number, :type)""",
                                {"subject": subject, "year": year, "number": number, "type": type_})

    def add_class_to_set(self, set_id, class_id):
        with self.connection:
            self.cursor.execute("""INSERT INTO set_classes (Set_ID, Class_ID) 
                                   VALUES (:set, :class)""",
                                {"set": set_id, "class": class_id})

    def create_block(self, name, year, number):
        with self.connection:
            self.cursor.execute("""INSERT INTO blocks (Block_Name, Block_Year, Block_Number) 
                                   VALUES (:name, :year, :number)""",
                                {"name": name, "year": year, "number": number})

    def add_set_to_block(self, block_id, set_id):
        with self.connection:
            self.cursor.execute("""INSERT INTO block_sets (Block_ID, Set_ID) 
                                   VALUES (:block, :set)""",
                                {"block": block_id, "set": set_id})

    def get_set_id(self, subject, year, number, type_):
        self.cursor.execute("""SELECT Set_ID FROM sets
                                WHERE Subject_ID = (:subject)
                                AND Set_Year = (:year)
                                AND Set_Number = (:number)
                                AND Set_Type = (:type)""",
                            {"subject": subject, "year": year, "number": number, "type": type_})
        return self.unpack_tuple(self.cursor.fetchone())

    def get_last_insert_rowid(self):
        self.cursor.execute("""SELECT last_insert_rowid()""")
        return self.unpack_tuple(self.cursor.fetchone())

    def search_students(self, phrase):
        if phrase == "":
            return None
        self.cursor.execute("""SELECT * FROM students""")
        students = self.cursor.fetchall()
        if phrase == "*":
            return students
        results = []
        for student in students:
            for i in range(4):
                data = str(student[i])[:len(phrase)].lower()
                if phrase == data or phrase == data.title():
                    results.append(student)
                    break
        if len(results) == 0:
            return None
        return results

    def search_teachers(self, phrase):
        if phrase == "":
            return None
        self.cursor.execute("""SELECT Teacher_ID, 
                                      Teacher_Forename, 
                                      Teacher_Surname, 
                                      Teacher_Code 
                               FROM teachers""")
        teachers = self.cursor.fetchall()
        if phrase == "*":
            return teachers
        results = []
        for teacher in teachers:
            for i in range(3):
                data = str(teacher[i])[:len(phrase)].lower()
                if phrase == data or phrase == data.title():
                    results.append(teacher)
                    break
        if len(results) == 0:
            return None
        return results

    def search_classrooms(self, phrase):
        if phrase == "":
            return None
        self.cursor.execute("""SELECT * FROM classrooms""")
        classrooms = self.cursor.fetchall()
        results = []
        if phrase == "*":
            return classrooms
        for classroom in classrooms:
            for i in range(3):
                data = str(classroom[i])[:len(phrase)].lower()
                if phrase == data or phrase == data.title():
                    results.append(classroom)
                    break
        if len(results) == 0:
            return None
        return results

    @staticmethod
    def tuples_to_list(list_of_tuples):
        return [item for t in list_of_tuples for item in t]

    @staticmethod
    def unpack_tuple(single_tuple):
        if single_tuple is None:
            return None
        return single_tuple[0]


if __name__ == "__main__":
    pass
