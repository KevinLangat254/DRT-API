from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, PaymentMethodViewSet, ReceiptViewSet, TagViewSet,
    ReceiptTagViewSet, BudgetViewSet, ReceiptPaymentViewSet, ReceiptItemViewSet,
    CustomLoginView, CustomLogoutView, RegisterView, HomeView
)
from rest_framework.authtoken.views import obtain_auth_token


router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'payment-methods', PaymentMethodViewSet)
router.register(r'receipts', ReceiptViewSet, basename='receipt')
router.register(r'tags', TagViewSet)
router.register(r'receipt-tags', ReceiptTagViewSet, basename='receipt-tag')
router.register(r'budgets', BudgetViewSet, basename='budget')
router.register(r'receipt-payments', ReceiptPaymentViewSet, basename='receipt-payment')
router.register(r'receipt-items', ReceiptItemViewSet, basename='receipt-item')

urlpatterns = [
    path('', HomeView, name='index'),
    path('', include(router.urls)),
    path('api/token/', obtain_auth_token, name='api_token_auth'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    
]
