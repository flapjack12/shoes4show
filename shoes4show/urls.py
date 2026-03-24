from django.urls import path
from shoes4show import views

app_name = "shoes4show"

urlpatterns = [
    path('', views.index, name='index'),
    path('shoe/<slug:shoe_slug>/', views.show_listing, name='show_listing'),
    path('shoe/<slug:shoe_slug>/add_review/', views.add_review, name='add_review'),
    path('add_listing/', views.add_listing, name='add_listing'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('account/', views.account, name='account'),
    path('restricted/', views.restricted, name='restricted'),
    path('logout/', views.user_logout, name='logout'),
    path('search/', views.search, name='search'),
    path('about/', views.about, name='about'),
    path('contact_us/', views.contact_us, name='contact_us'),
    path('site_map/', views.site_map, name='site_map'),
    path('shoe_size_conversion/', views.shoe_size_conversion, name='shoe_size_conversion'),
]