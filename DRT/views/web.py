from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView, ListView
from django.contrib.auth import get_user_model, login
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from decimal import Decimal, InvalidOperation
from django.utils import timezone

# Assuming your forms and models are in the parent directory as per your imports
from ..forms import LoginForm, RegistrationForm, ReceiptForm, BudgetForm
from ..models import Receipt, Budget, Notification

User = get_user_model()

# --- AUTHENTICATION VIEWS ---

class CustomLoginView(LoginView):
    template_name = "auth/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True
    next_page = 'index'


class RegisterView(CreateView):
    model = User
    form_class = RegistrationForm
    template_name = "auth/register.html"
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        
        # Optional: Welcome Notification
        Notification.objects.create(
            user=self.object,
            message="Welcome to Receipt Tracker! Start by adding your first receipt."
        )
        return response


def HomeView(request):
    return render(request, "index.html")


# --- RECEIPT VIEWS ---

@login_required
def receipts(request):
    """Receipts view with search functionality."""
    receipts_list = Receipt.objects.filter(user=request.user).select_related('category').order_by('-purchase_date', '-uploaded_at')
    
    # Get search query from request
    search_query = request.GET.get('q', '').strip()
    category_filter = request.GET.get('category', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    amount_min = request.GET.get('amount_min', '')
    amount_max = request.GET.get('amount_max', '')
    
    # Apply search filters
    if search_query:
        receipts_list = receipts_list.filter(
            Q(store_name__icontains=search_query) |
            Q(notes__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    if category_filter:
        receipts_list = receipts_list.filter(category_id=category_filter)
    
    if date_from:
        receipts_list = receipts_list.filter(purchase_date__gte=date_from)
    
    if date_to:
        receipts_list = receipts_list.filter(purchase_date__lte=date_to)
    
    if amount_min:
        try:
            min_amount = Decimal(amount_min)
            receipts_list = receipts_list.filter(total_amount__gte=min_amount)
        except (InvalidOperation, ValueError):
            pass
    
    if amount_max:
        try:
            max_amount = Decimal(amount_max)
            receipts_list = receipts_list.filter(total_amount__lte=max_amount)
        except (InvalidOperation, ValueError):
            pass
    
    # Get all categories for filter dropdown
    from ..models import Category
    categories = Category.objects.all().order_by('name')
    
    context = {
        'receipts': receipts_list,
        'search_query': search_query,
        'category_filter': category_filter,
        'date_from': date_from,
        'date_to': date_to,
        'amount_min': amount_min,
        'amount_max': amount_max,
        'categories': categories,
    }
    
    return render(request, "Receipts/receipts.html", context)


class ReceiptCreateView(LoginRequiredMixin, CreateView):
    """Create a new receipt."""
    model = Receipt
    form_class = ReceiptForm
    template_name = "receipts/receipt_form.html"
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        
        # Save the receipt first to get the ID/Object
        response = super().form_valid(form)
        
        messages.success(self.request, 'Receipt created successfully!')

        # Create Notification
        Notification.objects.create(
            user=self.request.user,
            message=f"Receipt from '{self.object.store_name}' for Ksh {self.object.total_amount} was added."
        )

        return response
    
    def get_success_url(self):
        return reverse_lazy('receipt_detail', kwargs={'pk': self.object.pk})


class ReceiptDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """View receipt details."""
    model = Receipt
    template_name = "receipts/receipt_detail.html"
    context_object_name = 'receipt'
    
    def test_func(self):
        receipt = self.get_object()
        return receipt.user == self.request.user
    
    def get_queryset(self):
        return Receipt.objects.filter(user=self.request.user).select_related('category', 'user').prefetch_related('items', 'payments__payment_method', 'receipttag_set__tag')


class ReceiptUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update an existing receipt."""
    model = Receipt
    form_class = ReceiptForm
    template_name = "receipts/receipt_form.html"
    
    def test_func(self):
        receipt = self.get_object()
        return receipt.user == self.request.user
    
    def form_valid(self, form):
        # Save the changes
        response = super().form_valid(form)
        
        messages.success(self.request, 'Receipt updated successfully!')
        
        # Create Notification
        Notification.objects.create(
            user=self.request.user,
            message=f"Receipt from '{self.object.store_name}' was updated."
        )
        
        return response
    
    def get_success_url(self):
        return reverse_lazy('receipt_detail', kwargs={'pk': self.object.pk})


class ReceiptDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a receipt."""
    model = Receipt
    template_name = "receipts/receipt_confirm_delete.html"
    success_url = reverse_lazy('receipts')
    
    def test_func(self):
        receipt = self.get_object()
        return receipt.user == self.request.user
    
    def delete(self, request, *args, **kwargs):
        # 1. Capture details BEFORE deleting
        receipt = self.get_object()
        store_name = receipt.store_name
        amount = receipt.total_amount
        
        # 2. Perform the delete
        response = super().delete(request, *args, **kwargs)
        
        messages.success(self.request, 'Receipt deleted successfully!')
        
        # 3. Create Notification
        Notification.objects.create(
            user=self.request.user,
            message=f"Receipt from '{store_name}' (Ksh {amount}) was deleted."
        )
        
        return response


# --- BUDGET VIEWS ---

class BudgetListView(LoginRequiredMixin, ListView):
    """List budgets for the logged-in user."""

    model = Budget
    template_name = "budgets/budget_list.html"
    context_object_name = "budgets"

    def get_queryset(self):
        return (
            Budget.objects.filter(user=self.request.user)
            .select_related("category")
            .order_by("-period_start", "-period_end")
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        # Add is_expired attribute to each budget
        for budget in context['budgets']:
            budget.is_expired = budget.period_end < today
        return context


class BudgetCreateView(LoginRequiredMixin, CreateView):
    """Create a new budget."""

    model = Budget
    form_class = BudgetForm
    template_name = "budgets/budget_form.html"
    success_url = reverse_lazy("budget_list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        
        # Save budget
        response = super().form_valid(form)
        
        messages.success(self.request, "Budget created successfully!")
        
        # Create Notification
        Notification.objects.create(
            user=self.request.user,
            message=f"Budget for '{self.object.category.name}' (Ksh {self.object.amount}) created."
        )
        
        return response


class BudgetUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update an existing budget."""

    model = Budget
    form_class = BudgetForm
    template_name = "budgets/budget_form.html"
    success_url = reverse_lazy("budget_list")

    def test_func(self):
        budget = self.get_object()
        return budget.user == self.request.user

    def form_valid(self, form):
        # Save changes
        response = super().form_valid(form)
        
        messages.success(self.request, "Budget updated successfully!")
        
        # Create Notification
        Notification.objects.create(
            user=self.request.user,
            message=f"Budget for '{self.object.category.name}' updated to Ksh {self.object.amount}."
        )
        
        return response


class BudgetDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a budget."""

    model = Budget
    template_name = "budgets/budget_confirm_delete.html"
    success_url = reverse_lazy("budget_list")

    def test_func(self):
        budget = self.get_object()
        return budget.user == self.request.user

    def delete(self, request, *args, **kwargs):
        # 1. Capture details BEFORE deleting
        budget = self.get_object()
        category_name = budget.category.name
        amount = budget.amount

        # 2. Perform delete
        response = super().delete(request, *args, **kwargs)
        
        messages.success(self.request, "Budget deleted successfully!")
        
        # 3. Create Notification
        Notification.objects.create(
            user=self.request.user,
            message=f"Budget for '{category_name}' (Ksh {amount}) was deleted."
        )
        
        return response
    
class NotificationListView(LoginRequiredMixin, ListView):
    """List notifications for the logged-in user."""

    model = Notification
    template_name = "notifications/notifications.html"
    context_object_name = "notifications"

    def get_queryset(self):
        return (
            Notification.objects.filter(user=self.request.user)
            .order_by("-created_at")
        )
    
@login_required   
def MarkAllNotificationsRead(request):
    """Mark all notifications as read for the logged-in user."""
    if request.user.is_authenticated:
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        messages.success(request, "All notifications marked as read.")
    return render(request, "notifications/notifications.html")  

@login_required   
def MarkNotificationRead(request, pk):
    """Mark a single notification as read."""
    if request.user.is_authenticated:
        try:
            notification = Notification.objects.get(pk=pk, user=request.user)
            notification.is_read = True
            notification.save()
            messages.success(request, "Notification marked as read.")
        except Notification.DoesNotExist:
            messages.error(request, "Notification not found.")
    return render(request, "notifications/notifications.html")  

