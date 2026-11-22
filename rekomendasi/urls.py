from django.urls import path
from . import views

urlpatterns = [
    path('api/rekomendasi/', views.api_rekomendasi_laptop, name='api_rekomendasi'),
    path('api/best-cluster/', views.api_best_per_cluster, name='api_best_cluster'),
]