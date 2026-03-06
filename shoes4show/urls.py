from django.urls import path
from shoes4show import views

app_name = "shoes4show"

urlpatterns = [
    path("", views.index, name="index"),
    path("aboutus/", views.about, name="aboutus"),

    path("category/<slug:category_name_slug>/", views.show_item, name="show_item"),
    path("add_category/", views.add_item, name="add_item"),
    path("category/<slug:category_name_slug>/add_page/", views.add_page, name="add_page"),

    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("account/", views.account, name="account"),
    path("restricted/", views.restricted, name="restricted"),

    path("search/", views.search, name="search"),
]