from __future__ import unicode_literals
from django.db import models
from .managers import UserManager
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import AbstractBaseUser

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('Email Address'), unique=True, db_index=True)
    first_name = models.CharField(_('First Name'), max_length=250, blank=True)
    last_name = models.CharField(_('Last Name'), max_length=250, blank=True)
    is_active = models.BooleanField(_('Active'), default=False)
    is_staff = models.BooleanField(_('Staff'), default=False)
    is_suspended = models.BooleanField(_('Suspended'), default=False) # True for payment fails
    
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name','last_name' ]

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        '''
        Displays email on admin panel
        '''
        return self.email
    