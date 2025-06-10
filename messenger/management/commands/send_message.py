from django.core.management.base import BaseCommand

from messenger.models import Message


class Command(BaseCommand):
    help = 'Sending messages to specified post addresses'

    def handle(self, *args, **kwargs):
        pass







# from django.core.mail import send_mail
# from yourapp.models import Message
#
# class Command(BaseCommand):
#     help = 'Send messages'
#
#     def handle(self, *args, **kwargs):
#         messages = Message.objects.filter(is_sent=False)
#         for message in messages:
#             send_mail(
#                 message.subject,
#                 message.body,
#                 'from@example.com',  # Замените на ваш email
#                 ['to@example.com'],  # Замените на email получателя
#             )
#             message.is_sent = True
#             message.save()
#             self.stdout.write(self.style.SUCCESS(f'Sent: {message.subject}'))



# from django.core.mail import send_mail
#
# send_mail(
#     subject="Тема письма",
#     message="Текст письма",
#     from_email="отправитель@example.com",
#     recipient_list=["получатель1@example.com", "получатель2@example.com"],
#     fail_silently=False,  # Если True, ошибки не будут вызывать исключений
# )