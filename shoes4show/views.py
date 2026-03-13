from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from shoes4show.forms import ItemForm, ReviewForm, UserForm, UserProfileForm
from shoes4show.models import Item, Review
from shoes4show.search import run_query


def index(request):
    request
    item_list = Item.objects.order_by('-likes')[:5]
    reviews_list = Review.objects.order_by('-views')[:5]
    context_dict={}
    context_dict['boldmessage'] = "Welcome to Shoes4Show."
    context_dict['items'] = item_list
    context_dict['reviews'] = reviews_list
    context_dict['category_choices'] = Item.SHOES_CATEGORIES
    context_dict['sorting'] = Item.SORTING_OPTIONS
    visitor_cookie_handler(request)
    return render(request, "shoes4show/index.html", context=context_dict)


def about(request):
    visitor_cookie_handler(request)
    context_dict = {
        "visits": request.session.get("visits", 1),
    }
    return render(request, "shoes4show/about.html", context=context_dict)


def show_item(request, category_name_slug):
    context_dict = {}

    try:
        item = Item.objects.get(slug=category_name_slug)
        reviews = Review.objects.filter(item=item)
        context_dict["reviews"] = reviews
        context_dict["item"] = item
    except Item.DoesNotExist:
        context_dict["item"] = None
        context_dict["reviews"] = None

    return render(request, "shoes4show/category.html", context=context_dict)


@login_required
def add_review(request, category_name_slug): #do we need a separate review view?
    try:
        category = Item.objects.get(slug=category_name_slug)
    except Item.DoesNotExist:
        category = None

    if category is None:
        return redirect(reverse("shoes4show:index"))

    form = ReviewForm()

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            page = form.save(commit=False)
            page.category = category
            page.views = 0
            page.save()
            return redirect(
                reverse(
                    "shoes4show:show_item",
                    kwargs={"category_name_slug": category_name_slug},
                )
            )
        else:
            print(form.errors)

    context_dict = {"form": form, "category": category}
    return render(request, "shoes4show/add_page.html", context=context_dict)
  
  
@login_required  
def add_listing(request):
        context_dict={}
        context_dict['category_choices'] = Item.SHOES_CATEGORIES
        
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
        },
    )


def user_login(request):
    if request.user.is_authenticated:
        return redirect(reverse("shoes4show:account"))

    context_dict = {}

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect(reverse("shoes4show:account"))
            return HttpResponse("Your account is disabled.")

        context_dict["error_message"] = "Invalid username or password."

    return render(request, "shoes4show/login.html", context=context_dict)


@login_required
def account(request):
    return render(request, "shoes4show/account.html")


@login_required
def restricted(request):
    return render(request, "shoes4show/restricted.html")


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
    result_list = []

    if request.method == "POST":
        query = request.POST["query"]
        result_list, used_trigram, old_word, new_word= run_query(request)
        if used_trigram:
            context_dict = {"result_list":result_list, "used_trigram":used_trigram, "new_word":new_word, "old_word":old_word, "query":query, }
            context_dict['category_choices'] = Item.SHOES_CATEGORIES
            context_dict['sorting'] = Item.SORTING_OPTIONS
        else:
            context_dict = {"result_list":result_list, "query":query, "old_word":old_word}
            context_dict['category_choices'] = Item.SHOES_CATEGORIES
            context_dict['sorting'] = Item.SORTING_OPTIONS
    return render(request, 'shoes4show/listings.html', context=context_dict)


def about(request):
    context_dict = {}
    context_dict['category_choices'] = Item.SHOES_CATEGORIES
    
    return render(request, 'shoes4show/about.html', context=context_dict)


def contact_us(request):
    context_dict = {}
    context_dict['category_choices'] = Item.SHOES_CATEGORIES
    
    return render(request, 'shoes4show/contact_us.html', context=context_dict)


def site_map(request):
    context_dict = {}
    context_dict['category_choices'] = Item.SHOES_CATEGORIES
    
    return render(request, 'shoes4show/site_map.html', context=context_dict)


def shoe_size_conversion(request):
    context_dict = {}
    context_dict['category_choices'] = Item.SHOES_CATEGORIES
    
    return render(request, 'shoes4show/shoe_size_conversion.html', context=context_dict)
