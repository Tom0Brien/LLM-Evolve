import os
import time
import json
from pathlib import Path
from src.core.types import Individual

RESULTS_DIR = Path("results")

def save_result(best_individual: Individual, output_dir: Path):
    """
    Save the best individual and metadata to the specified results directory.
    """
    if not isinstance(output_dir, Path):
        output_dir = Path(output_dir)
        
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save Code
    code_path = output_dir / "solution.py"
    with open(code_path, "w", encoding="utf-8") as f:
        f.write(best_individual.code)

    # Save Metadata
    metadata = {
        "fitness": best_individual.fitness,
        "feedback": best_individual.feedback,
        # "task" field removed from arguments, could re-add if needed but keeping signature validation clean
    }
    
    meta_path = output_dir / "meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)
    
    return output_dir
