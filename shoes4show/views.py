from datetime import datetime

from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from shoes4show.forms import ItemForm, ReviewForm, UserForm, UserProfileForm
from shoes4show.models import Item, Review, DailyItemView
from shoes4show.search import run_query

CATEGORY_CHOICES = Item.SHOES_CATEGORIES.copy()
CATEGORY_CHOICES.update({'none': 'All Categories'})
SORTING_CHOICES = Item.SORTING_OPTIONS.copy()
SORTING_CHOICES.update({'none': 'Filter'})


def index(request):
    item_list_1 = Item.objects.order_by('-views')[:4]
    item_list_2 = Item.objects.order_by('-views')[4:8]
    item_list_3 = Item.objects.order_by('-views')[8:12]

    context_dict = {}
    context_dict['boldmessage'] = "Welcome to Shoes4Show!"
    context_dict['items'] = [item_list_1, item_list_2, item_list_3]
    context_dict['category_choices'] = CATEGORY_CHOICES
    context_dict['sorting'] = SORTING_CHOICES
    context_search = request.GET.getlist('search_context')
    if not context_search:
        context_search = ["", "none", "none"]
    context_dict['search_context'] = context_search
    today = timezone.now().date()
    most_viewed_today = DailyItemView.objects.filter(date=today).order_by('-count').first()
    context_dict['most_viewed_today'] = most_viewed_today.item if most_viewed_today else None

    visitor_cookie_handler(request)
    return render(request, "shoes4show/index.html", context=context_dict)


def show_listing(request, shoe_slug):
    context_dict = {}
    context_dict['category_choices'] = CATEGORY_CHOICES
    context_dict['sorting'] = SORTING_CHOICES
    context_search = request.GET.getlist('search_context')
    if not context_search:
        context_search = ["", "none", "none"]
    context_dict['search_context'] = context_search

    try:
        shoe = Item.objects.get(slug=shoe_slug)
        reviews = Review.objects.filter(item=shoe).order_by('created_time')
        context_dict["reviews"] = reviews
        context_dict["shoe"] = shoe
        today = timezone.now().date()
        daily_view, created = DailyItemView.objects.get_or_create(item=shoe, date=today)
        daily_view.count += 1
        daily_view.save()
        shoe.views += 1
        shoe.save()
    except Item.DoesNotExist:
        context_dict["shoe"] = None
        context_dict["reviews"] = None

    return render(request, "shoes4show/listing.html", context=context_dict)


@login_required
def add_review(request, shoe_slug):
    try:
        shoe = Item.objects.get(slug=shoe_slug)
    except Item.DoesNotExist:
        shoe = None

    if shoe is None:
        return redirect(reverse("shoes4show:index"))

    form = ReviewForm()

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.item = shoe
            review.user = request.user
            review.views = 0
            review.save()
            return redirect(
                reverse(
                    "shoes4show:show_listing",
                    kwargs={"shoe_slug": shoe_slug},
                )
            )
        else:
            print(form.errors)

    context_dict = {
        "form": form,
        "shoe": shoe,
        "category_choices": CATEGORY_CHOICES,
        "sorting": SORTING_CHOICES,
        "search_context": ["", "none", "none"],
    }
    return redirect(
        reverse(
            "shoes4show:show_listing",
            kwargs={"shoe_slug": shoe_slug},
            )
        )


@login_required
def add_listing(request):
    context_dict = {}
    context_dict['category_choices'] = CATEGORY_CHOICES
    context_dict['sorting'] = SORTING_CHOICES
    context_dict['search_context'] = ["", "none", "none"]

    form = ItemForm()
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(commit=True)
            return redirect(reverse('shoes4show:index'))
        else:
            print(form.errors)

    context_dict['form'] = form
    return render(request, 'shoes4show/add_listing.html', context=context_dict)


def register(request):
    if request.user.is_authenticated:
        return redirect(reverse("shoes4show:account"))

    if request.method == "POST":
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            login(request, user)
            return redirect(reverse("shoes4show:account"))
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(
        request,
        "shoes4show/register.html",
        context={
            "user_form": user_form,
            "profile_form": profile_form,
            "category_choices": CATEGORY_CHOICES,
            "sorting": SORTING_CHOICES,
            "search_context": ["", "none", "none"],
        },
    )


def user_login(request):
    if request.user.is_authenticated:
        return redirect(reverse("shoes4show:account"))

    context_dict = {
        "category_choices": CATEGORY_CHOICES,
        "sorting": SORTING_CHOICES,
        "search_context": ["", "none", "none"],
    }

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        next_url = request.POST.get("next")

        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)

                if next_url and url_has_allowed_host_and_scheme(
                    next_url,
                    allowed_hosts={request.get_host()},
                    require_https=request.is_secure(),
                ):
                    return redirect(next_url)

                return redirect(reverse("shoes4show:account"))

            return HttpResponse("Your account is disabled.")

        context_dict["error_message"] = "Invalid username or password."

    return render(request, "shoes4show/login.html", context=context_dict)


@login_required
def account(request):
    return render(
        request,
        "shoes4show/account.html",
        context={
            "badge_text": "Badge coming soon",
            "review_count_text": "Coming soon",
            "category_choices": CATEGORY_CHOICES,
            "sorting": SORTING_CHOICES,
            "search_context": ["", "none", "none"],
        },
    )


@login_required
def restricted(request):
    return render(
        request,
        "shoes4show/restricted.html",
        context={
            "category_choices": CATEGORY_CHOICES,
            "sorting": SORTING_CHOICES,
            "search_context": ["", "none", "none"],
        },
    )


@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse("shoes4show:index"))


def get_server_side_cookie(request, cookie, default_val=None):
    return request.session.get(cookie, default_val)


def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, "visits", "1"))
    last_visit_cookie = get_server_side_cookie(request, "last_visit", str(datetime.now()))

    try:
        last_visit_time = datetime.strptime(last_visit_cookie[:-7], "%Y-%m-%d %H:%M:%S")
    except ValueError:
        last_visit_time = datetime.now()

    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        request.session["last_visit"] = str(datetime.now())
    else:
        request.session["last_visit"] = last_visit_cookie

    request.session["visits"] = visits


def search(request):
    result_list, used_trigram, old_word, new_word, search_context = run_query(request)
    context_dict = {
        "result_list": result_list,
        "old_word": old_word,
        "category_choices": CATEGORY_CHOICES,
        "sorting": SORTING_CHOICES,
        "search_context": search_context,
        "is_search": True,
    }
    if used_trigram:
        context_dict["used_trigram"] = used_trigram
        context_dict["new_word"] = new_word

    return render(request, 'shoes4show/listings.html', context=context_dict)


def about(request):
    context_dict = {}
    context_dict['category_choices'] = CATEGORY_CHOICES
    context_dict['sorting'] = SORTING_CHOICES
    context_dict['search_context'] = ["", "none", "none"]

    visitor_cookie_handler(request)
    context_dict['visits'] = request.session.get("visits", 1)

    return render(request, 'shoes4show/about.html', context=context_dict)


def contact_us(request):
    context_dict = {}
    context_dict['category_choices'] = CATEGORY_CHOICES
    context_dict['sorting'] = SORTING_CHOICES
    context_dict['search_context'] = ["", "none", "none"]

    return render(request, 'shoes4show/contact_us.html', context=context_dict)


def site_map(request):
    context_dict = {}
    context_dict['category_choices'] = CATEGORY_CHOICES
    context_dict['sorting'] = SORTING_CHOICES
    context_dict['search_context'] = ["", "none", "none"]

    return render(request, 'shoes4show/site_map.html', context=context_dict)


def shoe_size_conversion(request):
    context_dict = {}
    context_dict['category_choices'] = CATEGORY_CHOICES
    context_dict['sorting'] = SORTING_CHOICES
    context_dict['search_context'] = ["", "none", "none"]

    return render(request, 'shoes4show/shoe_size_conversion.html', context=context_dict)
