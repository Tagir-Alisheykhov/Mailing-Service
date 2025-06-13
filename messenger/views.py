import os
from dotenv import load_dotenv
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    TemplateView
)
from django.views.generic.edit import (
    CreateView,
    UpdateView,
    DeleteView,
)

from .forms import MessageForm
from .models import Message
from .services import the_logic_of_sending_a_msg

load_dotenv()

SENDER = os.getenv('EMAIL_HOST_USER')


class HomePageView(TemplateView):
    """Домашняя станица"""
    models = Message
    template_name = 'messenger/home.html'

    def get_context_data(self,  *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'total_campaigns': 127,
                'active_campaigns': 9,
                'unique_recipients': 48362
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
        return context


class MessageCreateView(CreateView):
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
            result = the_logic_of_sending_a_msg(
                sender_email=SENDER,
                recipient_email=[self.object.recipient_email],
                subject=self.object.topic,
                body=self.object.body
            )
            if result.get('status') == 'success':
                self.object.is_sent = True
                self.object.save()
        return super().form_valid(form)


class MessageUpdateView(UpdateView):
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


class MessageDeleteView(DeleteView):
    """Удаление сообщения"""
    model = Message
    template_name = 'messenger/msg_delete.html'
    success_url = reverse_lazy('messenger:draft_msg')
