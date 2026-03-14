from django.urls import path
from shoes4show import views

app_name = "shoes4show"

urlpatterns = [
    path("", views.index, name="index"),
    path("about/", views.about, name="about"),
    path("contact-us/", views.contact_us, name="contact_us"),
    path("site-map/", views.site_map, name="site_map"),
    path("shoe-size-conversion/", views.shoe_size_conversion, name="shoe_size_conversion"),

    path("category/<slug:category_name_slug>/", views.show_item, name="show_item"),

    path("add-listing/", views.add_listing, name="add_listing"),
    path("add-review/<slug:category_name_slug>/", views.add_review, name="add_review"),

    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("account/", views.account, name="account"),
    path("restricted/", views.restricted, name="restricted"),

    path("search/", views.search, name="search"),
]