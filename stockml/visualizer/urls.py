from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/<str:symbol>/', views.dashboard_symbol, name='dashboard_symbol'),
    path('login/', views.login, name='login')
]