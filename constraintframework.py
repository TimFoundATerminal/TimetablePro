from typing import Generic, TypeVar, Dict, List, Set, Optional
from abc import ABC, abstractmethod
import copy
from random import choice


V = TypeVar("V")
D = TypeVar("D")


class Stack(list):
    """Using a list to create a stack"""
    def __init__(self) -> None:
        list.__init__([])
        self._size = 0

    def push(self, obj: object) -> None:
        """Adds item to top of stack"""
        self._size += 1
        self.append(obj)

    def pop_item(self) -> object:
        """Removes item from top of stack and returns it"""
        self._size -= 1
        return self.pop()

    def top(self) -> object:
        """Return reference to top of stack"""
        return self[-1]

    def size(self) -> int:
        """Size of the stack"""
        return self._size

    def empty(self) -> bool:
        """Checks if stack is empty"""
        return self._size == 0


class Queue(list):
    """First in, first out data structure"""
    def __init__(self) -> None:
        super().__init__()

    def enqueue(self, obj: object) -> None:
        """Places item in the queue"""
        self.append(obj)

    def dequeue(self) -> object:
        """Removes and returns first item in the queue"""
        return self.pop(0)

    def first(self) -> object:
        """Returns value of first item in queue"""

    def last(self) -> object:
        """Returns value of last item in queue"""


class Constraint(Generic[V, D], ABC):
    """Framework for a constraint"""
    def __init__(self, variables: List[V]) -> None:
        self.variables = variables

    def __repr__(self) -> str:
        return "C:" + str(self.variables)

    @abstractmethod
    def satisfied(self, var1: V, val1: D, var2: V, val2: D, assignment: Dict[V, D]) -> bool:
        """Needs to be overwritten to create a custom constraint"""
        ...


class UnaryConstraint(Generic[V, D], ABC):
    """Framework for a unary constraint"""
    def __init__(self, variables: List[V]) -> None:
        self.variables = variables

    @abstractmethod
    def satisfied(self, val1: D) -> bool:
        """Needs to be overwritten to create a custom constraint"""
        ...


class BinaryConstraint(Generic[V, D], ABC):
    """Framework for a unary constraint"""
    def __init__(self, variables: List[V]) -> None:
        self.variables = variables

    @abstractmethod
    def satisfied(self, val1: D, val2: D) -> bool:
        """Needs to be overwritten to create a custom constraint"""
        ...


class CSP(Generic[V, D]):
    """Constraint satisfaction framework stores variables, domains and constraints"""
    def __init__(self) -> None:
        self.num_backtracks, self.num_assigns = 0, 0
        self.mcv, self.fc = False, False
        self.variables: List[V] = []
        self.domains: Dict[V, List[D]] = {}
        self.constraints: Dict[V, List[Constraint[V, D]]] = {}
        self.neighbours: Dict[V, Set[V]] = {}
        self.initial_assignment: Dict[V, D] = {}
        self.current_domains: Dict[V, List[D]] = {}
        self.current_domain_stack = Stack()

    def set_domains(self, variables: List[V], domains: Dict[V, List[D]]):
        """Sets the domains of the CSP"""
        self.variables = variables or domains.keys()
        self.domains = domains
        for variable in self.variables:
            self.constraints[variable] = []
            self.neighbours[variable] = set()
            if variable not in self.domains:
                raise LookupError("Every variable should have a domain assigned to it")

    def _assign(self, variable: V, value: D, assignment: Dict[V, D]) -> None:
        """Adds to assignment and discards old value. Bookkeeping for current_domains and num_assigns"""
        self.num_assigns += 1
        assignment[variable] = value
        if self.fc:
            self.current_domain_stack.push(copy.deepcopy(self.current_domains))
            self._forward_check(variable, value, self.current_domains, assignment)
            self._AC3([(var, variable) for var in self.neighbours[variable]])

    @staticmethod
    def _unassign(variable: V, assignment: Dict[V, D]) -> None:
        """Backtrack by removing the value set to a variable in assignment"""
        if variable in assignment:
            del assignment[variable]

    def _num_conflicts(self, var: V, val: D, assignment: Dict[V, D]) -> int:
        """Return the number of conflicts var=val with other variables already assigned"""
        num_conflicts: int = 0
        for variable in self.neighbours[var]:
            value: Optional[D] = assignment.get(variable, None)
            if value is not None and not self._constraints_satisfied(var, val, variable, value, assignment):
                num_conflicts += 1
        return num_conflicts

    def _backtrack_domains(self) -> None:
        """Backtrack by removing items of the stack to reflect recursion depth"""
        self.num_backtracks += 1
        if self.fc:
            self.current_domains = self.current_domain_stack.pop_item()

    def add_constraint(self, constraint: Constraint[V, D]) -> None:
        """Adds the constraint to all the variables specified in the constraint"""
        for variable in constraint.variables:
            if variable not in self.variables:
                raise LookupError("Variable in constraint not in CSP")
            else:
                self.constraints[variable].append(constraint)  # adds the constraint to the variable
                self.neighbours[variable] |= set(constraint.variables)  # union of sets to remove duplicates
                self.neighbours[variable].remove(variable)  # cannot be a neighbour to itself

    def _AC3(self, queue: List = None) -> None:
        """Arc consistency checking algorithm"""
        if queue is None:
            queue = [(a, b) for a in self.variables for b in self.neighbours[a]]
        while queue:
            a, c = queue.pop(0)
            if self._remove_inconsistent_values(a, c):
                for b in self.neighbours[a]:
                    queue.append((b, a))

    def _remove_inconsistent_values(self, a, c) -> bool:
        """Returns true if a value is removed, false otherwise"""
        removed = False
        for val in self.current_domains[a][:]:
            result = [self._constraints_satisfied(a, val, c, value, {}) for value in self.current_domains[c]]
            if not any(result):
                self.current_domains[a].remove(val)
                removed = True
        return removed

    def _constraints_satisfied(self, var1: V, val1: D, var2: V, val2: D, assignment: Dict[V, D]) -> bool:
        """Checks for these conditions satisfy all constraints on variable 1"""
        for constraint in self.constraints[var1]:
            if not constraint.satisfied(var1, val1, var2, val2, assignment):
                return False
        return True

    def _forward_check(self, var: V, val: D, domains: Dict[V, List[D]],  assignment: Dict[V, D]) -> None:
        """Checks each constraint and its variables to see if any of their domains can be reduced"""
        for variable in self.neighbours[var]:  # fetches all of the variables the variable relates to
            if variable not in assignment:  # variables already assigned, domains do not need to be reduced
                for value in domains[variable][:]:
                    if not self._constraints_satisfied(var, val, variable, value, assignment):
                        domains[variable].remove(value)  # removes inconsistent values from domains

    def _check_complete(self, assignment: Dict[V, D]) -> bool:
        """Checks if the program is complete by checking if all the variables have values"""
        return len(assignment) == len(self.variables)

    def _select_unassigned_variable(self, assignment: Dict[V, D]) -> V:
        """Considers which variable to try next"""
        # selects variables that are in the CSP but are not in the assignment
        unassigned = [v for v in self.variables if v not in assignment]
        if self.mcv:  # most constrained value heuristic
            weighted_vars = [(v, self._num_legal_values(v)) for v in unassigned]  # assigns a weight to each variable
            weighted_vars.sort(key=lambda k: k[1])  # sorts the variables by domain length
            return weighted_vars[0][0]
        return choice(unassigned)  # if mcv not specified then a random variable is returned

    def _num_legal_values(self, var: V) -> int:
        """Returns the number of items in a domain"""
        if self.current_domains:
            return len(self.current_domains[var])
        return len(self.domains[var])

    def _order_domain_values(self, variable: V, assignment: Dict[V, D]) -> D:
        """Decides whether reduced variable domain should be used"""
        if self.current_domains:
            domain = self.current_domains[variable]
            if not domain:
                self._unassign(variable, assignment)
        else:
            domain = self.domains[variable][:]
        return domain

    def backtracking_search(self, mcv=False, fc=False):
        """Call point to begin the backtracking search"""
        self.num_backtracks = 0
        if fc:
            for variable in self.variables:
                self.current_domains[variable] = self.domains[variable][:]
            self._AC3()
        self.fc, self.mcv = fc, mcv
        return self._recursive_backtracking(self.initial_assignment)

    def _recursive_backtracking(self, assignment: Dict[V, D]) -> Optional[Dict[V, D]]:
        """Depth-first search which backtracks to the last known decision and chooses a different path"""
        if self._check_complete(assignment):  # Checks if program is complete
            return assignment  # returns solution back down the stack
        # gets every possible domain value of the most constrained unassigned variable
        var: V = self._select_unassigned_variable(assignment)
        for val in self._order_domain_values(var, assignment):
            if self._num_conflicts(var, val, assignment) == 0:  # if still consistent then recurse again
                self._assign(var, val, assignment)
                result: Optional[Dict[V, D]] = self._recursive_backtracking(assignment)
                if result is not None:  # if the result is not found, the program will backtrack
                    return result
                self._backtrack_domains()
            self._unassign(var, assignment)
        return None


if __name__ == '__main__':
    pass
