"""
AI-powered legal answer generator
"""
from bot.ai.gemini_client import gemini_client
import logging

class LegalAIResponder:
    """Generate legal answers using AI"""
    
    async def generate_answer(self, question: str, category: str = "boshqa") -> str:
        """
        Generate professional legal answer
        
        Args:
            question: User's legal question
            category: Legal category
        
        Returns:
            Professional answer in Uzbek
        """
        prompt = f"""Sen professional advokat bo'lsang. O'zbekistonda yuridik maslahat berasiz.

Kategoriya: {category}
Savol: "{question}"

Quyidagi formatda javob ber:

1. Qisqa javob (2-3 jumla)
2. Batafsil tushuntirish
3. Amaliy yo'riqnoma (agar kerak bo'lsa)
4. Tegishli qonunlar (agar bilsang)

Professional, rasmiy va tushunarli til ishlatgin.
Javob oxirida: "⚠️ Bu umumiy ma'lumot. Konkret holatingiz uchun advokat bilan maslahatlashing."

Javob (Uzbek tilida):"""

        response = await gemini_client.generate_text(prompt, temperature=0.7)
        
        if not response:
            return self._fallback_answer(question)
        
        # Add disclaimer if not present
        if "⚠️" not in response:
            response += "\n\n⚠️ Bu umumiy ma'lumot. Konkret holatingiz uchun advokat bilan maslahatlashing."
        
        return response
    
    def _fallback_answer(self, question: str) -> str:
        """Fallback answer when AI is unavailable"""
        return (
            "⚖️ <b>Sizning savolingiz professional ko'rib chiqish uchun qabul qilindi.</b>\n\n"
            "Hozirda AI xizmati mavjud emas. "
            "Sizning savolingizga professional advokat javob beradi.\n\n"
            "⚠️ Professional maslahat uchun to'lov talab qilinadi."
        )

# Global instance
ai_responder = LegalAIResponder()
