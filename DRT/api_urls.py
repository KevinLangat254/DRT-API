from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from .views import (
    UserViewSet, CategoryViewSet, PaymentMethodViewSet, ReceiptViewSet, TagViewSet,
    ReceiptTagViewSet, BudgetViewSet, ReceiptPaymentViewSet, ReceiptItemViewSet, RegisterAPIView, LogoutAPIView
)

# Create API router
api_router = DefaultRouter()

# Register ViewSets with proper API naming
api_router.register(r'users', UserViewSet, basename='user')
api_router.register(r'categories', CategoryViewSet, basename='category')
api_router.register(r'payment-methods', PaymentMethodViewSet, basename='payment-method')
api_router.register(r'receipts', ReceiptViewSet, basename='receipt')
api_router.register(r'tags', TagViewSet, basename='tag')
api_router.register(r'receipt-tags', ReceiptTagViewSet, basename='receipt-tag')
api_router.register(r'budgets', BudgetViewSet, basename='budget')
api_router.register(r'receipt-payments', ReceiptPaymentViewSet, basename='receipt-payment')
api_router.register(r'receipt-items', ReceiptItemViewSet, basename='receipt-item')

# API URL patterns
urlpatterns = [
    # Authentication endpoints
    path('auth/token/', obtain_auth_token, name='api_token_auth'),
    path('auth/register/', RegisterAPIView.as_view(), name='api_register'),
    path('auth/logout/', LogoutAPIView.as_view(), name='api_logout'),
    
    # API router endpoints
    path('', include(api_router.urls)),
]
