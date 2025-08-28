from django.urls import path
from .views import home, signup, login_view, logout_view, dashboard, tracking

urlpatterns = [
    path('', home, name='home'),
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('tracking/', tracking, name='tracking'),
]