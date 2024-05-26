from django.urls import path

from accounts.views import SignupAPIView, LoginAPIView, UserDetailsAPIView

urlpatterns = [
    path('signup', SignupAPIView.as_view(), name='signup'),
    path('login', LoginAPIView.as_view(), name='login'),
    path('details', UserDetailsAPIView.as_view(), name='details'),
    ]