from django.urls import path
from . import views
from . import apps

# app_name = apps.MessengerConfig.name
app_name = 'messenger'


urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('draft-msgs/', views.MessageDraftView.as_view(), name='draft_msg'),
    path('sent-msgs/', views.MessageSentView.as_view(), name='sent_msg'),
    path('create-msg/', views.MessageCreateView.as_view(), name='create_msg'),
    path('edit-msg/<int:pk>', views.MessageUpdateView.as_view(), name='update_msg'),
    path('detail-msg/<int:pk>', views.MessageDetailView.as_view(), name='detail_msg'),
    path('delete-msg/<int:pk>', views.MessageDeleteView.as_view(), name='delete_msg'),
]
