from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, validate_email

from .models import Message, Mailing, Recipient

FORBIDDEN_WORDS = [
    "казино",
    "криптовалюта",
    "крипта",
    "биржа",
    "дешево",
    "бесплатно",
    "обман",
    "полиция",
    "радар"
]


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


class RecipientForm(forms.ModelForm):
    """Форма для создания и редактирования получателей рассылок"""

    # email = forms.EmailField(validators=[EmailValidator()])

    def __init__(self, *args, **kwargs):
        super(RecipientForm, self).__init__(*args, **kwargs)

        for field_name in self.fields:
            self.fields[field_name].help_text = None
            self.fields[field_name].widget.attrs.update({
                'class': 'form-control',
                'placeholder': f'Введите: {self.fields[field_name].label}'
            })

    def clean_email(self):
        """Валидация формата email"""
        email = self.cleaned_data.get('email')

        try:
            validate_email(email)  # Стандартный валидатор Django
        except ValidationError:
            raise ValidationError('Введите корректный email адрес')

        return email

    def clean_fullname(self):
        """Валидация поля с названием товара."""
        name = self.cleaned_data.get("fullname")
        for keyword in FORBIDDEN_WORDS:
            if name.strip() == keyword.upper() or name.strip() == keyword.lower():
                raise ValidationError(
                    f"Слово '{name}' входит в список запрещенных слов!"
                )
        return name

    def clean_comment(self):
        """Валидация поля с описанием товара."""
        comment = self.cleaned_data.get("comment")
        for keyword in FORBIDDEN_WORDS:
            if keyword.upper() in comment or keyword.lower() in comment:
                raise ValidationError(
                    f"Слово '{comment}' входит в список запрещенных слов!"
                )
        return comment

    class Meta:
        model = Recipient
        fields = ['email', 'fullname', 'comment']
