from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.views import APIView
from .serializers import UserSerializer, LoginSerializer
from .models import User
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

class SignupView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            'message': 'User created successfully',
            'user': serializer.data,
            }, status=status.HTTP_201_CREATED)
        # return Response(status=status.HTTP_400_BAD_REQUEST)

# Login view
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        # data = UserSerializer(data)
        token = RefreshToken(user).for_user()

        return Response({
            'message': 'Login successful',
            'user': UserSerializer(user).data,
            'token': {
            'access token': token.access_token,
            'refresh_token': token
            }
        }, status=status.HTTP_200_OK)


# View users

