from django.contrib import admin

# Register your models here.
from django.contrib import admin
from shoes4show.models import Item, Review
from shoes4show.models import UserProfile


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('title', 'item', 'url')

class ItemAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('name',)}

admin.site.register(Item, ItemAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(UserProfile)