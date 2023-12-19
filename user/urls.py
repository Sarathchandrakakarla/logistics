from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('',views.user_dashboard),
    path('logout/',views.logout),
    path('profile/',views.profile),
    path('profile/save/',views.save),
    path('journeys/',views.journeys),
    path('payment/',views.payment),
]