from timetableconstraints import *
from abc import abstractmethod
from database import MainDatabase
from math import ceil
import statistics as stats
from pprint import pprint


class Entity:
    """Represents any item within the database that has PK"""
    def __init__(self, id_: int, type_: str) -> None:
        self.id: int = id_
        self.type: str = type_


class Year(Entity):
    def __init__(self, id_: int, option: bool) -> None:
        super().__init__(id_, "Y")
        self.subjects: Subjects = Subjects()
        self.prd_clss: Periods = Periods()
        self.num_clss: int = 0
        self.option: bool = option


class Years(dict):
    def __init__(self: Dict[int, Year]) -> None:
        super().__init__()


class Subject(Entity):
    def __init__(self, id_: int, req_prds: int, num_tchrs: int) -> None:
        super().__init__(id_, "Sj")
        self.req_prds = req_prds
        self.num_tchrs = num_tchrs
        self.sbjt_prds: Periods = Periods()
        self.clss_distribution: tuple = ()


class Subjects(dict):
    def __init__(self: Dict[int, Subject]) -> None:
        super().__init__()


class Period(Entity):
    def __init__(self, id_: int, num_clss: int) -> None:
        super().__init__(id_, "P")
        self.num_clss = num_clss


class Periods(dict):
    def __init__(self: Dict[int, Period]) -> None:
        super().__init__()


class SubjectsEntity(Entity):
    def __init__(self, id_: int, type_: str):
        super().__init__(id_, type_)
        self.subjects: List[Entity] = []

    def add_sbjt(self, id_: int) -> None:
        self.subjects.append(Entity(id_, "Sj"))


class Students:
    def __init__(self) -> None:
        self.students: List[SubjectsEntity] = []


class Teachers:
    def __init__(self) -> None:
        self.teachers: List[SubjectsEntity] = []


class Classrooms:
    def __init__(self) -> None:
        self.teachers: List[SubjectsEntity] = []


class Class(Entity):
    def __init__(self, id_: int, sbjt_id: int) -> None:
        super().__init__(id_, "Cl")
        self.students: List[Entity] = []
        self.subject: Entity = Entity(sbjt_id, "Sj")
        self.num_prds = 0
        self.teacher = None
        self.classroom = None

    def add_stdt(self, id_: int) -> None:
        self.students.append(Entity(id_, "St"))

    def add_tchr(self, id_: int) -> None:
        self.teacher = Entity(id_, "T")

    def add_clrm(self, id_: int) -> None:
        self.teacher = Entity(id_, "Cm")


class Classes:
    def __init__(self):
        self.classes: List[Class] = []


class CSPManager:

    db = None

    def __init__(self, database):
        self.db = database
        self.curriculum_csp = CurriculumCSP(self.db)

    def configure_curriculum_csp(self):
        self.curriculum_csp.config_data()
        self.curriculum_csp.config_csp()


class CurriculumCSP(CSP):
    def __init__(self, database) -> None:
        super().__init__()
        self.db: MainDatabase = database
        self.error_log = []
        self.years: Years = Years()

    def config_data(self) -> None:
        """Updates data from database"""
        self._set_years()

    def config_csp(self) -> None:
        """Updates CSP to match the data"""
        # insert for loop here for each year
        yr: Year = self.years[1]
        classes: List[ClassVariable] = []
        domains: Dict[ClassVariable, List[int]] = {}
        domain: List[int] = list(range(1, 50 * yr.num_clss + 1))
        for sbjt in yr.subjects.values():
            for num, set_ in enumerate(sbjt.clss_distribution, 1):
                for cls in range(set_):
                    for prd in range(sbjt.req_prds):
                        classes.append(ClassVariable(sbjt.id, num, cls, prd))
                        domains[classes[-1]] = domain
        self.set_domains(classes, domains)
        start = timer()
        solution = self.backtracking_search()
        print(timer()-start)
        print(solution)

    def _set_years(self) -> None:
        """Instantiates the year class for each year"""
        for yr in self.db.get_all_year_data():
            year: Year = Year(yr[0], bool(yr[3]))
            year.num_clss = self._get_num_clss(yr[0])
            self._set_num_clss_prds(year)
            self._set_subjects(year)
            self.years[yr[0]] = year

    def _get_num_clss(self, yr_id: int) -> int:
        """Calculates the number of classes needed in that particular year"""
        ideal_class_size = round(stats.mean(self.db.get_classroom_sizes()))
        num_students = len(self.db.get_students_in_year(yr_id))
        return ceil(num_students/ideal_class_size)

    def _set_num_clss_prds(self, year: Year) -> None:
        """Sets periods: Dict[id, Period] to the existing classes during each period of that year"""
        for prd in self.db.get_num_yr_clss_prd(year.id):
            year.prd_clss[prd[0]] = Period(*prd)

    def _set_subjects(self, year: Year) -> None:
        """Sets subjects: Dict[id, Subject] to the subjects in each year"""
        for sbjt in self.db.get_subject_teachers(year.id):
            subject: Subject = Subject(*sbjt)
            self._set_num_sbjt_prds(year, subject)
            self._set_req_clss(year.num_clss, subject)
            year.subjects[sbjt[0]] = subject
            # pprint(vars(subject))

    def _set_num_sbjt_prds(self, year: Year, subject: Subject) -> None:
        """Sets periods: Dict[id, Period] to the existing classes for each subject"""
        for prd in self.db.get_num_sbjt_clss_prd(year.id):
            subject.sbjt_prds[prd[0]] = Period(*prd)

    def _set_req_clss(self, num_clss: int, subject: Subject) -> None:
        """Sets the required number of classes"""
        num_sets = self._cal_num_sets(num_clss, subject.num_tchrs)
        if num_sets:
            subject.clss_distribution = self.split_int(num_clss, num_sets)

    def _cal_num_sets(self, num_clss: int, num_tchrs: int) -> int:
        """Calculates the number of sets needed"""
        num_sets: int = 0
        try:
            num_sets = ceil(num_clss / num_tchrs)
        except ZeroDivisionError as no_tchr_error:
            self.error_log.append(no_tchr_error)
        finally:
            return num_sets

    @staticmethod
    def split_int(num, div):
        """Splits integer into values as close as possible to equal length"""
        remainder = num % div
        integer = num // div
        splits = []
        for i in range(div):
            splits.append(integer)
        for i in range(remainder):
            splits[i] += 1
        return tuple(splits)


if __name__ == '__main__':
    main_database = MainDatabase("Main Database")
    csp_manager = CSPManager(main_database)
    csp_manager.configure_curriculum_csp()
