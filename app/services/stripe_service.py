import stripe
from typing import Dict, Optional
from app.config import settings

# Configure Stripe
stripe.api_key = settings.stripe_secret_key


class StripeService:
    def __init__(self):
        self.price_id = settings.stripe_price_id
    
    def create_customer(self, email: str, mobile_number: str) -> Dict:
        """Create a new Stripe customer"""
        try:
            customer = stripe.Customer.create(
                email=email,
                phone=mobile_number,
                metadata={
                    'mobile_number': mobile_number
                }
            )
            return {
                'success': True,
                'customer_id': customer.id,
                'customer': customer
            }
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_checkout_session(self, customer_id: str, success_url: str, cancel_url: str) -> Dict:
        """Create Stripe checkout session for Pro subscription"""
        try:
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price': self.price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'customer_id': customer_id
                }
            )
            return {
                'success': True,
                'session_id': session.id,
                'checkout_url': session.url
            }
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_subscription(self, subscription_id: str) -> Optional[Dict]:
        """Get subscription details from Stripe"""
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return {
                'id': subscription.id,
                'status': subscription.status,
                'current_period_start': subscription.current_period_start,
                'current_period_end': subscription.current_period_end,
                'customer_id': subscription.customer
            }
        except stripe.error.StripeError:
            return None
    
    def cancel_subscription(self, subscription_id: str) -> Dict:
        """Cancel a subscription"""
        try:
            subscription = stripe.Subscription.delete(subscription_id)
            return {
                'success': True,
                'subscription': subscription
            }
        except stripe.error.StripeError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def construct_webhook_event(self, payload: bytes, sig_header: str) -> Optional[Dict]:
        """Construct webhook event from Stripe"""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.stripe_webhook_secret
            )
            return event
        except (ValueError, stripe.error.SignatureVerificationError):
            return None


# Global instance
stripe_service = StripeService()

