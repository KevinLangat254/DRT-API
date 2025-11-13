from .receipts import ReceiptViewSet
from .users import UserViewSet
from .auth import RegisterAPIView, LoginAPIView, LogoutAPIView, web_logout
from .web import (
    CustomLoginView,
    RegisterView,
    HomeView,
    receipts,
    ReceiptCreateView,
    ReceiptDetailView,
    ReceiptUpdateView,
    ReceiptDeleteView,
    BudgetListView,
    BudgetCreateView,
    BudgetUpdateView,
    BudgetDeleteView,
)


