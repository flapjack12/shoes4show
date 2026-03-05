from datetime import datetime
from django import views
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.urls import reverse
from shoes4show.models import Item, Review
from shoes4show.forms import ItemForm, ReviewForm
from shoes4show.forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from shoes4show.search import run_query

def index(request):
    request
    item_list = Item.objects.order_by('-likes')[:5]
    reviews_list = Review.objects.order_by('-views')[:5]
    context_dict={}
    context_dict['boldmessage'] = "Welcome message"
    context_dict['items'] = item_list
    context_dict['reviews'] = reviews_list
    context_dict['category_choices'] = Item.SHOES_CATEGORIES
    visitor_cookie_handler(request)
    response = render(request, 'shoes4show/index.html', context=context_dict)
    return response


def show_item(request, category_name_slug):
    context_dict = {}

    try:
        item = Item.objects.get(slug=category_name_slug)
        reviews = Review.objects.filter(item=item)
        context_dict['reviews'] = reviews
        context_dict['item'] = item
    except Item.DoesNotExist:
        context_dict['item'] = None
        context_dict['reviews'] = None
    return render(request, 'shoes4show/category.html', context=context_dict)


def add_item(request):
        form = ItemForm()
        if request.method == 'POST':
            form = ItemForm(request.POST)
            if form.is_valid():
                form.save(commit=True)
                return redirect(reverse('shoes4show:index'))
            else:
                print(form.errors)
        return render(request, 'shoes4show/add_category.html', {'form':form})

def add_page(request, category_name_slug):
    try:
        category = Item.objects.get(slug=category_name_slug)
    except Item.DoesNotExist:
        category = None

    if category is None:
        return redirect(reverse('shoes4show:index'))
    
    if request.user.is_authenticated:
        form = ReviewForm()
        if request.method == 'POST':
            form = ReviewForm(request.POST)
            if form.is_valid():
                if category:
                    page=form.save(commit=False)
                    page.category = category
                    page.views = 0
                    page.save()
                    return redirect(reverse('shoes4show:show_item', kwargs={'category_name_slug': category_name_slug}))
            else:
                print(form.errors)
        context_dict = {'form': form, 'category': category}
        return render(request, 'shoes4show/add_page.html', context=context_dict)
    else:
        return redirect(reverse('shoes4show:login'))


def register(request):
    registered = False

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            profile.save()
            registered = True
        else:
            print(user_form.errors, profile_form.errors)

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    return render(request, 'shoes4show/register.html', 
                  context={'user_form':user_form, 
                           'profile_form':profile_form, 
                           'registered':registered})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('shoes4show:index'))
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'shoes4show/login.html')


@login_required
def restricted(request):
    return render(request, 'shoes4show/restricted.html')


@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('shoes4show:index'))


def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits','1'))
    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],'%Y-%m-%d %H:%M:%S')
    if (datetime.now() - last_visit_time).days > 0:
        visits = visits + 1
        request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = last_visit_cookie
    request.session['visits'] = visits

def search(request):
    result_list = []

    if request.method == "POST":
        result_list = run_query(request)
    return render(request, 'shoes4show/listings.html', {"result_list":result_list})


def about(request):
    context_dict = {}
    
    return render(request, 'shoes4show/about.html', context=context_dict)

def contact_us(request):
    context_dict = {}
    
    return render(request, 'shoes4show/contact_us.html', context=context_dict)

def site_map(request):
    context_dict = {}
    
    return render(request, 'shoes4show/site_map.html', context=context_dict)

def shoe_size_conversion(request):
    context_dict = {}
    
    return render(request, 'shoes4show/shoe_size_conversion.html', context=context_dict)
