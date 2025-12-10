from src.tasks.base import AbstractBaseTask

class SortingTask(AbstractBaseTask):
    @property
    def name(self) -> str:
        return "Sorting"

    @property
    def description(self) -> str:
        return "Sort a list of integers in ascending order"

    def evaluate(self, code: str) -> float:
        """
        Tests if the code sorts a list correctly.
        """
        try:
            # Clean the code string 
            clean_code = code.replace("```python", "").replace("```", "").strip()
            
            # Create a namespace
            namespace = {}
            exec(clean_code, namespace)
            
            # Find the function
            func = None
            for name, obj in namespace.items():
                if callable(obj):
                    func = obj
                    break
            
            if not func:
                raise ValueError("No function found")

            # Test cases
            test_cases = [
                ([3, 1, 2], [1, 2, 3]),
                ([5, 4, 3, 2, 1], [1, 2, 3, 4, 5]),
                ([], []),
                ([-1, 5, 0], [-1, 0, 5])
            ]
            
            score = 0
            for input_list, expected in test_cases:
                # IMPORTANT: pass a copy so in-place sorts don't mess up next check
                result = func(input_list.copy())
                if result == expected:
                    score += 1
            
            return score / len(test_cases)
            
        except Exception as e:
            raise e
