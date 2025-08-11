from django.db import models
import uuid
from django.core.validators import EmailValidator

# Create your models here.
class Order(models.Model):
    """Enhanced Order model for production"""
    name = models.CharField(max_length=100)
    order_id = models.CharField(max_length=20, null=True, unique=True)
    email = models.EmailField(validators=[EmailValidator()], blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    total_price = models.IntegerField()
    is_paid = models.BooleanField(default=False)
    paid_amount = models.IntegerField(null=True, blank=True)
    payment_method = models.CharField(max_length=20, null=True, blank=True)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional production fields
    currency = models.CharField(max_length=3, default='NPR')
    status = models.CharField(
        max_length=20, 
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('paid', 'Paid'),
            ('failed', 'Failed'),
            ('cancelled', 'Cancelled'),
            ('refunded', 'Refunded')
        ],
        default='pending'
    )

    class Meta:
        ordering = ['-created_at']
    
    # search field
    search_fields = ['name', 'order_id', 'is_paid', 'email', 'phone']
    
    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = str(uuid.uuid4())[:8].upper()
        
        # Auto-update status based on payment
        if self.is_paid and self.status == 'pending':
            self.status = 'paid'
        elif not self.is_paid and self.status == 'paid':
            self.status = 'pending'
            
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} - {self.order_id} - Rs.{self.total_price}"


class PaymentLog(models.Model):
    """Enhanced payment log model for production audit trail"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payment_logs')
    payment_method = models.CharField(max_length=20)
    transaction_id = models.CharField(max_length=100)
    amount = models.IntegerField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('initiated', 'Initiated'),
            ('processing', 'Processing'),
            ('success', 'Success'),
            ('failed', 'Failed'),
            ('cancelled', 'Cancelled'),
            ('refunded', 'Refunded')
        ]
    )
    gateway_response = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Additional production fields
    currency = models.CharField(max_length=3, default='NPR')
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    gateway_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.order.order_id} - {self.payment_method} - {self.status}"
    
    class Meta:
        ordering = ['-created_at']