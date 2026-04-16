"""
Flask Web UI for Sudoku Solver
Modern, responsive web interface with real-time solving
"""

from flask import Flask, render_template, request, jsonify
from copy import deepcopy
from typing import Dict, List, Tuple, Set, Optional
import json
import os

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


class SudokuCSP:
    """CSP Solver for Sudoku"""
    
    def __init__(self, grid: List[List[int]]):
        self.grid = [row[:] for row in grid]
        self.original_grid = [row[:] for row in grid]
        self.domains = self._initialize_domains()
        self.neighbors = {}
        for row in range(9):
            for col in range(9):
                self.neighbors[(row, col)] = self._compute_neighbors(row, col)
        self.backtrack_count = 0
        self.backtrack_failures = 0
        
    def _initialize_domains(self) -> Dict[Tuple[int, int], Set[int]]:
        domains = {}
        for row in range(9):
            for col in range(9):
                if self.grid[row][col] != 0:
                    domains[(row, col)] = {self.grid[row][col]}
                else:
                    domains[(row, col)] = set(range(1, 10))
        return domains
    
    def _compute_neighbors(self, row: int, col: int) -> Set[Tuple[int, int]]:
        neighbors = set()
        for c in range(9):
            if c != col:
                neighbors.add((row, c))
        for r in range(9):
            if r != row:
                neighbors.add((r, col))
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                if (r, c) != (row, col):
                    neighbors.add((r, c))
        return neighbors
    
    def _revise(self, xi: Tuple[int, int], xj: Tuple[int, int]) -> bool:
        revised = False
        if len(self.domains[xj]) == 1:
            xj_val = next(iter(self.domains[xj]))
            if xj_val in self.domains[xi]:
                self.domains[xi].discard(xj_val)
                revised = True
        return revised
    
    def ac3(self) -> bool:
        queue = []
        for row in range(9):
            for col in range(9):
                if len(self.domains[(row, col)]) == 1:
                    xi = (row, col)
                    for xj in self.neighbors[xi]:
                        queue.append((xj, xi))
        
        while queue:
            xi, xj = queue.pop(0)
            if self._revise(xi, xj):
                if len(self.domains[xi]) == 0:
                    return False
                for xk in self.neighbors[xi]:
                    if xk != xj:
                        queue.append((xk, xi))
        return True
    
    def constraint_propagation(self) -> bool:
        if not self.ac3():
            return False
        changed = True
        while changed:
            changed = False
            for row in range(9):
                for col in range(9):
                    cell = (row, col)
                    if len(self.domains[cell]) == 1:
                        value = next(iter(self.domains[cell]))
                        for neighbor in self.neighbors[cell]:
                            if value in self.domains[neighbor] and len(self.domains[neighbor]) > 1:
                                self.domains[neighbor].discard(value)
                                changed = True
                                if len(self.domains[neighbor]) == 0:
                                    return False
        return True
    
    def select_unassigned_variable(self) -> Optional[Tuple[int, int]]:
        unassigned = []
        for row in range(9):
            for col in range(9):
                cell = (row, col)
                if len(self.domains[cell]) > 1:
                    unassigned.append(cell)
        if not unassigned:
            return None
        return min(unassigned, key=lambda var: len(self.domains[var]))
    
    def backtrack(self) -> bool:
        var = self.select_unassigned_variable()
        if var is None:
            return True
        self.backtrack_count += 1
        for value in sorted(self.domains[var]):
            domains_backup = deepcopy(self.domains)
            self.domains[var] = {value}
            if self.constraint_propagation():
                if self.backtrack():
                    return True
            self.domains = domains_backup
            self.backtrack_failures += 1
        return False
    
    def solve(self) -> bool:
        if not self.constraint_propagation():
            return False
        return self.backtrack()
    
    def get_solution(self) -> List[List[int]]:
        solution = [[0] * 9 for _ in range(9)]
        for row in range(9):
            for col in range(9):
                domain = self.domains[(row, col)]
                if len(domain) == 1:
                    solution[row][col] = next(iter(domain))
        return solution


# Routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/load_puzzle', methods=['POST'])
def load_puzzle():
    data = request.json
    puzzle_name = data.get('puzzle')
    
    filepath = os.path.join(os.getcwd(), f"{puzzle_name}.txt")
    
    try:
        with open(filepath, 'r') as f:
            grid = []
            for line in f:
                line = line.strip()
                if len(line) == 9:
                    row = [int(digit) for digit in line]
                    grid.append(row)
        
        if len(grid) == 9:
            return jsonify({
                'success': True,
                'grid': grid,
                'message': f'Loaded: {puzzle_name}.txt'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/solve', methods=['POST'])
def solve():
    data = request.json
    grid = data.get('grid')
    
    try:
        csp = SudokuCSP(grid)
        success = csp.solve()
        solution = csp.get_solution()
        
        clues = len([x for row in grid for x in row if x != 0])
        
        return jsonify({
            'success': success,
            'solution': solution,
            'backtrack_calls': csp.backtrack_count,
            'backtrack_failures': csp.backtrack_failures,
            'clues': clues,
            'difficulty': get_difficulty(csp.backtrack_count)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


def get_difficulty(backtracks):
    if backtracks == 0:
        return "Easy"
    elif backtracks < 20:
        return "Medium"
    elif backtracks < 50:
        return "Hard"
    else:
        return "Very Hard"


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
