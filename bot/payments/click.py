"""
Click.uz payment provider (Test Mode)
Documentation: https://docs.click.uz/
"""
import hashlib
import time
from typing import Dict, Any
from bot.payments import PaymentProvider

class ClickPayment(PaymentProvider):
    """Click.uz payment integration"""
    
    def __init__(self, merchant_id: int, service_id: int, secret_key: str, test_mode: bool = True):
        self.merchant_id = merchant_id
        self.service_id = service_id
        self.secret_key = secret_key
        self.test_mode = test_mode
        self.base_url = "https://my.click.uz/services/pay" if not test_mode else "https://my.click.uz/services/pay"
    
    async def create_invoice(self, amount: float, order_id: str, description: str) -> Dict[str, Any]:
        """
        Create Click payment invoice
        
        In test mode, returns a mock invoice.
        In production, this would call Click API.
        """
        # Test mode - return mock data
        if self.test_mode or not self.merchant_id:
            return {
                'invoice_id': f"CLK_TEST_{order_id}_{int(time.time())}",
                'payment_url': f"https://my.click.uz/services/pay?service_id=DEMO&merchant_id=DEMO&amount={amount}&transaction_param={order_id}",
                'status': 'pending',
                'test_mode': True
            }
        
        # Production mode (when credentials are provided)
        payment_url = (
            f"{self.base_url}?"
            f"service_id={self.service_id}&"
            f"merchant_id={self.merchant_id}&"
            f"amount={amount}&"
            f"transaction_param={order_id}&"
            f"return_url=https://t.me/your_bot"
        )
        
        return {
            'invoice_id': f"CLK_{order_id}_{int(time.time())}",
            'payment_url': payment_url,
            'status': 'pending',
            'test_mode': False
        }
    
    async def check_payment_status(self, invoice_id: str) -> Dict[str, Any]:
        """Check Click payment status"""
        # Test mode - always return pending
        if self.test_mode or "TEST" in invoice_id:
            return {
                'status': 'pending',
                'amount': 0,
                'paid_at': None,
                'test_mode': True
            }
        
        # Production: Would call Click API to check status
        return {
            'status': 'pending',
            'amount': 0,
            'paid_at': None
        }
    
    def verify_signature(self, params: Dict[str, Any], signature: str) -> bool:
        """Verify Click webhook signature"""
        # Build signature string according to Click documentation
        sign_string = f"{params.get('click_trans_id')}{self.service_id}{self.secret_key}{params.get('merchant_trans_id')}{params.get('amount')}{params.get('action')}{params.get('sign_time')}"
        
        expected_signature = hashlib.md5(sign_string.encode()).hexdigest()
        return signature == expected_signature
