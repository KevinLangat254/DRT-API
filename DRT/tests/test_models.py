from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta

from DRT.models import (
    Category,
    PaymentMethod,
    Receipt,
    ReceiptItem,
    ReceiptPayment,
    Tag,
    ReceiptTag,
    Budget,
)


@override_settings(DATABASES={
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
})
class ModelValidationTests(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(username="tester", password="strongpass123")
        self.category = Category.objects.create(name="Groceries")
        self.method = PaymentMethod.objects.create(name="Cash", is_digital=False)

    def test_receipt_positive_amount_and_not_future_date(self):
        receipt = Receipt(
            user=self.user,
            category=self.category,
            store_name="Store A",
            total_amount=Decimal("100.00"),
            currency="KES",
            purchase_date=date.today(),
        )
        receipt.save()
        self.assertIsNotNone(receipt.id)

    def test_receipt_invalid_negative_amount(self):
        receipt = Receipt(
            user=self.user,
            store_name="Store B",
            total_amount=Decimal("-5.00"),
            currency="KES",
            purchase_date=date.today(),
        )
        with self.assertRaisesMessage(Exception, "Amount must be greater than zero"):
            receipt.save()

    def test_receipt_invalid_future_date(self):
        tomorrow = date.today() + timedelta(days=1)
        receipt = Receipt(
            user=self.user,
            store_name="Store C",
            total_amount=Decimal("10.00"),
            currency="KES",
            purchase_date=tomorrow,
        )
        with self.assertRaisesMessage(Exception, "Purchase date cannot be in the future"):
            receipt.save()

    def test_receipt_item_validation(self):
        receipt = Receipt.objects.create(
            user=self.user,
            category=self.category,
            store_name="Store A",
            total_amount=Decimal("100.00"),
            currency="KES",
            purchase_date=date.today(),
        )
        # valid
        item = ReceiptItem(
            receipt=receipt,
            item_name="Milk",
            quantity=2,
            unit_price=Decimal("5.00"),
            total_price=Decimal("10.00"),
        )
        item.save()
        self.assertIsNotNone(item.id)

        # invalid mismatch
        bad_item = ReceiptItem(
            receipt=receipt,
            item_name="Bread",
            quantity=1,
            unit_price=Decimal("5.00"),
            total_price=Decimal("9.00"),
        )
        with self.assertRaisesMessage(Exception, "Total price should equal quantity multiplied by unit price"):
            bad_item.save()

    def test_receipt_payment_validation(self):
        receipt = Receipt.objects.create(
            user=self.user,
            category=self.category,
            store_name="Store A",
            total_amount=Decimal("100.00"),
            currency="KES",
            purchase_date=date.today(),
        )
        payment = ReceiptPayment(
            receipt=receipt,
            payment_method=self.method,
            amount_paid=Decimal("25.00"),
            paid_at=timezone.now() - timedelta(days=1),
        )
        payment.save()
        self.assertIsNotNone(payment.id)

        future = timezone.now() + timedelta(days=1)
        bad_payment = ReceiptPayment(
            receipt=receipt,
            payment_method=self.method,
            amount_paid=Decimal("10.00"),
            paid_at=future,
        )
        with self.assertRaisesMessage(Exception, "Payment date cannot be in the future"):
            bad_payment.save()

    def test_tag_and_receipt_tag_unique(self):
        tag = Tag.objects.create(name="Work")
        receipt = Receipt.objects.create(
            user=self.user,
            category=self.category,
            store_name="Store A",
            total_amount=Decimal("100.00"),
            currency="KES",
            purchase_date=date.today(),
        )
        ReceiptTag.objects.create(receipt=receipt, tag=tag)
        with self.assertRaises(Exception):
            ReceiptTag.objects.create(receipt=receipt, tag=tag)

    def test_budget_constraints(self):
        start = date.today() + timedelta(days=1)
        end = start + timedelta(days=30)
        budget = Budget(
            user=self.user,
            category=self.category,
            amount_limit=Decimal("500.00"),
            period_start=start,
            period_end=end,
        )
        budget.save()
        self.assertIsNotNone(budget.id)

        # start in the past should fail
        past_start = date.today() - timedelta(days=1)
        bad_budget = Budget(
            user=self.user,
            category=self.category,
            amount_limit=Decimal("500.00"),
            period_start=past_start,
            period_end=end,
        )
        with self.assertRaisesMessage(Exception, "Period start date cannot be in the past"):
            bad_budget.save()


