from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('tracking/', views.tracking, name='tracking'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard_stats/', views.dashboard_stats, name='dashboard_stats'),
]
