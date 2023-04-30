from django.contrib import admin
from .models import Genres, Movies, Collection

# Register your models here.
admin.site.register([Genres, Movies, Collection])
