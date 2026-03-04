from django import forms
from shoes4show.models import Item, Review, UserProfile
from django.contrib.auth.models import User
from shoes4show.models import UserProfile

class ItemForm(forms.ModelForm):
    name = forms.CharField(max_length=Item.NAME_MAX_LENGTH, help_text="Please enter the category name.")
    descriprion = forms.TimeField(help_text="Please enter the description.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    slug = forms.CharField(widget=forms.HiddenInput(), required=False)
    category = forms.ChoiceField(required=False, choices=Item.SHOES_CATEGORIES, help_text="Choose a category.")
    

    class Meta:
        model = Item
        fields = ('name', )


class ReviewForm(forms.ModelForm):
    title = forms.CharField(max_length=Item.NAME_MAX_LENGTH, help_text="Please enter the title of the page.")
    url = forms.URLField(max_length=200,help_text="Please enter the URL of the page.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    def clean(self):
        cleaned_data = self.cleaned_data
        url = cleaned_data.get('url')
        if url and not url.startswith('http://'):
            url = f'http://{url}'
            cleaned_data['url'] = url
        return cleaned_data

    class Meta:
        model = Review
        exclude = ('category', )


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password',)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('website', 'picture',)


