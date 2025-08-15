from django.contrib import admin
from .models import Category, PaymentMethod, Receipt, Tag, ReceiptTag, Budget, ReceiptPayment, ReceiptItem

admin.site.register(Category)
admin.site.register(PaymentMethod)
admin.site.register(Receipt)
admin.site.register(Tag)
admin.site.register(ReceiptTag)
admin.site.register(Budget)
admin.site.register(ReceiptPayment)
admin.site.register(ReceiptItem)

