from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """Форма для создания пользователя"""

    phone_number = forms.CharField(
        max_length=15,
        required=False,
        help_text='Необязательное поле. Введите ваш номер телефона'
    )
    username = forms.CharField(
        max_length=50,
        required=True
    )

    class Meta:
        model = CustomUser
        fields = (
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'username',
            'password1',
            'password2'
        )

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number and not phone_number.isdigit():
            raise forms.ValidationError('Номер телефона должен состоять только из цифр')
        return phone_number


class CustomUserChangeForm(UserChangeForm):
    """Форма для редактирования данных пользователя"""
    class Meta:
        model = CustomUser
        fields = (
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'username'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'password' in self.fields:
            del self.fields['password']

        for field_name, field in self.fields.items():
            if hasattr(field, 'help_text') and field.help_text:
                field.help_text = field.help_text.replace('../password/', '')

        assert 'password' not in self.fields, \
            "ОШИБКА: Поле пароля всё ещё присутствует в форме"
