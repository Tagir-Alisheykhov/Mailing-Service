import os
from dotenv import load_dotenv
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from messenger.models import Message

load_dotenv()

SENDER = os.getenv('EMAIL_HOST_USER')


class Command(BaseCommand):
    """Ручная отправка сообщений на почту"""
    help = 'Send messages'

    def handle(self, *args, **kwargs):
        messages = Message.objects.filter(is_sent=False)
        for message in messages:
            send_mail(
                message.topic,
                message.body,
                SENDER,  # Замените на ваш email
                ['mock@gmail.com'],  # Замените на email получателя
            )
            message.is_sent = True
            message.save()
            self.stdout.write(self.style.SUCCESS(f'Sent: {message.topic}'))
