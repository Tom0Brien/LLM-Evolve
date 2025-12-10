import typer
import os
from dotenv import load_dotenv
from rich.console import Console
from src.core.llm import LLMProvider
from src.core.engine import EvolutionEngine
from src.tasks.sorting import SortingTask
from src.utils.storage import save_result

load_dotenv()
app = typer.Typer()
console = Console()

@app.command()
def run(
    task_name: str = typer.Argument(..., help="Name of the task to run (e.g., 'sorting')"),
    generations: int = typer.Option(3, help="Number of generations to evolve"),
    population: int = typer.Option(5, help="Population size"),
    model: str = typer.Option("ollama/gemma3:4b", help="LLM model to use")
):
    """
    Run the AlphaEvolve agent on a specific task.
    """
    # 1. Select Task
    if task_name.lower() == "sorting":
        task = SortingTask()
    else:
        console.print(f"[red]Unknown task: {task_name}[/red]")
        raise typer.Exit(code=1)

    # 2. Setup LLM
    try:
        llm = LLMProvider(model_name=model)
    except Exception as e:
        console.print(f"[red]Failed to initialize LLM: {e}[/red]")
        raise typer.Exit(code=1)

    # 3. Initialize Engine
    engine = EvolutionEngine(llm=llm, task=task, population_size=population)

    # 4. Evolve
    console.print(f"[bold]Starting evolution for {task.name}...[/bold]")
    best_ind = engine.run(generations=generations)

    # 5. Save Results
    if best_ind:
        console.print(f"\n[green]Evolution complete! Best fitness: {best_ind.fitness}[/green]")
        result_dir = save_result(task_name, best_ind)
        console.print(f"Results saved to: [bold]{result_dir}[/bold]")
        console.print(f"Code:\n{best_ind.code}")
    else:
        console.print("[red]Evolution failed to produce any individuals.[/red]")

@app.command()
def list_tasks():
    """List available tasks."""
    console.print("Available tasks:")
    console.print("- sorting")

if __name__ == "__main__":
    app()
