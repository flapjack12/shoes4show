import os
from pathlib import Path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoes4show_project.settings')

import django
django.setup()
from shoes4show.models import Item, Review
from django.core.files import File
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User

IMAGE_SOURCE_DIR = Path("media/listing_images/references")


user = User.objects.all().filter(id=7)

def populate():
    items = [
    {"name": "New Balance trainers", "description": "New Balance 530 trainers in white and grey", "category": "SN", "uploaded_by": user[0]},
    {"name": "adidas slides", "description": "adidas Training Adilette Aqua slides in black", "category": "SA", "uploaded_by": user[0]},
    {"name": "Dr. Martens boots", "description": "Dr. Martens 1460 smooth leather boots in black", "category": "BO", "uploaded_by": user[0]},
    {"name": "Gucci loafers", "description": "Gucci horsebit loafers in brown leather", "category": "LO", "uploaded_by": user[0]},
    {"name": "Clarks oxfords", "description": "Clarks men's formal oxford shoes in tan", "category": "FS", "uploaded_by": user[0]},
    {"name": "Ugg slippers", "description": "Ugg Scuff slippers in chestnut", "category": "SL", "uploaded_by": user[0]},
    {"name": "Tieks flats", "description": "Tieks ballet flats in red", "category": "FL", "uploaded_by": user[0]},
    {"name": "Christian Louboutin pumps", "description": "Christian Louboutin So Kate pumps in black patent", "category": "PU", "uploaded_by": user[0]},
    {"name": "Nike running shoes", "description": "Nike Air Zoom Pegasus 38 running shoes in blue", "category": "AT", "uploaded_by": user[0]},
    {"name": "Crocs clogs", "description": "Crocs Classic clogs in navy", "category": "CL", "uploaded_by": user[0]},
    {"name": "Soludos espadrilles", "description": "Soludos classic espadrilles in natural linen", "category": "ES", "uploaded_by": user[0]},
]

    for item in items:
        image_filename = slugify(item["name"]) + ".jpg"
        image_path = IMAGE_SOURCE_DIR / image_filename
        add_item(**item, image_path=image_path)



def add_item(name, description, category, image_path=None, uploaded_by=None):
    p = Item.objects.get_or_create(name=name, description=description, category=category, uploaded_by=uploaded_by)[0]

    if image_path and not p.image:
        with open(image_path, 'rb') as f:
        
            p.image.save(image_path.name, File(f), save=True)
        print(f"Added image for '{name}'")
    elif not image_path:
        print(f"No image provided for '{name}'")
    p.save()
    return p

if __name__ == '__main__':
    print('Starting population script...')
    populate()