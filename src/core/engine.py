from typing import List, Optional
from rich.console import Console
from rich.progress import track
from src.core.llm import LLMProvider
from src.core.types import Individual
from src.tasks.base import AbstractBaseTask

console = Console()

class EvolutionEngine:
    def __init__(self, llm: LLMProvider, task: AbstractBaseTask, population_size: int = 5):
        self.llm = llm
        self.task = task
        self.population_size = population_size
        self.population: List[Individual] = []

    def seed_population(self):
        """Generate initial population."""
        console.print(f"[bold green]Seeding population for task: {self.task.name}[/bold green]")
        prompt = self.task.initial_prompt()
        
        for i in track(range(self.population_size), description="Generating initial solutions..."):
            try:
                code = self.llm.generate(
                    prompt=prompt,
                    system_prompt="You are an expert Python coder. Output only valid Python code."
                )
                self.population.append(Individual(code=code))
            except Exception as e:
                console.print(f"[red]Error generating individual: {e}[/red]")

    def run(self, generations: int = 3) -> Optional[Individual]:
        """Run the evolutionary loop and return the best individual."""
        if not self.population:
            self.seed_population()

        for gen in range(generations):
            console.print(f"\n[bold blue]Generation {gen + 1}/{generations}[/bold blue]")
            
            # Evaluate
            for ind in self.population:
                try:
                    score = self.task.evaluate(ind.code)
                    ind.fitness = score
                except Exception as e:
                    ind.fitness = 0.0
                    ind.feedback = str(e)

            # Sort by fitness
            self.population.sort(key=lambda x: x.fitness, reverse=True)
            if self.population:
                best = self.population[0]
                console.print(f"Best fitness: {best.fitness}")
                if best.fitness == 1.0:
                    console.print("[bold green]Perfect solution found![/bold green]")
                    # We could stop early here, but let's run all gens for now or add a flag
            
            # Selection & Mutation
            if not self.population:
                continue

            new_population = [self.population[0]] # Elitism
            
            # Fill the rest
            while len(new_population) < self.population_size:
                # Simple tournament or just prompt mutation of the best/random
                parent = self.population[len(new_population) % len(self.population)]
                
                mutation_prompt = self.task.mutation_prompt(parent.code, parent.feedback, parent.fitness)
                
                try:
                    new_code = self.llm.generate(mutation_prompt, system_prompt="Improve the code based on feedback.")
                    new_population.append(Individual(code=new_code))
                except Exception as e:
                     console.print(f"[red]Error mutating: {e}[/red]")
            
            self.population = new_population

        # Final sort
        self.population.sort(key=lambda x: x.fitness, reverse=True)
        return self.population[0] if self.population else None
