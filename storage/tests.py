from storage.models import Location, SubLocation, Area, SubArea, Storage
from django.test import TestCase
from django.db.utils import IntegrityError
from django.db import transaction
from django.core.exceptions import ValidationError
import uuid

# <--- Location Tests --->

class LocationModelTest(TestCase):
    
    def setUp(self):
        self.location_1 = Location.objects.create(name="Warehouse A")

    def test_location_attributes(self):
        """Test basic creation, UUID, and name retrieval."""
        self.assertEqual(Location.objects.count(), 1)
        self.assertIsInstance(self.location_1.id, uuid.UUID)
        self.assertEqual(self.location_1.name, "Warehouse A")
        self.assertEqual(str(self.location_1), "Warehouse A")

    def test_location_name_uniqueness(self):
        """
        Test that attempting to create a second location with the same name 
        results in an IntegrityError.
        """
        initial_count = Location.objects.count()

        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Location.objects.create(name="Warehouse A")
        
        self.assertEqual(Location.objects.count(), initial_count)

    def test_location_cascading_delete(self):
        """
        Test that deleting a Location correctly deletes all related 
        SubLocations (due to on_delete=CASCADE).
        """
        subloc = SubLocation.objects.create(name="Basement", location=self.location_1)
        self.assertEqual(SubLocation.objects.count(), 1)
        self.location_1.delete()
        self.assertEqual(Location.objects.count(), 0)
        self.assertEqual(SubLocation.objects.count(), 0)

# <--- Sub Location Tests --->

class SubLocationModelTest(TestCase):
    
    def setUp(self):
        self.location_a = Location.objects.create(name="Warehouse A")
        self.location_b = Location.objects.create(name="Warehouse B")
        
        self.subloc_a_1 = SubLocation.objects.create(
            name="Ground Floor",
            location=self.location_a
        )
        
        self.subloc_b_1 = SubLocation.objects.create(
            name="Ground Floor",
            location=self.location_b
        )

    def test_sublocation_attributes(self):
        """Test basic creation, UUID, and linkage to parent location."""
        self.assertEqual(SubLocation.objects.count(), 2)
        self.assertIsInstance(self.subloc_a_1.id, uuid.UUID)
        self.assertEqual(self.subloc_a_1.location, self.location_a)
        self.assertEqual(str(self.subloc_a_1), "Warehouse A - Ground Floor")

    def test_unique_together_constraint_fails(self):
        """
        Test that creating a SubLocation with a duplicate name under the 
        SAME Location raises an IntegrityError.
        """
        initial_count = SubLocation.objects.count()
        
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                SubLocation.objects.create(
                    name="Ground Floor",
                    location=self.location_a
                )
        
        self.assertEqual(SubLocation.objects.count(), initial_count)

    def test_unique_together_constraint_passes(self):
        """
        Test that creating a SubLocation with the same name under a 
        DIFFERENT Location is allowed.
        """
        self.assertEqual(SubLocation.objects.filter(name="Ground Floor").count(), 2)
        
        SubLocation.objects.create(
            name="First Floor",
            location=self.location_a
        )
        self.assertEqual(SubLocation.objects.count(), 3)

# <--- Area Tests --->

class AreaModelTest(TestCase):
    
    def setUp(self):
        self.location_a = Location.objects.create(name="Warehouse A")
        self.location_b = Location.objects.create(name="Warehouse B")
        
        self.subloc_a = SubLocation.objects.create(
            name="Ground Floor",
            location=self.location_a
        )
        self.subloc_b = SubLocation.objects.create(
            name="First Floor",
            location=self.location_b
        )
        
        self.area_a_1 = Area.objects.create(
            name="Aisle 1",
            sub_location=self.subloc_a
        )
        
        self.area_b_1 = Area.objects.create(
            name="Aisle 1",
            sub_location=self.subloc_b
        )

    def test_area_attributes(self):
        """Test basic creation, UUID, and linkage to parent SubLocation."""
        self.assertEqual(Area.objects.count(), 2)
        self.assertIsInstance(self.area_a_1.id, uuid.UUID)
        self.assertEqual(self.area_a_1.sub_location, self.subloc_a)
        expected_str = f"{self.subloc_a.name} - {self.area_a_1.name}"
        self.assertEqual(str(self.area_a_1), expected_str)

    def test_unique_together_constraint_fails(self):
        """
        Test that creating an Area with a duplicate name under the 
        SAME SubLocation raises an IntegrityError.
        """
        initial_count = Area.objects.count()
        
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Area.objects.create(
                    name="Aisle 1",
                    sub_location=self.subloc_a
                )

        self.assertEqual(Area.objects.count(), initial_count)

    def test_unique_together_constraint_passes(self):
        """
        Test that creating an Area with the same name under a 
        DIFFERENT SubLocation is allowed.
        """
        self.assertEqual(Area.objects.filter(name="Aisle 1").count(), 2)

        Area.objects.create(
            name="Aisle 2",
            sub_location=self.subloc_a
        )
        self.assertEqual(Area.objects.count(), 3)

# <--- SubArea Tests --->

class SubAreaModelTest(TestCase):
    
    def setUp(self):
        # Setup requires three levels deep: Location -> SubLocation -> Area
        self.location_a = Location.objects.create(name="Central")
        self.subloc_a = SubLocation.objects.create(name="Floor 1", location=self.location_a)
        self.area_1 = Area.objects.create(name="Rack A", sub_location=self.subloc_a)
        self.area_2 = Area.objects.create(name="Rack B", sub_location=self.subloc_a)
        
        self.subarea_1_a = SubArea.objects.create(
            name="Shelf 1",
            area=self.area_1
        )
        
        self.subarea_2_a = SubArea.objects.create(
            name="Shelf 1",
            area=self.area_2
        )

    def test_subarea_attributes(self):
        """Test basic creation, UUID, and linkage to parent Area."""
        self.assertEqual(SubArea.objects.count(), 2)
        self.assertIsInstance(self.subarea_1_a.id, uuid.UUID)
        self.assertEqual(self.subarea_1_a.area, self.area_1)
        expected_str = f"{self.area_1.name} - {self.subarea_1_a.name}"
        self.assertEqual(str(self.subarea_1_a), expected_str)

    def test_unique_together_constraint_fails(self):
        """
        Test that creating a SubArea with a duplicate name under the 
        SAME Area raises an IntegrityError.
        """
        initial_count = SubArea.objects.count()
        
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                SubArea.objects.create(
                    name="Shelf 1",
                    area=self.area_1 
                )
        
        self.assertEqual(SubArea.objects.count(), initial_count)
    
    def test_unique_together_constraint_passes(self):
        """
        Test that creating a SubArea with the same name under a 
        DIFFERENT Area is allowed.
        """
        self.assertEqual(SubArea.objects.filter(name="Shelf 1").count(), 2)
        
        SubArea.objects.create(
            name="Shelf 2",
            area=self.area_1
        )
        self.assertEqual(SubArea.objects.count(), 3)

# <--- Storage Tests --->

class StorageModelTest(TestCase):
    
    def setUp(self):
        self.loc = Location.objects.create(name="W1")
        self.subloc = SubLocation.objects.create(name="F1", location=self.loc)
        self.area = Area.objects.create(name="A1", sub_location=self.subloc)
        self.subarea = SubArea.objects.create(name="S1", area=self.area)
        self.item = Storage.objects.create(
            sub_area=self.subarea,
            item_description="Server Rack Component"
        )
        
    def test_storage_creation_and_linkage(self):
        """Test basic creation and linkage to SubArea."""
        self.assertEqual(Storage.objects.count(), 1)
        self.assertEqual(self.item.sub_area, self.subarea)
        self.assertIsInstance(self.item.id, uuid.UUID)

    def test_on_delete_protect_constraint(self):
        """
        Test that deleting a SubArea with an attached Storage item 
        is prevented by models.PROTECT.
        """
        initial_subarea_count = SubArea.objects.count()
        
        with self.assertRaises(IntegrityError):
            self.subarea.delete() 
            
        self.assertEqual(SubArea.objects.count(), initial_subarea_count)
        self.assertTrue(SubArea.objects.filter(pk=self.subarea.pk).exists())

    def test_item_description_max_length(self):
        """Test that item_description respects the max_length=250 constraint."""
        invalid_description = 'X' * 251 
        invalid_item = Storage(
            sub_area=self.subarea,
            item_description=invalid_description 
        )

        with self.assertRaises(ValidationError) as cm:
            invalid_item.full_clean()
        
        self.assertIn('item_description', cm.exception.message_dict)

    def test_get_full_location_display(self):
        """Test the custom method for displaying the full location path."""
        expected_path = "W1 > F1 > A1 > S1"
        self.assertEqual(self.item.get_full_location_display(), expected_path)