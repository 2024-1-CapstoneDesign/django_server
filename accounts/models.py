from django.contrib.auth.models import AbstractUser
from django.db import models
# Create your models here.
class User(AbstractUser):
    name = models.CharField(max_length=254, null=True, blank=True)
    picture = models.CharField(max_length=254, null=True, blank=True)

    class Meta:
        db_table = 'member'

    @staticmethod
    def get_user_or_none_by_email(email):
        try:
            return User.objects.get(email=email)
        except Exception:
            return None
