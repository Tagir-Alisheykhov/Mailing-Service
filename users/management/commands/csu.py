import os
from dotenv import load_dotenv
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

load_dotenv()

FIRSTNAME = os.getenv("SUPERUSER_FIRST_NAME")
LASTNAME = os.getenv("SUPERUSER_LAST_NAME")
PASSWORD = os.getenv("SUPERUSER_PASSWORD")
EMAIL = os.getenv("SUPERUSER_EMAIL")


class Command(BaseCommand):
    """Команда для создания суперпользователя"""

    def handle(self, *args, **options):
        us_model = get_user_model()
        user = us_model.objects.create(
            email=EMAIL, first_name=FIRSTNAME, last_name=LASTNAME
        )
        user.set_password(PASSWORD)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created superuser with email `{user.email}`!"
            )
        )
