from src.tasks.base import AbstractBaseTask
from src.tasks.registry import register_task
import zlib
import base64

@register_task(name_override="compression")
class CompressionTask(AbstractBaseTask):
    @property
    def name(self) -> str:
        return "Compression"

    @property
    def description(self) -> str:
        return """Write two functions:
1. `compress(text: str) -> bytes`: Compresses the input string.
2. `decompress(data: bytes) -> str`: Decompresses the data back to the original string.
Goal: Minimize the size of the compressed data while maintaining perfect reconstruction."""

    def initial_prompt(self) -> str:
        return """
Write a Python script with two functions:
1. `compress(text: str) -> bytes`
2. `decompress(data: bytes) -> str`

The goal is to make the output of `compress` as small as possible.
Important: `decompress(compress(text))` must equal `text` exactly.

RECOMMENDATION: Use standard libraries like `zlib`, `gzip`, or `lzma` for reliable and efficient compression. 
Do not implement custom algorithms unless you are sure they are lossless and handle edge cases (like Unicode) correctly.
"""

    def evaluate(self, code: str) -> float:
        try:
            # Clean Code
            clean_code = code.replace("```python", "").replace("```", "").strip()
            namespace = {}
            exec(clean_code, namespace)
            
            if "compress" not in namespace or "decompress" not in namespace:
                return 0.0
                
            compress_func = namespace["compress"]
            decompress_func = namespace["decompress"]

            # Test Data
            test_cases = [
                "Hello World" * 10,
                "A" * 1000,
                "Random string with symbols: !@#$%^&*()_+",
                "Python is a high-level, general-purpose programming language. " * 5
            ]

            total_ratio = 0.0
            
            for text in test_cases:
                try:
                    compressed = compress_func(text)
                    if not isinstance(compressed, bytes):
                        raise ValueError(f"compress() returned {type(compressed)}, expected bytes")
                        
                    reconstructed = decompress_func(compressed)
                    
                    # Hard Constraint: Correctness
                    if reconstructed != text:
                        # Create a short snippet for feedback
                        snippet = reconstructed[:20] + "..." if len(reconstructed) > 20 else reconstructed
                        expected = text[:20] + "..." if len(text) > 20 else text
                        raise ValueError(f"Decompression mismatch: Expected '{expected}', Got '{snippet}'")
                    
                    # Metric: Compression Ratio
                    original_len = len(text.encode('utf-8'))
                    compressed_len = len(compressed)
                    
                    if original_len == 0:
                        continue
                        
                    ratio = compressed_len / original_len
                    fitness = 1.0 - ratio
                    
                    # Clamp fitness
                    fitness = max(0.0, min(1.0, fitness))
                    total_ratio += fitness
                    
                except Exception as e:
                    # Re-raise with context if it's not our ValueError
                    if isinstance(e, ValueError):
                        raise e
                    raise RuntimeError(f"Runtime error during test: {e}")

            return total_ratio / len(test_cases)

        except Exception as e:
            # This allows the engine to capture the error as feedback
            raise e
