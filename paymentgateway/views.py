from django.shortcuts import render
from models import Order
# Create your views here.

def order_list(request):
    orders = Order.objects.all()
    return render(request, "order.html", {"orders": orders})

def order_checkout(request, order_id):
    if request.method == "POST":
        #  <!--  This Form redirects us to esewa to carry out payment process  -->
        # <form action="https://uat.esewa.com.np/epay/main" method="POST">
        #     <input value="10" name="tAmt" type="hidden">
        #     <input value="10" name="amt" type="hidden">
        #     <input value="0" name="txAmt" type="hidden">
        #     <input value="0" name="psc" type="hidden">
        #     <input value="0" name="pdc" type="hidden">
        #     <input value="EPAYTEST" name="scd" type="hidden">
        #     <input value="{{order.order_id}}" name="pid" type="hidden">
        #     <input value="http://127.0.0.1:8000/esewa-callback/" type="hidden" name="su">
        #     <input value="http://127.0.0.1:8000/payment-failed/" type="hidden" name="fu">
        #     <input value="Pay With Esewa" type="submit" class="btn btn-success"> 
        #     </form>
        amount = request.POST.get('amount')
        

 
    order = Order.objects.get(id=order_id)
    return render(request, "order_checkout.html", {"order": order})

def order_success(request, order_id):
    order = Order.objects.get(id=order_id)
    order.is_paid = True
    order.save()
    return render(request, "order_success.html", {"order": order})
