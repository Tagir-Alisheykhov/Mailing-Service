import os

from django.utils import timezone
from dotenv import load_dotenv
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from .forms import MessageForm, MailingForm, RecipientForm
from .models import Message, Mailing, Recipient
from .services import sending_msg, get_mailing_from_cache, get_recipients_from_cache

load_dotenv()

SENDER = os.getenv('EMAIL_HOST_USER')


class HomePageView(TemplateView):
    """Домашняя станица"""
    models = Message
    template_name = 'messenger/home.html'

    def get_context_data(self,  *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        cache_mailings = get_mailing_from_cache()
        cache_recipients = get_recipients_from_cache().count()
        total_campaigns = cache_mailings.count()
        active_campaigns = cache_mailings.filter(mailing_status='running').count()
        unique_recipients = ''
        context.update(
            {
                'total_campaigns': total_campaigns,
                'active_campaigns': active_campaigns,
                'unique_recipients': cache_recipients
            }
        )
        return context


class MessageDraftView(ListView):
    """Черновик (неотправленные сообщения)"""
    models = Message
    fields = ['topic', 'body', 'is_sent']
    template_name = 'messenger/msg_list.html'
    context_object_name = 'messages_draft'

    def get_queryset(self):
        """Выбираем только неотправленные сообщения"""
        return Message.objects.filter(is_sent=False)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['context_name'] = 'Черновик'
        context['all_messages'] = Message.objects.all().filter(is_sent=False)
        context['is_draft_page'] = True
        return context


class MessageSentView(ListView):
    """Отправленные сообщения"""
    models = Message
    fields = ['topic', 'body', 'is_sent']
    template_name = 'messenger/msg_list.html'
    context_object_name = 'messages_sent'

    def get_queryset(self):
        """Выбираем только отправленные сообщения"""
        return Message.objects.filter(is_sent=True)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['context_name'] = 'Отправленные сообщения'
        context['all_messages'] = Message.objects.all().filter(is_sent=True)
        context['is_sent_page'] = True
        return context


class MessageCreateView(LoginRequiredMixin, CreateView):
    """Ручное создание сообщения"""
    model = Message
    form_class = MessageForm
    template_name = 'messenger/msg_form.html'
    success_url = reverse_lazy('messenger:draft_msg')
    context_object_name = 'create_msg'

    def form_valid(self, form):
        """
        Обработка валидной формы
        и ручная отправка сообщения
        """
        self.object = form.save()
        if self.object.is_sent:
            result = sending_msg(
                sender_email=SENDER,
                recipient_email=[self.object.recipient_email],
                subject=self.object.topic,
                body=self.object.body
            )
            if result.get('status') == 'success':
                self.object.is_sent = True
                self.object.save()
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    """Изменение сообщения"""
    model = Message
    form_class = MessageForm
    template_name = 'messenger/msg_form.html'
    success_url = reverse_lazy('messenger:draft_msg')
    context_object_name = 'update_msg'

    def form_valid(self, form):
        """Обработка формы после изменений"""
        return MessageCreateView().form_valid(form)


class MessageDetailView(DetailView):
    """Детальная информация о сообщении"""
    model = Message
    template_name = 'messenger/msg_detail.html'


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление сообщения"""
    model = Message
    template_name = 'messenger/msg_delete.html'
    success_url = reverse_lazy('messenger:draft_msg')


class MailingListView(ListView):
    """Список всех рассылок"""
    model = Mailing
    template_name = 'messenger/mailing_list.html'
    context_object_name = 'mailings'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_filter'] = 'all'
        return context


class MailingCreatedView(LoginRequiredMixin, ListView):
    """Отображение рассылок по категории 'Создана'"""
    model = Mailing
    template_name = 'messenger/mailing_list.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        return super().get_queryset().filter(mailing_status='created')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_filter'] = 'created'
        return context


class MailingRunningView(ListView):
    """Отображение рассылок по категории 'Запущено'"""
    model = Mailing
    template_name = 'messenger/mailing_list.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        now = timezone.now()
        Mailing.objects.filter(
            mailing_status='running',
            end_datetime__lt=now
        ).update(mailing_status='completed')
        return super().get_queryset().filter(mailing_status='running')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_filter'] = 'running'
        context['now_datetime'] = timezone.now()
        return context


class MailingCompletedView(ListView):
    """Отображение рассылок по категории 'Завершено'"""
    model = Mailing
    template_name = 'messenger/mailing_list.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        return super().get_queryset().filter(mailing_status='completed')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_filter'] = 'completed'
        return context


class MailingCreateView(LoginRequiredMixin, CreateView):
    """Создание объекта рассылки"""
    model = Mailing
    form_class = MailingForm
    template_name = 'messenger/mailing_form.html'
    success_url = reverse_lazy('messenger:mailing_created')


class MailingDetailView(DetailView):
    """Детальная информация о рассылке"""
    model = Mailing
    template_name = 'messenger/mailing_detail.html'


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    """Обновление информации в объекте рассылки"""
    model = Mailing
    form_class = MailingForm
    template_name = 'messenger/mailing_form.html'
    success_url = reverse_lazy('messenger:mailing_created')


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление объекта рассылки"""
    model = Mailing
    template_name = 'messenger/mailing_delete.html'
    success_url = reverse_lazy('messenger:mailing_list')


class RecipientListView(ListView):
    """Список получателей"""
    model = Recipient
    template_name = 'messenger/recipient_list.html'
    context_object_name = 'recipients'


class RecipientCreateView(LoginRequiredMixin, CreateView):
    """Создание получателя"""
    model = Recipient
    form_class = RecipientForm
    template_name = 'messenger/recipient_form.html'
    success_url = reverse_lazy('messenger:recipients_list')


class RecipientUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование получателя"""
    model = Recipient
    form_class = RecipientForm
    template_name = 'messenger/recipient_form.html'
    success_url = reverse_lazy('messenger:recipients_list')


class RecipientDetailView(DetailView):
    """Детальная информация о получателе"""
    model = Recipient
    template_name = 'messenger/recipient_detail.html'


class RecipientDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление получателя"""
    model = Recipient
    template_name = 'messenger/recipient_delete.html'
    success_url = reverse_lazy('messenger:recipients_list')
