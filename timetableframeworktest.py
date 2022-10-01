from timetableconstraintframework import *
from timeit import default_timer as timer


class SetConstraint(Constraint):
    """Makes sure sets are scheduled at the same time"""
    def __init__(self, classes: List[C]) -> None:
        super().__init__(classes)

    def satisfied(self, cls1, prd1, tchr1, rm1, cls2, prd2, tchr2, rm2) -> bool:
        return prd1 == prd2


class BandConstraint(Constraint):
    """Makes sure classes of the same number cannot be scheduled at the same time"""
    def __init__(self, classes: List[C]) -> None:
        super().__init__(classes)

    def satisfied(self, cls1: C, prd1: P, tchr1: T, rm1: R, cls2: C, prd2: P, tchr2: T, rm2: R) -> bool:
        return prd1 != prd2


class SubjectTeacherConstraint(Constraint):
    """Makes sure classes have the correct subject teacher"""
    def __init__(self, classes: List[C], teachers: List[T]) -> None:
        super().__init__(classes)
        self.teachers = teachers

    def satisfied(self, cls1: C, prd1: P, tchr1: T, rm1: R, cls2: C, prd2: P, tchr2: T, rm2: R) -> bool:
        return tchr1 in self.teachers


class MaxTeacherConstraint(Constraint):
    """Teachers cannot teach more than their max number of periods"""
    def __init__(self, classes: List[C]) -> None:
        super().__init__(classes)

    def satisfied(self, cls1: C, prd1: P, tchr1: T, rm1: R, cls2: C, prd2: P, tchr2: T, rm2: R) -> bool:
        return prd1 != prd2


def main():
    classes = [1, 2, 3]
    periods = [11, 12, 13]
    teachers = [21, 22, 23]
    classrooms = [31, 32, 33]
    period_domains = {}
    teacher_domains = {}
    classroom_domains = {}
    for cls in classes:
        period_domains[cls] = periods
        teacher_domains[cls] = teachers
        classroom_domains[cls] = classrooms

    csp: CSP = CSP(classes, periods, teachers, classrooms)
    csp.set_domains(period_domains, teacher_domains, classroom_domains)
    csp.add_constraint(SetConstraint([1, 2]))
    csp.add_constraint(BandConstraint([1, 3]))
    start = timer()
    solution: Optional[Dict[str, str]] = csp.backtracking_search()
    print(timer() - start)
    if solution is None:
        print("No solution found")
    else:
        print(solution, csp.num_backtracks)


if __name__ == '__main__':
    main()
