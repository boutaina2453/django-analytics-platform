from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_file, name='upload_file'),
    path('stats/', views.show_statistics, name='show_statistics'),
    path('visualizations/', views.show_visualizations, name='show_visualizations'),
]
