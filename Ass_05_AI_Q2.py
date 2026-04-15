"""
CSP-based Sudoku Solver with Backtracking, Forward Checking, and AC-3
Author: AI Assistant  
Description: Solves Sudoku puzzles using Constraint Satisfaction Problem (CSP) approach
             with backtracking search, forward checking, and AC-3 constraint propagation.
"""

from copy import deepcopy
from typing import Dict, List, Tuple, Set, Optional


class SudokuCSP:
    """
    Constraint Satisfaction Problem solver for Sudoku puzzles.
    Uses backtracking with forward checking and AC-3 constraint propagation.
    """
    
    def __init__(self, grid: List[List[int]]):
        """
        Initialize the CSP with a 9x9 Sudoku grid.
        
        Args:
            grid: 9x9 list of integers where 0 represents empty cells
        """
        self.grid = [row[:] for row in grid]
        self.original_grid = [row[:] for row in grid]
        
        # Initialize domains: each variable (cell) has possible values
        self.domains = self._initialize_domains()
        
        # Pre-compute neighbors for efficiency
        self.neighbors = {}
        for row in range(9):
            for col in range(9):
                self.neighbors[(row, col)] = self._compute_neighbors(row, col)
        
        # Track statistics
        self.backtrack_count = 0
        self.backtrack_failures = 0
        
    def _initialize_domains(self) -> Dict[Tuple[int, int], Set[int]]:
        """
        Create initial domains for each cell.
        Pre-assigned cells have only one value in their domain.
        Empty cells have domain {1,2,...,9}.
        """
        domains = {}
        for row in range(9):
            for col in range(9):
                if self.grid[row][col] != 0:
                    # Pre-assigned cell
                    domains[(row, col)] = {self.grid[row][col]}
                else:
                    # Empty cell - can be any value 1-9
                    domains[(row, col)] = set(range(1, 10))
        return domains
    
    def _compute_neighbors(self, row: int, col: int) -> Set[Tuple[int, int]]:
        """
        Compute all neighboring cells that share constraints with (row, col).
        Neighbors include:
        - All cells in the same row
        - All cells in the same column
        - All cells in the same 3x3 box
        """
        neighbors = set()
        
        # Same row
        for c in range(9):
            if c != col:
                neighbors.add((row, c))
        
        # Same column
        for r in range(9):
            if r != row:
                neighbors.add((r, col))
        
        # Same 3x3 box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                if (r, c) != (row, col):
                    neighbors.add((r, c))
        
        return neighbors
    
    def _revise(self, xi: Tuple[int, int], xj: Tuple[int, int]) -> bool:
        """
        Revise domain of xi with respect to xj.
        Returns True if the domain of xi was modified.
        
        AC-3 core: If xj is assigned, remove its value from xi's domain
        if xj has only one value (is assigned).
        """
        revised = False
        
        # Only revise if xj is assigned (has exactly one value)
        if len(self.domains[xj]) == 1:
            xj_val = next(iter(self.domains[xj]))
            if xj_val in self.domains[xi]:
                self.domains[xi].discard(xj_val)
                revised = True
        
        return revised
    
    def ac3(self) -> bool:
        """
        AC-3 algorithm: Enforce arc consistency.
        Returns False if an inconsistency is detected (no solution possible).
        
        AC-3 efficiently processes constraints to reduce domains.
        """
        # Queue of all arcs (initially includes all assigned variables' neighbors)
        queue = []
        for row in range(9):
            for col in range(9):
                if len(self.domains[(row, col)]) == 1:  # Assigned variable
                    xi = (row, col)
                    for xj in self.neighbors[xi]:
                        queue.append((xj, xi))
        
        while queue:
            xi, xj = queue.pop(0)
            
            if self._revise(xi, xj):
                # Domain of xi was reduced
                if len(self.domains[xi]) == 0:
                    return False  # Inconsistency
                
                # Add neighbors of xi to queue
                for xk in self.neighbors[xi]:
                    if xk != xj:
                        queue.append((xk, xi))
        
        return True
    
    def constraint_propagation(self) -> bool:
        """
        Combined constraint propagation: forward checking + AC-3.
        After each value assignment, propagate constraints.
        """
        # Apply immediate AC-3 once
        if not self.ac3():
            return False
        
        # Check for cells with only one value (naked singles) and propagate
        changed = True
        while changed:
            changed = False
            for row in range(9):
                for col in range(9):
                    cell = (row, col)
                    # If cell has exactly one value
                    if len(self.domains[cell]) == 1:
                        value = next(iter(self.domains[cell]))
                        # Remove this value from all neighbors
                        for neighbor in self.neighbors[cell]:
                            if value in self.domains[neighbor] and len(self.domains[neighbor]) > 1:
                                self.domains[neighbor].discard(value)
                                changed = True
                                if len(self.domains[neighbor]) == 0:
                                    return False
        
        return True
    
    def select_unassigned_variable(self) -> Optional[Tuple[int, int]]:
        """
        Select the next unassigned variable using the Minimum Remaining Values (MRV) heuristic.
        This heuristic chooses the variable with the smallest domain,
        which helps detect failures early and reduces the search space.
        """
        unassigned = []
        for row in range(9):
            for col in range(9):
                cell = (row, col)
                # Check if cell is unassigned (has more than 1 value in domain)
                if len(self.domains[cell]) > 1:
                    unassigned.append(cell)
        
        if not unassigned:
            return None
        
        # Return the variable with minimum remaining values (MRV heuristic)
        return min(unassigned, key=lambda var: len(self.domains[var]))
    
    def backtrack(self) -> bool:
        """
        Backtracking search with constraint propagation.
        
        Algorithm:
        1. If all variables assigned, return True (solution found)
        2. Select unassigned variable using MRV heuristic
        3. For each value in variable's domain (sorted for consistency):
           a. Try assigning the value
           b. Apply constraint propagation
           c. Recursively backtrack
           d. If successful, return True
           e. Otherwise, undo assignment (backtrack)
        4. If no value works, return False
        """
        # Check if all variables are assigned
        var = self.select_unassigned_variable()
        if var is None:
            return True  # Solution found
        
        self.backtrack_count += 1
        
        # Try each value in the domain (sorted for consistency)
        for value in sorted(self.domains[var]):
            # Save the current state for backtracking
            domains_backup = deepcopy(self.domains)
            
            # Assign the value
            self.domains[var] = {value}
            
            # Apply constraint propagation
            if self.constraint_propagation():
                # Constraint propagation succeeded, try recursive search
                if self.backtrack():
                    return True
            
            # Backtracking: restore the domain
            self.domains = domains_backup
            self.backtrack_failures += 1
        
        return False
    
    def solve(self) -> bool:
        """
        Main solving method.
        Applies initial constraint propagation and then calls backtracking search.
        """
        # Apply initial constraint propagation for all initially assigned cells
        if not self.constraint_propagation():
            return False
        
        # Start backtracking search
        return self.backtrack()
    
    def get_solution(self) -> List[List[int]]:
        """
        Extract the solution from the domains.
        Each variable should have exactly one value in its domain.
        """
        solution = [[0] * 9 for _ in range(9)]
        for row in range(9):
            for col in range(9):
                domain = self.domains[(row, col)]
                if len(domain) == 1:
                    solution[row][col] = domain.pop()
                    domain.add(solution[row][col])  # Put it back
        return solution
    
    def print_solution(self):
        """Pretty print the solution."""
        solution = self.get_solution()
        for i, row in enumerate(solution):
            if i % 3 == 0 and i != 0:
                print("------+-------+------")
            row_str = " ".join(str(x) for x in row[:3])
            row_str += " | " + " ".join(str(x) for x in row[3:6])
            row_str += " | " + " ".join(str(x) for x in row[6:9])
            print(row_str)


def read_sudoku_file(filename: str) -> List[List[int]]:
    """
    Read a Sudoku puzzle from a text file.
    Expected format: 9 lines, each with exactly 9 digits (0-9).
    0 represents an empty cell.
    """
    grid = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if len(line) == 9:
                    row = [int(digit) for digit in line]
                    grid.append(row)
        
        if len(grid) == 9:
            return grid
        else:
            raise ValueError(f"Expected 9 rows, got {len(grid)}")
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None
    except ValueError as e:
        print(f"Error reading file: {e}")
        return None


def solve_sudoku_file(filename: str, board_name: str) -> Tuple[bool, int, int, List[List[int]]]:
    """
    Solve a Sudoku puzzle from a file.
    
    Returns:
        - Success flag (bool)
        - Number of backtrack calls
        - Number of backtrack failures
        - Solution grid
    """
    grid = read_sudoku_file(filename)
    if grid is None:
        return False, 0, 0, None
    
    print(f"\n{'='*60}")
    print(f"Solving {board_name}")
    print(f"{'='*60}")
    print("\nInitial puzzle:")
    for i, row in enumerate(grid):
        if i % 3 == 0 and i != 0:
            print("------+-------+------")
        row_str = " ".join(str(x) for x in row[:3])
        row_str += " | " + " ".join(str(x) for x in row[3:6])
        row_str += " | " + " ".join(str(x) for x in row[6:9])
        print(row_str)
    
    # Create CSP and solve
    csp = SudokuCSP(grid)
    success = csp.solve()
    
    print("\nSolution:")
    csp.print_solution()
    
    print(f"\nSolver Statistics:")
    print(f"  - Solved: {'Yes' if success else 'No'}")
    print(f"  - BACKTRACK calls: {csp.backtrack_count}")
    print(f"  - BACKTRACK failures: {csp.backtrack_failures}")
    
    return success, csp.backtrack_count, csp.backtrack_failures, csp.get_solution()


if __name__ == "__main__":
    """
    Main execution: Solve all four Sudoku boards and collect statistics.
    """
    
    # Define the boards to solve
    boards = [
        ("easy.txt", "Easy Board"),
        ("medium.txt", "Medium Board"),
        ("hard.txt", "Hard Board"),
        ("veryhard.txt", "Very Hard Board"),
    ]
    
    results = []
    
    # Solve each board
    for filename, board_name in boards:
        success, backtrack_calls, backtrack_failures, solution = solve_sudoku_file(filename, board_name)
        results.append({
            'name': board_name,
            'success': success,
            'backtrack_calls': backtrack_calls,
            'backtrack_failures': backtrack_failures,
            'solution': solution
        })
    
    # Print comprehensive summary
    print("\n\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60)
    
    for result in results:
        print(f"\n{result['name']}:")
        status_str = "Solved" if result['success'] else "Failed"
        print(f"  Status: {status_str}")
        print(f"  BACKTRACK calls: {result['backtrack_calls']}")
        print(f"  BACKTRACK failures: {result['backtrack_failures']}")
        if result['backtrack_calls'] > 0:
            failure_ratio = (result['backtrack_failures'] / result['backtrack_calls']) * 100
            print(f"  Failure ratio: {failure_ratio:.2f}%")
    
    print("\n" + "="*60)
    print("ANALYSIS")
    print("="*60)
    print("""
The BACKTRACK function represents the number of times the search mechanism
had to explore different variable assignments during the search process.
The BACKTRACK_FAILURES represents the number of times an assignment did not
lead to a solution and the algorithm had to backtrack to try a different value.

Key observations:
1. Easier puzzles typically require fewer backtrack calls due to more initial constraints
2. Harder puzzles may require significantly more exploration  
3. The AC-3 constraint propagation helps reduce the search space early
4. Forward checking (removing assigned values from neighbors) helps detect failures quickly
5. The MRV (Minimum Remaining Values) heuristic guides better variable selection
6. Constraint propagation with naked singles further prunes the search space

The combination of these techniques (AC-3, forward checking, MRV, naked singles)
creates a powerful solver that efficiently navigates the constraint satisfaction space.
""")
