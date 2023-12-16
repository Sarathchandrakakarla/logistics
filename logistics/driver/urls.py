from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('',views.driver_dashboard),
    path('profile/',views.profile),
    path('profile/save/',views.save),
    path('logout/',views.logout),
]