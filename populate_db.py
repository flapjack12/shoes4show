import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shoes4show_project.settings')

import django
django.setup()
from shoes4show.models import Item, Review

def populate():
    items = [
    {"name": "New Balance trainers", "description": "New Balance 530 trainers in white and grey", "category": "SN"},
    {"name": "adidas slides", "description": "adidas Training Adilette Aqua slides in black", "category": "SA"},
    {"name": "Dr. Martens boots", "description": "Dr. Martens 1460 smooth leather boots in black", "category": "BO"},
    {"name": "Gucci loafers", "description": "Gucci horsebit loafers in brown leather", "category": "LO"},
    {"name": "Clarks oxfords", "description": "Clarks men's formal oxford shoes in tan", "category": "FS"},
    {"name": "Ugg slippers", "description": "Ugg Scuff slippers in chestnut", "category": "SL"},
    {"name": "Tieks flats", "description": "Tieks ballet flats in red", "category": "FL"},
    {"name": "Christian Louboutin pumps", "description": "Christian Louboutin So Kate pumps in black patent", "category": "PU"},
    {"name": "Nike running shoes", "description": "Nike Air Zoom Pegasus 38 running shoes in blue", "category": "AT"},
    {"name": "Crocs clogs", "description": "Crocs Classic clogs in navy", "category": "CL"},
    {"name": "Soludos espadrilles", "description": "Soludos classic espadrilles in natural linen", "category": "ES"},
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