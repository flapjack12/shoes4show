from django.utils import timezone
import uuid

from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.core.validators import MaxLengthValidator
import os

def item_image_upload_path(instance, filename):
    name = slugify(instance.name)
    ext = filename.split('.')[-1].lower()
    unique = uuid.uuid4().hex[:8] 
    new_filename = f"{name}-{unique}.{ext}"
    print(new_filename)
    return os.path.join('media/listing_images/', new_filename)
  
  

class DailyItemView(models.Model):
    item = models.ForeignKey('Item', on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    count = models.IntegerField(default=0)

    class Meta:
        unique_together = ('item', 'date')
        

class Item(models.Model):
    NAME_MAX_LENGTH = 128
    SORTING_OPTIONS = {"price":"price ascending", "-price":"price descending", 
                       "views":"views ascending", "-views":"views descending"}
    SHOES_CATEGORIES = {
    "HE": "Heels",
    "SN": "Sneakers",
    "SA": "Sandals",
    "BO": "Boots",
    "LO": "Loafers",
    "FS": "Formal Shoes",
    "SL": "Slippers",
    "FL": "Flats",
    "PU": "Pumps",
    "AT": "Athletic Shoes",
    "CL": "Clogs",
    "ES": "Espadrilles",
    }

    name = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)
    description = models.TextField(default="default description", validators=[MaxLengthValidator(250)])
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='listing_images/', blank=False)
    price = models.DecimalField(decimal_places=2, max_digits=8, validators=[MinValueValidator(0)], default=0.00)
    views = models.IntegerField(default=0)
    slug = models.SlugField(unique=True)
    category = models.CharField(choices=SHOES_CATEGORIES, null=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Item, self).save(*args, **kwargs)

    class Meta():
        verbose_name_plural = "Items"

    def __str__(self):
        return self.name
      
    
class Review(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    url = models.URLField(default='')
    views = models.IntegerField(default=0)

    def __str__(self):
        return self.title


def user_directory_path(instance,filename):
    extension = filename.split('.')[-1]
    return f'{instance.user.username}/profilepic/profile.{extension}'



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to=user_directory_path, blank=True, null=True)

    def __str__(self):
        return self.user.username

    def delete(self,*args, **kwargs):
        if self.picture and self.picture.path:
            if os.path.isfile(self.picture.path):
                os.remove(self.picture.path)
        super().delete(*args, **kwargs)

    


