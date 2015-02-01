import uuid
import random
import os

from django.conf import settings
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


NAMES = ['Liam', 'Emma', 'Noah', 'Olivia', 'Ethan', 'Sophia', 'Mason', 'Ava', 'Logan', 'Isabella', 'Lucas', 'Mia', 'Jacob', 'Charlotte', 'Aiden', 'Emily', 'Jackson', 'Abigail', 'Jack', 'Harper', 'Elijah', 'Avery', 'Benjamin', 'Madison', 'James', 'Ella', 'Luke', 'Amelia', 'William', 'Lily', 'Michael', 'Chloe', 'Alexander', 'Sofia', 'Oliver', 'Evelyn', 'Gabriel', 'Hannah', 'Daniel', 'Zoey', 'Carter', 'Aria', 'Owen', 'Addison', 'Henry', 'Grace', 'Matthew', 'Aubrey', 'Ryan', 'Ellie', 'Jayden', 'Zoe', 'Wyatt', 'Audrey', 'Caleb', 'Natalie', 'Nathan', 'Elizabeth', 'Andrew', 'Scarlett', 'Dylan', 'Layla', 'Isaac', 'Victoria', 'Joshua', 'Brooklyn', 'Connor', 'Lucy', 'Sebastian', 'Claire', 'Hunter', 'Lillian', 'David', 'Anna', 'Eli', 'Mila', 'Landon', 'Nora', 'Samuel', 'Leah']


def file_name_generator(ins, filename):
    _, ext = os.path.splitext(filename)
    filename = '{}{}'.format(uuid.uuid4(), ext)
    return os.path.join('files', filename)


class ExtendedUserManager(BaseUserManager):
    def create_user(self, email, password=None, first_name=None, last_name=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        if first_name is None or last_name is None:
            first_name = random.choice(NAMES)
            last_name = 'Jung'

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(email,
                                password=password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class ExtendedUser(AbstractBaseUser):
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    lat = models.DecimalField(max_digits=10, decimal_places=7, default=0.0)
    lang = models.DecimalField(max_digits=10, decimal_places=7, default=0.0)
    placename = models.TextField(default='')
    address = models.TextField(default='')

    USERNAME_FIELD = 'email'

    objects = ExtendedUserManager()
    REQUIRED_FIELDS = []

    def get_full_name(self):
        # The user is identified by their email address
        return self.first_name + ' ' + self.last_name

    def get_short_name(self):
        # The user is identified by their email address
        return self.first_name

    def __unicode__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


class UserFiles(models.Model):
    userid = models.ForeignKey(ExtendedUser, related_name='files')
    uploaded_file = models.FileField(upload_to=file_name_generator, max_length=100)
    actual_name = models.CharField(max_length=100)
    upload_time = models.DateTimeField(auto_now_add=True)
