"""
Google Gemini AI client for legal bot (Direct REST API)
"""
import aiohttp
import logging
import json
from typing import Optional
from bot.config import config

class GeminiClient:
    """Google Gemini AI client wrapper using direct REST API"""
    
    
    # List of models to try in order (Comprehensive Fallback)
    MODELS = [
        'gemini-1.5-flash',
        'gemini-1.5-pro',
        'gemini-pro',
        'gemini-2.0-flash-lite-preview-02-05',
        'gemini-2.0-flash-exp',
    ]
    
    # Try both v1beta and v1 API versions
    BASE_URL_BETA = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    BASE_URL_V1 = "https://generativelanguage.googleapis.com/v1/models/{model}:generateContent"
    
    def __init__(self):
        self.api_key = config.gemini_api_key.get_secret_value() if config.gemini_api_key else None
        self.enabled = config.enable_ai_responses and self.api_key is not None
        if self.enabled:
            logging.info("Gemini AI initialized successfully (REST API)")
        else:
            logging.info("Gemini AI disabled (no API key or disabled in config)")
    
    async def generate_text(self, prompt: str, temperature: float = 0.7) -> Optional[str]:
        """
        Generate text using Gemini REST API with model fallback
        """
        if not self.enabled:
            return None
        
        last_error = None
        
        async with aiohttp.ClientSession() as session:
            for model_name in self.MODELS:
                # Try v1beta first, then v1
                for base_url in [self.BASE_URL_BETA, self.BASE_URL_V1]:
                    try:
                        version = "v1beta" if "v1beta" in base_url else "v1"
                        logging.info(f"Trying Gemini model: {model_name} ({version})")
                        
                        url = base_url.format(model=model_name)
                        params = {"key": self.api_key}
                        
                        headers = {"Content-Type": "application/json"}
                        payload = {
                            "contents": [{
                                "parts": [{"text": prompt}]
                            }],
                            "generationConfig": {
                                "temperature": temperature,
                                "maxOutputTokens": 2048
                            }
                        }
                        
                        async with session.post(url, params=params, json=payload, headers=headers) as response:
                            if response.status == 200:
                                data = await response.json()
                                # Extract text from response
                                if 'candidates' in data and data['candidates']:
                                    content = data['candidates'][0].get('content', {})
                                    parts = content.get('parts', [])
                                    if parts:
                                        logging.info(f"SUCCESS: Model {model_name} ({version}) worked!")
                                        return parts[0].get('text', '')
                                
                                logging.warning(f"Empty response from {model_name}: {data}")
                                continue
                                
                            error_text = await response.text()
                            logging.warning(f"Model {model_name} ({version}) failed with status {response.status}: {error_text}")
                            last_error = f"Status {response.status}: {error_text}"
                            
                    except Exception as e:
                        logging.warning(f"Model {model_name} ({version}) error: {e}")
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
