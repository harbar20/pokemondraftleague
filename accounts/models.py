from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.files.storage import default_storage as storage
from PIL import Image
from enum import Enum

class profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    timezone = models.CharField(max_length=30, null=True,blank=True)
    pfp = models.ImageField(default='profile_pics/defaultpfp.png',upload_to='profile_pics',null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'

class sitesettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sprite = models.CharField(max_length=20,choices=(
        ("xyani.gif","XY Animated"),
        ("xyani-shiny.gif","XY Shiny Animated"),
        ("xyani.png","XY"),
        ("xyani-shiny.png","XY Shiny"),
        ("bw.png","BW"),
        ("bw-shiny.png","BW Shiny"),
        ("afd.png","April Fools Day"),
        ("afd-shiny.png","April Fools Day Shiny"),
        ),
        default="xyani.gif")