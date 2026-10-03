import sys


class CSP:
    def __init__(self, variables, domains, constraints):
        self.variables = variables  # list of variables
        self.domains = domains  # dict of domains for each variable
        self.constraints = constraints  # list of constraints (functions)

    def is_consistent(self, variable, assignment):
        """Check if the current assignment is consistent."""
        for constraint in self.constraints:
            if not constraint(assignment):
                return False
        return True

    def backtrack(self, assignment):
        """Backtrack search to find a solution."""
        if len(assignment) == len(self.variables):
            return assignment

        unassigned = [v for v in self.variables if v not in assignment]
        first = unassigned[0]
        for value in self.domains[first]:
            local_assignment = assignment.copy()
            local_assignment[first] = value
            if self.is_consistent(first, local_assignment):
                result = self.backtrack(local_assignment)
                if result is not None:
                    return result
        return None

    def solve(self):
        """Solve the CSP."""
        return self.backtrack({})

    def backtrack_all(self, assignment, solutions):
        """Same search, but record each complete assignment and keep going."""
        if len(assignment) == len(self.variables):
            solutions.append(assignment)
            return solutions

        unassigned = [v for v in self.variables if v not in assignment]
        first = unassigned[0]
        for value in self.domains[first]:
            local_assignment = assignment.copy()
            local_assignment[first] = value
            if self.is_consistent(first, local_assignment):
                self.backtrack_all(local_assignment, solutions)
        return solutions

    def solve_all(self):
        """Solve the CSP, returning every valid assignment."""
        return self.backtrack_all({}, [])


# Example CSP: Sudoku
def sudoku_constraints(assignment):
    """Define constraints for Sudoku."""
    for i in range(9):
        row = [assignment.get((i, j)) for j in range(9) if (i, j) in assignment]
        col = [assignment.get((j, i)) for j in range(9) if (j, i) in assignment]
        if len(set(row)) != len(row) or len(set(col)) != len(col):
            return False
    return True


def sudoku_example():
    """The handout's 4x4 Sudoku.

    It constrains rows and columns but not the 2x2 boxes, so the answer is a
    Latin square rather than a true Sudoku grid.
    """
    # Variables and domains for a simple 4x4 Sudoku
    variables = [(i, j) for i in range(4) for j in range(4)]
    domains = {var: list(range(1, 5)) for var in variables}
    constraints = [sudoku_constraints]

    # Creating CSP instance
    sudoku_csp = CSP(variables, domains, constraints)
    solution = sudoku_csp.solve()
    print("Sudoku Solution:", solution)

    for i in range(4):
        print("   ", " ".join(str(solution[(i, j)]) for j in range(4)))


def different_colors(region_a, region_b):
    """Constraint: two bordering regions cannot share a color.

    Returns True while either region is still unassigned, so the constraint
    works on the partial assignments backtracking produces.
    """
    def constraint(assignment):
        if region_a in assignment and region_b in assignment:
            return assignment[region_a] != assignment[region_b]
        return True
    return constraint


def map_coloring_csp(regions, borders, colors):
    """Variables = regions, domains = colors, constraints = one per border."""
    domains = {region: list(colors) for region in regions}
    constraints = [different_colors(a, b) for a, b in borders]
    return CSP(list(regions), domains, constraints)


def is_valid(assignment, borders):
    """Verify a finished coloring against every border."""
    return all(assignment[a] != assignment[b] for a, b in borders)


def minimum_colors(regions, borders, palette):
    """Smallest number of colors that works: try 1, then 2, then 3..."""
    for k in range(1, len(palette) + 1):
        solution = map_coloring_csp(regions, borders, palette[:k]).solve()
        if solution is not None:
            return k, solution
    return None, None


# Three colors, per the problem statement.
COLORS = ["red", "green", "blue"]

# One spare color, used only to report maps that 3 cannot handle.
SPARE = "yellow"

# Maps are (name, regions, borders). Add your own to the MAPS list below.

# All three of these border each other, so none can share a color. This is
# the case that makes 3 the minimum rather than 2.
BORDER_TRIO = (
    "Mexico, Guatemala, Belize",
    ["Mexico", "Guatemala", "Belize"],
    [("Mexico", "Guatemala"), ("Mexico", "Belize"), ("Guatemala", "Belize")],
)

# El Salvador and Nicaragua meet only across the Gulf of Fonseca, so they
# are not neighbors by land and may share a color.
CENTRAL_AMERICA = (
    "Central America",
    ["Mexico", "Belize", "Guatemala", "El Salvador", "Honduras",
     "Nicaragua", "Costa Rica", "Panama"],
    [("Mexico", "Belize"), ("Mexico", "Guatemala"), ("Belize", "Guatemala"),
     ("Guatemala", "El Salvador"), ("Guatemala", "Honduras"),
     ("El Salvador", "Honduras"), ("Honduras", "Nicaragua"),
     ("Nicaragua", "Costa Rica"), ("Costa Rica", "Panama")],
)

# Brazil, Bolivia, Paraguay and Argentina all border one another, so this
# map cannot be done in 3 colors at all.
SOUTH_AMERICA = (
    "South America",
    ["Colombia", "Venezuela", "Guyana", "Suriname", "French Guiana", "Brazil",
     "Ecuador", "Peru", "Bolivia", "Paraguay", "Chile", "Argentina", "Uruguay"],
    [("Colombia", "Venezuela"), ("Colombia", "Brazil"), ("Colombia", "Peru"),
     ("Colombia", "Ecuador"), ("Venezuela", "Guyana"), ("Venezuela", "Brazil"),
     ("Guyana", "Suriname"), ("Guyana", "Brazil"), ("Suriname", "French Guiana"),
     ("Suriname", "Brazil"), ("French Guiana", "Brazil"), ("Ecuador", "Peru"),
     ("Peru", "Brazil"), ("Peru", "Bolivia"), ("Peru", "Chile"),
     ("Brazil", "Bolivia"), ("Brazil", "Paraguay"), ("Brazil", "Argentina"),
     ("Brazil", "Uruguay"), ("Bolivia", "Paraguay"), ("Bolivia", "Chile"),
     ("Bolivia", "Argentina"), ("Paraguay", "Argentina"), ("Chile", "Argentina"),
     ("Argentina", "Uruguay")],
)

MAPS = [BORDER_TRIO, CENTRAL_AMERICA, SOUTH_AMERICA]

# How many colorings to print under --all before summarizing the rest.
LIST_LIMIT = 30


def show(assignment, regions, prefix="    "):
    """'region=color' pairs, wrapped so a pair never splits across lines."""
    pad = " " * len(prefix)
    lines, line = [], prefix
    for region in regions:
        pair = f"{region}={assignment[region]}"
        if line.strip() and len(line) + len(pair) > 78:
            lines.append(line.rstrip())
            line = pad
        line += pair + "   "
    lines.append(line.rstrip())
    return "\n".join(lines)


def report(name, regions, borders, show_all=False):
    print(f"\n{name}")
    print("-" * len(name))
    print(f"  {len(regions)} regions, {len(borders)} borders")

    palette = COLORS
    solutions = map_coloring_csp(regions, borders, palette).solve_all()
    if not solutions:
        print(f"  no coloring exists with {len(COLORS)} colors, retrying "
              f"with {SPARE}")
        palette = COLORS + [SPARE]
        solutions = map_coloring_csp(regions, borders, palette).solve_all()

    k, _ = minimum_colors(regions, borders, palette)
    print(f"  fewest colors needed: {k}")
    print("  one solution:")
    print(show(solutions[0], regions))
    print(f"  {len(solutions)} solution(s) with {len(palette)} colors, "
          f"all valid: {all(is_valid(s, borders) for s in solutions)}")

    if show_all:
        for i, each in enumerate(solutions[:LIST_LIMIT], 1):
            print(show(each, regions, prefix=f"  {i:>4}. "))
        if len(solutions) > LIST_LIMIT:
            print(f"  ... and {len(solutions) - LIST_LIMIT:,} more "
                  f"(solve_all() returns the full list)")


def main():
    show_all = "--all" in sys.argv

    print("Part 2: basic solver on the handout's 4x4 Sudoku")
    sudoku_example()

    print("\nPart 3: map coloring")
    print("Variables: regions   Domains: colors   Constraints: neighbors differ")
    if not show_all:
        print("(run with --all to list every solution)")

    for name, regions, borders in MAPS:
        report(name, regions, borders, show_all)

    print("\nThree colors is the minimum for most maps: two is never enough")
    print("once three countries all border each other, as Mexico, Guatemala")
    print("and Belize do. But three is not always sufficient. In South America,")
    print("Brazil, Bolivia, Paraguay and Argentina each border the other three,")
    print("so that map needs a fourth color. Four is always enough for a flat")
    print("map (Four Color Theorem).")


if __name__ == "__main__":
    main()
