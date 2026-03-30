from django.contrib.auth.views import LoginView
from django.urls import path, include
from accounts import views
from accounts.forms import UserLoginForm
from accounts.views import register
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('login/', LoginView.as_view(authentication_form=UserLoginForm), name='login'),
    path('register/', register, name='register'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('profile/', views.profile, name='profile'),
    path('',include('django.contrib.auth.urls')),
    # 1. صفحة طلب استعادة كلمة السر (إدخال الإيميل)
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),

    # 2. صفحة تأكيد إرسال الإيميل
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),

    # 3. الرابط الذي يضغط عليه المستخدم في الإيميل (تغيير السر)
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    # 4. صفحة نجاح العملية
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),


]





