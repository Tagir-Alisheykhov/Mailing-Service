from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """Кастомное создание пользователя"""

    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True
    )
    token = models.CharField(
        max_length=100,
        verbose_name='Token',
        blank=True,
        null=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username',]

    def __str__(self):
        return self.email

