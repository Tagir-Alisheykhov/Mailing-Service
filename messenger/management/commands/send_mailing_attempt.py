from django.core.management.base import BaseCommand

from messenger.services import send_mailing_attempt


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        """Попытка отправки рассылки"""
        send_mailing_attempt()
