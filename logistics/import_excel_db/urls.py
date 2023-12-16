from django.urls import path
from . import views  
from logistics import settings
from django.conf.urls.static import static
import os
urlpatterns =[
path("",views.Import_Excel_pandas,name="Import_Excel_pandas"),
] 
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_URL)
