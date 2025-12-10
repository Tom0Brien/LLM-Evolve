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
        You are an Evolutionary Agent. Your goal is to improve the following code.
        
        Current Fitness: {current_fitness}
        Previous Feedback: {feedback}
        
        CRITICAL INSTRUCTION:
        1. ANALYZE: Why did the previous code fail or perform poorly?
        2. HYPOTHESIZE: Propose a SPECIFIC algorithmic change to improve fitness.
        3. IMPLEMENT: Write the new code.
        
        Add your Analysis and Hypothesis as a docstring or comment at the top of the code.
        
        Code to Improve:
        {code}
        
        Return ONLY the valid Python code (with your hypothesis in comments).
        """
