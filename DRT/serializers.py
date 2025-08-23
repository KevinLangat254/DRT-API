from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
from .models import (
    Category,
    PaymentMethod,
    Receipt,
    Tag,
    ReceiptTag,
    Budget,
    ReceiptPayment,
    ReceiptItem
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = "__all__"


class ReceiptItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceiptItem
        fields = "__all__"
    
    def validate_quantity(self, value):
        """Validate quantity is positive."""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value
    
    def validate_unit_price(self, value):
        """Validate unit price is positive."""
        if value <= Decimal('0'):
            raise serializers.ValidationError("Unit price must be greater than zero.")
        return value
    
    def validate_total_price(self, value):
        """Validate total price is positive."""
        if value <= Decimal('0'):
            raise serializers.ValidationError("Total price must be greater than zero.")
        return value
    
    def validate(self, data):
        """Validate that total_price matches quantity * unit_price."""
        quantity = data.get('quantity')
        unit_price = data.get('unit_price')
        total_price = data.get('total_price')
        
        if quantity and unit_price and total_price:
            expected_total = quantity * unit_price
            if total_price != expected_total:
                raise serializers.ValidationError({
                    'total_price': f'Total price should be {expected_total} (quantity × unit price)'
                })
        
        return data


class ReceiptPaymentSerializer(serializers.ModelSerializer):
    payment_method_name = serializers.CharField(
        source="payment_method.name", read_only=True
    )

    class Meta:
        model = ReceiptPayment
        fields = "__all__"
    
    def validate_amount_paid(self, value):
        """Validate payment amount is positive."""
        if value <= Decimal('0'):
            raise serializers.ValidationError("Payment amount must be greater than zero.")
        return value
    
    def validate_paid_at(self, value):
        """Validate payment date is not in the future."""
        if value and value > timezone.now():
            raise serializers.ValidationError("Payment date cannot be in the future.")
        return value


class ReceiptSerializer(serializers.ModelSerializer):
    # Nested serializers for related objects
    items = ReceiptItemSerializer(many=True, read_only=True)
    payments = ReceiptPaymentSerializer(many=True, read_only=True)

    category_name = serializers.CharField(source="category.name", read_only=True)
    user_username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Receipt
        fields = "__all__"
    
    def validate_total_amount(self, value):
        """Validate receipt amount is positive."""
        if value <= Decimal('0'):
            raise serializers.ValidationError("Receipt amount must be greater than zero.")
        return value
    
    def validate_purchase_date(self, value):
        """Validate purchase date is not in the future."""
        if value and value > timezone.now().date():
            raise serializers.ValidationError("Purchase date cannot be in the future.")
        return value


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class ReceiptTagSerializer(serializers.ModelSerializer):
    receipt_info = serializers.StringRelatedField(source="receipt", read_only=True)
    tag_name = serializers.CharField(source="tag.name", read_only=True)

    class Meta:
        model = ReceiptTag
        fields = "__all__"


class BudgetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    user_username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Budget
        fields = "__all__"
    
    def validate_amount_limit(self, value):
        """Validate budget amount is positive."""
        if value <= Decimal('0'):
            raise serializers.ValidationError("Budget amount must be greater than zero.")
        return value
    
    def validate_period_start(self, value):
        """Validate period start date is not in the past."""
        if value and value < timezone.now().date():
            raise serializers.ValidationError("Period start date cannot be in the past.")
        return value
