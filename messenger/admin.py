from django.contrib import admin

from .models import Message, Mailing, MailingAttempt, Recipient


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("topic", "body")
    search_fields = ("topic",)


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = (
        "start_datetime",
        "end_datetime",
        "mailing_status",
        "message",
    )
    list_filter = ("recipients",)
    search_fields = ("start_datetime", "end_datetime", "recipients")


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = (
        "sending_datetime",
        "sending_status",
        "mail_server_response",
        "mailing",
    )
    search_fields = ("mailing", "sending_datetime", "sending_status")


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ("email", "fullname", "comment")
    list_filter = ("fullname",)
    search_fields = ("email", "fullname", "comment")
