/* ===========================================
   CSP Sudoku Solver - JavaScript App Logic
   =========================================== */

let currentPuzzle = null;
let currentSolution = null;

// Initialize grid on page load
document.addEventListener('DOMContentLoaded', function() {
    generateEmptyGrid();
});

/**
 * Generate empty 9x9 grid structure
 */
function generateEmptyGrid() {
    const grid = document.getElementById('sudokuGrid');
    grid.innerHTML = '';
    
    for (let i = 0; i < 81; i++) {
        const cell = document.createElement('div');
        cell.className = 'grid-cell empty';
        cell.dataset.row = Math.floor(i / 9);
        cell.dataset.col = i % 9;
        cell.textContent = '';
        grid.appendChild(cell);
    }
}

/**
 * Display puzzle on grid
 */
function displayPuzzle(grid) {
    for (let row = 0; row < 9; row++) {
        for (let col = 0; col < 9; col++) {
            const cell = document.querySelector(
                `.grid-cell[data-row="${row}"][data-col="${col}"]`
            );
            const value = grid[row][col];
            
            if (value !== 0) {
                cell.textContent = value;
                cell.className = 'grid-cell given';
            } else {
                cell.textContent = '';
                cell.className = 'grid-cell empty';
            }
        }
    }
}

/**
 * Display solution on grid
 */
function displaySolution(grid) {
    for (let row = 0; row < 9; row++) {
        for (let col = 0; col < 9; col++) {
            const cell = document.querySelector(
                `.grid-cell[data-row="${row}"][data-col="${col}"]`
            );
            const value = grid[row][col];
            const originalValue = currentPuzzle[row][col];
            
            if (value !== 0) {
                cell.textContent = value;
                if (originalValue !== 0) {
                    cell.className = 'grid-cell given';
                } else {
                    cell.className = 'grid-cell solved';
                }
            }
        }
    }
}

/**
 * Load puzzle from server
 */
function loadPuzzle() {
    const puzzleName = document.querySelector('input[name="puzzle"]:checked').value;
    updateStatus(`Loading ${puzzleName} puzzle...`);
    
    fetch('/load_puzzle', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ puzzle: puzzleName })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            currentPuzzle = data.grid;
            currentSolution = null;
            displayPuzzle(currentPuzzle);
            updateStatus(`Loaded: ${data.message}`);
            resetStatistics();
            shake(document.getElementById('sudokuGrid'));
        } else {
            alert('Error: ' + data.error);
            updateStatus('Error loading puzzle');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error loading puzzle: ' + error);
        updateStatus('Error loading puzzle');
    });
}

/**
 * Solve the current puzzle
 */
function solvePuzzle() {
    if (!currentPuzzle) {
        alert('Please load a puzzle first!');
        return;
    }
    
    updateStatus('Solving puzzle...');
    disableButtons(true);
    
    fetch('/solve', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ grid: currentPuzzle })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            currentSolution = data.solution;
            displaySolution(currentSolution);
            updateStatistics(data);
            updateStatus('Puzzle solved successfully!');
            shake(document.getElementById('sudokuGrid'));
        } else {
            alert('Could not solve this puzzle: ' + data.error);
            updateStatus('Could not solve puzzle');
        }
        disableButtons(false);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error solving puzzle: ' + error);
        updateStatus('Error solving puzzle');
        disableButtons(false);
    });
}

/**
 * Reset puzzle to original
 */
function resetPuzzle() {
    if (!currentPuzzle) {
        alert('Please load a puzzle first!');
        return;
    }
    
    currentSolution = null;
    displayPuzzle(currentPuzzle);
    updateStatus('Puzzle reset');
    resetStatistics();
    shake(document.getElementById('sudokuGrid'));
}

/**
 * Update statistics display
 */
function updateStatistics(data) {
    const clues = data.clues;
    const backtracks = data.backtrack_calls;
    const failures = data.backtrack_failures;
    const difficulty = data.difficulty;
    
    document.getElementById('statusValue').textContent = 'Solved ✓';
    document.getElementById('cluesValue').textContent = clues;
    document.getElementById('backtrackValue').textContent = backtracks;
    document.getElementById('failureValue').textContent = failures;
    document.getElementById('difficultyValue').textContent = difficulty;
    
    const ratio = backtracks > 0 
        ? ((failures / backtracks) * 100).toFixed(2) + '%'
        : 'N/A';
    document.getElementById('ratioValue').textContent = ratio;
    
    // Color code difficulty
    const diffElement = document.getElementById('difficultyValue');
    diffElement.className = 'stat-value difficulty';
    switch(difficulty) {
        case 'Easy':
            diffElement.style.background = '#28a745';
            break;
        case 'Medium':
            diffElement.style.background = '#ffc107';
            break;
        case 'Hard':
            diffElement.style.background = '#fd7e14';
            break;
        case 'Very Hard':
            diffElement.style.background = '#dc3545';
            break;
    }
}

/**
 * Reset statistics display
 */
function resetStatistics() {
    document.getElementById('statusValue').textContent = 'No solution';
    document.getElementById('cluesValue').textContent = '-';
    document.getElementById('backtrackValue').textContent = '-';
    document.getElementById('failureValue').textContent = '-';
    document.getElementById('difficultyValue').textContent = '-';
    document.getElementById('ratioValue').textContent = '-';
}

/**
 * Update status bar
 */
function updateStatus(message) {
    const statusBar = document.getElementById('statusBar');
    statusBar.textContent = message;
    
    // Add pulse animation
    statusBar.style.animation = 'none';
    setTimeout(() => {
        statusBar.style.animation = 'pulse 0.5s ease';
    }, 10);
}

/**
 * Disable/Enable action buttons during solving
 */
function disableButtons(disable) {
    document.querySelectorAll('.btn').forEach(btn => {
        btn.disabled = disable;
        btn.style.opacity = disable ? '0.5' : '1';
    });
}

/**
 * Show instructions modal
 */
function showInstructions() {
    document.getElementById('instructionsModal').style.display = 'block';
}

/**
 * Close instructions modal
 */
function closeInstructions() {
    document.getElementById('instructionsModal').style.display = 'none';
}

/**
 * Close modal when clicking outside
 */
window.onclick = function(event) {
    const modal = document.getElementById('instructionsModal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
}

/**
 * Shake animation for grid
 */
function shake(element) {
    element.style.animation = 'none';
    setTimeout(() => {
        element.style.animation = 'shake 0.5s ease';
    }, 10);
}

// Add shake animation to stylesheet dynamically
const style = document.createElement('style');
style.textContent = `
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
        20%, 40%, 60%, 80% { transform: translateX(5px); }
    }
`;
document.head.appendChild(style);

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    if (event.ctrlKey || event.metaKey) {
        if (event.key === 'Enter' || event.key === '/') {
            event.preventDefault();
            solvePuzzle();
        }
    }
    if (event.key === 'Escape') {
        closeInstructions();
    }
});
