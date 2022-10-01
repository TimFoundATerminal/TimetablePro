from constraintframework import Constraint, CSP, Dict, List, Optional
from timeit import default_timer as timer


class ClassVariable:
    def __init__(self, sbjt_id, set_num, cls_num, prd_num) -> None:
        self.sbjt: int = sbjt_id
        self.set_num: int = set_num
        self.cls_num: int = cls_num
        self.cls_prd_num: int = prd_num

    def __repr__(self):
        return str((self.sbjt, self.set_num, self.cls_num, self.cls_prd_num))


class SameSetConstraint(Constraint[ClassVariable, int]):
    def __init__(self, classes: List[ClassVariable]) -> None:
        Constraint.__init__(self, classes)
        self.classes: List[ClassVariable] = classes

    def satisfied(self, var1, val1, var2, val2, assignment: Dict[int, int]) -> bool:
        if var1.sbjt == var2.sbjt and var1.set_num == var2.set_num:
            return True
        return False


def main():
    clss: List[ClassVariable] = []
    prds: Dict[ClassVariable, List[int]] = {}
    domain: List[int] = list(range(28))
    for set_num, set_ in enumerate((2, )):
        for cls in range(set_):
            for prd in range(4):
                clss.append(ClassVariable(0, set_num, cls, prd))
                prds[clss[-1]] = domain
    for set_num, set_ in enumerate((1, 1)):
        for cls in range(set_):
            for prd in range(3):
                clss.append(ClassVariable(1, set_num, cls, prd))
                prds[clss[-1]] = domain
    for set_num, set_ in enumerate((1, 1)):
        for cls in range(set_):
            for prd in range(5):
                clss.append(ClassVariable(2, set_num, cls, prd))
                prds[clss[-1]] = domain
    csp: CSP[str, int] = CSP()
    csp.set_domains(clss, prds)
    csp.add_constraint(SameSetConstraint(clss))
    print(csp.variables)
    print(csp.domains)
    print(csp.neighbours)
    print(csp.constraints)
    start = timer()
    solution: Optional[Dict[str, int]] = csp.backtracking_search(mcv=True)
    print(timer()-start)
    if solution is None:
        print("No solution found!")
    else:
        print(solution, csp.num_backtracks)


if __name__ == '__main__':
    main()
