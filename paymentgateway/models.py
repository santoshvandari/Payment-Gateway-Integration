from django.db import models

# Create your models here.
class Order(models.Model):
    name = models.CharField(max_length=50)
    order_id = models.CharField(max_length=6, null=True, unique=True)
    total_price = models.IntegerField()
    is_paid = models.BooleanField(default=False)
    paid_amount = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
    # search field
    search_fields = ['name', 'order_id', 'is_paid']
    def __str__(self):
        return self.name