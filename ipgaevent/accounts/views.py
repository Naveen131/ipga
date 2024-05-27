from django.db import transaction
from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User, State, City, Country, Membership
from accounts.serializers import SignUpSerializer, LoginSerializer, UserProfileSerializer, StateSerializer, \
    CitySerializer, CountrySerializer
from ipgaevent import settings
from utils.utils import APIResponse
from utils.views import ListAPIViewWithPagination


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
        try:
            sid = transaction.savepoint()
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

        except Exception as e:
            transaction.savepoint_rollback(sid)
            return APIResponse(data=None, status_code=400, message="Error in updating user details")


class StateListView(ListAPIViewWithPagination):
    queryset = State.objects.all()
    serializer_class = StateSerializer

    def get_queryset(self):
        queryset = State.objects.all()
        if self.request.query_params.get('search'):
            queryset = queryset.filter(name__istartswith=self.request.query_params.get('search'))
        return queryset


class CityListView(ListAPIViewWithPagination):
    queryset = City.objects.all()
    serializer_class = CitySerializer

    def get_queryset(self):
        queryset = City.objects.all()
        if self.request.query_params.get('search'):
            queryset = queryset.filter(name__istartswith=self.request.query_params.get('search'))
        return queryset


class CountryListView(ListAPIViewWithPagination):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

    def get_queryset(self):
        queryset = Country.objects.all()
        if self.request.query_params.get('search'):
            queryset = queryset.filter(name__istartswith=self.request.query_params.get('search'))
        return queryset


class CheckMembership(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        code = data.get('code')

        try:
            membership = Membership.objects.filter(code=code)
            if membership.exists():
               data = {
                    'is_membership': True
                }
            else:
                data = {
                    'is_membership': False
                }
            return APIResponse(data=data, status_code=200, message="Membership code applied successfully")

        except Exception as e:

            return APIResponse(data=data, status_code=400, message=str(e))


def send_email(request):
    # import pdb;pdb.set_trace()
    subject = 'Thank you for registering to our site'
    message = ' it  means a world to us '
    email_from = settings.EMAIL_HOST_USER