from rest_framework import generics
from rest_framework.response import Response
from .serializers import RegisterSerializer, UserSerializer
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt import views as jwt_views
from datetime import datetime
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
# from rest_framework_simplejwt import jwt
from MovieProject.settings import SECRET_KEY
import jwt


#Register API
class RegisterApi(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args,  **kwargs):
        username = request.data["username"]
        password = request.data["password"]
        try:
            u1 = User.objects.get(username=username)
            return JsonResponse({"message": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist: 
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()  
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            return Response({'refresh': str(refresh), 'access': str(access)}, status=status.HTTP_201_CREATED)
            
           
        
        
        
        
        
        
        
        
       