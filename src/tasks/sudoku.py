from src.tasks.base import AbstractBaseTask
from src.tasks.registry import register_task

@register_task(name_override="sudoku")
class SudokuSolverTask(AbstractBaseTask):
    @property
    def name(self) -> str:
        return "SudokuSolver"

    @property
    def description(self) -> str:
        return "Write a function `solve_sudoku(board)` that solves a 9x9 Sudoku grid. The board is a list of lists of integers, where 0 represents an empty cell. The function should return the solved board."

    def evaluate(self, code: str) -> float:
        """
        Tests if the code solves a simple Sudoku puzzle.
        """
        try:
            clean_code = code.replace("```python", "").replace("```", "").strip()
            namespace = {}
            exec(clean_code, namespace)
            
            func = None
            for name, obj in namespace.items():
                if callable(obj) and "solve" in name.lower():
                    func = obj
                    break
            
            if not func:
                # Try finding any function
                for name, obj in namespace.items():
                    if callable(obj):
                        func = obj
                        break
            
            if not func:
                raise ValueError("No function found")

            # Simple Easy Puzzle
            # 0 represents empty
            input_board = [
                [5, 3, 0, 0, 7, 0, 0, 0, 0],
                [6, 0, 0, 1, 9, 5, 0, 0, 0],
                [0, 9, 8, 0, 0, 0, 0, 6, 0],
                [8, 0, 0, 0, 6, 0, 0, 0, 3],
                [4, 0, 0, 8, 0, 3, 0, 0, 1],
                [7, 0, 0, 0, 2, 0, 0, 0, 6],
                [0, 6, 0, 0, 0, 0, 2, 8, 0],
                [0, 0, 0, 4, 1, 9, 0, 0, 5],
                [0, 0, 0, 0, 8, 0, 0, 7, 9]
            ]
            
            # Expected solution not strictly needed if we validate rules, 
            # but for simplicity let's just check validity of the result.
            
            try:
                # Pass a deep copy
                import copy
                result = func(copy.deepcopy(input_board))
            except Exception as e:
                # Execution error
                raise e

            if not isinstance(result, list) or len(result) != 9:
                return 0.1 # Wrong format

            return self._calculate_fitness(result)
            
        except Exception as e:
            # print(f"Eval Error: {e}")
            raise e

    def _calculate_fitness(self, board) -> float:
        """Check how many constraints are satisfied."""
        score = 0
        total_checks = 0
        
        # Check rows
        for row in board:
            if self._is_valid_unit(row):
                score += 1
            total_checks += 1
            
        # Check cols
        for col in range(9):
            column = [board[row][col] for row in range(9)]
            if self._is_valid_unit(column):
                score += 1
            total_checks += 1
            
        # Check 3x3 squares
        for i in range(0, 9, 3):
            for j in range(0, 9, 3):
                square = []
                for x in range(3):
                    for y in range(3):
                        square.append(board[i+x][j+y])
                if self._is_valid_unit(square):
                    score += 1
                total_checks += 1
        
        return score / total_checks

    def _is_valid_unit(self, unit) -> bool:
        # Must be 1-9, no duplicates, no zeros
        unit = [x for x in unit if isinstance(x, int)]
        if len(unit) != 9: return False
        if 0 in unit: return False
        return len(set(unit)) == 9
