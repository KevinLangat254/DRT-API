from rest_framework import viewsets
from .models import (
    Category, PaymentMethod, Receipt, Tag, ReceiptTag,
    Budget, ReceiptPayment, ReceiptItem
)
from .serializers import (
    CategorySerializer, PaymentMethodSerializer, ReceiptSerializer, TagSerializer,
    ReceiptTagSerializer, BudgetSerializer, ReceiptPaymentSerializer, ReceiptItemSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class PaymentMethodViewSet(viewsets.ModelViewSet):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer


class ReceiptViewSet(viewsets.ModelViewSet):
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class ReceiptTagViewSet(viewsets.ModelViewSet):
    queryset = ReceiptTag.objects.all()
    serializer_class = ReceiptTagSerializer


class BudgetViewSet(viewsets.ModelViewSet):
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer


class ReceiptPaymentViewSet(viewsets.ModelViewSet):
    queryset = ReceiptPayment.objects.all()
    serializer_class = ReceiptPaymentSerializer


class ReceiptItemViewSet(viewsets.ModelViewSet):
    queryset = ReceiptItem.objects.all()
    serializer_class = ReceiptItemSerializer
