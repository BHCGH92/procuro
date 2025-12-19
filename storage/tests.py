from django.test import TestCase
from django.db.utils import IntegrityError
from django.db import transaction
from django.core.exceptions import ValidationError
import uuid
from storage.models import Location, SubLocation, Area, SubArea
from inventory.models import Inventory
from items.models import Item, Category
from suppliers.models import Supplier 

# <--- Location Tests --->

class LocationModelTest(TestCase):
    
    def setUp(self):
        self.initial_count = Location.objects.count()
        self.location_1 = Location.objects.create(name="Warehouse A")

    def test_location_attributes(self):
        """Test basic creation, UUID, and name retrieval."""
        self.assertEqual(Location.objects.count(), self.initial_count + 1)
        self.assertIsInstance(self.location_1.id, uuid.UUID)
        self.assertEqual(self.location_1.name, "Warehouse A")
        self.assertEqual(str(self.location_1), "Warehouse A")

    def test_location_name_uniqueness(self):
        """Test that duplicate location names raise IntegrityError."""
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Location.objects.create(name="Warehouse A")
        
        self.assertEqual(Location.objects.count(), self.initial_count + 1)

    def test_location_cascading_delete(self):
        """Test that deleting a Location deletes related SubLocations."""
        sub_initial = SubLocation.objects.count()
        subloc = SubLocation.objects.create(name="Basement", location=self.location_1)
        self.assertEqual(SubLocation.objects.count(), sub_initial + 1)
        self.location_1.delete()
        self.assertEqual(Location.objects.count(), self.initial_count)
        self.assertEqual(SubLocation.objects.count(), sub_initial)

# <--- Sub Location Tests --->

class SubLocationModelTest(TestCase):
    
    def setUp(self):
        self.initial_count = SubLocation.objects.count()
        self.location_a = Location.objects.create(name="Warehouse Alpha")
        self.location_b = Location.objects.create(name="Warehouse Beta")
        
        self.subloc_a_1 = SubLocation.objects.create(name="Ground Floor", location=self.location_a)
        self.subloc_b_1 = SubLocation.objects.create(name="Ground Floor", location=self.location_b)

    def test_sublocation_attributes(self):
        self.assertEqual(SubLocation.objects.count(), self.initial_count + 2)
        self.assertEqual(str(self.subloc_a_1), "Warehouse Alpha - Ground Floor")

    def test_unique_together_constraint_passes(self):
        """Test same name under DIFFERENT Location is allowed."""
        SubLocation.objects.create(name="First Floor", location=self.location_a)
        self.assertEqual(SubLocation.objects.count(), self.initial_count + 3)

# <--- Area Tests --->

class AreaModelTest(TestCase):
    
    def setUp(self):
        self.initial_count = Area.objects.count()
        self.loc = Location.objects.create(name="W-Alpha")
        self.subloc = SubLocation.objects.create(name="G-Floor", location=self.loc)
        
        self.area_1 = Area.objects.create(name="Aisle 1", sub_location=self.subloc)
        self.area_2 = Area.objects.create(name="Aisle 2", sub_location=self.subloc)

    def test_area_attributes(self):
        self.assertEqual(Area.objects.count(), self.initial_count + 2)
        self.assertEqual(str(self.area_1), "G-Floor - Aisle 1")

# <--- SubArea Tests --->

class SubAreaModelTest(TestCase):
    
    def setUp(self):
        self.initial_count = SubArea.objects.count()
        self.loc = Location.objects.create(name="Central")
        self.sub = SubLocation.objects.create(name="Floor 1", location=self.loc)
        self.area = Area.objects.create(name="Rack A", sub_location=self.sub)
        
        self.subarea_1 = SubArea.objects.create(name="Shelf 1", area=self.area)

    def test_subarea_attributes(self):
        self.assertEqual(SubArea.objects.count(), self.initial_count + 1)
        self.assertEqual(str(self.subarea_1), "Rack A - Shelf 1")

# <--- Inventory (replacing old Storage) Tests --->

class InventoryModelTest(TestCase):
    
    def setUp(self):
        # Create dependencies
        self.cat = Category.objects.create(name="Hardware")
        self.sup = Supplier.objects.create(supplier_name="Generic Supplier")
        self.item = Item.objects.create(
            item_code="TEST-01", 
            name="Bolt", 
            category=self.cat, 
            supplier=self.sup,
            price=1.00,
            internal_value=0.50
        )
        
        self.loc = Location.objects.create(name="Storehouse")
        self.subloc = SubLocation.objects.create(name="Zone 1", location=self.loc)
        self.area = Area.objects.create(name="Bin A", sub_location=self.subloc)
        self.subarea = SubArea.objects.create(name="Slot 1", area=self.area)
        
        self.inventory_item = Inventory.objects.create(
            item=self.item,
            location=self.subarea,
            quantity=100
        )
        
    def test_inventory_creation_and_linkage(self):
        """Test linkage to Item and SubArea."""
        self.assertEqual(Inventory.objects.count(), 1)
        self.assertEqual(self.inventory_item.item.name, "Bolt")
        self.assertEqual(self.inventory_item.location, self.subarea)

    def test_on_delete_protect_constraint(self):
        """Verify we cannot delete a SubArea if it contains Inventory."""
        with self.assertRaises(IntegrityError):
            self.subarea.delete() 

    def test_get_full_location_display(self):
        """Verify the full breadcrumb path logic (Location > SubLoc > Area > SubArea)."""
        expected_path = "Storehouse > Zone 1 > Bin A > Slot 1"
        actual_path = self.inventory_item.location.get_full_location_display()
        self.assertEqual(actual_path, expected_path)