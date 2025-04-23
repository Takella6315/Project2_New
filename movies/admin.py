from django.contrib import admin
from .models import Movie, Review, BudgetCategory


class MovieAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']

admin.site.register(Movie, MovieAdmin)
admin.site.register(Review)
admin.site.register(BudgetCategory)

