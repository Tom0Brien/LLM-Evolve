import litellm
import os
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()


class LLMProvider:
    def __init__(self, model_name: str = "gemini/gemini-flash-latest", api_key: str = None):
        """
        Initialize the LLM provider.
        
        Args:
            model_name: The name of the model to use. 
                        Examples: 
                        - "ollama/llama3" for local Ollama
                        - "gemini/gemini-2.0-flash" for Google Gemini
            api_key: Optional API key. If not provided, litellm will look for env vars.
        """
        self.model_name = model_name
        self.api_key = api_key

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=2, min=10, max=60))
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        """
        Generate text from the LLM.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})

        try:
            response = litellm.completion(
                model=self.model_name,
                messages=messages,
                api_key=self.api_key
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating response: {e}")
            raise

if __name__ == "__main__":
    # Test the provider
    # provider = LLMProvider(model_name="ollama/llama3") # Example for local
    # For now, let's assume the user might want to test with a dummy or if they have keys setup.
    print("LLMProvider module ready.")
