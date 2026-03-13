from shoes4show.models import Item
from django.contrib.postgres.search import SearchVector, TrigramWordSimilarity, TrigramSimilarity


def run_query(request):
    SIMILARITY_CONST = 0.4
    used_trigram = False
    query = request.POST["query"]
    category_choice = request.POST["category"]
    sorting_choice = request.POST.get("sorting", "none")
    old_word = query
    new_word = ""

    if category_choice != 'none':
        found_items = Item.objects.all().filter(category=category_choice)
    else:
        found_items = Item.objects.all()

    if query:
        found_items_name = found_items.annotate(search=SearchVector("name")).filter(search=query)
    else:
        found_items_name = found_items


    if not found_items_name:
        found_items_name = Item.objects.annotate(similarity=TrigramWordSimilarity(query, "name")).filter(similarity__gt=SIMILARITY_CONST)
        if found_items_name:
            used_trigram = True
            query_list = [x.lower() for x in query.strip().split()]
            name_list = [x.lower() for x in found_items_name[0].name.strip().split()]
            for i in query_list:
                for j in name_list:
                    if find_similarity(split_word(i), split_word(j)) > SIMILARITY_CONST:
                        new_word = j

    if sorting_choice != "none":
        found_items_name = found_items_name.order_by(sorting_choice)

    return found_items_name, used_trigram, old_word, new_word


def split_word(word):
    word = "  " + word + " "
    return [word[i:i+3] for i in range(len(word)-3)]

def find_similarity(trigrams1, trigrams2):
    return sum([1 for i in range(min(len(trigrams1) - 1, len(trigrams2) - 1)) if (trigrams1[i] in trigrams2 or trigrams2[i] in trigrams1)])/max(len(trigrams1) - 1, len(trigrams2) - 1)
