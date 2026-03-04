from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User

class Item(models.Model):
    NAME_MAX_LENGTH = 128
    SHOES_CATEGORIES = {
        "HE":"Heels",
        "SN":"Sneakers",
        "SA":"Sandals",
    }
    name = models.CharField(max_length=NAME_MAX_LENGTH, unique=True)
    description = models.TextField(default="default description")
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
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
    

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)

    def __str__(self):
        return self.user.username

    


