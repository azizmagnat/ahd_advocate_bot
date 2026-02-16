import asyncio
from google import genai
import os

# Hardcode key for local debug script or try to read from env
API_KEY = "AIzaSyCtu7QdRF18-D_siYfLsim56ehb1GbOa8M"

async def list_models():
    client = genai.Client(api_key=API_KEY)
    
    print("Listing available models:")
    try:
        async for model in client.aio.models.list():
            print(f"- {model.name}")
            if hasattr(model, 'supported_generation_methods'):
                print(f"  Methods: {model.supported_generation_methods}")
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    asyncio.run(list_models())
    
    print("Listing available models:")
    try:
        # Pager object is not directly awaitable, iterate through it
        async for model in client.aio.models.list():
            print(f"- {model.name}")
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    asyncio.run(list_models())
