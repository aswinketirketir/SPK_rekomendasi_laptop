from django.urls import path
from . import views

urlpatterns = [
    # Halaman Web
    path('', views.halaman_utama, name='halaman_utama'),
    path('katalog/', views.halaman_katalog, name='halaman_katalog'),
    path('rekomendasi/', views.halaman_rekomendasi, name='halaman_rekomendasi'),

    # REST API
    path('api/katalog/', views.api_katalog_laptop, name='api_katalog'),
    path('api/rekomendasi/', views.api_rekomendasi_laptop, name='api_rekomendasi'),
    path('api/best-cluster/', views.api_best_per_cluster, name='api_best_cluster'),
    path('api/filter-options/', views.api_filter_options, name='api_filter_options'),
]