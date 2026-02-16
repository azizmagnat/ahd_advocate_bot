"""
Google Gemini AI client for legal bot
"""
import google.generativeai as genai
from typing import Optional
from bot.config import config
import logging

class GeminiClient:
    """Google Gemini AI client wrapper"""
    
    def __init__(self):
        self.enabled = config.enable_ai_responses and config.gemini_api_key is not None
        if self.enabled:
            genai.configure(api_key=config.gemini_api_key.get_secret_value())
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            logging.info("Gemini AI initialized successfully")
        else:
            logging.info("Gemini AI disabled (no API key or disabled in config)")
    
    async def generate_text(self, prompt: str, temperature: float = 0.7) -> Optional[str]:
        """
        Generate text using Gemini
        
        Args:
            prompt: The prompt to send to Gemini
            temperature: Creativity level (0.0 - 1.0)
        
        Returns:
            Generated text or None if disabled/error
        """
        if not self.enabled:
            return None
        
        try:
            response = await self.model.generate_content_async(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=2048
                )
            )
            return response.text
        except Exception as e:
            logging.error(f"Gemini API error: {e}")
            return None
    
    async def classify_question(self, question: str) -> dict:
        """
        Classify legal question complexity
        
        Returns:
            {
                'complexity': 'simple' | 'medium' | 'complex',
                'confidence': float,
                'category': str,
                'reasoning': str
            }
        """
        prompt = f"""Sen professional yuridik bo'tsan. Quyidagi savolni tahlil qil va javob ber JSON formatda:

Savol: "{question}"

JSON format:
{{
    "complexity": "simple/medium/complex",
    "confidence": 0.0-1.0,
    "category": "mehnat/fuqarolik/oilaviy/jinoiy/boshqa",
    "reasoning": "qisqa tushuntirish"
}}

Mezonlar:
- simple: Umumiy ma'lumot, oddiy savol (masalan: "yoshlar daftari nima?")
- medium: Konkret holat, professional maslahat kerak
- complex: Murakkab nizolar, sud jarayoni, biznes ishlar

Faqat JSON javob ber, boshqa matn yo'q."""

        try:
            response = await self.generate_text(prompt, temperature=0.3)
            if not response:
                return self._default_classification()
            
            # Parse JSON from response
            import json
            # Remove markdown code blocks if present
            response = response.strip()
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            response = response.strip()
            
            result = json.loads(response)
            return result
        except Exception as e:
            logging.error(f"Classification error: {e}")
            return self._default_classification()
    
    def _default_classification(self) -> dict:
        """Default fallback classification"""
        return {
            'complexity': 'medium',
            'confidence': 0.5,
            'category': 'boshqa',
            'reasoning': 'Avtomatik tasnif ishlamadi'
        }

# Global instance
gemini_client = GeminiClient()
