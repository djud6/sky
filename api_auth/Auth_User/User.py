from django.contrib.auth.models import AbstractUser
import uuid
from django.db import models
from .user_manager import UserManager

class User(AbstractUser):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    db_access = models.CharField(max_length=50)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = [] 

    objects = UserManager()

    def __str__(self):
        return self.email