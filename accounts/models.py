from django.contrib.auth.models import AbstractUser
# Create your models here.
class User(AbstractUser):
    pass

    @staticmethod
    def get_user_or_none_by_email(email):
        try:
            return User.objects.get(email=email)
        except Exception:
            return None