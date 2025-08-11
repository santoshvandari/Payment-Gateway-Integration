from django.db import models
import uuid

# Create your models here.
class Order(models.Model):
    name = models.CharField(max_length=50)
    order_id = models.CharField(max_length=20, null=True, unique=True)
    total_price = models.IntegerField()
    is_paid = models.BooleanField(default=False)
    paid_amount = models.IntegerField(null=True, blank=True)
    payment_method = models.CharField(max_length=20, null=True, blank=True)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
    
    # search field
    search_fields = ['name', 'order_id', 'is_paid']
    
    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} - {self.order_id}"


class PaymentLog(models.Model):
    """Model to store payment transaction logs"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payment_logs')
    payment_method = models.CharField(max_length=20)
    transaction_id = models.CharField(max_length=100)
    amount = models.IntegerField()
    status = models.CharField(max_length=20)
    gateway_response = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.order.order_id} - {self.payment_method} - {self.status}"