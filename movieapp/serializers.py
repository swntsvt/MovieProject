from rest_framework import serializers
from .models import Genres, Movies, Collection


class GenresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genres
        fields = ("title",)


class MoviesSerializer(serializers.ModelSerializer):
    genres = GenresSerializer(many=True)

    class Meta:
        model = Movies
        fields = ("title", "description", "genres", "uuid")


class CollectionSerializer(serializers.ModelSerializer):
    movies = MoviesSerializer(many=True)

    class Meta:
        model = Collection
        fields = ("title", "description", "movies")
