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

# Maps are (name, regions, borders). Add your own to the MAPS list below.

# Australia: the textbook map. Tasmania is an island, so it borders nothing
# and is free to take any color.
AUSTRALIA = (
    "Australia",
    ["WA", "NT", "SA", "Q", "NSW", "V", "T"],
    [("WA", "NT"), ("WA", "SA"), ("NT", "SA"), ("NT", "Q"), ("SA", "Q"),
     ("SA", "NSW"), ("SA", "V"), ("Q", "NSW"), ("NSW", "V")],
)

# Four regions in a ring: opposite corners can reuse a color, so 2 is enough.
RING = (
    "Four regions in a ring",
    ["A", "B", "C", "D"],
    [("A", "B"), ("B", "C"), ("C", "D"), ("D", "A")],
)

# Three regions that all border each other. None can reuse a color, so this
# is the case that makes 3 the minimum rather than 2.
TRIANGLE = (
    "Three mutually bordering regions",
    ["X", "Y", "Z"],
    [("X", "Y"), ("Y", "Z"), ("X", "Z")],
)

MAPS = [AUSTRALIA, RING, TRIANGLE]


def show(assignment, regions, indent="    "):
    """One line of 'region=color' pairs, lined up in columns."""
    width = max(len(r) for r in regions) + 7
    return indent + " ".join(f"{r + '=' + assignment[r]:<{width}}"
                             for r in regions)


def report(name, regions, borders, show_all=False):
    print(f"\n{name}")
    print("-" * len(name))
    print(f"  {len(regions)} regions, {len(borders)} borders")

    solutions = map_coloring_csp(regions, borders, COLORS).solve_all()
    if not solutions:
        print(f"  no coloring exists with {len(COLORS)} colors")
        return

    k, _ = minimum_colors(regions, borders, COLORS)
    print(f"  fewest colors needed: {k}")
    print("  one solution:")
    print(show(solutions[0], regions))
    print(f"  {len(solutions)} solution(s) with {len(COLORS)} colors, "
          f"all valid: {all(is_valid(s, borders) for s in solutions)}")

    if show_all:
        for i, each in enumerate(solutions, 1):
            print(f"    {i:>3}." + show(each, regions, indent=" "))


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

    print("\nThree colors handles all three maps. Two is sometimes enough")
    print("(the ring), but three mutually bordering regions rule it out, which")
    print("is what makes 3 the minimum. minimum_colors() reports the smallest")
    print("palette that works by re-solving the CSP with 1, then 2, then 3.")


if __name__ == "__main__":
    main()
