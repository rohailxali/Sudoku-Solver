"""
Flask Web UI for Sudoku Solver
Vercel-compatible entry point
"""

from flask import Flask, render_template, request, jsonify
from copy import deepcopy
from typing import Dict, List, Tuple, Set, Optional
import json
import os
import sys

# Add parent directory to path to import sudoku solver
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Ass_05_AI_Q2 import SudokuCSP

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config['JSON_SORT_KEYS'] = False


@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')


@app.route('/load_puzzle', methods=['POST'])
def load_puzzle():
    """Load a puzzle from file"""
    try:
        data = request.json
        filename = data.get('filename', 'easy.txt')
        filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), filename)
        
        with open(filepath, 'r') as f:
            grid = json.load(f)
        
        return jsonify({
            'success': True,
            'puzzle': grid
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/solve', methods=['POST'])
def solve():
    """Solve a Sudoku puzzle"""
    try:
        data = request.json
        grid = data.get('puzzle')
        
        # Count clues
        clues = sum(1 for row in grid for cell in row if cell != 0)
        
        # Create CSP solver and solve
        csp = SudokuCSP(grid)
        csp.ac3()
        success = csp.backtrack()
        solution = csp.grid if success else None
        
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


# For local testing
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
