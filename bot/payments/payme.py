"""
Payme payment provider (Test Mode)
Documentation: https://developer.help.paycom.uz/
"""
import base64
import hashlib
import time
from typing import Dict, Any
from bot.payments import PaymentProvider

class PaymePayment(PaymentProvider):
    """Payme payment integration"""
    
    def __init__(self, merchant_id: str, secret_key: str, test_mode: bool = True):
        self.merchant_id = merchant_id or "DEMO_MERCHANT"
        self.secret_key = secret_key or "DEMO_SECRET"
        self.test_mode = test_mode
        self.base_url = "https://checkout.paycom.uz" if not test_mode else "https://checkout.test.paycom.uz"
    
    async def create_invoice(self, amount: float, order_id: str, description: str) -> Dict[str, Any]:
        """
        Create Payme payment invoice
        
        In test mode, returns a mock invoice.
        In production, this would generate proper Payme checkout link.
        """
        # Amount in tiyin (1 sum = 100 tiyin)
        amount_tiyin = int(amount * 100)
        
        # Test mode - return mock data
        if self.test_mode or self.merchant_id == "DEMO_MERCHANT":
            return {
                'invoice_id': f"PAYME_TEST_{order_id}_{int(time.time())}",
                'payment_url': f"https://checkout.test.paycom.uz/{base64.b64encode(f'm={self.merchant_id};ac.order_id={order_id};a={amount_tiyin}'.encode()).decode()}",
                'status': 'pending',
                'test_mode': True
            }
        
        # Production mode
        # Encode parameters
        params = f"m={self.merchant_id};ac.order_id={order_id};a={amount_tiyin}"
        encoded_params = base64.b64encode(params.encode()).decode()
        
        payment_url = f"{self.base_url}/{encoded_params}"
        
        return {
            'invoice_id': f"PAYME_{order_id}_{int(time.time())}",
            'payment_url': payment_url,
            'status': 'pending',
            'test_mode': False
        }
    
    async def check_payment_status(self, invoice_id: str) -> Dict[str, Any]:
        """Check Payme payment status"""
        # Test mode - always return pending
        if self.test_mode or "TEST" in invoice_id:
            return {
                'status': 'pending',
                'amount': 0,
                'paid_at': None,
                'test_mode': True
            }
        
        # Production: Would call Payme API to check status
        return {
            'status': 'pending',
            'amount': 0,
            'paid_at': None
        }
    
    def get_auth_header(self) -> str:
        """Get Basic Auth header for Payme API"""
        credentials = f"Paycom:{self.secret_key}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"
