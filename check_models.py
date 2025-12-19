import google.generativeai as genai
import sys

# Configuration
# Replace 'YOUR_API_KEY_HERE' with your actual Google API Key.
API_KEY = "YOUR_API_KEY_HERE"

def list_available_models():
    """
    Retrieves and displays a list of available Gemini models 
    associated with the provided API key.
    """
    try:
        # Validate API Key
        if not API_KEY or API_KEY == "YOUR_API_KEY_HERE":
            print("Error: API Key is missing. Please update the API_KEY variable.")
            return

        # Configure the Generative AI client
        genai.configure(api_key=API_KEY)

        print("-" * 50)
        print(f"{'Model Name':<30} | {'Capabilities'}")
        print("-" * 50)

        # Iterate through available models
        for model in genai.list_models():
            # Filter for models that support content generation
            if 'generateContent' in model.supported_generation_methods:
                print(f"{model.name:<30} | {model.supported_generation_methods}")

        print("-" * 50)

    except Exception as e:
        print(f"Authentication Failed or Connection Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    print("Initializing Google AI Client...")
    list_available_models()