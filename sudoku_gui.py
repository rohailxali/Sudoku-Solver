"""
CSP-Based Sudoku Solver with GUI
Provides an interactive visual interface for solving Sudoku puzzles
Features: Puzzle loading, visualization, solving with statistics display
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tkinter.font as tkFont
from copy import deepcopy
from typing import Dict, List, Tuple, Set, Optional
import os


class SudokuCSP:
    """CSP Solver (same as before - for solving logic)"""
    
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


class SudokuGUI:
    """Professional GUI for Sudoku Solver"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("CSP Sudoku Solver - Professional UI")
        self.root.geometry("1200x800")
        self.root.configure(bg="#1e1e1e")
        
        # Color scheme
        self.BG_COLOR = "#1e1e1e"
        self.FRAME_COLOR = "#2d2d2d"
        self.TEXT_COLOR = "#e0e0e0"
        self.ACCENT_COLOR = "#0078d4"
        self.SUCCESS_COLOR = "#28a745"
        self.WARNING_COLOR = "#ffc107"
        self.ERROR_COLOR = "#dc3545"
        
        self.original_grid = None
        self.csp = None
        self.solution = None
        self.cells = {}
        
        self._setup_ui()
        
    def _setup_ui(self):
        """Create the main UI layout"""
        # Main container
        main_frame = tk.Frame(self.root, bg=self.BG_COLOR)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_font = tkFont.Font(family="Helvetica", size=18, weight="bold")
        title = tk.Label(main_frame, text="CSP-Based Sudoku Solver", 
                        font=title_font, bg=self.BG_COLOR, fg=self.ACCENT_COLOR)
        title.pack(pady=10)
        
        # Create two main sections: Left (Grid) and Right (Controls)
        content_frame = tk.Frame(main_frame, bg=self.BG_COLOR)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # LEFT SECTION - Sudoku Grid
        left_frame = tk.Frame(content_frame, bg=self.BG_COLOR)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        self._create_grid_display(left_frame)
        
        # RIGHT SECTION - Controls and Statistics
        right_frame = tk.Frame(content_frame, bg=self.FRAME_COLOR, relief=tk.RAISED)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10)
        
        self._create_control_panel(right_frame)
        
    def _create_grid_display(self, parent):
        """Create the 9x9 Sudoku grid display"""
        grid_frame = tk.Frame(parent, bg=self.BG_COLOR)
        grid_frame.pack()
        
        grid_title = tk.Label(grid_frame, text="Puzzle Grid", 
                             font=("Helvetica", 12, "bold"),
                             bg=self.BG_COLOR, fg=self.ACCENT_COLOR)
        grid_title.pack(pady=5)
        
        # Create grid with visual separation for 3x3 boxes
        self.grid_frame = tk.Frame(grid_frame, bg="black", padx=2, pady=2)
        self.grid_frame.pack()
        
        for row in range(9):
            for col in range(9):
                # Determine cell colors based on 3x3 box
                if (row // 3 + col // 3) % 2 == 0:
                    cell_bg = "#f0f0f0"
                else:
                    cell_bg = "#e8e8e8"
                
                cell = tk.Label(self.grid_frame, width=4, height=2,
                              font=("Helvetica", 14, "bold"),
                              bg=cell_bg, fg="#000000",
                              relief=tk.SOLID, borderwidth=1)
                cell.grid(row=row, column=col, padx=1, pady=1)
                self.cells[(row, col)] = cell
        
        # Add visual borders for 3x3 boxes
        self._add_grid_borders()
        
    def _add_grid_borders(self):
        """Add visual borders to 3x3 boxes"""
        for i in range(1, 3):
            # Horizontal lines
            line = tk.Frame(self.grid_frame, height=2, bg="black")
            line.grid(row=i*3-1, column=0, columnspan=9, sticky="ew", padx=1)
            
            # Vertical lines
            line = tk.Frame(self.grid_frame, width=2, bg="black")
            line.grid(row=0, column=i*3-1, rowspan=9, sticky="ns", pady=1)
    
    def _create_control_panel(self, parent):
        """Create the control and statistics panel"""
        # Panel title
        panel_title = tk.Label(parent, text="Control Panel",
                              font=("Helvetica", 12, "bold"),
                              bg=self.FRAME_COLOR, fg=self.ACCENT_COLOR)
        panel_title.pack(pady=10)
        
        # File selection
        file_frame = tk.LabelFrame(parent, text="Load Puzzle",
                                  bg=self.FRAME_COLOR, fg=self.TEXT_COLOR,
                                  font=("Helvetica", 10))
        file_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.file_var = tk.StringVar(value="easy.txt")
        files = ["easy.txt", "hard.txt", "veryhard.txt"]
        
        for file in files:
            rb = tk.Radiobutton(file_frame, text=file, variable=self.file_var,
                              value=file, bg=self.FRAME_COLOR, fg=self.TEXT_COLOR,
                              selectcolor=self.ACCENT_COLOR, activebackground=self.FRAME_COLOR)
            rb.pack(anchor=tk.W, padx=10, pady=2)
        
        load_btn = self._create_button(file_frame, "Load Puzzle", self.load_puzzle,
                                       bg=self.SUCCESS_COLOR)
        load_btn.pack(fill=tk.X, padx=5, pady=8)
        
        # Action buttons
        action_frame = tk.LabelFrame(parent, text="Actions",
                                    bg=self.FRAME_COLOR, fg=self.TEXT_COLOR,
                                    font=("Helvetica", 10))
        action_frame.pack(fill=tk.X, padx=10, pady=10)
        
        solve_btn = self._create_button(action_frame, "Solve Puzzle", self.solve_puzzle,
                                       bg=self.ACCENT_COLOR)
        solve_btn.pack(fill=tk.X, padx=5, pady=5)
        
        reset_btn = self._create_button(action_frame, "Reset Puzzle", self.reset_puzzle,
                                       bg=self.WARNING_COLOR)
        reset_btn.pack(fill=tk.X, padx=5, pady=5)
        
        # Statistics
        stats_frame = tk.LabelFrame(parent, text="Statistics",
                                   bg=self.FRAME_COLOR, fg=self.TEXT_COLOR,
                                   font=("Helvetica", 10))
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.stats_text = tk.Text(stats_frame, height=10, width=25,
                                 bg="#2d2d2d", fg=self.TEXT_COLOR,
                                 font=("Courier", 9), relief=tk.FLAT)
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Initial statistics
        self._update_statistics("No puzzle loaded yet", 0, 0, 0, False)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(parent, textvariable=self.status_var,
                             bg=self.ACCENT_COLOR, fg="white",
                             font=("Helvetica", 9), pady=5)
        status_bar.pack(fill=tk.X, padx=5, pady=5)
    
    def _create_button(self, parent, text, command, bg=None):
        """Create a styled button"""
        btn = tk.Button(parent, text=text, command=command,
                       bg=bg or self.ACCENT_COLOR, fg="white",
                       font=("Helvetica", 10, "bold"),
                       relief=tk.RAISED, cursor="hand2",
                       activebackground="#005a9e")
        return btn
    
    def load_puzzle(self):
        """Load a puzzle from file"""
        filename = self.file_var.get()
        filepath = os.path.join(os.getcwd(), filename)
        
        if not os.path.exists(filepath):
            messagebox.showerror("Error", f"File not found: {filename}")
            self.status_var.set("Error: File not found")
            return
        
        try:
            with open(filepath, 'r') as f:
                grid = []
                for line in f:
                    line = line.strip()
                    if len(line) == 9:
                        row = [int(digit) for digit in line]
                        grid.append(row)
            
            if len(grid) == 9:
                self.original_grid = grid
                self.csp = None
                self.solution = None
                self.display_puzzle(self.original_grid)
                self.status_var.set(f"Loaded: {filename}")
                self._update_statistics(f"Puzzle from {filename}", 0, 0, 0, False)
            else:
                messagebox.showerror("Error", "Invalid puzzle format")
                self.status_var.set("Error: Invalid format")
        except Exception as e:
            messagebox.showerror("Error", f"Error loading file: {str(e)}")
            self.status_var.set(f"Error: {str(e)}")
    
    def solve_puzzle(self):
        """Solve the current puzzle"""
        if self.original_grid is None:
            messagebox.showwarning("Warning", "Please load a puzzle first")
            return
        
        self.status_var.set("Solving...")
        self.root.update()
        
        self.csp = SudokuCSP(self.original_grid)
        success = self.csp.solve()
        self.solution = self.csp.get_solution()
        
        if success:
            self.display_solution(self.solution)
            self.status_var.set("Solved successfully!")
            self._update_statistics(
                f"Success!",
                self.csp.backtrack_count,
                self.csp.backtrack_failures,
                len([x for row in self.original_grid for x in row if x != 0]),
                True
            )
            messagebox.showinfo("Success", "Puzzle solved successfully!")
        else:
            self.status_var.set("Could not solve puzzle")
            self._update_statistics("Failed to solve", 0, 0, 0, False)
            messagebox.showerror("Error", "Could not solve this puzzle")
    
    def reset_puzzle(self):
        """Reset to original puzzle"""
        if self.original_grid is None:
            messagebox.showwarning("Warning", "No puzzle loaded")
            return
        
        self.csp = None
        self.solution = None
        self.display_puzzle(self.original_grid)
        self.status_var.set("Puzzle reset")
        self._update_statistics("Puzzle reset", 0, 0, 0, False)
    
    def display_puzzle(self, grid):
        """Display the current puzzle"""
        for row in range(9):
            for col in range(9):
                value = grid[row][col]
                cell = self.cells[(row, col)]
                if value != 0:
                    cell.config(text=str(value), fg="#0078d4", bg="#f0f0f0")
                else:
                    cell.config(text="", fg="#000000", bg="#f0f0f0")
    
    def display_solution(self, grid):
        """Display the solved puzzle"""
        for row in range(9):
            for col in range(9):
                value = grid[row][col]
                original_value = self.original_grid[row][col]
                cell = self.cells[(row, col)]
                
                if original_value != 0:
                    # Original number - blue
                    cell.config(text=str(value), fg="#0078d4", bg="#f0f0f0")
                else:
                    # Solved number - green
                    cell.config(text=str(value), fg="#28a745", bg="#e6ffe6")
    
    def _update_statistics(self, message, backtracks, failures, clues, solved):
        """Update statistics display"""
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        
        stats = f"""
╔════════════════════════╗
║    SOLVER STATISTICS   ║
╚════════════════════════╝

Status: {message}

Solved: {'Yes ✓' if solved else 'No ✗'}

Clues: {clues}
Cells to fill: {81 - clues}

Backtrack Calls: {backtracks}
Backtrack Failures: {failures}

Failure Ratio: {
    f'{(failures/backtracks)*100:.2f}%' 
    if backtracks > 0 
    else 'N/A'
}

Difficulty: {
    'Easy' if backtracks == 0
    else 'Medium' if backtracks < 20
    else 'Hard' if backtracks < 50
    else 'Very Hard'
}
"""
        self.stats_text.insert(1.0, stats)
        self.stats_text.config(state=tk.DISABLED)


def main():
    root = tk.Tk()
    gui = SudokuGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
