from src.tasks.base import AbstractBaseTask
from src.tasks.registry import register_task
import time
import math

@register_task(name_override="primes")
class PrimesTask(AbstractBaseTask):
    @property
    def name(self) -> str:
        return "Primes"

    @property
    def description(self) -> str:
        return "Write a function `get_primes(n: int) -> list[int]` that returns a list of all prime numbers less than n. The function must be EFFICIENT."

    def evaluate(self, code: str) -> float:
        """
        Tests correctness and speed.
        """
        try:
            # Clean Code
            clean_code = code.replace("```python", "").replace("```", "").strip()
            namespace = {}
            exec(clean_code, namespace)
            
            func = None
            for name, obj in namespace.items():
                if callable(obj) and "prime" in name.lower():
                    func = obj
                    break
            
            if not func:
                # Fallback to finding any function
                for name, obj in namespace.items():
                    if callable(obj):
                        func = obj
                        break
            
            if not func:
                 raise ValueError("No function found")

            # Correctness Check (small n)
            reference = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
            if func(30) != reference:
                return 0.0 # Fail if basic correctness is wrong

            # Performance Check (larger n)
            start_time = time.perf_counter()
            result = func(10000)
            end_time = time.perf_counter()
            duration = end_time - start_time
            
            # Verify result length roughly (there are 1229 primes < 10000)
            if len(result) != 1229:
                return 0.1 # Correct logic but wrong count?

            # Fitness based on speed relative to a baseline
            # Baseline (Sieve) ~ 0.002s
            # Slow (Trial division) ~ 0.2s
            # We want to encourage < 0.01s
            
            target_time = 0.002
            # Score = target / max(actual, target)
            # If actual <= target, score = 1.0
            # If actual = 0.02 (10x slower), score = 0.1
            
            score = target_time / max(duration, target_time)
            return max(0.1, min(1.0, score)) # Floor at 0.1 if correct

        except Exception as e:
            # print(f"Error: {e}")
            return 0.0
