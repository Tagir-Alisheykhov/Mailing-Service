import secrets

from django.contrib.auth import login
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser
from .services import send_welcome_email


import os
from dotenv import load_dotenv
from django.core.mail import send_mail
from django.contrib import messages

load_dotenv()


class RegisterView(CreateView):
    template_name = 'users/form_user.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('users:login')
    usable_password = None

    def form_valid(self, form):
        user = form.save()
        send_welcome_email(user_email=user.email)
        return super().form_valid(form)


class ProfileDetailView(LoginRequiredMixin, DetailView):
    """Профиль пользователя"""
    model = CustomUser
    template_name = 'users/profile.html'
    context_object_name = 'object'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.session.pop('email_just_verified', False):
            context['show_confirmation_message'] = True
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Обновление данных пользователя"""
    # model = CustomUser
    form_class = CustomUserChangeForm
    template_name = 'users/form_user.html'
    success_url = reverse_lazy('users:profile')
    usable_password = None

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editing'] = True
        return context


class ProfileVerificationView(LoginRequiredMixin, View):
    """Верификация пользователя"""
    model = CustomUser
    success_url = reverse_lazy('users:profile')

    def post(self, request, *args, **kwargs):
        """Отправка письма с подтверждением"""
        user = request.user
        if user.is_email_verified:
            messages.info(request, 'Ваш email уже подтвержден!')
            return redirect(self.success_url)
        else:
            token = secrets.token_hex(16)
            user.token = token
            user.save()
            host = request.get_host()
            url = f'http://{host}{reverse("users:email_verification", kwargs={"token": token})}'
            send_mail(
                subject='Подтверждение почты',
                message=f'Для подтверждения email перейдите по ссылке: {url}',
                from_email=os.getenv('EMAIL_HOST_USER'),
                recipient_list=[user.email],
                fail_silently=False,
            )
            messages.success(request, 'Ссылка для подтверждения отправлена на ваш email!')
            return redirect(self.success_url)


def email_verification(request, token):
    user = get_object_or_404(CustomUser, token=token)
    user.is_active = True
    user.is_email_verified = True
    user.token = None
    user.save()
    request.session['email_just_verified'] = True
    login(request, user)

    # messages.success(request, 'Ваш email успешно подтвержден!')
    return redirect(reverse('users:profile'))