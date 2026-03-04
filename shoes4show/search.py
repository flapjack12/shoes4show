from shoes4show.models import Item


def run_query(query):
    found_items = set()
    for word in query:
        results = Item.objects.filter(name__icontains=word).filter(description__icontains=word)
        found_items.update(results)
    return list(found_items)