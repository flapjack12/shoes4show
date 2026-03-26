from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import MaxLengthValidator, MinValueValidator

from shoes4show.models import Item, Review, UserProfile


class ItemForm(forms.ModelForm):
    name = forms.CharField(
        max_length=Item.NAME_MAX_LENGTH,
        help_text="Please enter the item name:"
    )
    description = forms.CharField(
        help_text="Please enter the item description:",
        validators=[MaxLengthValidator(250)]
    )
    image = forms.ImageField(help_text="Choose photo:")
    price = forms.DecimalField(
        decimal_places=2,
        max_digits=8,
        validators=[MinValueValidator(0)],
        widget=forms.NumberInput(attrs={"step": "0.01"}),
        help_text="Enter price:"
    )
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    slug = forms.CharField(widget=forms.HiddenInput(), required=False)
    category = forms.ChoiceField(
        required=False,
        choices=Item.SHOES_CATEGORIES,
        help_text="Choose a category:"
    )

    class Meta:
        model = Item
        fields = ("name", "description", "image", "price", "category")


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("review_text", "rating")


class UserForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )
    password2 = forms.CharField(
        label="Re-enter password",
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("picture",)
        widgets = {
            "picture": forms.ClearableFileInput(attrs={"class": "form-control-file"})
        }