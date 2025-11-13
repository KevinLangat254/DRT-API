from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from .models import Receipt, Category, Budget

User = get_user_model() 

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={"placeholder": "Enter username", "class": "form-control"})
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Enter password", "class": "form-control"})
    )

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter email'})
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })


class ReceiptForm(forms.ModelForm):
    """Form for creating and editing receipts."""
    
    class Meta:
        model = Receipt
        fields = ['store_name', 'category', 'total_amount', 'currency', 'purchase_date', 'notes']
        widgets = {
            'store_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter store name'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'total_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01'
            }),
            'currency': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'KES',
                'maxlength': '10'
            }),
            'purchase_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional notes about this receipt'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make category optional
        self.fields['category'].required = False
        self.fields['category'].queryset = Category.objects.all().order_by('name')
        self.fields['category'].empty_label = '-- Select Category --'
        
        # Set default currency
        if not self.instance.pk:
            self.fields['currency'].initial = 'KES'


class BudgetForm(forms.ModelForm):
    """Form for creating and editing budgets."""

    class Meta:
        model = Budget
        fields = ["category", "amount_limit", "period_start", "period_end"]
        widgets = {
            "category": forms.Select(attrs={"class": "form-select"}),
            "amount_limit": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "0.00", "step": "0.01", "min": "0.01"}
            ),
            "period_start": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "period_end": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.all().order_by("name")
        self.fields["category"].empty_label = "-- Select Category --"
        for name, field in self.fields.items():
            base_class = field.widget.attrs.get("class", "form-control")
            field.widget.attrs.setdefault("class", base_class)
            if self.is_bound and name in self.errors:
                field.widget.attrs["class"] = f"{field.widget.attrs['class']} is-invalid"