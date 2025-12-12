from django.contrib import admin
from .models import Supplier, PaymentMethod

# Register your models here.

class SupplierAdmin(admin.ModelAdmin):
    list_display = (
        'supplier_name', 
        'contact_number', 
        'email', 
        'supplier_status', 
        'payment_method'
    )
    search_fields = (
        'supplier_name', 
        'email', 
        'main_contact'
    )
    list_filter = (
        'supplier_status', 
        'payment_method'
    )
    list_editable = (
        'supplier_status',
    )
    ordering = ('supplier_name',)
admin.site.register(Supplier, SupplierAdmin)