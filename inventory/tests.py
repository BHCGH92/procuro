from django.test import TestCase
from django.core.exceptions import ValidationError

# Cross-app imports
from items.models import Item, Category
from suppliers.models import Supplier
from storage.models import Location, SubLocation, Area, SubArea

# Local app import
from .models import Inventory

class InventoryModelTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(name="Electronics")
        self.supplier = Supplier.objects.create(supplier_name="Global Tech")
        
        self.item = Item.objects.create(
            item_code="T-100",
            name="Test Item",
            category=self.category,
            supplier=self.supplier,
            price=10.00,
            internal_value=5.00
        )

        self.location = Location.objects.create(name="Warehouse A")
        self.subloc = SubLocation.objects.create(name="Zone 1", location=self.location)
        self.area = Area.objects.create(name="Rack 1", sub_location=self.subloc)
        self.subarea = SubArea.objects.create(name="Shelf 1", area=self.area)

        self.inventory_item = Inventory.objects.create(
            item=self.item,
            location=self.subarea,
            quantity=10
        )

    def test_inventory_creation(self):
        """Test that inventory links correctly to items and stores quantity."""
        self.assertEqual(self.inventory_item.item.name, "Test Item")
        self.assertEqual(self.inventory_item.quantity, 10)
        self.assertIn("Test Item", str(self.inventory_item))

    def test_negative_quantity_validation(self):
        """Test that the PositiveIntegerField/Validator prevents negative stock."""
        self.inventory_item.quantity = -1
        with self.assertRaises(ValidationError):
            self.inventory_item.full_clean()

    def test_cascade_delete_item(self):
        """Test that deleting the Item also removes its Inventory records."""
        self.item.delete()
        self.assertEqual(Inventory.objects.count(), 0)