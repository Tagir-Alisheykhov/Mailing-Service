from django import forms
from .models import Message


class MessageForm(forms.ModelForm):
    """Форма для ручного создания и обновления сообщения"""
    class Meta:
        model = Message
        fields = ['topic', 'body', 'recipient_email', 'is_sent']

    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)

        for field_name in self.fields:
            self.fields[field_name].help_text = None

        self.fields['topic'].widget.attrs.update(
            {
                'class': 'form-control',
                'placeholder': 'Введите тему письма'
            }
        )

        self.fields['body'].widget.attrs.update(
            {
                'class': 'form-control',
                'placeholder': ' . . . '
            }
        )

        self.fields['recipient_email'].widget.attrs.update(
            {
                'class': 'form-control',
                'placeholder': 'Введите email-адрес получателя'
            }
        )

        self.fields['is_sent'].widget.attrs.update(
        {
            'class': 'form-check-input',
            'style': 'margin-left: 10px; width: 20px; height: 20px;'
            }
        )
        self.fields['is_sent'].label = 'Отправить письмо сразу'

    def clean(self):
        """Делает поля обязательными"""
        cleaned_data = super().clean()
        required_fields = ['topic', 'body', 'recipient_email']
        for field in required_fields:
            if not cleaned_data.get(field):
                self.add_error(field, 'Обязательное поле.')
        return cleaned_data
