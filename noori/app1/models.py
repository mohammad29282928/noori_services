# Create your models here.
import uuid
import os
from django.db.models                   import UUIDField, TextField, CharField, ForeignKey, CASCADE, ImageField
from django.db.models                   import BooleanField, DateTimeField, Model, FloatField, IntegerField
from django.contrib.auth.models         import AbstractUser
from .utils.manager                     import UserManager
from django.core.validators             import RegexValidator
from django.db                          import models

def user_image_directory(instance, filename):
    ext      = filename.split('.')[-1]              # Seprate the file ext.
    filename = "%s.%s" % (str(uuid.uuid4()), ext)   # rename the file 
    return os.path.join(f"userImages/{filename}")


def user_avatar_directory(instance, filename):
    ext      = filename.split('.')[-1]              # Seprate the file ext.
    filename = "%s.%s" % (str(uuid.uuid4()), ext)   # rename the file 
    return os.path.join(f"userAvatars/{filename}")



class Agent(Model):
    created_at          = DateTimeField(auto_now_add = True)
    updated_at          = DateTimeField(auto_now_add = True)
    # owner               = ForeignKey(User, related_name = 'owner', on_delete = CASCADE)
    title               = CharField(max_length=190) 
    description         = TextField(blank = True, null =True) 

    def __str__(self):
        return str(self.title)


permision_types = [
    ('1', 'normal user'),
    ('2', 'type 2'),
]


class User(AbstractUser):
    phone           = CharField(max_length=17, blank = False, unique = False, validators=[RegexValidator(r'^\d{1,10}$')])
    image           = ImageField(upload_to = user_image_directory, null = True, blank = True)
    avatar          = ImageField(upload_to = user_avatar_directory, null = True, blank = True)
    is_superuser    = BooleanField(default=False)
    objects         = UserManager()
    last_seen       = DateTimeField(auto_now_add=True)
    agent           = ForeignKey(Agent, related_name = 'user_agent', on_delete = CASCADE, null = True, blank = True)
    permision_type  = CharField( max_length = 50, default="1", choices = permision_types)
    trend_permission               = BooleanField(default=False)
    is_active                      = BooleanField(default=True)
    segmentation_permission        = BooleanField(default=False)
    info_permission                = BooleanField(default=False)
    adduser_permission             = BooleanField(default=False)
    deluser_permission             = BooleanField(default=False)
    edituser_permission            = BooleanField(default=False)
    agent_permission               = BooleanField(default=False)
    importdata_permission          = BooleanField(default=False)
    sendsms_permission             = BooleanField(default=False)

    def __str__(self):
        return str(self.username)
