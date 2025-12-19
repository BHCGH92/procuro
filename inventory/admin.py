from django.contrib import admin
from .models import Inventory
from items.models import Item, Category

admin.site.register(Category)

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('item_code', 'name', 'category', 'supplier', 'price', 'internal_value')
    list_filter = ('category', 'supplier')
    search_fields = ('item_code', 'name')

class InventoryAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'quantity', 'full_location_path')
    search_fields = ('item__name', 'item__item_code')
    list_filter = ('location__area__sub_location__location',)

    def item_name(self, obj):
        return obj.item.name
    item_name.short_description = 'Item Name'

    def full_location_path(self, obj):
        return obj.location.get_full_location_display()
    full_location_path.short_description = 'Exact Location'

admin.site.register(Inventory, InventoryAdmin)