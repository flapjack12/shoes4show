from shoes4show.models import Item


def run_query(request):
    query = request.POST["query"].strip().split()
    category_choice = request.POST["category"]
    found_items = set()
    if query:
        for word in query:
            results = Item.objects.filter(name__icontains=word).filter(description__icontains=word)
            found_items.add(results.pk)
        found_items_queryset = Item.objects.filter(pk__in=found_items)
    else:
        found_items_queryset = Item.objects.all()
    if category_choice != 'none':
        found_items_queryset = found_items_queryset.filter(category=category_choice)

    return list(found_items_queryset)