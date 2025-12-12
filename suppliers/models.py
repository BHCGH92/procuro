import uuid
from django.db import models

# Create your models here.

class PaymentMethod(models.TextChoices):
    BACS = 'BACS', 'BACS'
    BANK_TRANSFER = 'BANK TRANSFER', 'Bank Transfer'
    CASH = 'CASH', 'Cash'
    CHEQUE = 'CHEQUE', 'Cheque'

class Supplier(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    supplier_name = models.CharField(max_length=250, unique=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    supplier_status = models.BooleanField(default=True)
    main_contact = models.CharField(max_length=250, blank=True, null=True)
    payment_method = models.CharField(max_length=15, choices=PaymentMethod.choices, default=PaymentMethod.BANK_TRANSFER)
