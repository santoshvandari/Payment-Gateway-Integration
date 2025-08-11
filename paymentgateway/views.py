from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
import json
from .models import Order, PaymentLog
from .payment_gateways import EsewaPaymentGateway, KhaltiPaymentGateway

# Create your views here.

def order_list(request):
    """Display list of all orders"""
    orders = Order.objects.all()
    return render(request, "orders.html", {"orders": orders})


def order_checkout(request, order_id):
    """Handle order checkout with payment gateway selection"""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == "POST":
        payment_method = request.POST.get('payment_method')
        
        if payment_method == 'esewa':
            # Initialize eSewa payment
            esewa = EsewaPaymentGateway()
            payment_data = esewa.generate_payment_data(order)
            
            context = {
                'order': order,
                'payment_data': payment_data,
                'payment_url': esewa.payment_url,
                'payment_method': 'esewa'
            }
            return render(request, "payment_form.html", context)
            
        elif payment_method == 'khalti':
            # Initialize Khalti payment
            khalti = KhaltiPaymentGateway()
            success, response = khalti.initiate_payment(order)
            
            if success:
                # Redirect to Khalti payment page
                return redirect(response['payment_url'])
            else:
                messages.error(request, f"Khalti payment initiation failed: {response}")
                return redirect('order_checkout', order_id=order_id)
    
    return render(request, "order_checkout.html", {"order": order})


def order_success(request, order_id):
    """Display order success page"""
    order = get_object_or_404(Order, id=order_id)
    return render(request, "order_success.html", {"order": order})


def esewa_success(request):
    """Handle eSewa payment success callback"""
    esewa = EsewaPaymentGateway()
    success, message = esewa.verify_payment(request)
    
    if success:
        oid = request.GET.get('oid')
        try:
            order = Order.objects.get(order_id=oid)
            messages.success(request, "Payment completed successfully!")
            return redirect('order_success', order_id=order.id)
        except Order.DoesNotExist:
            messages.error(request, "Order not found")
            return redirect('order_list')
    else:
        messages.error(request, f"Payment verification failed: {message}")
        return redirect('order_list')


def esewa_failure(request):
    """Handle eSewa payment failure callback"""
    messages.error(request, "Payment was cancelled or failed. Please try again.")
    return redirect('order_list')


def khalti_success(request):
    """Handle Khalti payment success callback"""
    pidx = request.GET.get('pidx')
    
    if not pidx:
        messages.error(request, "Invalid payment session")
        return redirect('order_list')
    
    khalti = KhaltiPaymentGateway()
    success, response = khalti.verify_payment(pidx)
    
    if success:
        order_id = response.get('purchase_order_id')
        try:
            order = Order.objects.get(order_id=order_id)
            messages.success(request, "Payment completed successfully!")
            return redirect('order_success', order_id=order.id)
        except Order.DoesNotExist:
            messages.error(request, "Order not found")
            return redirect('order_list')
    else:
        messages.error(request, f"Payment verification failed: {response}")
        return redirect('order_list')


def khalti_failure(request):
    """Handle Khalti payment failure callback"""
    messages.error(request, "Payment was cancelled or failed. Please try again.")
    return redirect('order_list')


@csrf_exempt
def khalti_webhook(request):
    """Handle Khalti webhook notifications"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Process webhook data
            # This is for additional verification and logging
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


# API Views for AJAX requests
class PaymentStatusView(View):
    """API endpoint to check payment status"""
    
    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
            return JsonResponse({
                'status': 'success',
                'is_paid': order.is_paid,
                'payment_method': order.payment_method,
                'transaction_id': order.transaction_id
            })
        except Order.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Order not found'})


def create_test_order(request):
    """Create a test order for demonstration"""
    if request.method == 'POST':
        name = request.POST.get('name', 'Test Customer')
        amount = request.POST.get('amount', 1000)
        
        order = Order.objects.create(
            name=name,
            total_price=int(amount)
        )
        
        messages.success(request, f"Test order created: {order.order_id}")
        return redirect('order_checkout', order_id=order.id)
    
    return render(request, "create_test_order.html")
