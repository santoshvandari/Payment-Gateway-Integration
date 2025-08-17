import requests
import json
import hashlib
import hmac
import base64
import uuid
from django.conf import settings
from django.urls import reverse
from .models import Order, PaymentLog
import logging

logger = logging.getLogger(__name__)


class EsewaPaymentGateway:
    """eSewa Payment Gateway Integration - Production Ready"""
    
    def __init__(self):
        self.scd = settings.ESEWA_SCD
        self.success_url = settings.ESEWA_SUCCESS_URL
        self.failure_url = settings.ESEWA_FAILURE_URL
        self.payment_url = settings.ESEWA_PAYMENT_URL
        self.verify_url = getattr(settings, 'ESEWA_VERIFY_URL', None)
        self.mode = getattr(settings, 'PAYMENT_GATEWAY_MODE', 'sandbox')
    
    def generate_payment_data(self, order):
        """Generate payment data for eSewa"""
        # Generate unique transaction UUID
        transaction_uuid = str(uuid.uuid4())
        
        payment_data = {
            'tAmt': str(order.total_price),
            'amt': str(order.total_price),
            'txAmt': '0',  # Tax amount
            'psc': '0',    # Service charge
            'pdc': '0',    # Delivery charge
            'scd': self.scd,
            'pid': order.order_id,
            'su': self.success_url,
            'fu': self.failure_url,
        }
        
        # Log payment initiation
        PaymentLog.objects.create(
            order=order,
            payment_method='eSewa',
            transaction_id=transaction_uuid,
            amount=order.total_price,
            status='Initiated',
            gateway_response={'payment_data': payment_data}
        )
        
        return payment_data
    
    def verify_payment(self, request):
        """Verify eSewa payment with proper API verification"""
        oid = request.GET.get('oid')
        amt = request.GET.get('amt')
        refId = request.GET.get('refId')
        
        if not all([oid, amt, refId]):
            logger.error(f"eSewa payment verification failed: Missing parameters - oid: {oid}, amt: {amt}, refId: {refId}")
            return False, "Missing required parameters"
        
        try:
            order = Order.objects.get(order_id=oid)
            
            # In production mode, verify with eSewa API
            if self.mode == 'production' and self.verify_url:
                verification_success = self._verify_with_esewa_api(oid, amt, refId)
                if not verification_success:
                    self._log_failed_payment(order, refId, amt, "API verification failed")
                    return False, "Payment verification failed with eSewa API"
            
            # Verify amount matches
            if int(float(amt)) != order.total_price:
                self._log_failed_payment(order, refId, amt, "Amount mismatch")
                return False, "Payment amount does not match order amount"
            
            # Update order
            order.is_paid = True
            order.paid_amount = int(float(amt))
            order.payment_method = 'eSewa'
            order.transaction_id = refId
            order.save()
            
            # Log successful payment
            PaymentLog.objects.create(
                order=order,
                payment_method='eSewa',
                transaction_id=refId,
                amount=int(float(amt)),
                status='Success',
                gateway_response={
                    'oid': oid,
                    'amt': amt,
                    'refId': refId,
                    'verification_mode': self.mode
                }
            )
            
            logger.info(f"eSewa payment successful for order {oid}, amount: {amt}, refId: {refId}")
            return True, "Payment verified successfully"
                
        except Order.DoesNotExist:
            logger.error(f"eSewa payment verification failed: Order {oid} not found")
            return False, "Order not found"
        except Exception as e:
            logger.error(f"eSewa payment verification error: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def _verify_with_esewa_api(self, oid, amt, refId):
        """Verify payment with eSewa's verification API"""
        try:
            verify_data = {
                'amt': amt,
                'scd': self.scd,
                'rid': refId,
                'pid': oid
            }
            
            response = requests.post(self.verify_url, data=verify_data, timeout=30)
            
            if response.status_code == 200:
                # Check if response contains success indicator
                if 'Success' in response.text or 'success' in response.text.lower():
                    return True
                    
            logger.warning(f"eSewa API verification failed: {response.status_code} - {response.text}")
            return False
            
        except Exception as e:
            logger.error(f"eSewa API verification exception: {str(e)}")
            return False
    
    def _log_failed_payment(self, order, refId, amt, reason):
        """Log failed payment attempt"""
        PaymentLog.objects.create(
            order=order,
            payment_method='eSewa',
            transaction_id=refId or 'unknown',
            amount=int(float(amt)) if amt else 0,
            status='Failed',
            gateway_response={'reason': reason}
        )


class KhaltiPaymentGateway:
    """Khalti Payment Gateway Integration - Production Ready"""
    
    def __init__(self):
        self.public_key = settings.KHALTI_PUBLIC_KEY
        self.secret_key = settings.KHALTI_SECRET_KEY
        self.payment_url = settings.KHALTI_PAYMENT_URL
        self.verify_url = settings.KHALTI_VERIFY_URL
        self.success_url = settings.KHALTI_SUCCESS_URL
        self.failure_url = settings.KHALTI_FAILURE_URL
        self.website_url = getattr(settings, 'KHALTI_WEBSITE_URL', 'https://yourdomain.com/')
        self.mode = getattr(settings, 'PAYMENT_GATEWAY_MODE', 'sandbox')
    
    def initiate_payment(self, order):
        """Initiate Khalti payment with proper error handling"""
        headers = {
            'Authorization': f'Key {self.secret_key}',
            'Content-Type': 'application/json'
        }
        
        payment_data = {
            "return_url": self.success_url,
            "website_url": self.website_url,
            "amount": order.total_price * 100,  # Khalti expects amount in paisa
            "purchase_order_id": order.order_id,
            "purchase_order_name": f"Order - {order.name}",
            "customer_info": {
                "name": order.name,
                "email": getattr(order, 'email', 'customer@example.com'),
                "phone": getattr(order, 'phone', '9800000000')
            }
        }
        
        try:
            response = requests.post(
                self.payment_url,
                headers=headers,
                data=json.dumps(payment_data),
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Log the initiation
                PaymentLog.objects.create(
                    order=order,
                    payment_method='Khalti',
                    transaction_id=data.get('pidx', ''),
                    amount=order.total_price,
                    status='Initiated',
                    gateway_response=data
                )
                
                logger.info(f"Khalti payment initiated for order {order.order_id}")
                return True, data
            else:
                error_data = response.json() if response.content else {"error": f"HTTP {response.status_code}"}
                
                # Log the failed initiation
                PaymentLog.objects.create(
                    order=order,
                    payment_method='Khalti',
                    transaction_id='',
                    amount=order.total_price,
                    status='Failed',
                    gateway_response=error_data
                )
                
                logger.error(f"Khalti payment initiation failed: {error_data}")
                return False, error_data
                
        except requests.RequestException as e:
            error_data = {"error": f"Network error: {str(e)}"}
            
            # Log the exception
            PaymentLog.objects.create(
                order=order,
                payment_method='Khalti',
                transaction_id='',
                amount=order.total_price,
                status='Failed',
                gateway_response=error_data
            )
            
            logger.error(f"Khalti payment initiation exception: {str(e)}")
            return False, error_data
        except Exception as e:
            error_data = {"error": str(e)}
            
            # Log the exception
            PaymentLog.objects.create(
                order=order,
                payment_method='Khalti',
                transaction_id='',
                amount=order.total_price,
                status='Failed',
                gateway_response=error_data
            )
            
            logger.error(f"Khalti payment initiation unexpected error: {str(e)}")
            return False, error_data
    
    def verify_payment(self, pidx):
        """Verify Khalti payment with comprehensive validation"""
        headers = {
            'Authorization': f'Key {self.secret_key}',
            'Content-Type': 'application/json'
        }
        
        verify_data = {
            "pidx": pidx
        }
        
        try:
            response = requests.post(
                self.verify_url,
                headers=headers,
                data=json.dumps(verify_data),
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'Completed':
                    # Get order by purchase_order_id
                    order_id = data.get('purchase_order_id')
                    order = Order.objects.get(order_id=order_id)
                    
                    # Verify amount matches
                    expected_amount = order.total_price * 100  # Convert to paisa
                    actual_amount = data.get('total_amount', 0)
                    
                    if actual_amount != expected_amount:
                        logger.error(f"Khalti amount mismatch: expected {expected_amount}, got {actual_amount}")
                        return False, {"error": "Amount mismatch"}
                    
                    # Update order
                    order.is_paid = True
                    order.paid_amount = actual_amount // 100  # Convert paisa to rupees
                    order.payment_method = 'Khalti'
                    order.transaction_id = data.get('transaction_id')
                    order.save()
                    
                    # Log payment
                    PaymentLog.objects.create(
                        order=order,
                        payment_method='Khalti',
                        transaction_id=data.get('transaction_id'),
                        amount=actual_amount // 100,
                        status='Success',
                        gateway_response=data
                    )
                    
                    logger.info(f"Khalti payment verified successfully for order {order_id}")
                    return True, data
                else:
                    logger.warning(f"Khalti payment not completed: {data}")
                    return False, data
            else:
                error_data = response.json() if response.content else {"error": f"HTTP {response.status_code}"}
                logger.error(f"Khalti verification failed: {error_data}")
                return False, error_data
                
        except Order.DoesNotExist:
            error_msg = {"error": "Order not found"}
            logger.error(f"Khalti verification failed: Order not found for pidx {pidx}")
            return False, error_msg
        except requests.RequestException as e:
            error_msg = {"error": f"Network error: {str(e)}"}
            logger.error(f"Khalti verification network error: {str(e)}")
            return False, error_msg
        except Exception as e:
            error_msg = {"error": str(e)}
            logger.error(f"Khalti verification unexpected error: {str(e)}")
            return False, error_msg
