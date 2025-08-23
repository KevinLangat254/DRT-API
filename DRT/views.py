from rest_framework import viewsets, permissions, status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta
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

User = get_user_model()


# User = settings.AUTH_USER_MODEL

class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for user management. Users can only access their own profile."""
    serializer_class = None  # We'll create a simple serializer for user data
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Users can only see their own profile."""
        return User.objects.filter(id=self.request.user.id)
    
    @action(detail=False, methods=['get'])
    def profile(self, request):
        """Get current user's profile information."""
        user = request.user
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'date_joined': user.date_joined,
            'is_active': user.is_active,
        })
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Update current user's profile."""
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing receipt categories. Categories are shared across all users."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']


class PaymentMethodViewSet(viewsets.ModelViewSet):
    """ViewSet for managing payment methods. Payment methods are shared across all users."""
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']


class ReceiptViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user receipts. Users can only access their own receipts."""
    serializer_class = ReceiptSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'purchase_date']
    search_fields = ['store_name', 'notes']
    ordering_fields = ['purchase_date', 'uploaded_at', 'total_amount']
    ordering = ['-purchase_date', '-uploaded_at']

    def get_queryset(self):
        """Filter receipts to only show current user's receipts."""
        queryset = Receipt.objects.filter(user=self.request.user).select_related(
            'category', 'user'
        ).prefetch_related(
            'payments__payment_method',
            'items',
            'tags__tag'
        )
        
        # Custom filtering for payment method and tags
        payment_method = self.request.query_params.get('payment_method', None)
        tags = self.request.query_params.get('tags', None)
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        amount_min = self.request.query_params.get('amount_min', None)
        amount_max = self.request.query_params.get('amount_max', None)
        
        if payment_method:
            queryset = queryset.filter(payments__payment_method__name__icontains=payment_method)
        
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            queryset = queryset.filter(tags__tag__name__in=tag_list)
        
        if date_from:
            queryset = queryset.filter(purchase_date__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(purchase_date__lte=date_to)
        
        if amount_min:
            queryset = queryset.filter(total_amount__gte=amount_min)
        
        if amount_max:
            queryset = queryset.filter(total_amount__lte=amount_max)
        
        return queryset.distinct()

    def perform_create(self, serializer):
        """Automatically assign the current user when creating a receipt."""
        serializer.save(user=self.request.user)
    
    def perform_update(self, serializer):
        """Ensure users can only update their own receipts."""
        receipt = self.get_object()
        if receipt.user != self.request.user:
            raise permissions.PermissionDenied("You can only update your own receipts.")
        serializer.save()
    
    def perform_destroy(self, instance):
        """Ensure users can only delete their own receipts."""
        if instance.user != self.request.user:
            raise permissions.PermissionDenied("You can only delete your own receipts.")
        instance.delete()
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get receipt analytics for the current user."""
        user = request.user
        
        # Get date range from query params (default to last 30 days)
        days = int(request.query_params.get('days', 30))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Filter receipts by date range
        receipts = Receipt.objects.filter(
            user=user,
            purchase_date__range=[start_date, end_date]
        )
        
        # Total expenses
        total_expenses = receipts.aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Expenses by category
        category_expenses = receipts.values('category__name').annotate(
            total=Sum('total_amount'),
            count=Count('id')
        ).order_by('-total')
        
        # Expenses by month
        monthly_expenses = receipts.annotate(
            month=TruncMonth('purchase_date')
        ).values('month').annotate(
            total=Sum('total_amount'),
            count=Count('id')
        ).order_by('month')
        
        # Payment method breakdown
        payment_methods = ReceiptPayment.objects.filter(
            receipt__user=user,
            receipt__purchase_date__range=[start_date, end_date]
        ).values('payment_method__name').annotate(
            total=Sum('amount_paid'),
            count=Count('id')
        ).order_by('-total')
        
        return Response({
            'period': {
                'start_date': start_date,
                'end_date': end_date,
                'days': days
            },
            'summary': {
                'total_expenses': total_expenses,
                'total_receipts': receipts.count()
            },
            'by_category': list(category_expenses),
            'by_month': list(monthly_expenses),
            'by_payment_method': list(payment_methods)
        })


class TagViewSet(viewsets.ModelViewSet):
    """ViewSet for managing tags. Tags are shared across all users."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']


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
            raise permissions.PermissionDenied("You can only delete payments for their own receipts.")
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
                raise permissions.PermissionDenied("You can only create items for their own receipts.")
        else:
            serializer.save()
    
    def perform_update(self, serializer):
        """Ensure users can only update items for their own receipts."""
        item = self.get_object()
        if item.receipt.user != self.request.user:
            raise permissions.PermissionDenied("You can only update items for their own receipts.")
        serializer.save()
    
    def perform_destroy(self, instance):
        """Ensure users can only delete items for their own receipts."""
        if instance.receipt.user != self.request.user:
            raise permissions.PermissionDenied("You can only delete items for their own receipts.")
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