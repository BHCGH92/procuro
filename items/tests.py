from django.test import TestCase
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from .models import Item, Category
from suppliers.models import Supplier

class ItemModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Fasteners")
        self.supplier = Supplier.objects.create(supplier_name="Bolt Supply Co")

    def test_item_string_representation(self):
        """Verify the [CODE] Name format."""
        item = Item.objects.create(
            item_code="B-001",
            name="M8 Bolt",
            category=self.category,
            supplier=self.supplier,
            price=1.50,
            internal_value=0.75
        )
        self.assertEqual(str(item), "[B-001] M8 Bolt")

    def test_duplicate_item_code_fails(self):
        """Verify that item codes must be unique."""
        Item.objects.create(
            item_code="UNIQUE-1", name="Item 1", 
            category=self.category, supplier=self.supplier, 
            price=1.0, internal_value=0.5
        )
        with self.assertRaises(IntegrityError):
            Item.objects.create(
                item_code="UNIQUE-1", name="Item 2", 
                category=self.category, supplier=self.supplier, 
                price=2.0, internal_value=1.0
            )

    def test_price_validation(self):
        """Ensure price cannot be negative"""
        item = Item(
            item_code="NEG-1", name="Bad Price", 
            category=self.category, supplier=self.supplier, 
            price=-5.00, internal_value=2.00
        )
        with self.assertRaises(ValidationError):
            item.full_clean()