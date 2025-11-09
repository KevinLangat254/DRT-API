from .receipts import ReceiptViewSet
from .users import UserViewSet
from .auth import RegisterAPIView, LoginAPIView, LogoutAPIView, web_logout
from .web import (
    CustomLoginView, RegisterView, HomeView, dashboard,
    ReceiptCreateView, ReceiptDetailView, ReceiptUpdateView, ReceiptDeleteView
)


