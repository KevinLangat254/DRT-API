from django.urls import path
from .views import (
    CustomLoginView,
    RegisterView,
    HomeView,
    web_logout,
    receipts,
    ReceiptCreateView,
    ReceiptDetailView,
    ReceiptUpdateView,
    ReceiptDeleteView,
    BudgetListView,
    BudgetCreateView,
    BudgetUpdateView,
    BudgetDeleteView,
    NotificationListView,
    MarkAllNotificationsRead as MarkAll,
    MarkNotificationRead as MarkRead,
)

urlpatterns = [
    # Web interface endpoints
    path('', HomeView, name='index'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', web_logout, name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('receipts/', receipts, name='receipts'),
    
    # Receipt management
    path('receipts/create/', ReceiptCreateView.as_view(), name='receipt_create'),
    path('receipts/<int:pk>/', ReceiptDetailView.as_view(), name='receipt_detail'),
    path('receipts/<int:pk>/edit/', ReceiptUpdateView.as_view(), name='receipt_update'),
    path('receipts/<int:pk>/delete/', ReceiptDeleteView.as_view(), name='receipt_delete'),

    # Budget management
    path('budgets/', BudgetListView.as_view(), name='budget_list'),
    path('budgets/create/', BudgetCreateView.as_view(), name='budget_create'),
    path('budgets/<int:pk>/edit/', BudgetUpdateView.as_view(), name='budget_update'),
    path('budgets/<int:pk>/delete/', BudgetDeleteView.as_view(), name='budget_delete'),

    # Notifications
    path('notifications/', NotificationListView.as_view(), name='notifications'),
    path('notifications/<int:pk>/read/', MarkRead, name='mark_notification_read'),
    path('notifications/read_all/', MarkAll, name='mark_all_read'),
]
