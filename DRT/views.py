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
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

User = get_user_model()


# User = settings.AUTH_USER_MODEL

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


class BudgetViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user budgets. Users can only access their own budgets."""
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['category', 'period_start', 'period_end']
    ordering_fields = ['period_start', 'period_end', 'amount_limit']
    ordering = ['-period_start']

    def get_queryset(self):
        """Filter budgets to only show current user's budgets."""
        return Budget.objects.filter(user=self.request.user).select_related(
            'category'
        )

    def perform_create(self, serializer):
        """Automatically assign the current user when creating a budget."""
        serializer.save(user=self.request.user)
    
    def perform_update(self, serializer):
        """Ensure users can only update their own budgets."""
        budget = self.get_object()
        if budget.user != self.request.user:
            raise permissions.PermissionDenied("You can only update your own budgets.")
        serializer.save()
    
    def perform_destroy(self, instance):
        """Ensure users can only delete their own budgets."""
        if instance.user != self.request.user:
            raise permissions.PermissionDenied("You can only delete your own budgets.")
        instance.delete()


class ReceiptPaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing receipt payments. Users can only access payments for their own receipts."""
    serializer_class = ReceiptPaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['payment_method', 'paid_at']
    ordering_fields = ['paid_at', 'amount_paid']
    ordering = ['-paid_at']

    def get_queryset(self):
        """Filter receipt payments to only show payments for current user's receipts."""
        return ReceiptPayment.objects.filter(receipt__user=self.request.user).select_related(
            'receipt', 'payment_method'
        )
    
    def perform_create(self, serializer):
        """Ensure users can only create payments for their own receipts."""
        receipt_id = self.request.data.get('receipt')
        if receipt_id:
            try:
                receipt = Receipt.objects.get(id=receipt_id, user=self.request.user)
                serializer.save()
            except Receipt.DoesNotExist:
                raise permissions.PermissionDenied("You can only create payments for your own receipts.")
        else:
            serializer.save()
    
    def perform_update(self, serializer):
        """Ensure users can only update payments for their own receipts."""
        payment = self.get_object()
        if payment.receipt.user != self.request.user:
            raise permissions.PermissionDenied("You can only update payments for your own receipts.")
        serializer.save()
    
    def perform_destroy(self, instance):
        """Ensure users can only delete payments for their own receipts."""
        if instance.receipt.user != self.request.user:
            raise permissions.PermissionDenied("You can only delete payments for your own receipts.")
        instance.delete()


class ReceiptItemViewSet(viewsets.ModelViewSet):
    """ViewSet for managing receipt items. Users can only access items for their own receipts."""
    serializer_class = ReceiptItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['receipt']
    ordering_fields = ['item_name', 'total_price']
    ordering = ['item_name']

    def get_queryset(self):
        """Filter receipt items to only show items for current user's receipts."""
        return ReceiptItem.objects.filter(receipt__user=self.request.user).select_related(
            'receipt'
        )
    
    def perform_create(self, serializer):
        """Ensure users can only create items for their own receipts."""
        receipt_id = self.request.data.get('receipt')
        if receipt_id:
            try:
                receipt = Receipt.objects.get(id=receipt_id, user=self.request.user)
                serializer.save()
            except Receipt.DoesNotExist:
                raise permissions.PermissionDenied("You can only create items for your own receipts.")
        else:
            serializer.save()
    
    def perform_update(self, serializer):
        """Ensure users can only update items for their own receipts."""
        item = self.get_object()
        if item.receipt.user != self.request.user:
            raise permissions.PermissionDenied("You can only update items for your own receipts.")
        serializer.save()
    
    def perform_destroy(self, instance):
        """Ensure users can only delete items for their own receipts."""
        if instance.receipt.user != self.request.user:
            raise permissions.PermissionDenied("You can only delete items for your own receipts.")
        instance.delete()


class ReceiptTagViewSet(viewsets.ModelViewSet):
    """ViewSet for managing receipt tags. Users can only access tags for their own receipts."""
    serializer_class = ReceiptTagSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['receipt', 'tag']
    ordering_fields = ['receipt', 'tag']

    def get_queryset(self):
        """Filter receipt tags to only show tags for current user's receipts."""
        return ReceiptTag.objects.filter(receipt__user=self.request.user).select_related(
            'receipt', 'tag'
        )
    
    def perform_create(self, serializer):
        """Ensure users can only create tags for their own receipts."""
        receipt_id = self.request.data.get('receipt')
        if receipt_id:
            try:
                receipt = Receipt.objects.get(id=receipt_id, user=self.request.user)
                serializer.save()
            except Receipt.DoesNotExist:
                raise permissions.PermissionDenied("You can only create tags for your own receipts.")
        else:
            serializer.save()
    
    def perform_update(self, serializer):
        """Ensure users can only update tags for their own receipts."""
        receipt_tag = self.get_object()
        if receipt_tag.receipt.user != self.request.user:
            raise permissions.PermissionDenied("You can only update tags for your own receipts.")
        serializer.save()
    
    def perform_destroy(self, instance):
        """Ensure users can only delete tags for their own receipts."""
        if instance.receipt.user != self.request.user:
            raise permissions.PermissionDenied("You can only delete tags for your own receipts.")
        instance.delete()

# Custom Login View to use the LoginForm
class CustomLoginView(LoginView):
    template_name = "auth/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True  
    next_page = 'index'  # Where to redirect after login

# Custom Logout View to redirect after logout
class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("login")  # Where to redirect after logout

# Registration View    
class RegisterView(CreateView):
    model = User
    form_class = RegistrationForm
    template_name = "auth/register.html"
    success_url = reverse_lazy("index")  # Redirect somewhere after login

    def form_valid(self, form):
        response = super().form_valid(form)
        # Log the new user in
        login(self.request, self.object)
        return response
    
def HomeView(request):
    
    return render(request, "index.html")  # Ensure you have a home.html template    