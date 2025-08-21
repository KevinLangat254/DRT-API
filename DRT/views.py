from rest_framework import viewsets
from .models import (
    Category, PaymentMethod, Receipt, Tag, ReceiptTag,
    Budget, ReceiptPayment, ReceiptItem
)
from .serializers import (
    CategorySerializer, PaymentMethodSerializer, ReceiptSerializer, TagSerializer,
    ReceiptTagSerializer, BudgetSerializer, ReceiptPaymentSerializer, ReceiptItemSerializer
)
from django.contrib.auth.views import LoginView, LogoutView
from .forms import LoginForm, RegistrationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.conf import settings
from django.shortcuts import render

User = settings.AUTH_USER_MODEL

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

# Custom Login View to use the LoginForm
class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True  # If already logged in, redirect

# Custom Logout View to redirect after logout
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("login")  # Where to redirect after logout

# Registration View    
class RegisterView(CreateView):
    model = User
    form_class = RegistrationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("login")  # Redirect to login after sign-

def HomeView(request):
    
    return render(request, "index.html")  # Ensure you have a home.html template    