from django.conf import settings
from django.db import models


class Recipient(models.Model):
    """Модель получателя рассылки."""

    email = models.EmailField(
        unique=True,
        verbose_name="Почтовый адрес получателя",
        help_text="Введите почтовый адрес получателя",
        blank=True,
        null=True,
    )
    fullname = models.CharField(verbose_name="ФИО получателя", help_text="Введите ФИО")
    comment = models.TextField(
        verbose_name="Комментарий",
        help_text="Введите комментарий",
        null=True,
        blank=True,
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Создатель получателя",
        on_delete=models.SET_NULL,
        related_name="recipients",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.fullname

    class Meta:
        verbose_name = "Получатель"
        verbose_name_plural = "Получатели"
        ordering = ["fullname"]


class Message(models.Model):
    """Модель для управления сообщениями."""

    topic = models.CharField(
        verbose_name="Тема письма",
        help_text="Введите тему письма",
        null=True,
        blank=True,
    )
    body = models.TextField(
        verbose_name="Содержание письма",
        help_text="Введите содержимое письма",
        null=True,
        blank=True,
    )
    recipient_email = models.EmailField(
        verbose_name="Почтовый адрес получателя",
        help_text="Введите почтовый адрес получателя",
        null=True,
        blank=True,
    )
    is_sent = models.BooleanField(default=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Создатель сообщения",
        on_delete=models.SET_NULL,
        related_name="messages",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.topic

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"


class Mailing(models.Model):
    """Модель для управления рассылками."""

    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    MAILING_STATUS = [
        (CREATED, "Создана"),
        (RUNNING, "Запущена"),
        (COMPLETED, "Завершена"),
    ]

    start_datetime = models.DateTimeField(
        verbose_name="Время и дата начала рассылки",
        help_text="Укажите дату и время начала рассылки",
    )
    end_datetime = models.DateTimeField(
        verbose_name="Время и дата окончания рассылки",
        help_text="Укажите дату и время окончания рассылки",
    )
    mailing_status = models.CharField(
        verbose_name="Статус рассылки",
        max_length=10,
        choices=MAILING_STATUS,
        help_text="Выберите статус рассылки",
    )
    message = models.ForeignKey(
        Message,
        verbose_name="Сообщение рассылки",
        related_name="messenger",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    recipients = models.ManyToManyField(
        Recipient,
        verbose_name="Получатель рассылки",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Создатель рассылки",
        on_delete=models.SET_NULL,
        related_name="mailings",
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"Рассылка ({self.start_datetime} - {self.end_datetime})"

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        permissions = [
            ("can_view_statistics", "can view statistics"),
            ("can_disable_mailing", "can disable mailing"),
        ]


class MailingAttempt(models.Model):
    """Попытка отправки рассылки"""

    SUCCESSFULLY = "successfully"
    UNSUCCESSFULLY = "unsuccessfully"
    SENDING_STATUS = [(SUCCESSFULLY, "Успешно"), (UNSUCCESSFULLY, "Не успешно")]

    sending_datetime = models.DateTimeField(
        auto_now=True, verbose_name="Фиксация даты и времени отправки рассылки"
    )
    sending_status = models.CharField(
        verbose_name="Статус отправки рассылки", choices=SENDING_STATUS
    )
    mail_server_response = models.TextField(
        max_length=150, verbose_name="Ответ почтового сервера"
    )
    mailing = models.ForeignKey(
        Mailing, verbose_name="Рассылка", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"Попытка {self.sending_datetime} ({self.sending_status})"

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылок"
