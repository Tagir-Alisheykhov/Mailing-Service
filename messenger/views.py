import os
from dotenv import load_dotenv
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.views.generic import ListView, DetailView, TemplateView
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.cache import cache_page

from .forms import MessageForm, MailingForm, RecipientForm, MailingManagerForm
from .models import Message, Mailing, Recipient
from .services import (
    get_mailing_from_cache,
    get_recipients_from_cache,
    send_mailing_attempt,
    get_message_from_cache,
    get_mailings_attempt,
    create_msg_validation,
)

load_dotenv()

SENDER = os.getenv("EMAIL_HOST_USER")


@method_decorator(cache_page(3), name='dispatch')
class HomePageView(TemplateView):
    """Домашняя станица"""

    models = Message
    template_name = "messenger/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        mailings = get_mailing_from_cache()
        recipients = get_recipients_from_cache()
        if user.is_authenticated and not user.is_superuser:
            mailings = mailings.filter(owner=user)
            recipients = recipients.filter(owner=user)
        context.update(
            {
                "total_campaigns": mailings.count(),
                "active_campaigns": mailings.filter(mailing_status="running").count(),
                "unique_recipients": recipients.count(),
                "is_superuser": user.is_superuser if user.is_authenticated else False,
            }
        )
        return context


@method_decorator(cache_page(3), name="dispatch")
class MessageDraftView(LoginRequiredMixin, ListView):
    """Черновик (неотправленные сообщения)"""

    model = Message
    template_name = "messenger/msg_list.html"
    context_object_name = "messages_draft"
    login_url = "users:login"

    def get_queryset(self):
        """Выбираем только неотправленные сообщения"""
        if not self.request.user.is_superuser:
            return super().get_queryset().filter(is_sent=False, owner=self.request.user)
        return super().get_queryset().filter(is_sent=False)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["context_name"] = "Черновик"
        context["all_messages"] = self.get_queryset()
        context["is_draft_page"] = True
        return context


@method_decorator(cache_page(3), name="dispatch")
class MessageSentView(LoginRequiredMixin, ListView):
    """Отправленные сообщения"""

    model = Message
    template_name = "messenger/msg_list.html"
    context_object_name = "messages_sent"
    login_url = "users:login"

    def get_queryset(self):
        """Выбираем только неотправленные сообщения"""
        if not self.request.user.is_superuser:
            return super().get_queryset().filter(is_sent=True, owner=self.request.user)
        return super().get_queryset().filter(is_sent=True)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["context_name"] = "Отправленные сообщения"
        context["all_messages"] = self.get_queryset()
        context["is_sent_page"] = True
        return context


@method_decorator(cache_page(3), name="dispatch")
class MessageCreateView(LoginRequiredMixin, CreateView):
    """Ручное создание сообщения"""

    model = Message
    login_url = "users:login"
    form_class = MessageForm
    template_name = "messenger/msg_form.html"
    success_url = reverse_lazy("messenger:draft_msg")
    context_object_name = "create_msg"

    def form_valid(self, form):
        """Обработка валидной формы"""
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        # Всегда сохраняем сообщение сначала
        self.object.save()
        if form.cleaned_data.get("is_sent", False):
            create_msg_validation(object=self.object)
        return super().form_valid(form)


@method_decorator(cache_page(3), name="dispatch")
class MessageUpdateView(LoginRequiredMixin, UpdateView):
    """Изменение сообщения"""

    model = Message
    login_url = "users:login"
    form_class = MessageForm
    template_name = "messenger/msg_form.html"
    success_url = reverse_lazy("messenger:draft_msg")
    context_object_name = "update_msg"

    def form_valid(self, form):
        """Обработка формы после изменений"""
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        if not form.cleaned_data.get("is_sent", False):
            self.object.is_sent = False
            self.object.save()
            return super().form_valid(form)
        self.object.save()
        create_msg_validation(object=self.object)
        return super().form_valid(form)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=None)
        if obj.owner == self.request.user or self.request.user.is_superuser:
            return obj
        raise PermissionDenied

    def dispatch(self, request, *args, **kwargs):
        """Перехват ошибки запрета доступа"""
        try:
            return super().dispatch(request, *args, **kwargs)
        except PermissionDenied:
            return HttpResponseForbidden(
                "403 - У вас нет прав на редактирование данного сообщения ;] "
            )


@method_decorator(cache_page(3), name="dispatch")
class MessageDetailView(DetailView):
    """Детальная информация о сообщении"""

    model = Message
    template_name = "messenger/msg_detail.html"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=None)
        if obj.owner == self.request.user or self.request.user.is_superuser:
            return obj
        raise PermissionDenied

    def dispatch(self, request, *args, **kwargs):
        """Перехват ошибки запрета доступа"""
        try:
            return super().dispatch(request, *args, **kwargs)
        except PermissionDenied:
            return HttpResponseForbidden(
                "403 - У вас нет прав на просмотр данного сообщения ;] "
            )


@method_decorator(cache_page(3), name="dispatch")
class MessageDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление сообщения"""

    model = Message
    login_url = "users:login"
    template_name = "messenger/msg_delete.html"
    success_url = reverse_lazy("messenger:draft_msg")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=None)
        if obj.owner == self.request.user or self.request.user.is_superuser:
            return obj
        raise PermissionDenied

    def dispatch(self, request, *args, **kwargs):
        """Перехват ошибки запрета доступа"""
        try:
            return super().dispatch(request, *args, **kwargs)
        except PermissionDenied:
            return HttpResponseForbidden(
                "403 - У вас нет прав на удаление данного сообщения ;] "
            )


@method_decorator(cache_page(3), name="dispatch")
class MailingListView(LoginRequiredMixin, ListView):
    """Список всех рассылок"""

    model = Mailing
    template_name = "messenger/mailing_list.html"
    context_object_name = "mailings"
    login_url = "users:login"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        successfully, unsuccessfully = get_mailings_attempt(user)
        messages = get_message_from_cache(user)
        context.update(
            {
                "total_messages": messages.count(),
                "total_mailings_successfully": successfully.count(),
                "total_mailings_unsuccessfully": unsuccessfully.count(),
            }
        )
        context["is_superuser"] = user.is_superuser
        context["current_user"] = user
        context["current_url_name"] = self.request.resolver_match.url_name
        context["current_filter"] = "all"
        return context


@method_decorator(cache_page(3), name="dispatch")
class MailingCreatedView(LoginRequiredMixin, ListView):
    """Отображение рассылок по категории 'Создана'"""

    model = Mailing
    login_url = "users:login"
    template_name = "messenger/mailing_list.html"
    context_object_name = "mailings"

    def get_queryset(self):
        return super().get_queryset().filter(mailing_status="created")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_filter"] = "created"
        context["is_superuser"] = self.request.user.is_superuser
        context["current_user"] = self.request.user
        return context


@method_decorator(cache_page(3), name="dispatch")
class MailingRunningView(LoginRequiredMixin, ListView):
    """Отображение рассылок по категории 'Запущено'"""

    model = Mailing
    template_name = "messenger/mailing_list.html"
    context_object_name = "mailings"
    login_url = "users:login"

    def get(self, request, *args, **kwargs):
        now = timezone.now()
        Mailing.objects.filter(mailing_status="running", end_datetime__lt=now).update(
            mailing_status="completed"
        )
        try:
            send_mailing_attempt()
        except Exception as err:
            print(f"Возникла ошибка {err}")
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().filter(mailing_status="running")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_filter"] = "running"
        context["now_datetime"] = timezone.now()
        context["is_superuser"] = self.request.user.is_superuser
        context["current_user"] = self.request.user
        return context


@method_decorator(cache_page(3), name="dispatch")
class MailingCompletedView(LoginRequiredMixin, ListView):
    """Отображение рассылок по категории 'Завершено'"""

    model = Mailing
    template_name = "messenger/mailing_list.html"
    context_object_name = "mailings"
    login_url = "users:login"

    def get_queryset(self):
        return super().get_queryset().filter(mailing_status="completed")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_filter"] = "completed"
        context["is_superuser"] = self.request.user.is_superuser
        context["current_user"] = self.request.user
        return context


@method_decorator(cache_page(3), name="dispatch")
class MailingCreateView(LoginRequiredMixin, CreateView):
    """Создание объекта рассылки"""

    model = Mailing
    login_url = "users:login"
    form_class = MailingForm
    template_name = "messenger/mailing_form.html"
    success_url = reverse_lazy("messenger:mailing_created")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["message_form"] = MessageForm(
            self.request.POST or None, prefix="message"
        )
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["message_form"] = self.get_form().message_form
        context["current_url_name"] = self.request.resolver_match.url_name
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        if form.cleaned_data.get("create_new_message"):
            message = form.message_form.save(commit=False)
            message.owner = self.request.user
            message.save()
            self.object.message = message
        self.object.save()
        form.save_m2m()
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        if (
            request.user.has_perm("messenger.can_disable_mailing")
            and not request.user.is_superuser
        ):
            raise PermissionDenied("Менеджеры не могут создавать рассылки")
        return super().dispatch(request, *args, **kwargs)


@method_decorator(cache_page(3), name="dispatch")
class MailingDetailView(LoginRequiredMixin, DetailView):
    """Детальная информация о рассылке"""

    model = Mailing
    template_name = "messenger/mailing_detail.html"
    login_url = "users:login"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=None)
        if (
            obj.owner == self.request.user
            or self.request.user.is_superuser
            or self.request.user.has_perm("messenger.can_disable_mailing")
        ):
            return obj
        raise PermissionDenied

    def dispatch(self, request, *args, **kwargs):
        """Перехват ошибки запрета доступа"""
        try:
            return super().dispatch(request, *args, **kwargs)
        except PermissionDenied:
            return HttpResponseForbidden(
                "403 - У вас нет прав на просмотр данной рассылки ;] "
            )


@method_decorator(cache_page(3), name="dispatch")
class MailingUpdateView(LoginRequiredMixin, UpdateView):
    """Обновление информации в объекте рассылки"""

    model = Mailing
    login_url = "users:login"
    form_class = MailingForm
    template_name = "messenger/mailing_form.html"
    success_url = reverse_lazy("messenger:mailing_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_url_name"] = self.request.resolver_match.url_name
        return context

    def get_form_class(self):
        user = self.request.user
        if user == self.object.owner:
            return MailingForm
        if user.has_perm("messenger.can_disable_mailing"):
            return MailingManagerForm
        raise PermissionDenied

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=None)
        if (
            obj.owner == self.request.user
            or self.request.user.is_superuser
            or self.request.user.has_perm("messenger.can_disable_mailing")
        ):
            return obj
        raise PermissionDenied

    def dispatch(self, request, *args, **kwargs):
        """Перехват ошибки запрета доступа"""
        try:
            return super().dispatch(request, *args, **kwargs)
        except PermissionDenied:
            return HttpResponseForbidden(
                "403 - У вас нет прав на обновление данной рассылки ;] "
            )


@method_decorator(cache_page(3), name="dispatch")
class MailingDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление объекта рассылки"""

    model = Mailing
    login_url = "users:login"
    template_name = "messenger/mailing_delete.html"
    success_url = reverse_lazy("messenger:mailing_list")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=None)
        if obj.owner == self.request.user or self.request.user.is_superuser:
            return obj
        raise PermissionDenied

    def dispatch(self, request, *args, **kwargs):
        """Перехват ошибки запрета доступа"""
        try:
            return super().dispatch(request, *args, **kwargs)
        except PermissionDenied:
            return HttpResponseForbidden(
                "403 - У вас нет прав на удаление данной рассылки ;] "
            )


@method_decorator(cache_page(3), name="dispatch")
class RecipientListView(LoginRequiredMixin, ListView):
    """Список получателей"""

    model = Recipient
    template_name = "messenger/recipient_list.html"
    context_object_name = "recipients"
    login_url = "users:login"

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(owner=self.request.user)
        return queryset


@method_decorator(cache_page(3), name="dispatch")
class RecipientCreateView(LoginRequiredMixin, CreateView):
    """Создание получателя"""

    model = Recipient
    login_url = "users:login"
    form_class = RecipientForm
    template_name = "messenger/recipient_form.html"
    success_url = reverse_lazy("messenger:recipients_list")

    def form_valid(self, form):
        """Обработка валидной формы"""
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        if not form.cleaned_data.get("is_sent", False):
            self.object.is_sent = False
            self.object.save()
            return super().form_valid(form)
        create_msg_validation(object=self.object)
        return super().form_valid(form)


@method_decorator(cache_page(3), name="dispatch")
class RecipientUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование получателя"""

    model = Recipient
    login_url = "users:login"
    form_class = RecipientForm
    template_name = "messenger/recipient_form.html"
    success_url = reverse_lazy("messenger:recipients_list")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=None)
        if obj.owner == self.request.user or self.request.user.is_superuser:
            return obj
        raise PermissionDenied

    def dispatch(self, request, *args, **kwargs):
        """Перехват ошибки запрета доступа"""
        try:
            return super().dispatch(request, *args, **kwargs)
        except PermissionDenied:
            return HttpResponseForbidden(
                "403 - У вас нет прав на обновление получателей ;] "
            )


@method_decorator(cache_page(3), name="dispatch")
class RecipientDetailView(LoginRequiredMixin, DetailView):
    """Детальная информация о получателе"""

    model = Recipient
    template_name = "messenger/recipient_detail.html"
    login_url = "users:login"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=None)
        if obj.owner == self.request.user or self.request.user.is_superuser:
            return obj
        raise PermissionDenied

    def dispatch(self, request, *args, **kwargs):
        """Перехват ошибки запрета доступа"""
        try:
            return super().dispatch(request, *args, **kwargs)
        except PermissionDenied:
            return HttpResponseForbidden("403 - У вас нет прав на просмотр ;] ")


@method_decorator(cache_page(3), name="dispatch")
class RecipientDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление получателя"""

    model = Recipient
    login_url = "users:login"
    template_name = "messenger/recipient_delete.html"
    success_url = reverse_lazy("messenger:recipients_list")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=None)
        if obj.owner == self.request.user or self.request.user.is_superuser:
            return obj
        raise PermissionDenied

    def dispatch(self, request, *args, **kwargs):
        """Перехват ошибки запрета доступа"""
        try:
            return super().dispatch(request, *args, **kwargs)
        except PermissionDenied:
            return HttpResponseForbidden(
                "403 - У вас нет прав на удаление данного получателя ;] "
            )
