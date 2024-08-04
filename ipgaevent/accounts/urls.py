from django.urls import path

from accounts.payment import CCAvenuePaymentView, payment_webhook, PaymentSuccessResponse
from accounts.views import SignupAPIView, LoginAPIView, UserDetailsAPIView, StateListView, CityListView, \
    CountryListView, CheckMembership, PaymentTransferAPIView, UpdateUserDetails, download_user_report, \
    RegisterOffsiteView, OffsiteUserMembership

urlpatterns = [
    path('signup', SignupAPIView.as_view(), name='signup'),
    path('login', LoginAPIView.as_view(), name='login'),
    path('details', UserDetailsAPIView.as_view(), name='details'),
    path('details/update', UpdateUserDetails.as_view(), name='user-details'),
    path('states', StateListView.as_view(), name='state-list'),
    path('cities', CityListView.as_view(), name='city-list'),
    path('country', CountryListView.as_view(), name='city-list'),
    path('check-membership', CheckMembership.as_view(), name='check-membership'),
    path('bank-transfer', PaymentTransferAPIView.as_view(), name='bank-transfer'),
    path('payment', CCAvenuePaymentView.as_view(), name='ccavenue-payment'),
    path('status', payment_webhook, name='payment-webhook'),
    path('payment-success',PaymentSuccessResponse.as_view(),name='payment-success'),
    path('download_user_report', download_user_report, name='download_user_report'),
    path('offsite-register',RegisterOffsiteView.as_view(),name='offsite-register'),
    path('offsite-member', OffsiteUserMembership.as_view(), name='offsite-member'),

]