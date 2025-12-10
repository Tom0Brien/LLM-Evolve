from typing import List, Optional
import time
import signal
from contextlib import contextmanager
from rich.console import Console
from rich.progress import track, Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from src.core.llm import LLMProvider
from src.core.types import Individual
from src.tasks.base import AbstractBaseTask

try:
    from tensorboardX import SummaryWriter
except ImportError:
    SummaryWriter = None

console = Console()

# Timeout context manager (Unix only usually, but we'll try careful threading or just simple alarm if on Linux, 
# but for Windows we might need a thread-based approach. 
# Implementing a simple thread-based timeout for cross-platform compatibility.)
import threading
import _thread

class TimeoutException(Exception):
    pass

@contextmanager
def time_limit(seconds):
    if seconds is None:
        yield
        return
        
    timer = threading.Timer(seconds, lambda: _thread.interrupt_main())
    timer.start()
    try:
        yield
    except KeyboardInterrupt:
        raise TimeoutException("Timed out!")
    finally:
        timer.cancel()

class EvolutionEngine:
    def __init__(self, llm: LLMProvider, task: AbstractBaseTask, population_size: int = 5, log_dir: str = None):
        self.llm = llm
        self.task = task
        self.population_size = population_size
        self.population: List[Individual] = []
        self.writer = SummaryWriter(log_dir=log_dir) if SummaryWriter and log_dir else None

    def print_generation_summary(self, generation: int, total_gens: int):
        """Print a summary table of the current population."""
        table = Table(title=f"Generation {generation}/{total_gens} Summary")
        table.add_column("Rank", style="cyan", no_wrap=True)
        table.add_column("Fitness", style="magenta")
        table.add_column("Code Length", style="green")
        table.add_column("Status", style="yellow")

        # Sort just for display
        sorted_pop = sorted(self.population, key=lambda x: x.fitness, reverse=True)
        
        # Show top 5 only to keep it clean if population is large
        for i, ind in enumerate(sorted_pop[:5]):
            # Use ASCII safe characters for Windows compatibility
            if ind.fitness == 1.0:
                status = "[OK]"
            elif ind.feedback:
                status = "[!]"
            else:
                status = "[X]"
                
            table.add_row(
                str(i + 1),
                f"{ind.fitness:.2f}",
                str(len(ind.code)),
                status
            )
        if len(self.population) > 5:
            table.add_row("...", "...", "...", "...")
            
        console.print(table)

    def seed_population(self):
        """Generate initial population."""
        console.print(f"[bold green]Seeding population for task: {self.task.name}[/bold green]")
        prompt = self.task.initial_prompt()
        
        # Use simple track for progress
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
            console.rule(f"[bold blue]Generation {gen + 1}/{generations}[/bold blue]")
            
            # 1. Evaluate
            with console.status("Evaluating population...", spinner="dots"):
                for ind in self.population:
                    try:
                        # Enforce timeout of 5 seconds per evaluation to prevent hangs
                        # Using a simple try/except block with threading timer logic above
                        try:
                            # Note: Windows signal.alarm is not supported, so using the thread hack
                            with time_limit(5): 
                                score = self.task.evaluate(ind.code)
                                ind.fitness = score
                        except TimeoutException:
                            ind.fitness = 0.0
                            ind.feedback = "Execution Timed Out (>5s)"
                            
                    except Exception as e:
                        ind.fitness = 0.0
                        ind.feedback = str(e)
            
            # 2. Sort & Display
            self.population.sort(key=lambda x: x.fitness, reverse=True)
            self.print_generation_summary(gen + 1, generations)
            
            # 3. Logging
            if self.writer:
                best_fitness = self.population[0].fitness
                avg_fitness = sum(p.fitness for p in self.population) / len(self.population)
                avg_len = sum(len(p.code) for p in self.population) / len(self.population)
                
                self.writer.add_scalar(f"Fitness/Best", best_fitness, gen)
                self.writer.add_scalar(f"Fitness/Avg", avg_fitness, gen)
                self.writer.add_scalar(f"Stats/CodeLen", avg_len, gen)
            
            best = self.population[0]
            if best.fitness == 1.0:
                console.print("\n[bold green]*** Perfect solution found! ***[/bold green]")
                if self.writer: self.writer.close()
                # We stop early if perfect
                return best
            
            # 4. Selection & Mutation (if not last gen)
            if gen < generations - 1:
                with console.status("Creating next generation...", spinner="bouncingBall"):
                    new_population = [self.population[0]] # Elitism
                    
                    # Fill the rest
                    attempts = 0 # Safety break
                    while len(new_population) < self.population_size and attempts < self.population_size * 2:
                        attempts += 1
                        parent = self.population[len(new_population) % len(self.population)]
                        mutation_prompt = self.task.mutation_prompt(parent.code, parent.feedback, parent.fitness)
                        
                        try:
                            new_code = self.llm.generate(mutation_prompt, system_prompt="Improve the code based on feedback.")
                            new_population.append(Individual(code=new_code))
                        except Exception:
                            pass 
                    
                    self.population = new_population

        if self.writer: self.writer.close()
        return self.population[0] if self.population else None
