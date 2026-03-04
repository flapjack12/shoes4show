import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoes4show_project.settings')

import django
django.setup()
from shoes4show.models import Item, Review

def populate():
    items = [
        {"name":"New Balance trainers", "description":"New Balance 530 trainers in white and grey", "category":Item.SHOES_CATEGORIES.get("SN")},
        {"name":"adidas slides", "description":"adidas Training Adilette Aqua slides in black", "category":Item.SHOES_CATEGORIES.get("SA")},
    ]

    for item in items:
        add_item(**item)



def add_item(name, description, category):
    p = Item.objects.get_or_create(name=name, description=description, category=category)[0]
    p.save()
    return p

if __name__ == '__main__':
    print('Starting population script...')
    populate()