from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('',TemplateView.as_view(template_name="index.html")),
    path('auth/login_page/',TemplateView.as_view(template_name="login.html")),
    path('auth/signup/',views.signup),
    path('auth/signin/',views.signin),
]