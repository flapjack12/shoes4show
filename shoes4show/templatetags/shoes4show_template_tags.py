from django import template
from shoes4show.models import Item

register = template.Library()

@register.inclusion_tag('shoes4show/categories.html')
def get_category_list(current_category=None):
   return {'categories': Item.objects.all(),
           'current_category': current_category}

@register.filter(name='get_item')
def get_item(dictionary, key):
        return dictionary.get(key)