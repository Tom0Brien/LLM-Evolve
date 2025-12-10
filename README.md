# LLMEvolve

An evolutionary coding agent that autonomously generates and improves Python code using LLMs.

Inspired by [AlphaEvolve](https://arxiv.org/pdf/2506.13131).

## Prerequisites

1. **Python** (via `uv`)
2. **Ollama** installed and running.
   - Pull the model: `ollama pull gemma3:4b`

## Installation

```bash
uv sync
```

## Usage

Run the **Sorting** task example:

```bash
uv run main.py run sorting
```

This will:
1. Generate an initial population of sorting functions.
2. Evaluate them against test cases.
3. Evolve and improve the code over generations.
4. Save the best solution to `results/`.

### Options

```bash
# Custom Generatons
uv run main.py run sorting --generations 5

# Custom Model
uv run main.py run sorting --model ollama/llama3
```
