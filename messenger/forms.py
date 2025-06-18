from django import forms
from django.core.exceptions import ValidationError

from .models import Message, Mailing


class MessageForm(forms.ModelForm):
    """Форма для ручного создания и обновления сообщения"""

    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)

        for field_name in self.fields:
            self.fields[field_name].help_text = None

        self.fields['topic'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите тему письма'
        })
        self.fields['body'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': ' . . . '
        })
        self.fields['recipient_email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите email-адрес получателя'
        })
        self.fields['is_sent'].widget.attrs.update({
            'class': 'form-check-input',
            'style': 'margin-left: 10px; width: 20px; height: 20px;'
        })
        self.fields['is_sent'].label = 'Отправить письмо сразу'

    def clean(self):
        """Делает поля обязательными"""
        cleaned_data = super().clean()
        required_fields = ['topic', 'body', 'recipient_email']
        for field in required_fields:
            if not cleaned_data.get(field):
                self.add_error(field, 'Обязательное поле.')
        return cleaned_data

    class Meta:
        model = Message
        fields = ['topic', 'body', 'recipient_email', 'is_sent']


class MailingForm(forms.ModelForm):
    """Форма для создания и редактирования рассылок"""

    def __init__(self, *args, **kwargs):
        super(MailingForm, self).__init__(*args, **kwargs)

        for field_name in self.fields:
            self.fields[field_name].help_text = None
            self.fields[field_name].widget.attrs.update({
                'class': 'form-control',
                'placeholder': f'Введите: {self.fields[field_name].label}'
            })
        self.fields['start_datetime'].widget = forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        })
        self.fields['end_datetime'].widget = forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        })

    def clean(self):
        """
        Валидация на то, чтобы время окончания
        не было раньше времени начала
        """
        cleaned_data = super().clean()
        start_datetime = cleaned_data.get('start_datetime')
        end_datetime = cleaned_data.get('end_datetime')
        if start_datetime and end_datetime and end_datetime < start_datetime:
            raise ValidationError(
                "Дата окончания рассылки не может быть раньше даты начала!"
            )
        return cleaned_data

    class Meta:
        model = Mailing
        fields = [
            'start_datetime',
            'end_datetime',
            'mailing_status',
            'message',
            'recipients'
        ]
