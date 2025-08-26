from django.urls import path
from .views import (
    CustomLoginView, RegisterView, HomeView, web_logout,
)
from .views.web import dashboard  

urlpatterns = [
    # Web interface endpoints
    path('', HomeView, name='index'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', web_logout, name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('dashboard/', dashboard, name='dashboard'),  # New dashboard view
]
