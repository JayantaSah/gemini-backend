import google.generativeai as genai
from typing import List, Dict
from app.config import settings

# Configure Gemini API
genai.configure(api_key=settings.gemini_api_key)


class GeminiService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def generate_response(self, message: str, conversation_history: List[Dict[str, str]] = None) -> str:
        """Generate response from Gemini API"""
        try:
            # Prepare conversation context
            if conversation_history:
                context = "\n".join([
                    f"{msg['role']}: {msg['content']}" 
                    for msg in conversation_history[-10:]  # Last 10 messages for context
                ])
                prompt = f"Conversation history:\n{context}\n\nUser: {message}\nAssistant:"
            else:
                prompt = message
            
            # Generate response
            response = self.model.generate_content(prompt)
            return response.text
        
        except Exception as e:
            # Fallback response in case of API failure
            return f"I apologize, but I'm experiencing technical difficulties. Please try again later. Error: {str(e)}"
    
    def validate_api_key(self) -> bool:
        """Validate if Gemini API key is working"""
        try:
            test_response = self.model.generate_content("Hello")
            return bool(test_response.text)
        except Exception:
            return False


# Global instance
gemini_service = GeminiService()

