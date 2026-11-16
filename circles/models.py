import secrets
import string

from django.db import models

from accounts.models import CustomUser


def generate_invite_code():
    """Makes a random 8-character code that no other circle uses."""
    characters = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(secrets.choice(characters) for _ in range(8))
        if not FamilyCircle.objects.filter(invite_code=code).exists():
            return code


class FamilyCircle(models.Model):
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='circles_created')
    circle_name = models.CharField(max_length=100)
    invite_code = models.CharField(max_length=20, unique=True, default=generate_invite_code)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.circle_name


class FamilyMember(models.Model):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrator'
        MEMBER = 'MEMBER', 'Member'

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        REMOVED = 'REMOVED', 'Removed'

    family_circle = models.ForeignKey(FamilyCircle, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBER)
    membership_status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    location_sharing_enabled = models.BooleanField(default=False)
    joined_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['family_circle', 'user']

    def __str__(self):
        return f'{self.user.username} in {self.family_circle.circle_name}'