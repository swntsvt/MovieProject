from django.db import models
import uuid
from django.contrib.auth.models import User


class Genres(models.Model):
    title = models.CharField(max_length=200)

    class Meta:
        db_table = "genres"

    def __str__(self):
        return f"{self.__dict__}"


class Movies(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    genres = models.ManyToManyField(Genres, related_name="movies")

    class Meta:
        db_table = "movies"

    def __str__(self):
        return f"{self.__dict__}"


class Collection(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    movies = models.ManyToManyField(Movies, related_name="collections")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = "collections"
