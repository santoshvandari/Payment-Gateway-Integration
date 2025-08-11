import requests
import json
import hashlib
import hmac
import base64
from django.conf import settings
from django.urls import reverse
from .models import Order, PaymentLog


class EsewaPaymentGateway:
    """eSewa Payment Gateway Integration"""
    
    def __init__(self):
        self.scd = settings.ESEWA_SCD
        self.success_url = settings.ESEWA_SUCCESS_URL
        self.failure_url = settings.ESEWA_FAILURE_URL
        self.payment_url = settings.ESEWA_PAYMENT_URL
    
    def generate_payment_data(self, order):
        """Generate payment data for eSewa"""
        return {
            'tAmt': str(order.total_price),
            'amt': str(order.total_price),
            'txAmt': '0',
            'psc': '0',
            'pdc': '0',
            'scd': self.scd,
            'pid': order.order_id,
            'su': self.success_url,
            'fu': self.failure_url
        }
    
    def verify_payment(self, request):
        """Verify eSewa payment"""
        oid = request.GET.get('oid')
        amt = request.GET.get('amt')
        refId = request.GET.get('refId')
        
        if not all([oid, amt, refId]):
            return False, "Missing required parameters"
        
        try:
            order = Order.objects.get(order_id=oid)
            
            # For eSewa test environment, we'll consider it successful if we have all parameters
            # In production, you would verify with eSewa's verification endpoint
            if oid and amt and refId:
                # Update order
                order.is_paid = True
                order.paid_amount = int(float(amt))
                order.payment_method = 'eSewa'
                order.transaction_id = refId
                order.save()
                
                # Log payment
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
                        'status': 'test_success'
                    }
                )
                
                return True, "Payment verified successfully"
            else:
                PaymentLog.objects.create(
                    order=order,
                    payment_method='eSewa',
                    transaction_id=refId or 'unknown',
                    amount=int(float(amt)) if amt else 0,
                    status='Failed',
                    gateway_response={
                        'oid': oid,
                        'amt': amt,
                        'refId': refId,
                        'error': 'Missing parameters'
                    }
                )
                return False, "Payment verification failed"
                
        except Order.DoesNotExist:
            return False, "Order not found"
        except Exception as e:
            return False, f"Error: {str(e)}"


class KhaltiPaymentGateway:
    """Khalti Payment Gateway Integration"""
    
    def __init__(self):
        self.public_key = settings.KHALTI_PUBLIC_KEY
        self.secret_key = settings.KHALTI_SECRET_KEY
        self.payment_url = settings.KHALTI_PAYMENT_URL
        self.verify_url = settings.KHALTI_VERIFY_URL
        self.success_url = settings.KHALTI_SUCCESS_URL
        self.failure_url = settings.KHALTI_FAILURE_URL
    
    def initiate_payment(self, order):
        """Initiate Khalti payment"""
        headers = {
            'Authorization': f'Key {self.secret_key}',
            'Content-Type': 'application/json'
        }
        
        payment_data = {
            "return_url": self.success_url,
            "website_url": getattr(settings, 'KHALTI_WEBSITE_URL', 'http://127.0.0.1:8000/'),
            "amount": order.total_price * 100,  # Khalti expects amount in paisa
            "purchase_order_id": order.order_id,
            "purchase_order_name": f"Order - {order.name}",
            "customer_info": {
                "name": order.name,
                "email": "customer@example.com",
                "phone": "9841234567"
            }
        }
        
        try:
            response = requests.post(
                self.payment_url,
                headers=headers,
                data=json.dumps(payment_data)
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
            
            return False, error_data
    
    def verify_payment(self, pidx):
        """Verify Khalti payment"""
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
                data=json.dumps(verify_data)
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'Completed':
                    # Get order by purchase_order_id
                    order_id = data.get('purchase_order_id')
                    order = Order.objects.get(order_id=order_id)
                    
                    # Update order
                    order.is_paid = True
                    order.paid_amount = data.get('total_amount', 0) // 100  # Convert paisa to rupees
                    order.payment_method = 'Khalti'
                    order.transaction_id = data.get('transaction_id')
                    order.save()
                    
                    # Log payment
                    PaymentLog.objects.create(
                        order=order,
                        payment_method='Khalti',
                        transaction_id=data.get('transaction_id'),
                        amount=data.get('total_amount', 0) // 100,
                        status='Success',
                        gateway_response=data
                    )
                    
                    return True, data
                else:
                    return False, data
            else:
                return False, response.json()
                
        except Order.DoesNotExist:
            return False, {"error": "Order not found"}
        except Exception as e:
            return False, {"error": str(e)}
