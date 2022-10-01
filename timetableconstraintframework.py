from typing import Generic, TypeVar, Dict, List, Tuple, Optional
from abc import ABC, abstractmethod
from random import choice

C = TypeVar("C")
T = TypeVar("T")
R = TypeVar("R")
P = TypeVar("P")


class Constraint(Generic[C, P, T, R], ABC):
    """Framework for a constraint"""
    def __init__(self, classes: List[C]) -> None:
        self.classes = classes

    def __repr__(self) -> str:
        return "C:" + str(self.classes)

    @abstractmethod
    def satisfied(self, cls1: C, prd1: P, tchr1: T, rm1: R, cls2: C, prd2: P, tchr2: T, rm2: R) -> bool:
        """Needs to be overwritten to create a custom constraint"""
        ...


class CSP:
    """Constraint satisfaction framework stores variables, domains and constraints"""
    def __init__(self, classes: List[int], periods: List[int], teachers: List[int], classrooms: List[int]) -> None:
        self.num_backtracks, self.num_assigns = 0, 0
        self.fc, self.mcv = False, False
        self.len_clss = len(classes)

        self.classes: List[C] = classes
        self.periods: List[P] = periods
        self.teachers: List[T] = teachers
        self.classrooms: List[R] = classrooms

        self.assignment: Dict[C, Tuple[P, T, R]] = {}  # assigns a class a period, teacher, and a classroom

        self.prd_domain: Dict[C, List[P]] = {}  # the periods each class can take
        self.tchr_domain: Dict[C, List[T]] = {}  # the teacher each class can take, dependant on subject
        self.clsrm_domain: Dict[C, List[R]] = {}  # the classroom each can take, dependant on subject

        self.tchr_availability: Dict[P, List[T]] = {}  # check which teachers are available at any given time
        self.clsrm_availability: Dict[P, List[R]] = {}  # check which classrooms are available at any given time

        self.constraints: Dict[C, List[Constraint]] = {}  # constrains classes across all dimensions of the domains

        self.matrix: Dict[P, Dict[T, Dict[R, Optional[C]]]] = {}

        self._initialise_availability()
        self._initialise_constraints()
        self._initialise_matrix()

    def set_domains(self, periods: Dict[C, List[P]], teachers: Dict[C, List[T]], classrooms: Dict[C, List[R]]) -> None:
        """Sets the domains of the CSP"""
        self.prd_domain = periods
        self.tchr_domain = teachers
        self.clsrm_domain = classrooms
        # check they contain classes as variables

    def _initialise_availability(self) -> None:
        """Populates each period with resources available"""
        for period in self.periods:
            self.tchr_availability[period] = self.teachers
            self.clsrm_availability[period] = self.classrooms

    def _initialise_constraints(self) -> None:
        """Populates each class with an empty constraint list"""
        for cls in self.classes:
            self.constraints[cls] = []

    def _initialise_matrix(self) -> None:
        """Populates the 3D matrix with periods x teachers x classrooms"""
        for prd in self.periods:
            self.matrix[prd] = {}
            for tchr in self.teachers:
                self.matrix[prd][tchr] = {}
                for clsrm in self.classrooms:
                    self.matrix[prd][tchr][clsrm] = None

    def _assign(self, cls: C, prd: P, tchr: T, clsrm: R) -> None:
        """Adds to matrix and discards old value. Bookkeeping for num_assigns"""
        self.num_assigns += 1
        self.matrix[prd][tchr][clsrm] = cls
        self.assignment[cls] = (prd, tchr, clsrm)
        self.tchr_availability[prd].remove(tchr)
        self.clsrm_availability[prd].remove(clsrm)
        if self.fc:
            pass
            # self._forward_check(cls, prd, tchr, clsrm)

    def _unassign(self, cls: C) -> None:
        """Backtrack by removing the value set to a variable in assignment"""
        prd, tchr, clsrm = self.assignment[cls]
        self.matrix[prd][tchr][clsrm] = None
        self.tchr_availability[prd].append(tchr)
        self.clsrm_availability[prd].append(clsrm)
        del self.assignment[cls]

    def _num_conflicts(self, cls: C, prd: P, tchr: T, clsrm: R) -> int:
        """Return the number of conflicts var=val with other variables already assigned"""
        num_conflicts: int = 0
        for constraint in self.constraints[cls]:
            for class_ in constraint.classes:
                values: Optional[Tuple[P, T, R]] = self.assignment.get(class_)
                if values is not None:
                    if not constraint.satisfied(class_, values[0], values[1], values[2], cls, prd, tchr, clsrm):
                        num_conflicts += 1
        return num_conflicts

    def _backtrack_domains(self) -> None:
        """Backtrack by removing items of the stack to reflect recursion depth"""
        self.num_backtracks += 1
        if self.fc:
            pass
            # self.current_domains = self.current_domain_stack.pop_item()

    def add_constraint(self, constraint: Constraint) -> None:
        """Adds the constraint to all the variables specified in the constraint"""
        for cls in constraint.classes:
            if cls not in self.classes:
                raise LookupError("Class in constraint not in CSP")
            else:
                self.constraints[cls].append(constraint)  # adds the constraint to the variable

    def _forward_check(self) -> None:
        """Checks each constraint and its variables to see if any of their domains can be reduced"""
        """for constraint in self.constraints[var]:
            for variable in constraint.variables:
                if variable not in assignment:
                    for value in domains[variable][:]:
                        if not constraint.satisfied(var, val, variable, value, assignment):
                            domains[variable].remove(value)"""

    def _check_complete(self) -> bool:
        """Checks if the program is complete by checking if all the classes have been placed"""
        return len(self.assignment) == self.len_clss

    def _select_unassigned_class(self) -> C:
        """Considers which class to try to place into timetable next"""
        # gets all variables in the CSP but not in the assignment
        unassigned = [c for c in self.classes if c not in self.assignment.keys()]
        # fix mcv later
        if self.mcv:
            weighted_vars = [(v, self._num_legal_values(v)) for v in unassigned]
            weighted_vars.sort(key=lambda k: k[1])  # sorts the variables by domain length
            return weighted_vars[0][0]
        # selects at class at random if mcv heuristic not specified
        return choice(unassigned)

    def _num_legal_values(self, cls: C) -> tuple:
        """Returns the number of items in each of the domains"""
        return tuple(map(len, (self.prd_domain[cls], self.tchr_domain[cls], self.clsrm_domain[cls])))

    def _order_period_values(self, cls: C) -> List[P]:
        """Decides the order in which to try periods"""
        domain = self.prd_domain[cls][:]
        return domain

    def _order_teacher_values(self, cls: C, prd: P) -> List[T]:
        """Decides the order in which to try teachers"""
        list1 = self.tchr_domain[cls][:]
        list2 = self.tchr_availability[prd][:]
        domain = list(set(list1) & set(list2))
        return domain

    def _order_classroom_values(self, cls: C, prd: P, tchr: T) -> List[R]:
        """Decides the order in which to try classrooms"""
        list1 = self.clsrm_domain[cls][:]
        list2 = self.clsrm_availability[prd][:]
        domain = list(set(list1) & set(list2))
        return domain

    def backtracking_search(self, mcv=False, fc=False):
        """Call point to begin the backtracking search"""
        self.num_backtracks = 0
        self.fc, self.mcv = fc, mcv
        return self._period_recursive_backtracking()

    def _period_recursive_backtracking(self) -> Optional[Dict[C, P]]:
        """Depth-first search which back tracks to the last known decision and chooses a different path"""
        print(self.assignment)
        if self._check_complete():  # Checks if program is complete
            return self.assignment  # returns solution back down the stack
        # gets every possible domain value of the most constrained unassigned variable
        cls: C = self._select_unassigned_class()
        for prd in self._order_period_values(cls):
            if self._num_conflicts(cls, prd, None, None) == 0:  # if still consistent then call next layer
                result: Optional[Dict[C, P]] = self._teacher_recursive_backtracking(cls, prd)
                if result is not None:  # if the result is not found, the program will backtrack
                    return result
        return None

    def _teacher_recursive_backtracking(self, cls, prd) -> Optional[Dict[C, P]]:
        """Depth-first search which back tracks to the last known decision and chooses a different path"""
        for tchr in self._order_teacher_values(cls, prd):
            if self._num_conflicts(cls, prd, tchr, None) == 0:  # if still consistent then call next layer
                result: Optional[Dict[C, P]] = self._classroom_recursive_backtracking(cls, prd, tchr)
                if result is not None:  # if the result is not found, the program will backtrack
                    return result
        return None

    def _classroom_recursive_backtracking(self, cls, prd, tchr) -> Optional[Dict[C, P]]:
        """Depth-first search which back tracks to the last known decision and chooses a different path"""
        for clsrm in self._order_classroom_values(cls, prd, tchr):
            if self._num_conflicts(cls, prd, tchr, clsrm) == 0:  # if still consistent then call next layer
                self._assign(cls, prd, tchr, clsrm)
                result: Optional[Dict[C, P]] = self._period_recursive_backtracking()
                if result is not None:  # if the result is not found, the program will backtrack
                    return result
                self._backtrack_domains()
            self._unassign(cls)
        return None


if __name__ == '__main__':
    pass
