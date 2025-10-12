import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    MODEL_NAME = os.getenv("MODEL_NAME", "gemini-pro")
    
    def __init__(self):
        print(f"API Key loaded: {'Yes' if self.GEMINI_API_KEY else 'No'}")
        if self.GEMINI_API_KEY:
            print(f"Key preview: {self.GEMINI_API_KEY[:10]}...")
    
settings = Settings()