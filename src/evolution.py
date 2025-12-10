from dataclasses import dataclass
from typing import List, Callable
from src.llm_provider import LLMProvider
from rich.console import Console
from rich.progress import track

console = Console()

@dataclass
class Individual:
    code: str
    fitness: float = 0.0
    feedback: str = ""

class Evaluator:
    def evaluate(self, code: str) -> float:
        """
        Evaluate the code and return a fitness score.
        Must be implemented by specific tasks.
        """
        raise NotImplementedError

class EvolutionEngine:
    def __init__(self, llm: LLMProvider, evaluator: Evaluator, population_size: int = 5):
        self.llm = llm
        self.evaluator = evaluator
        self.population_size = population_size
        self.population: List[Individual] = []

    def seed_population(self, prompt: str):
        """Generate initial population."""
        console.print("[bold green]Seeding population...[/bold green]")
        for i in track(range(self.population_size), description="Generating initial solutions..."):
            code = self.llm.generate(
                prompt=f"Write a Python function for this task: {prompt}. Return ONLY the code, no markdown.",
                system_prompt="You are an expert Python coder. Output only valid Python code."
            )
            self.population.append(Individual(code=code))

    def evolve(self, generations: int = 3):
        """Run the evolutionary loop."""
        for gen in range(generations):
            console.print(f"\n[bold blue]Generation {gen + 1}/{generations}[/bold blue]")
            
            # Evaluate
            for ind in self.population:
                try:
                    score = self.evaluator.evaluate(ind.code)
                    ind.fitness = score
                except Exception as e:
                    ind.fitness = 0.0
                    ind.feedback = str(e)

            # Sort by fitness
            self.population.sort(key=lambda x: x.fitness, reverse=True)
            best = self.population[0]
            console.print(f"Best fitness: {best.fitness}")

            # Selection & Mutation (Simplified for now: keep best, mutate others)
            # In a real system, we'd do crossover, smarter prompting, etc.
            new_population = [best] # Elitism
            
            for i in range(1, self.population_size):
                parent = self.population[i % len(self.population)] # Simple selection
                mutation_prompt = f"""
                Improve this code. Current fitness: {parent.fitness}.
                Previous feedback/error: {parent.feedback}
                
                Code:
                {parent.code}
                
                Return ONLY the improved code.
                """
                new_code = self.llm.generate(mutation_prompt, system_prompt="Improve the code based on feedback.")
                new_population.append(Individual(code=new_code))
            
            self.population = new_population

if __name__ == "__main__":
    print("EvolutionEngine module ready.")
