from django.contrib import admin
from django.urls import path
from . import views as account_views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('signup/', account_views.signup, name='signup'),
    path('', account_views.login_view, name='login'),
    path('logout/', account_views.logout_view, name='logout'),
    path('index/', account_views.index, name='index'),  # Add payment view URL
    path('forgot_password/', account_views.recover_password, name='forgot-password'),
    path('reset_password/<uidb64>/<token>/', account_views.reset_password, name='reset_password'),
    path('password_reset/done/', account_views.password_reset_done, name='password_reset_done'),
]
