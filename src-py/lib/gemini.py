import os
from dotenv import load_dotenv

load_dotenv()

from google import genai
from google.genai import types
from google.genai.types import Content, Part
from typing import Optional, List


client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


class GeminiClient:
    def __init__(self, system_instruction: str = None):
        self.client = client
        self.system_instruction = system_instruction or "You are a helpful AI assistant. Respond in plain text."
    
    def generate_response(self, conversation_history: List[dict]) -> str:
        """
        Generate a response based on conversation history.
        
        Args:
            conversation_history: List of dicts with 'role' and 'content' keys
                                where role is either 'user' or 'model'
        
        Returns:
            Generated response text
        """
        # Convert our simple dict format to Gemini's Content format
        contents = []
        for message in conversation_history:
            role = "user" if message["role"] == "user" else "model"
            content = Content(role=role, parts=[Part(text=message["content"])])
            contents.append(content)
        
        try:
            response = self.client.models.generate_content(
                model=os.getenv("GEMINI_MODEL"),
                config=types.GenerateContentConfig(system_instruction=self.system_instruction),
                contents=contents
            )
            return response.text
        except Exception as e:
            raise Exception(f"Failed to generate response: {str(e)}")
    
    def generate_single_response(self, message: str) -> str:
        """Generate a response to a single message without conversation history."""
        return self.generate_response([{"role": "user", "content": message}])
	
	
	