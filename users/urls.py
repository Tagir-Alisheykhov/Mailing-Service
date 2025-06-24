from django.urls import path, reverse_lazy
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)

from .views import (
    RegisterView,
    ProfileDetailView,
    ProfileEditView,
    ProfileVerificationView,
    email_verification
)
from . import apps

# app_name = apps.UsersConfig.name
app_name = 'users'


urlpatterns = [

    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(
        template_name='users/login.html',
        next_page='users:profile'
    ), name='login'),
    path('logout/', LogoutView.as_view(next_page='messenger:home'), name='logout'),

    # User profile
    path('profile/', ProfileDetailView.as_view(), name='profile'),
    path('profile/edit/', ProfileEditView.as_view(), name='profile_edit'),

    # Email verification
    path('verify-email/', ProfileVerificationView.as_view(), name='verify_email'),
    path('email-confirm/<str:token>/', email_verification, name='email_verification'),

    # Password reset
    path('password-reset/',
         PasswordResetView.as_view(
             template_name='users/password_reset_form.html',
             email_template_name='users/password_reset_email.html',
             success_url=reverse_lazy('users:password_reset_done')
         ),
         name='password_reset'),

    path('password-reset/done/',
         PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
         name='password_reset_done'),

    path('password-reset/<uidb64>/<token>/',
        PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html',
            success_url=reverse_lazy('users:password_reset_complete')
        ),
        name='password_reset_confirm'),

    path('password-reset/complete/',
         PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),

]
