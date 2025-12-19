from django.db import models
from django.core.validators import MinValueValidator
import uuid

class Inventory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    item = models.ForeignKey('items.Item', on_delete=models.CASCADE)
    
    location = models.ForeignKey(
        'storage.SubArea', 
        on_delete=models.PROTECT,
        default='e60f4cc5-800a-4cd1-83a4-77dd360becfc'
    )

    quantity = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('item', 'location')
        verbose_name_plural = "Inventories"
        verbose_name = "Inventory"

    def __str__(self):
        return f"{self.item.name} at {self.location.name}"