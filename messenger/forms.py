from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

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
    "радар",
]


class MessageForm(forms.ModelForm):
    """Форма для ручного создания и обновления сообщения"""

    class Meta:
        model = Message
        fields = ["topic", "body", "recipient_email", "is_sent"]

    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)

        for field_name in self.fields:
            self.fields[field_name].help_text = None

        self.fields["topic"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Введите тему письма"}
        )
        self.fields["body"].widget.attrs.update(
            {"class": "form-control", "placeholder": " . . . "}
        )
        self.fields["recipient_email"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Введите email-адрес получателя"}
        )
        self.fields["is_sent"].widget.attrs.update(
            {
                "class": "form-check-input",
                "style": "margin-left: 10px; width: 20px; height: 20px;",
            }
        )
        self.fields["is_sent"].label = "Отправить письмо сразу"

    def clean(self):
        """Делает поля обязательными"""
        cleaned_data = super().clean()
        # # >>
        if cleaned_data.get("is_sent"):
            required_fields = ["topic", "body", "recipient_email"]
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, "Это поле обязательно для отправки письма")


class MailingForm(forms.ModelForm):
    """Форма для создания и редактирования рассылок"""

    create_new_message = forms.BooleanField(
        required=False,
        label="Создать новое сообщение",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    class Meta:
        model = Mailing
        fields = [
            "start_datetime",
            "end_datetime",
            "mailing_status",
            "message",
            "recipients",
            "create_new_message",
        ]
        widgets = {
            "start_datetime": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"}
            ),
            "end_datetime": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"}
            ),
            "message": forms.Select(attrs={"class": "form-select"}),
            "recipients": forms.SelectMultiple(
                attrs={"class": "form-select", "size": "5"}
            ),
        }

    def __init__(self, *args, **kwargs):
        self.message_form = kwargs.pop("message_form", None)
        super().__init__(*args, **kwargs)
        self.fields["message"].queryset = Message.objects.all()

        if "recipient_email" in self.fields:
            del self.fields["recipient_email"]
        if self.message_form is None:
            self.message_form = MessageForm(prefix="message")
        for field in self.fields.values():
            if field.widget.__class__ not in [forms.CheckboxInput]:
                field.widget.attrs.update({"class": "form-control"})

    def clean(self):
        cleaned_data = super().clean()
        create_new = cleaned_data.get("create_new_message")
        if create_new:
            if "message" in self._errors:
                del self._errors["message"]
            self.message_form = MessageForm(data=self.data, prefix="message")
            if not self.message_form.is_valid():
                raise forms.ValidationError(
                    "Пожалуйста, исправьте ошибки в форме сообщения"
                )
        else:
            if not cleaned_data.get("message"):
                raise forms.ValidationError("Выберите сообщение или создайте новое")
        return cleaned_data

    def save(self, commit=True):
        mailing = super().save(commit=False)
        if self.cleaned_data.get("create_new_message"):
            # Создание нового сообщения
            message = self.message_form.save(commit=commit)
            mailing.message = message
        if commit:
            mailing.save()
            self.save_m2m()  # ManyToMany (Recipients)
        return mailing


class MailingManagerForm(forms.ModelForm):
    """Права доступа для менеджера на внесении изменений в рассылку"""

    class Meta:
        model = Mailing
        fields = ["mailing_status"]


class RecipientForm(forms.ModelForm):
    """Форма для создания и редактирования получателей рассылок"""

    class Meta:
        model = Recipient
        fields = ["email", "fullname", "comment"]

    def __init__(self, *args, **kwargs):
        super(RecipientForm, self).__init__(*args, **kwargs)

        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update(
                {
                    "class": "form-control",
                    "placeholder": f"Введите: {self.fields[field_name].label}",
                }
            )

    def clean_email(self):
        """Валидация формата email"""
        email = self.cleaned_data.get("email")

        try:
            validate_email(email)  # Стандартный валидатор Django
        except ValidationError:
            raise ValidationError("Введите корректный email адрес")

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
