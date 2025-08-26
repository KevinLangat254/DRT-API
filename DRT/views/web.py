from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth import get_user_model, login
from django.shortcuts import render

from ..forms import LoginForm, RegistrationForm
from ..models import Receipt
from django.contrib.auth.decorators import login_required

User = get_user_model()


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
        return response


def HomeView(request):
    return render(request, "index.html")

@login_required
def dashboard(request):
    receipts = Receipt.objects.filter(user=request.user)
    return render(request, "Dashboard/dashboard.html", {"receipts": receipts})


