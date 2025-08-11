from django.contrib import admin
from .models import Order, PaymentLog

# Register your models here.

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'name', 'total_price', 'is_paid', 'payment_method', 'created_at']
    list_filter = ['is_paid', 'payment_method', 'created_at']
    search_fields = ['name', 'order_id']
    readonly_fields = ['order_id', 'created_at', 'updated_at']


@admin.register(PaymentLog)
class PaymentLogAdmin(admin.ModelAdmin):
    list_display = ['order', 'payment_method', 'transaction_id', 'amount', 'status', 'created_at']
    list_filter = ['payment_method', 'status', 'created_at']
    search_fields = ['order__order_id', 'transaction_id']
    readonly_fields = ['created_at']
