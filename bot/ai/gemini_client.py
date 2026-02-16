"""
Google Gemini AI client for legal bot
"""
import google.generativeai as genai
from typing import Optional
from bot.config import config
import logging
import asyncio

class GeminiClient:
    """Google Gemini AI client wrapper with fallback models (Legacy Library)"""
    
    # List of models to try in order
    MODELS = [
        'gemini-1.5-flash',
        'gemini-1.5-pro',
        'gemini-pro', # Very stable legacy model
    ]
    
    def __init__(self):
        self.enabled = config.enable_ai_responses and config.gemini_api_key is not None
        if self.enabled:
            genai.configure(api_key=config.gemini_api_key.get_secret_value())
            logging.info("Gemini AI initialized successfully (Legacy Lib)")
        else:
            logging.info("Gemini AI disabled (no API key or disabled in config)")
    
    async def generate_text(self, prompt: str, temperature: float = 0.7) -> Optional[str]:
        """
        Generate text using Gemini with model fallback
        """
        if not self.enabled:
            return None
        
        last_error = None
        
        for model_name in self.MODELS:
            try:
                logging.info(f"Trying Gemini model: {model_name}")
                model = genai.GenerativeModel(model_name)
                
                # Run sync generate_content in executor to avoid blocking
                loop = asyncio.get_running_loop()
                response = await loop.run_in_executor(
                    None, 
                    lambda: model.generate_content(
                        prompt,
                        generation_config=genai.types.GenerationConfig(
                            temperature=temperature,
                            max_output_tokens=2048
                        )
                    )
                )
                return response.text
            except Exception as e:
                logging.warning(f"Model {model_name} failed: {e}")
                last_error = e
                continue
        
        logging.error(f"All Gemini models failed. Last error: {last_error}")
        return None
    
    async def classify_question(self, question: str) -> dict:
        """
        Classify legal question complexity
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
