from rest_framework import serializers
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


class ReceiptPaymentSerializer(serializers.ModelSerializer):
    payment_method_name = serializers.CharField(
        source="payment_method.name", read_only=True
    )

    class Meta:
        model = ReceiptPayment
        fields = "__all__"


class ReceiptSerializer(serializers.ModelSerializer):
    # Nested serializers for related objects
    items = ReceiptItemSerializer(many=True, read_only=True)
    payments = ReceiptPaymentSerializer(many=True, read_only=True)

    category_name = serializers.CharField(source="category.name", read_only=True)
    user_username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Receipt
        fields = "__all__"


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
