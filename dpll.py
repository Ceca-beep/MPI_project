from typing import List, Set, Dict, Optional

import time
import tracemalloc

Clause = Set[str]
CNF = List[Clause]
Assignment = Dict[str, bool]

def parse_dimacs(filepath: str) -> CNF:
    cnf = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('c') or line.startswith('%') or line.startswith('0'):
                continue
            if line.startswith('p'):
                continue  # Skip problem line
            literals = line.split()
            if literals[-1] == '0':
                literals = literals[:-1]
            clause = set()
            for lit in literals:
                if lit.startswith('-'):
                    clause.add(f'¬{lit[1:]}')
                else:
                    clause.add(lit)
            cnf.append(clause)
    return cnf

def print_cnf_readable(cnf: CNF):
    print("CNF Formula (Human-readable):")
    for clause in cnf:
        print("(", " ∨ ".join(sorted(clause)), ")")
    print()

def negate(lit: str) -> str:
    return lit[1:] if lit.startswith('¬') else f'¬{lit}'

def is_satisfied(clause: Clause, assignment: Assignment) -> bool:
    for lit in clause:
        var = lit.strip('¬')
        if var in assignment:
            value = assignment[var]
            if (lit == var and value) or (lit == f'¬{var}' and not value):
                return True
    return False

def is_conflict(clause: Clause, assignment: Assignment) -> bool:
    return all(
        (lit.strip('¬') in assignment and (
            (lit.startswith('¬') and assignment[lit[1:]]) or
            (not lit.startswith('¬') and not assignment[lit]))
        )
        for lit in clause
    )

def unit_propagate(cnf: CNF, assignment: Assignment) -> Optional[Assignment]:
    changed = True
    while changed:
        changed = False
        for clause in cnf:
            if is_satisfied(clause, assignment):
                continue
            unassigned = [lit for lit in clause if lit.strip('¬') not in assignment]
            if len(unassigned) == 1:
                lit = unassigned[0]
                var = lit.strip('¬')
                val = not lit.startswith('¬')
                if var in assignment and assignment[var] != val:
                    return None
                assignment[var] = val
                changed = True
            elif all(lit.strip('¬') in assignment for lit in clause) and not is_satisfied(clause, assignment):
                return None
    return assignment

def pure_literal_assign(cnf: CNF, assignment: Assignment) -> Assignment:
    all_literals = {lit for clause in cnf for lit in clause}
    vars = set(lit.strip('¬') for lit in all_literals)
    for var in vars:
        pos = var in all_literals
        neg = f'¬{var}' in all_literals
        if pos != neg and var not in assignment:
            assignment[var] = pos
    return assignment

def dpll(cnf: CNF, assignment: Assignment = {}) -> Optional[Assignment]:
    cnf = [clause for clause in cnf if not is_satisfied(clause, assignment)]

    if any(is_conflict(clause, assignment) for clause in cnf):
        return None

    if not cnf:
        return assignment

    assignment = pure_literal_assign(cnf, assignment.copy())
    assignment = unit_propagate(cnf, assignment)
    if assignment is None:
        return None

    unassigned_vars = {lit.strip('¬') for clause in cnf for lit in clause} - assignment.keys()
    if not unassigned_vars:
        return assignment

    var = next(iter(unassigned_vars))
    for val in [True, False]:
        new_assignment = assignment.copy()
        new_assignment[var] = val
        result = dpll(cnf, new_assignment)
        if result is not None:
            return result
    return None

# -------- Main --------
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: py dpll.py myformula.cnf")
        sys.exit(1)

    path = sys.argv[1]
    cnf_formula = parse_dimacs(path)

    tracemalloc.start()
    start_time = time.time()

    print_cnf_readable(cnf_formula)

    result = dpll(cnf_formula)

    end_time = time.time()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    if result:
        print("SATISFIABLE")
    else:
        print("UNSATISFIABLE")
    print(f"Time taken: {end_time - start_time:.4f} seconds")
    print(f"Memory used: {current / 1024:.2f} KB")
    print(f"Peak memory: {peak / 1024:.2f} KB")


