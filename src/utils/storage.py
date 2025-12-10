import os
import time
import json
from pathlib import Path
from src.core.types import Individual

RESULTS_DIR = Path("results")

def save_result(task_name: str, best_individual: Individual):
    """
    Save the best individual and metadata to the results directory.
    """
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    run_dir = RESULTS_DIR / f"{task_name}_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    # Save Code
    code_path = run_dir / "solution.py"
    with open(code_path, "w", encoding="utf-8") as f:
        f.write(best_individual.code)

    # Save Metadata
    metadata = {
        "fitness": best_individual.fitness,
        "feedback": best_individual.feedback,
        "timestamp": timestamp,
        "task": task_name
    }
    
    meta_path = run_dir / "meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)
    
    return run_dir
