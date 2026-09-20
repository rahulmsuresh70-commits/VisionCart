from django.contrib.auth.models import AbstractUser
from django.db import  models

class User(AbstractUser):

    class Role(models.TextChoices):
        SUPER_ADMIN = "SUPER_ADMIN", "Super Admin"
        WEB_ADMIN = "WEB_ADMIN", "Web Admin"
        CUSTOMER = "CUSTOMER", "Customer"

    email = models.EmailField(
        unique=True
    )

    phone = models.CharField(
        max_length=15,
        blank=True
    )

    profile_image = models.ImageField(
        upload_to="profile_images/",
        blank=True,
        null=True
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER
    )

    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"
