import typer
import os
import time
from dotenv import load_dotenv
from rich.console import Console
from src.core.llm import LLMProvider
from src.core.engine import EvolutionEngine
from src.tasks.registry import get_task, list_tasks as registry_list_tasks
# Tasks must be imported to register
import src.tasks.sorting
import src.tasks.sudoku
import src.tasks.primes
from src.utils.storage import save_result

load_dotenv()
app = typer.Typer()
console = Console()

@app.command()
def run(
    task_name: str = typer.Argument(..., help="Name of the task to run"),
    generations: int = typer.Option(3, help="Number of generations to evolve"),
    population: int = typer.Option(5, help="Population size"),
    model: str = typer.Option("ollama/gemma3:4b", help="LLM model to use")
):
    """
    Run the AlphaEvolve agent on a specific task.
    """
    # 1. Select Task
    task = get_task(task_name)
    
    if not task:
        console.print(f"[red]Unknown task: {task_name}[/red]")
        console.print(f"Available tasks: {', '.join(registry_list_tasks())}")
        raise typer.Exit(code=1)

    # 2. Setup LLM
    try:
        llm = LLMProvider(model_name=model)
    except Exception as e:
        console.print(f"[red]Failed to initialize LLM: {e}[/red]")
        raise typer.Exit(code=1)

    # 3. Initialize Engine
    # Create unique run dir in results/
    run_dir = f"results/{task_name}_{time.strftime('%Y%m%d_%H%M%S')}"
    engine = EvolutionEngine(llm=llm, task=task, population_size=population, log_dir=run_dir)

    # 4. Evolve
    console.print(f"[bold]Starting evolution for {task.name}...[/bold]")
    console.print(f"[dim]Output directory: {run_dir}[/dim]")
    best_ind = engine.run(generations=generations)

    # 5. Save Results
    if best_ind:
        console.print(f"\n[green]Evolution complete! Best fitness: {best_ind.fitness}[/green]")
        saved_path = save_result(best_ind, run_dir)
        console.print(f"Results saved to: [bold]{saved_path}[/bold]")
        console.print(f"Code:\n{best_ind.code}")
    else:
        console.print("[red]Evolution failed to produce any individuals.[/red]")

@app.command()
def list_tasks():
    """List available tasks."""
    console.print("Available tasks:")
    for t in registry_list_tasks():
        console.print(f"- {t}")

if __name__ == "__main__":
    app()
