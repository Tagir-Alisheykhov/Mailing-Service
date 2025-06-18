import os
from dotenv import load_dotenv
from django.core.management.base import BaseCommand

from messenger.services import send_mailing_attempt

from messenger.models import Mailing


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        """Попытка отправки рассылки"""
        # Создаем объект.
        # create_mock_mailing = Mailing.objects.create(
        #     ''
        # )
        print('Начало попытки')
        send_mailing_attempt()
        print('Конец попытки')









# 2
# def the_logic_of_sending_a_msg(sender_email, recipient_email, subject, body):
#     """
#     Отправка всех неотправленных сообщений
#     :param sender_email: Email отправителя (str)
#     :param recipient_email: Список email получателей (list[str])
#     :return: Статистика отправки (dict)
#     """
#     try:
#         result = send_mail(
#             subject=subject,
#             message=body,
#             from_email=sender_email,
#             recipient_list=recipient_email,
#             fail_silently=False
#         )
#         stats['success'] += 1
#         return {'status': 'success', 'result': result}
#     except Exception as e:
#         error_msg = str(e)
#         stats['errors'].append({'error': error_msg})
#         return {'status': 'error', 'error': error_msg}



# 1
# class Command(BaseCommand):
#     """Ручная отправка сообщений на почту"""
#     help = 'Send messages'
#
#     def handle(self, *args, **kwargs):
#         messages = Message.objects.filter(is_sent=False)
#         for message in messages:
#             send_mail(
#                 message.topic,
#                 message.body,
#                 SENDER,  # Замените на ваш email
#                 ['mock@gmail.com'],  # Замените на email получателя
#             )
#             message.is_sent = True
#             message.save()
#             self.stdout.write(self.style.SUCCESS(f'Sent: {message.topic}'))
