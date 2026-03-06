from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from shoes4show.models import Item, Review, UserProfile


class ItemForm(forms.ModelForm):
    name = forms.CharField(
        max_length=Item.NAME_MAX_LENGTH,
        help_text="Please enter the item name."
    )

    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    slug = forms.CharField(widget=forms.HiddenInput(), required=False)

    category = forms.ChoiceField(
        required=False,
        choices=Item.SHOES_CATEGORIES,
        help_text="Choose a category."
    )

    class Meta:
        model = Item
        fields = ("name",)

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        exclude = ("category",)


class UserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ()