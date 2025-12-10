from src.llm_provider import LLMProvider
from src.evolution import EvolutionEngine, Evaluator
import ast

class SortEvaluator(Evaluator):
    def evaluate(self, code: str) -> float:
        """
        Tests if the code sorts a list correctly.
        """
        try:
            # Dangerous in production, but defined here for local testing
            # Clean the code string to remove markdown blocks if present
            clean_code = code.replace("```python", "").replace("```", "").strip()
            
            # Create a namespace
            namespace = {}
            exec(clean_code, namespace)
            
            # Find the function
            func = None
            for name, obj in namespace.items():
                if callable(obj):
                    func = obj
                    break
            
            if not func:
                raise ValueError("No function found")

            # Test cases
            test_cases = [
                ([3, 1, 2], [1, 2, 3]),
                ([5, 4, 3, 2, 1], [1, 2, 3, 4, 5]),
                ([], []),
                ([1], [1])
            ]
            
            score = 0
            for input_list, expected in test_cases:
                result = func(input_list.copy())
                if result == expected:
                    score += 1
            
            return score / len(test_cases)
            
        except Exception as e:
            # print(f"Evaluation failed: {e}")
            raise e

if __name__ == "__main__":
    # Ensure GEMINI_API_KEY is set in .env
    
    # Use Gemini by default as requested
    try:
        import time
        print("Waiting 10s to cool down rate limits...")
        time.sleep(10)
        provider = LLMProvider(model_name="gemini/gemini-flash-latest") 
        print("Using Gemini Flash Latest backend.")
    except Exception:
        print("Failed to init Gemini. Check GEMINI_API_KEY in .env")
        provider = LLMProvider(model_name="ollama/llama3")

    # Example usage
    # provider = LLMProvider(model_name="ollama/llama3.2")
    engine = EvolutionEngine(provider, SortEvaluator(), population_size=2)
    engine.seed_population('Sort a list of integers in ascending order')
    engine.evolve(generations=1)

