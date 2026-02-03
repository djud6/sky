from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from .db_constants import Constants

class UserManager(BaseUserManager):

  def _create_user(self, email, password, db_access=None, is_staff=False, is_superuser=False, **extra_fields): 
    if not email:
        raise ValueError('Users must have an email address')
    
    if db_access is None:
        db_access = "default" 
        
    now = timezone.now()
    email = self.normalize_email(email)
    user = self.model(
        username=email,
        email=email,
        is_staff=is_staff, 
        is_active=True,
        is_superuser=is_superuser, 
        last_login=now,
        date_joined=now, 
        db_access=db_access,
        **extra_fields
    )
    user.set_password(password)
    user.save()
    return user

  def create_user(self, email, password, **extra_fields): 
    db_access = extra_fields.pop('db_access', 'default')
    return self._create_user(email, password, db_access, False, False, **extra_fields)

  def create_superuser(self, email, password, **extra_fields): 
    db_access = extra_fields.pop('db_access', 'default')
    user=self._create_user(email, password, db_access, True, True, **extra_fields)
    return user