"""MovieProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from movieapp import views
from rest_framework_simplejwt import views as jwt_views
from users.views import RegisterApi
from movieapp.views import CollectionAPI, request_count, reset_count


urlpatterns = [
    path("admin/", admin.site.urls),
    path("movies/", views.movieapi, name="movieapi"),
    path("api/token/", jwt_views.TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", jwt_views.TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", RegisterApi.as_view(), name="register"),
    path("collection/", CollectionAPI.as_view(), name="get_all_collections"),
    path("collection/<str:uuid>/", CollectionAPI.as_view()),
    path("request-count/", request_count, name="request_count"),
    path("request-count/reset/", reset_count, name="reset_count"),
]
