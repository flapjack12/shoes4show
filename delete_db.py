import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoes4show_project.settings')

import django
django.setup()
from shoes4show.models import Item, Review, UserProfile


if __name__ == "__main__":
    Item.objects.all().delete()