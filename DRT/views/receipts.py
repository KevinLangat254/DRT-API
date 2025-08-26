from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Prefetch
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta

from django.contrib.auth import get_user_model

from ..models import Receipt, ReceiptTag, ReceiptPayment
from ..serializers import ReceiptSerializer

User = get_user_model()


class ReceiptViewSet(viewsets.ModelViewSet):
    """Manage user receipts; user-scoped with filters and analytics."""
    serializer_class = ReceiptSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'purchase_date']
    search_fields = ['store_name', 'notes']
    ordering_fields = ['purchase_date', 'uploaded_at', 'total_amount']
    ordering = ['-purchase_date', '-uploaded_at']

    def get_queryset(self):
        queryset = (
            Receipt.objects.filter(user=self.request.user)
            .select_related('category', 'user')
            .prefetch_related(
                'payments__payment_method',
                'items',
                Prefetch('receipttag_set', queryset=ReceiptTag.objects.select_related('tag')),
            )
        )

        payment_method = self.request.query_params.get('payment_method')
        tags = self.request.query_params.get('tags')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        amount_min = self.request.query_params.get('amount_min')
        amount_max = self.request.query_params.get('amount_max')

        if payment_method:
            queryset = queryset.filter(payments__payment_method__name__icontains=payment_method)
        if tags:
            tag_list = [t.strip() for t in tags.split(',')]
            queryset = queryset.filter(receipttag__tag__name__in=tag_list)
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
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        receipt = self.get_object()
        if receipt.user != self.request.user:
            raise permissions.PermissionDenied("You can only update your own receipts.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise permissions.PermissionDenied("You can only delete your own receipts.")
        instance.delete()

    @action(detail=False, methods=['get'])
    def analytics(self, request):
        user = request.user
        days = int(request.query_params.get('days', 30))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)

        receipts = Receipt.objects.filter(user=user, purchase_date__range=[start_date, end_date])
        total_expenses = receipts.aggregate(total=Sum('total_amount'))['total'] or 0

        category_expenses = receipts.values('category__name').annotate(
            total=Sum('total_amount'), count=Count('id')
        ).order_by('-total')

        monthly_expenses = receipts.annotate(month=TruncMonth('purchase_date')).values('month').annotate(
            total=Sum('total_amount'), count=Count('id')
        ).order_by('month')

        payment_methods = ReceiptPayment.objects.filter(
            receipt__user=user, receipt__purchase_date__range=[start_date, end_date]
        ).values('payment_method__name').annotate(total=Sum('amount_paid'), count=Count('id')).order_by('-total')

        return Response({
            'period': {'start_date': start_date, 'end_date': end_date, 'days': days},
            'summary': {'total_expenses': total_expenses, 'total_receipts': receipts.count()},
            'by_category': list(category_expenses),
            'by_month': list(monthly_expenses),
            'by_payment_method': list(payment_methods),
        })


