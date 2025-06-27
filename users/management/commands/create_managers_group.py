from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    """
    Команда для вызова:
    - `python manage.py create_managers_group` (вызов с заданными параметрами по умолчанию)
    Флаги:
    - `--group <"Super Managers"`> (вызов с кастомным именем группы (без ><))
    - `--permissions <view_mailing> <view_customuser>` (вызов с кастомными правами (без ><))
    """

    help = 'Creates or updates a user group with specified permissions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--group',
            type=str,
            default='Managers',
            help='Name of the group to create/update'
        )
        parser.add_argument(
            '--permissions',
            type=str,
            nargs='+',
            default=[
                'can_disable_mailing',
                'view_mailing',
                'view_mailingattempt',
                'view_message',
                'view_recipient',
                'view_customuser'
            ],
            help='List of permission codenames to add to the group'
        )

    def handle(self, *args, **options):
        group_name = options['group']
        permission_codenames = options['permissions']

        # Получение или создание группы
        group, created = Group.objects.get_or_create(name=group_name)

        if created:
            self.stdout.write(self.style.SUCCESS(f'Successfully created group "{group_name}"'))
        else:
            self.stdout.write(f'Group "{group_name}" already exists. Updating permissions.')

        # Очистка текущего права (если нужно сохранить существующие, удалите эту строку)
        group.permissions.clear()

        # Добавление новых прав
        added_count = 0
        for codename in permission_codenames:
            try:
                permission = Permission.objects.get(codename=codename)
                group.permissions.add(permission)
                added_count += 1
                self.stdout.write(f'Added permission: {codename}')
            except Permission.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Permission "{codename}" does not exist. Skipping.'))

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully {"created" if created else "updated"} group "{group_name}" '
                f'with {added_count} permissions'
            )
        )
