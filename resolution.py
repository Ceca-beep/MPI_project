from typing import List, Set, FrozenSet

import time
import tracemalloc


Clause = Set[str]
CNF = List[Clause]

def parse_dimacs(filepath: str) -> CNF:
    cnf = []
    with open(filepath, 'r') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('c') or line.startswith('p') or line.startswith('%') or line == '0':
                continue
            tokens = line.split()
            if tokens[-1] == '0':
                tokens = tokens[:-1]
            clause = set()
            for tok in tokens:
                if tok.startswith('-'):
                    clause.add(f'¬{tok[1:]}')
                else:
                    clause.add(tok)
            cnf.append(clause)
    return cnf

def print_cnf_readable(cnf: CNF):
    print("CNF Formula (Human-readable):")
    for clause in cnf:
        print("(", " ∨ ".join(sorted(clause)), ")")
    print()

def negate(literal: str) -> str:
    return literal[1:] if literal.startswith('¬') else f'¬{literal}'

def all_resolvents(c1: Clause, c2: Clause) -> List[Clause]:
    resolvents = []
    for lit in c1:
        if negate(lit) in c2:
            new_clause = (c1 - {lit}) | (c2 - {negate(lit)})
            resolvents.append(new_clause)
    return resolvents

def resolution_solver(cnf: CNF) -> str:
    clauses = set(frozenset(clause) for clause in cnf)
    new = set()

    while True:
        pairs = [(c1, c2) for i, c1 in enumerate(clauses) for j, c2 in enumerate(clauses) if i < j]
        for c1, c2 in pairs:
            resolvents = all_resolvents(set(c1), set(c2))
            for r in resolvents:
                fr = frozenset(r)
                if not r:
                    return "UNSATISFIABLE"
                if fr not in clauses:
                    new.add(fr)

        if not new:
            return "SATISFIABLE"
        clauses.update(new)
        new.clear()

# ------------------ MAIN ------------------
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: py resolution.py myformula.cnf")
        sys.exit(1)

    path = sys.argv[1]
    cnf_formula = parse_dimacs(path)

    tracemalloc.start()
    start_time = time.time()

    print_cnf_readable(cnf_formula)

    result = resolution_solver(cnf_formula)

    end_time = time.time()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()


    print("Assignment:", result)
    print(f"Time taken: {end_time - start_time:.4f} seconds")
    print(f"Memory used: {current / 1024:.2f} KB")
    print(f"Peak memory: {peak / 1024:.2f} KB")
