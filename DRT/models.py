from django.db import models
from django.conf import settings
from django.db.models import Q, F

# Alias for cleaner code
User = settings.AUTH_USER_MODEL


class Category(models.Model):
    """Expense category (e.g., Groceries, Utilities, Transport)."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class PaymentMethod(models.Model):
    """Payment method (e.g., Cash, Card, M-Pesa)."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_digital = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Receipt(models.Model):
    """A receipt recorded by a user."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receipts")
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="receipts"
    )
    store_name = models.CharField(max_length=255)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="KES")
    purchase_date = models.DateField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "purchase_date"]),
            models.Index(fields=["user", "category"]),
        ]
        ordering = ["-purchase_date", "-uploaded_at"]

    def __str__(self):
        return f"{self.store_name} - {self.total_amount} {self.currency}"


class ReceiptItem(models.Model):
    """Line items within a receipt."""
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, related_name="items")
    item_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        indexes = [models.Index(fields=["receipt"])]

    def __str__(self):
        return f"{self.item_name} x{self.quantity}"


class ReceiptPayment(models.Model):
    """
    Payments applied to a receipt.
    Keeps payment history and supports split payments across methods.
    """
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, related_name="payments")
    payment_method = models.ForeignKey(
        PaymentMethod, on_delete=models.SET_NULL, null=True, related_name="payments"
    )
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    paid_at = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=["receipt"]),
            models.Index(fields=["payment_method"]),
            models.Index(fields=["paid_at"]),
        ]

    def __str__(self):
        method = self.payment_method.name if self.payment_method else "Unknown"
        return f"{self.amount_paid} via {method} on {self.paid_at.date()}"


class Tag(models.Model):
    """User-defined tags like 'Work', 'Reimbursable'."""
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ReceiptTag(models.Model):
    """Many-to-many join between receipts and tags."""
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("receipt", "tag")
        indexes = [models.Index(fields=["receipt"]), models.Index(fields=["tag"])]

    def __str__(self):
        return f"{self.receipt_id}:{self.tag.name}"


class Budget(models.Model):
    """
    Budget for a user and category over a period.
    If your ERD requires category to be mandatory, keep null=False (default).
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="budgets")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="budgets")
    amount_limit = models.DecimalField(max_digits=10, decimal_places=2)
    period_start = models.DateField()
    period_end = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Ensure valid periods and prevent duplicate budgets for same user/category/period window
        constraints = [
            models.CheckConstraint(
                check=Q(period_end__gte=F("period_start")),
                name="budget_end_on_or_after_start",
            ),
        ]
        unique_together = ("user", "category", "period_start", "period_end")
        indexes = [
            models.Index(fields=["user", "period_start", "period_end"]),
            models.Index(fields=["user", "category"]),
        ]
        ordering = ["-period_start"]

    def __str__(self):
        return f"{self.user} • {self.category.name} • {self.period_start} → {self.period_end}"
