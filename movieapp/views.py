import requests
from django.db.models import Count
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

import movieapp
from movieapp.middlewares import RequestCountMiddleware
from movieapp.models import Collection, Genres, Movies
from MovieProject.settings import get_env_variable

from .serializers import CollectionSerializer

# Create your views here.

EXTERNAL_API_URL = "https://demo.credy.in/api/v1/maya/movies/"
MAX_RETRIES = 5
USERNAME = get_env_variable("USER")
PASSWORD = get_env_variable("PASSWORD")


def request_retry(url, num_retries=MAX_RETRIES, success_list=[200, 404]):
    """GET request API for accessing external API with retry  

    Args:
        url (_type_): URL of the external API
        num_retries (_type_, optional): Number of retries to be attempted. Defaults to MAX_RETRIES.
        success_list (list, optional): Error codes that would be considered as succesful responses. 
                                        Defaults to [200, 404].

    Returns:
        _type_: API response
    """
    for i in range(num_retries):
        response = requests.get(url, auth=(USERNAME, PASSWORD))
        if response.status_code in success_list:
            # Return response if successful
            return response
        else:
            print(
                "INFO Fetching response from external API failed, retry attempt: ",
                i + 1,
            )
    return None


@csrf_exempt
def movieapi(request):
    """API to get movies from the external API. Perform following additional tasks before sending response:
    1. given that the external API is flaky, incorporate retry mechanism
    2. modify the response as per requirements
    """
    # add page info to the url, if required
    page = request.GET.get("page")
    request_url = EXTERNAL_API_URL
    if page != None:
        request_url += "?page=" + page

    # pull data from third party rest api, with retries
    response = request_retry(request_url)
    response_dict = response.json()

    # handle the boundary case where response.status_code is 404 (Page not found)
    if response.status_code == 404:
        return JsonResponse(response_dict, status=404)

    # change the value of previous key, so that it refers to this API
    if response_dict["previous"] != None:
        response_dict["previous"] = response_dict["previous"].replace(
            EXTERNAL_API_URL, "http://127.0.0.1:8000/movies/"
        )

    # change the value of next key, so that it refers to this API
    if response_dict["next"] != None:
        response_dict["next"] = response_dict["next"].replace(
            EXTERNAL_API_URL, "http://127.0.0.1:8000/movies/"
        )

    # modify the key value in response, replace key value 'results' with 'data'
    data = response_dict["results"]
    response_dict["data"] = data
    response_dict.pop("results")

    return JsonResponse(response_dict, status=status.HTTP_200_OK)


class CollectionAPI(APIView):
    """For handling get, post, put and delete requests for Collections"""

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        movie_data = request.data.get("movies")
        movie_list = []
        for movie in movie_data:
            genres_str = movie["genres"]
            genres_obj_list = []
            if genres_str != "":
                split_genres = genres_str.split(",")
                for each_genres in split_genres:
                    try:
                        genres_obj = Genres.objects.get(title=each_genres)
                    except movieapp.models.Genres.DoesNotExist:
                        genres_obj = Genres(title=each_genres)
                        genres_obj.save()
                    genres_obj_list.append(genres_obj)

            list1 = []
            for each in genres_obj_list:
                list1.append(each.id)

            title = movie["title"]
            description = movie["description"]
            uuid = movie["uuid"]

            try:
                movie_obj = Movies.objects.get(uuid=uuid)
            except movieapp.models.Movies.DoesNotExist:
                movie_obj = Movies(title=title, description=description, uuid=uuid)
                movie_obj.save()
                for genre_obj in genres_obj_list:
                    movie_obj.genres.add(genre_obj)
            movie_list.append(movie_obj)

        title = request.data["title"]
        description = request.data["description"]
        collection_obj = Collection(
            title=title, description=description, user=request.user
        )
        collection_obj.save()
        for movie_obj in movie_list:
            collection_obj.movies.add(movie_obj)
        response_dict = {"collection_uuid": collection_obj.__dict__["uuid"]}
        return JsonResponse(response_dict, safe=False, status=status.HTTP_201_CREATED)

    def get(self, request, uuid=None):
        user = request.user.id
        if uuid:
            try:
                collection_obj = Collection.objects.filter(user=user).get(uuid=uuid)
            except movieapp.models.Collection.DoesNotExist:
                return JsonResponse(
                    {"message": f"Collection does not exist for UUID {uuid}"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            ser = CollectionSerializer(collection_obj)
            return JsonResponse(ser.data, status=status.HTTP_200_OK)
        else:
            collection_objs = Collection.objects.filter(user=user)
            collections_qs = collection_objs.values("title", "uuid", "description")
            collections_dict = [
                {
                    "title": collection["title"],
                    "uuid": collection["uuid"],
                    "description": collection["description"],
                }
                for collection in collections_qs
            ]

            # fetch top 3 genres
            top_genres = (
                Collection.objects.filter(user=user)
                .values("movies__genres__title")
                .annotate(count=Count("movies__genres"))
                .order_by("-count")[:3]
            )
            genre_names = [g["movies__genres__title"] for g in top_genres]

            response_dict = {
                "is_success": True,
                "data": {
                    "collections": collections_dict,
                    "favourite_genres": genre_names,
                },
            }

            return JsonResponse(response_dict, safe=False, status=status.HTTP_200_OK)

    def put(self, request, uuid=None):
        request_dict = request.data
        user = request.user.id
        if uuid:
            try:
                collection_obj = Collection.objects.filter(user=user).get(uuid=uuid)
            except movieapp.models.Collection.DoesNotExist:
                return JsonResponse(
                    {"msg": f"Collection does not exist for UUID {uuid}"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            ser = CollectionSerializer(instance=collection_obj, data=request_dict, partial=True)

            if ser.is_valid():
                ser.save()
                return JsonResponse(ser.data, status=status.HTTP_200_OK)
            else:
                return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse(
                {"message": f"UUID not passed"}, status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, uuid=None):
        user = request.user.id
        if uuid:
            try:
                collection_obj = Collection.objects.filter(user=user).get(uuid=uuid)
            except movieapp.models.Collection.DoesNotExist:
                return JsonResponse({"message": f"Collection does not exist for UUID {uuid}"})
            collection_obj.delete()
            return Response(
                {"message": "Data deleted successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
        else:
            return JsonResponse({"message": f"UUID not passed"}, status=status.HTTP_400_BAD_REQUEST)


def request_count(request):
    total_requests = request.count
    return JsonResponse({"requests": total_requests}, status=status.HTTP_200_OK)


@csrf_exempt
def reset_count(request):
    if request.method == "POST":
        RequestCountMiddleware.set_total_requests(0)
        return JsonResponse({"message": "request count reset successfully"},
                            status=status.HTTP_205_RESET_CONTENT,)
