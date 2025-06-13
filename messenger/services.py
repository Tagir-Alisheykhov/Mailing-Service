import os
from dotenv import load_dotenv
from django.core.mail import send_mail
from messenger.models import Message

load_dotenv()

SENDER = os.getenv('EMAIL_HOST_USER')

stats = {
    # 'total': unsent_messages.count(),
    'success': 0,
    'errors': []
}


# def the_logic_of_sending_a_msg(sender, recipient):
#     """
#     Логика для ручной отправки сообщения на почту.
#     :param self:
#     :param sender: Почта отправителя.
#     :return:
#     """
#     messages = Message.objects.filter(is_sent=False)
#     for message in messages:
#         send_mail(
#             message.topic,
#             message.body,
#             from_email=SENDER,
#             recipient_list=['alisheykhov99@gmail.com']
#         )
#         message.is_sent = True
#         message.save()
#         self.stdout.write(self.style.SUCCESS(f'Sent: {message.topic}'))


def the_logic_of_sending_a_msg(sender_email, recipient_email, subject, body):
    """
    Отправка всех неотправленных сообщений
    :param sender_email: Email отправителя (str)
    :param recipient_email: Список email получателей (list[str])
    :return: Статистика отправки (dict)
    """
    try:
        result = send_mail(
            subject=subject,
            message=body,
            from_email=sender_email,
            recipient_list=recipient_email,
            fail_silently=False
        )
        stats['success'] += 1
        return {'status': 'success', 'result': result}
    except Exception as e:
        error_msg = str(e)
        stats['errors'].append({'error': error_msg})
        return {'status': 'error', 'error': error_msg}
