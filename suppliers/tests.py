from django.test import TestCase
from django.db import models
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from suppliers.models import Supplier, PaymentMethod
from django.db import transaction
import uuid

# <--- Model tests, record creations and validation checks -->

class SupplierModelTest(TestCase):

    def setUp(self):
        self.valid_supplier = Supplier.objects.create(
            supplier_name="Acme Inc.",
            email="acme@example.com",
            contact_number="01234 567890",
            main_contact="Wile E. Coyote",
            payment_method=PaymentMethod.CHEQUE
        )

    def test_supplier_attributes_and_defaults(self):
        """Test that the supplier created in setUp has correct attributes and checks UUID/defaults."""
        self.assertEqual(Supplier.objects.count(), 1)
        self.assertIsInstance(self.valid_supplier.id, uuid.UUID) 
        self.assertEqual(self.valid_supplier.supplier_name, "Acme Inc.")
        self.assertTrue(self.valid_supplier.supplier_status)
        self.assertEqual(self.valid_supplier.payment_method, PaymentMethod.CHEQUE)

    def test_duplicate_supplier_name_raises_error(self):
        """
        Test that attempting to create a second supplier with the same name
        results in an IntegrityError from the database.
        """
        initial_count = Supplier.objects.count()
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Supplier.objects.create(
                    supplier_name="Acme Inc.", 
                    email="a_different_email@example.com"
                )
        self.assertEqual(Supplier.objects.count(), initial_count)

    def test_duplicate_email_raises_error(self):
        """
        Test that attempting to create a second supplier with a duplicate unique email
        results in an IntegrityError from the database.
        """
        initial_count = Supplier.objects.count()

        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Supplier.objects.create(
                    supplier_name="Beta Corp Unique",
                    email="acme@example.com"
                )
        self.assertEqual(Supplier.objects.count(), initial_count)

    def test_multiple_null_emails_allowed(self):
        """
        Test that the model allows multiple suppliers to be saved with a NULL email,
        as defined by null=True on the unique email field.
        """
        Supplier.objects.create(
            supplier_name="Null Email Co 1", 
            email=None
        )
        Supplier.objects.create(
            supplier_name="Null Email Co 2", 
            email=None
        )
        self.assertEqual(Supplier.objects.count(), 3)

    def test_field_max_lengths(self):
        """
        Test that both supplier_name and contact_number respect their max_length 
        and raise ValidationError when exceeded.
        """
        valid_name = 'A' * 250 
        invalid_name = 'B' * 251 
        valid_supplier = Supplier(supplier_name=valid_name)
        valid_supplier.full_clean() 
        invalid_supplier = Supplier(supplier_name=invalid_name)
        
        with self.assertRaises(ValidationError) as cm:
            invalid_supplier.full_clean()
        
        self.assertIn('supplier_name', cm.exception.message_dict)

        # --- Test 2: contact_number (Max 20) ---

        invalid_contact = '1' * 21
        invalid_supplier_2 = Supplier(
            supplier_name="Valid Name",
            contact_number=invalid_contact
        )
        
        with self.assertRaises(ValidationError) as cm:
            invalid_supplier_2.full_clean()
            
        self.assertIn('contact_number', cm.exception.message_dict)