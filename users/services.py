import os
from dotenv import load_dotenv
from django.core.mail import send_mail

load_dotenv()


def send_welcome_email(user_email):
    """
    Отправка приветственного сообщения
    новым пользователям.
    """
    subject = 'Добро пожаловать в наш сервис'
    message = 'Спасибо, что зарегистрировались в нашем сервисе'
    from_email = os.getenv('EMAIL_HOST_USER')
    recipient_list = [user_email]
    send_mail(subject, message, from_email, recipient_list)
