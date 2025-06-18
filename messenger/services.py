import os
import smtplib
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings
from dotenv import load_dotenv
from django.core.mail import send_mail

from messenger.models import Mailing, MailingAttempt, Recipient

load_dotenv()

SENDER = os.getenv('EMAIL_HOST_USER')


def send_mailing_attempt():
    """
    Логика попытки отправки рассылки по почте.
    """
    for obj in Mailing.objects.filter(mailing_status='running'):
        start_dt = obj.start_datetime
        current_dt = timezone.now()
        end_dt = obj.end_datetime
        start_dt = (
            timezone.make_aware(start_dt)
            if timezone.is_naive(start_dt)
            else start_dt
        )
        end_dt = (
            timezone.make_aware(end_dt)
            if timezone.is_naive(end_dt)
            else end_dt
        )
        if start_dt < current_dt < end_dt:
            try:
                target_email_addresses = [
                    client.email for client in Recipient.objects.all()
                ]
                email_server_response = send_mail(
                    subject=str(obj.message.topic),
                    message=str(obj.message.body),
                    from_email=SENDER,
                    recipient_list=target_email_addresses,
                    fail_silently=False
                )
                attempt = MailingAttempt.objects.create(
                    mailing=obj,
                    mail_server_response=email_server_response,
                    sending_status=MailingAttempt.SUCCESSFULLY,
                )
                attempt.save()
            except smtplib.SMTPException as err:
                attempt_err = MailingAttempt.objects.create(
                    mailing=obj,
                    mail_server_response=f'\nОшибка отправки: \n{str(err)}',
                    sending_status=MailingAttempt.UNSUCCESSFULLY
                )
                attempt_err.save()
            except Exception as err:
                print(f'Exception error: {err}')


def sending_msg(sender_email, recipient_email, subject, body):
    """
    Отправка всех неотправленных сообщений
    :param sender_email: Email отправителя (str)
    :param recipient_email: Список email получателей (list[str])
    :return: Статистика отправки (dict)
    """
    stats_msgs = {
        # 'total': unsent_messages.count(),
        'success': 0,
        'errors': []
    }
    try:
        result = send_mail(
            subject=subject,
            message=body,
            from_email=sender_email,
            recipient_list=recipient_email,
            fail_silently=False
        )
        stats_msgs['success'] += 1
        return {'status': 'success', 'result': result}
    except Exception as e:
        error_msg = str(e)
        stats_msgs['errors'].append({'error': error_msg})
        return {'status': 'error', 'error': error_msg}


def get_recipients_from_cache():
    """Получение кэшированных данных о получателях"""
    if not settings.CACHE_ENABLED:
        return Recipient.objects.all()
    else:
        key = 'recipients'
        recipients = cache.get(key)
        if not recipients:
            recipients = Recipient.objects.all()
            cache.set(key, recipients, 10)
        return recipients


def get_mailing_from_cache():
    """Получение кэшированных данных о рассылках"""
    if not settings.CACHE_ENABLED:
        return Mailing.objects.all()
    else:
        key = 'mailings'
        mailings = cache.get(key)
        if not mailings:
            mailings = Mailing.objects.all()
            cache.set(key, mailings, 10)
        return mailings


# def get_active_mailing_from_cache() -> list:
#     """Получение кэшированных данных о рассылках"""
#     if not settings.CACHE_ENABLED:
#         return Mailing.objects.all()
#     else:
#         key = 'mailings'
#         mailings = cache.get(key)
#         if not mailings:
#             mailings = Mailing.objects.all()
#             cache.set(key, mailings, 10)
#         return list(mailings)

