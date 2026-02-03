from django.db import models
from .user_manager import UserManager
from .User import User

class UserModelHistory(models.Model):

    user_history_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    date = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(unique=False)
    username = models.CharField(max_length=100)
    password = models.TextField(max_length=10000)
    db_access = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    is_superuser = models.BooleanField()
    is_staff = models.BooleanField()
    is_active = models.BooleanField()


    def __str__(self):
        return self.email