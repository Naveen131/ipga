from django.urls import path

from accounts.views import SignupAPIView, LoginAPIView, UserDetailsAPIView, StateListView, CityListView, \
    CountryListView, CheckMembership, PaymentTransferAPIView

urlpatterns = [
    path('signup', SignupAPIView.as_view(), name='signup'),
    path('login', LoginAPIView.as_view(), name='login'),
    path('details', UserDetailsAPIView.as_view(), name='details'),
    path('states', StateListView.as_view(), name='state-list'),
    path('cities', CityListView.as_view(), name='city-list'),
    path('country', CountryListView.as_view(), name='city-list'),
    path('check-membership', CheckMembership.as_view(), name='check-membership'),
    path('bank-transfer', PaymentTransferAPIView.as_view(), name='bank-transfer'),
    ]