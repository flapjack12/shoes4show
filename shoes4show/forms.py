from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import MinValueValidator
from django.core.validators import MaxLengthValidator
from shoes4show.models import Item, Review, UserProfile
from django.contrib.auth.models import User

from shoes4show.models import Item, Review, UserProfile


class ItemForm(forms.ModelForm):
    name = forms.CharField(max_length=Item.NAME_MAX_LENGTH, help_text="Please enter the item name:")
    description = forms.CharField(help_text="Please enter the item description:", validators=[MaxLengthValidator(250)])
    image = forms.ImageField(help_text="Choose photo:")
    price = forms.DecimalField(decimal_places=2, max_digits=8, validators=[MinValueValidator(0)], widget=forms.NumberInput(attrs={'step':'0.01'}), help_text="Enter price:")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    slug = forms.CharField(widget=forms.HiddenInput(), required=False)
    category = forms.ChoiceField(required=False, choices=Item.SHOES_CATEGORIES, help_text="Choose a category:")

    class Meta:
        model = Item
        fields = ('name', 'description', 'image', 'price', 'category')


class ReviewForm(forms.ModelForm):
    title = forms.CharField(max_length=Item.NAME_MAX_LENGTH, help_text="Please enter the title of the page.")
    url = forms.URLField(max_length=200,help_text="Please enter the URL of the page.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

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
        fields = ("picture",)
