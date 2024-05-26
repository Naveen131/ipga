from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User
from accounts.serializers import SignUpSerializer, LoginSerializer, UserProfileSerializer
from utils.utils import APIResponse


# Create your views here.

class SignupAPIView(CreateAPIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return APIResponse(data=serializer.data, status_code=200, message="User created successfully")

class LoginAPIView(CreateAPIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            errors = []
            for field, messages in serializer.errors.items():
                errors.append(messages[0] if type(messages) == list else messages)

            return APIResponse(data=None, status_code=400,
                               message=errors[0].__str__() if type(errors[0])=='rest_framework.exceptions.ErrorDetail'
                               else errors[0])

        data = serializer.validated_data
        email = data.get('email')
        password = data.get('password')
        user = User.objects.filter(email=email).first()

        refresh = RefreshToken.for_user(user)

        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        return APIResponse(data=data, status_code=200, message="Login successful")


class UserDetailsAPIView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserProfileSerializer

    def post(self, request, *args, **kwargs):
        # import pdb;pdb.set_trace()
        serializer = UserProfileSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            errors = []
            for field, messages in serializer.errors.items():
                errors.append(messages[0] if type(messages) == list else messages)

            return APIResponse(data=None, status_code=400,
                               message=errors[0].__str__() if type(errors[0])=='rest_framework.exceptions.ErrorDetail'
                               else errors[0])

        else:
            data = serializer.validated_data
            instance = serializer.create(data)
            return APIResponse(data=None,
                               status_code=200,
                               message="User details updated successfully")


