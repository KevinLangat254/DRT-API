from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, PaymentMethodViewSet, ReceiptViewSet, TagViewSet,
    ReceiptTagViewSet, BudgetViewSet, ReceiptPaymentViewSet, ReceiptItemViewSet
)
from rest_framework.authtoken.views import obtain_auth_token

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'payment-methods', PaymentMethodViewSet)
router.register(r'receipts', ReceiptViewSet)
router.register(r'tags', TagViewSet)
router.register(r'receipt-tags', ReceiptTagViewSet)
router.register(r'budgets', BudgetViewSet)
router.register(r'receipt-payments', ReceiptPaymentViewSet)
router.register(r'receipt-items', ReceiptItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api/token/', obtain_auth_token, name='api_token_auth'),
]
