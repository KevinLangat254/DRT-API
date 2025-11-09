from django.urls import path
from .views import (
    CustomLoginView, RegisterView, HomeView, web_logout, dashboard,
    ReceiptCreateView, ReceiptDetailView, ReceiptUpdateView, ReceiptDeleteView
)

urlpatterns = [
    # Web interface endpoints
    path('', HomeView, name='index'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', web_logout, name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('dashboard/', dashboard, name='dashboard'),
    
    # Receipt management
    path('receipts/create/', ReceiptCreateView.as_view(), name='receipt_create'),
    path('receipts/<int:pk>/', ReceiptDetailView.as_view(), name='receipt_detail'),
    path('receipts/<int:pk>/edit/', ReceiptUpdateView.as_view(), name='receipt_update'),
    path('receipts/<int:pk>/delete/', ReceiptDeleteView.as_view(), name='receipt_delete'),
]
