from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from .models import Category, PaymentMethod, Receipt, Tag, ReceiptTag, Budget, ReceiptPayment, ReceiptItem, Notification


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at', 'updated_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at', 'updated_at']
    ordering = ['name']


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'is_digital', 'created_at', 'updated_at']
    search_fields = ['name', 'description']
    list_filter = ['is_digital', 'created_at', 'updated_at']
    ordering = ['name']


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ['store_name', 'user', 'category', 'total_amount', 'currency', 'purchase_date', 'uploaded_at']
    list_filter = ['category', 'purchase_date', 'uploaded_at', 'user']
    search_fields = ['store_name', 'notes', 'user__username']
    readonly_fields = ['uploaded_at']
    ordering = ['-purchase_date', '-uploaded_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'category')
    
    def save_model(self, request, obj, form, change):
        """Ensure validation runs before saving in admin."""
        try:
            obj.clean()
            super().save_model(request, obj, form, change)
        except ValidationError as e:
            self.message_user(request, f"Validation error: {e}", level='ERROR')
            raise


@admin.register(ReceiptItem)
class ReceiptItemAdmin(admin.ModelAdmin):
    list_display = ['item_name', 'receipt', 'quantity', 'unit_price', 'total_price']
    list_filter = ['receipt__purchase_date']
    search_fields = ['item_name', 'receipt__store_name']
    ordering = ['item_name']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('receipt')
    
    def save_model(self, request, obj, form, change):
        """Ensure validation runs before saving in admin."""
        try:
            obj.clean()
            super().save_model(request, obj, form, change)
        except ValidationError as e:
            self.message_user(request, f"Validation error: {e}", level='ERROR')
            raise


@admin.register(ReceiptPayment)
class ReceiptPaymentAdmin(admin.ModelAdmin):
    list_display = ['receipt', 'payment_method', 'amount_paid', 'paid_at']
    list_filter = ['payment_method', 'paid_at', 'receipt__purchase_date']
    search_fields = ['receipt__store_name', 'payment_method__name']
    ordering = ['-paid_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('receipt', 'payment_method')
    
    def save_model(self, request, obj, form, change):
        """Ensure validation runs before saving in admin."""
        try:
            obj.clean()
            super().save_model(request, obj, form, change)
        except ValidationError as e:
            self.message_user(request, f"Validation error: {e}", level='ERROR')
            raise


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    ordering = ['name']


@admin.register(ReceiptTag)
class ReceiptTagAdmin(admin.ModelAdmin):
    list_display = ['receipt', 'tag']
    list_filter = ['tag', 'receipt__purchase_date']
    search_fields = ['receipt__store_name', 'tag__name']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('receipt', 'tag')


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'amount_limit', 'period_start', 'period_end', 'created_at']
    list_filter = ['category', 'period_start', 'period_end', 'created_at', 'user']
    search_fields = ['user__username', 'category__name']
    ordering = ['-period_start']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'category')
    
    def save_model(self, request, obj, form, change):
        """Ensure validation runs before saving in admin."""
        try:
            obj.clean()
            super().save_model(request, obj, form, change)
        except ValidationError as e:
            self.message_user(request, f"Validation error: {e}", level='ERROR')
            raise

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at', 'user']
    search_fields = ['message', 'user__username']
    ordering = ['-created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
