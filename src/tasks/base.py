from abc import ABC, abstractmethod

class AbstractBaseTask(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Short description for the initial prompt."""
        pass

    @abstractmethod
    def evaluate(self, code: str) -> float:
        """
        Evaluate the code and return a fitness score (0.0 to 1.0).
        """
        pass

    # Optional hooks for custom prompting strategies
    def initial_prompt(self) -> str:
        return f"Write a Python function for this task: {self.description}. Return ONLY the code, no markdown."

    def mutation_prompt(self, code: str, feedback: str, current_fitness: float) -> str:
        return f"""
        Improve this code. Current fitness: {current_fitness}.
        Previous feedback/error: {feedback}
        
        Code:
        {code}
        
        Return ONLY the improved code.
        """
