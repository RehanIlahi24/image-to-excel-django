from django.urls import path
from . import views

urlpatterns = [
    path('image-to-excel-convert', views.image_to_excel_convert_view),
    path('image-url-to-excel-convert', views.image_url_to_excel_convert_view),
    path('data', views.data_view)
]