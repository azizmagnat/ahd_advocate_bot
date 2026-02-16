"""
Base payment provider interface
"""
from abc import ABC, abstractmethod
from typing import Dict, Any

class PaymentProvider(ABC):
    """Base class for payment providers"""
    
    @abstractmethod
    async def create_invoice(self, amount: float, order_id: str, description: str) -> Dict[str, Any]:
        """
        Create payment invoice
        
        Returns:
            {
                'invoice_id': str,
                'payment_url': str,
                'status': str
            }
        """
        pass
    
    @abstractmethod
    async def check_payment_status(self, invoice_id: str) -> Dict[str, Any]:
        """
        Check payment status
        
        Returns:
            {
                'status': 'pending' | 'paid' | 'cancelled',
                'amount': float,
                'paid_at': datetime | None
            }
        """
        pass
