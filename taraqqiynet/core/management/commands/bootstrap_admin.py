import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "ADMIN_USERNAME/ADMIN_PASSWORD environment o'zgaruvchilari asosida "
        "admin hisob yaratadi (Render Shell'siz ishlaydi, build.sh ichida chaqiriladi)"
    )

    def handle(self, *args, **options):
        username = os.environ.get("ADMIN_USERNAME")
        password = os.environ.get("ADMIN_PASSWORD")

        if not username or not password:
            self.stdout.write(
                "ADMIN_USERNAME yoki ADMIN_PASSWORD berilmagan, admin yaratish o'tkazib yuborildi."
            )
            return

        User = get_user_model()
        user, created = User.objects.get_or_create(username=username)

        if created:
            user.set_password(password)

        user.role = "admin"
        user.is_staff = True
        user.is_superuser = True
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f"Admin '{username}' yaratildi."))
        else:
            self.stdout.write(
                f"'{username}' allaqachon mavjud edi — admin huquqlari yangilandi "
                f"(parol o'zgartirilmadi)."
            )