from shoes4show.models import Item
from django.contrib.postgres.search import SearchVector, TrigramWordSimilarity


def run_query(request):
    query = request.POST["query"]
    category_choice = request.POST["category"]

    if category_choice != 'any':
        found_items = Item.objects.all().filter(category=category_choice)
    else:
        found_items = Item.objects.all()

    if query:
        found_items_name = found_items.annotate(search=SearchVector("name")).filter(search=query)
    else:
        found_items_name = found_items


    if not found_items_name:
        found_items_name = Item.objects.annotate(similarity=TrigramWordSimilarity(query, "name")).filter(similarity__gt=0.3)

    return list(found_items_name)