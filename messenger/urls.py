from django.urls import path
from messenger.views import (
    HomePageView,
    MessageDraftView,
    MessageSentView,
    MessageCreateView,
    MessageUpdateView,
    MessageDetailView,
    MessageDeleteView,
    MailingListView,
    MailingCreatedView,
    MailingRunningView,
    MailingCompletedView,
    MailingCreateView,
    MailingDetailView,
    MailingUpdateView,
    MailingDeleteView,
    RecipientListView,
    RecipientCreateView,
    RecipientUpdateView,
    RecipientDetailView,
    RecipientDeleteView,
)

from messenger.apps import MessengerConfig

app_name = MessengerConfig.name


urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    # Сообщения
    path("draft-msgs/", MessageDraftView.as_view(), name="draft_msg"),
    path("sent-msgs/", MessageSentView.as_view(), name="sent_msg"),
    path("create-msg/", MessageCreateView.as_view(), name="create_msg"),
    path("edit-msg/<int:pk>/", MessageUpdateView.as_view(), name="update_msg"),
    path("detail-msg/<int:pk>/", MessageDetailView.as_view(), name="detail_msg"),
    path("delete-msg/<int:pk>/", MessageDeleteView.as_view(), name="delete_msg"),
    # Рассылки
    path("mailings/", MailingListView.as_view(), name="mailing_list"),
    path("mailings/created/", MailingCreatedView.as_view(), name="mailing_created"),
    path("mailings/running/", MailingRunningView.as_view(), name="mailing_running"),
    path(
        "mailings/completed/", MailingCompletedView.as_view(), name="mailing_completed"
    ),
    path("mailings/create/", MailingCreateView.as_view(), name="mailing_create"),
    path(
        "mailings/detail/<int:pk>/", MailingDetailView.as_view(), name="mailing_detail"
    ),
    path("mailings/edit/<int:pk>/", MailingUpdateView.as_view(), name="mailing_update"),
    path(
        "mailings/delete/<int:pk>/", MailingDeleteView.as_view(), name="mailing_delete"
    ),
    # Получатели
    path("recipients/", RecipientListView.as_view(), name="recipients_list"),
    path("recipients/create/", RecipientCreateView.as_view(), name="recipient_create"),
    path(
        "recipients/edit/<int:pk>/",
        RecipientUpdateView.as_view(),
        name="recipient_update",
    ),
    path(
        "recipients/detail/<int:pk>/",
        RecipientDetailView.as_view(),
        name="recipient_detail",
    ),
    path(
        "recipients/delete/<int:pk>/",
        RecipientDeleteView.as_view(),
        name="recipient_delete",
    ),
]
