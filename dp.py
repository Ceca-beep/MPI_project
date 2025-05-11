from typing import List, Set

import time
import tracemalloc

Clause = Set[str]
CNF = List[Clause]

def print_cnf_readable(cnf: CNF):
    print("CNF Formula (Human-readable):")
    for clause in cnf:
        print("(", " ∨ ".join(sorted(clause)), ")")
    print()

def negate(literal: str) -> str:
    return literal[1:] if literal.startswith('¬') else f'¬{literal}'

def is_tautology(clause: Clause) -> bool:
    return any(negate(lit) in clause for lit in clause)

def resolve(c1: Clause, c2: Clause, var: str) -> Clause:
    new_clause = (c1 - {var}) | (c2 - {negate(var)})
    return new_clause

def davis_putnam(cnf: CNF) -> str:
    # Set of all clauses to avoid duplicates
    clause_set = set(frozenset(c) for c in cnf)

    variables = {lit.strip('¬') for clause in cnf for lit in clause}

    while variables:
        var = variables.pop()

        pos_clauses = [c for c in clause_set if var in c]
        neg_clauses = [c for c in clause_set if negate(var) in c]

        new_clauses = set()
        for pc in pos_clauses:
            for nc in neg_clauses:
                resolvent = resolve(set(pc), set(nc), var)
                if not resolvent:
                    return "UNSATISFIABLE"
                if not is_tautology(resolvent):
                    new_clauses.add(frozenset(resolvent))

        # Remove all clauses containing var or ¬var
        clause_set = {
            c for c in clause_set
            if var not in c and negate(var) not in c
        }

        # Check if any new clause was added; if not, break to avoid infinite loop
        before = len(clause_set)
        clause_set.update(new_clauses)
        after = len(clause_set)
        if before == after:
            break  # No progress — exit

    return "SATISFIABLE" if not clause_set else "UNSATISFIABLE"


# ---------- CNF Parsing from DIMACS format (string version) ----------

def parse_dimacs_string(dimacs: str) -> CNF:
    cnf = []
    for line in dimacs.strip().splitlines():
        line = line.strip()
        if not line or line.startswith('c') or line.startswith('%') or line.startswith('0'):
            continue
        if line.startswith('p'):
            continue
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


# ------------------ MAIN ------------------
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: py dp.py myformula.cnf")
        sys.exit(1)

    path = sys.argv[1]
    cnf_formula = parse_dimacs_string(path)

    tracemalloc.start()
    start_time = time.time()

    print_cnf_readable(cnf_formula)

    result = davis_putnam(cnf_formula)

    end_time = time.time()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print("Assignment:", result)

    print(f"Time taken: {end_time - start_time:.4f} seconds")
    print(f"Memory used: {current / 1024:.2f} KB")
    print(f"Peak memory: {peak / 1024:.2f} KB")
