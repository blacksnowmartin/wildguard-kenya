from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        COMMUNITY_MEMBER = 'COMMUNITY_MEMBER', 'Community member'
        RANGER = 'RANGER', 'Ranger'
        SUPERVISOR = 'SUPERVISOR', 'Supervisor'
        ADMIN = 'ADMIN', 'Administrator'

    role = models.CharField(max_length=24, choices=Role.choices, default=Role.COMMUNITY_MEMBER)
    phone_number = models.CharField(max_length=32, blank=True)

    def __str__(self) -> str:
        return self.get_full_name() or self.username
