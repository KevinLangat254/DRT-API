from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from ..models import (
    Category, PaymentMethod, Tag, ReceiptTag, Budget, ReceiptPayment, ReceiptItem
)
from ..serializers import (
    CategorySerializer, PaymentMethodSerializer, TagSerializer, ReceiptTagSerializer,
    BudgetSerializer, ReceiptPaymentSerializer, ReceiptItemSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']


class PaymentMethodViewSet(viewsets.ModelViewSet):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']


class ReceiptTagViewSet(viewsets.ModelViewSet):
    serializer_class = ReceiptTagSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['receipt', 'tag']
    ordering_fields = ['receipt', 'tag']

    def get_queryset(self):
        return ReceiptTag.objects.filter(receipt__user=self.request.user).select_related('receipt', 'tag')


class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['category', 'period_start', 'period_end']
    ordering_fields = ['period_start', 'period_end', 'amount_limit']
    ordering = ['-period_start']

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user).select_related('category')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ReceiptPaymentViewSet(viewsets.ModelViewSet):
    serializer_class = ReceiptPaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['payment_method', 'paid_at']
    ordering_fields = ['paid_at', 'amount_paid']
    ordering = ['-paid_at']

    def get_queryset(self):
        return ReceiptPayment.objects.filter(receipt__user=self.request.user).select_related('receipt', 'payment_method')

    def perform_create(self, serializer):
        receipt_id = self.request.data.get('receipt')
        if receipt_id:
            from ..models import Receipt
            receipt = Receipt.objects.filter(id=receipt_id, user=self.request.user).first()
            if not receipt:
                raise permissions.PermissionDenied("You can only create payments for your own receipts.")
        serializer.save()


class ReceiptItemViewSet(viewsets.ModelViewSet):
    serializer_class = ReceiptItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['receipt']
    ordering_fields = ['item_name', 'total_price']
    ordering = ['item_name']

    def get_queryset(self):
        return ReceiptItem.objects.filter(receipt__user=self.request.user).select_related('receipt')

    def perform_create(self, serializer):
        receipt_id = self.request.data.get('receipt')
        if receipt_id:
            from ..models import Receipt
            receipt = Receipt.objects.filter(id=receipt_id, user=self.request.user).first()
            if not receipt:
                raise permissions.PermissionDenied("You can only create items for your own receipts.")
        serializer.save()


