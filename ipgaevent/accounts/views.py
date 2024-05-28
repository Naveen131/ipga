import base64

from django.db import transaction
from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User, State, City, Country, Membership, Address
from accounts.serializers import SignUpSerializer, LoginSerializer, UserProfileSerializer, StateSerializer, \
    CitySerializer, CountrySerializer, PaymentTransferSerializer
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
        return APIResponse(data=serializer.data, status_code=200, message="User created successfully, Please login to continue")

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
               return APIResponse(data=data, status_code=200, message="Membership code applied successfully")
            else:
                data = {
                    'is_membership': False
                }
                return APIResponse(data=data, status_code=200, message="Membership code Invalid")


        except Exception as e:

            return APIResponse(data=data, status_code=400, message=str(e))


# def send_email(request):
#     # import pdb;pdb.set_trace()
#     subject = 'Thank you for registering to our site'
#     message = ' it  means a world to us '
#     email_from = settings.EMAIL_HOST_USER


import requests

from django.core.mail import EmailMessage
from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML
import io


# def send_proforma_invoice_email(request):
#     # Replace with your dynamic data
#     context = {
#         'gstn': '27AACCI6531P1Z5',
#         'customer_name': 'Test, Mr Onsite Smt',
#         'customer_address': 'Jhjhjhjhj, Kmm Kjkk, India, 78787',
#         'customer_gstn': '',
#         'delegate_type': 'EB INDIAN SPOUSE',
#         'gst_amount': '7200',
#         'qty': '1',
#         'amount': '35400.00',
#         'total_owing': '47,200.00'
#     }
#
#
#
#     html_string = render_to_string('proforma_invoice.html', context)
#     html = HTML(string=html_string)
#     pdf_file = html.write_pdf()
#
#     # Create a file-like buffer to receive the PDF data
#     pdf_buffer = io.BytesIO(pdf_file)
#     email.attach('proforma_invoice.pdf', pdf_buffer.getvalue(), 'application/pdf')
#
#     try:
#         email.send()
#         return HttpResponse("Email sent successfully")
#     except Exception as e:
#         return HttpResponse(f"Failed to send email: {str(e)}")



def send_zeptomail_email(to_address, to_name, subject, html_body, attachments=None):
    url = "https://api.zeptomail.in/v1.1/email"

    payload = {
        "from": {"address": "contact@anrevents.in"},
        "to": [{"email_address": {"address": to_address, "name": to_name}}],
        "subject": subject,
        "htmlbody": html_body
    }

    if attachments:
        payload["attachments"] = []
        for attachment in attachments:
            with open(attachment, "rb") as file:
                content = base64.b64encode(file.read()).decode("utf-8")
            payload["attachments"].append({
                "content": content,
                "filename": attachment.split("/")[-1]  # Extracting filename from path
            })

    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'authorization': "Zoho-enczapikey PHtE6r1fQem4jTYsoxED4PXuRJKhMtgsruMyKFJPuI5KCfJVTk0Gq9x/x2K++U17VPMTHPKay4lo5LrPsbnWIW3qZ21PCWqyqK3sx/VYSPOZsbq6x00et1QSdEbZXIbsdddr1iTUstbTNA==",
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        print("Email sent successfully")
    else:
        print(f"Failed to send email: {response.status_code}, {response.text}")


# views.py or another suitable file

def send_registration_confirmation_email(user, payment):
    to_address = user.email
    to_name = user.first_name + ' ' + user.last_name
    subject = "Registration Acknowledgement - BHARAT DALHAN SEMINAR 2024"
    amount = payment.amount
    amount_paid = payment.amount_paid if payment.amount_paid else 0
    amount_outstanding = amount - amount_paid
    country = Address.objects.filter(user=user).first().country.name
    if country == 'India':
        currency = 'INR'
    else:
        currency = 'USD'


    # HTML content with placeholders
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Registration Confirmation</title>
        <style>
            body {
                font-family: Arial, sans-serif;
            }
            .container {
                width: 60%;
                margin: 0 auto;
                padding: 20px;
                border: 1px solid #ccc;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }
            .header, .footer {
                text-align: center;
                margin-bottom: 20px;
            }
            .details-table, .bank-details-table {
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }
            .details-table th, .details-table td,
            .bank-details-table th, .bank-details-table td {
                border: 1px solid #ccc;
                padding: 8px;
                text-align: left;
            }
            .details-table th {
                background-color: #f2f2f2;
            }
            .instructions {
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>

    <div class="container">
        <div class="header">
            <h1>BHARAT DALHAN SEMINAR 2024</h1>
            <p>Registration ID: <strong>{{ RegID }}</strong></p>
        </div>

        <p>Dear {{ Title }} {{ Firstname }} {{ Lastname }}</p>

        <p>Thank you for initiating your registration for BHARAT DALHAN SEMINAR 2024 taking place on 09th August 2024 at Vigyan Bhawan, Delhi.</p>

        <p>Please note that your registration is not confirmed until you complete the process & remit the payment. We request you to kindly make full payment of your outstanding dues at the earliest in order to confirm your registration.</p>

        <h3>Registration Details</h3>
        <table class="details-table">
            <tr>
                <th>Details</th>
                <td>{{ RegCategory }} </td>
            </tr>
            <tr>
                <th>Name Badge</th>
                <td>{{ Title }} {{ Firstname }} {{ Lastname }}</td>
            </tr>
            <tr>
                <th>Amount Required</th>
                <td>{{Currency}} {{ Amountrequired }} </td>
            </tr>
            <tr>
                <th>Amount Outstanding</th>
                <td>{{Currency}} {{ Amountrequired }} </td>
            </tr>
            <tr>
                <th>Payment Status</th>
                <td>{{ Payment Status }}</td>
            </tr>
        </table>

        <p>Attached herewith please find Proforma Invoice towards registration. Final GST Invoice will be emailed within 30 days of payment being received in our account.</p>

        <p>The online link to make payments will be LIVE soon, till then you can use the bank details to transfer/remit the amount.</p>

        <h3>Bank Details for Payment</h3>
        <table class="bank-details-table">
            <tr>
                <th>Account Name</th>
                <td>India Pulses and Grains Association</td>
            </tr>
            <tr>
                <th>Account No</th>
                <td>50100104107473</td>
            </tr>
            <tr>
                <th>Bank Name</th>
                <td>HDFC Bank</td>
            </tr>
            <tr>
                <th>Branch Address</th>
                <td>Santacruz (West), Mumbai, India</td>
            </tr>
            <tr>
                <th>IFSC Code</th>
                <td>HDFC0000079</td>
            </tr>
            <tr>
                <th>SWIFT Code</th>
                <td>HDFCINBB</td>
            </tr>
            <tr>
                <th>Correspondent Bank</th>
                <td>J P MORGAN CHASE BANK, NEW YORK, USA</td>
            </tr>
            <tr>
                <th>Correspondent Bank SWIFT Code</th>
                <td>CHASUS33</td>
            </tr>
            <tr>
                <th>Correspondent Bank Account No</th>
                <td>001-1-406717</td>
            </tr>
        </table>

        <p class="instructions">In case you have already processed your payment, please update with the payment details for us to confirm the same and validate your registration. Kindly let us know if you need any further assistance to process the payment.</p>

        <p>Best regards,</p>
        <p><strong>Registration Support Desk | BHARAT DALHAN SEMINAR 2024</strong></p>
        <p>Email ID: <a href="mailto:bds2024@ipga.co.in">bds2024@ipga.co.in</a></p>
        <p>Phone: 022 - 24909133 / 022 - 35619327</p>
    </div>

    </body>
    </html>
    """

    # Populate the HTML content with actual values
    html_body = html_template.replace('{{ RegID }}', user.reg_id if user.reg_id else '')
    html_body = html_body.replace('{{ Title }}', user.title if user.title else '')
    html_body = html_body.replace('{{ Firstname }}', user.first_name)
    html_body = html_body.replace('{{ Lastname }}', user.last_name if user.last_name else '')
    html_body = html_body.replace('{{ RegCategory }}', 'Delegate')
    html_body = html_body.replace('{{Currency}}', currency)
    html_body = html_body.replace('{{ Amountrequired }}', str(amount))
    html_body = html_body.replace('{{ Payment Status }}', 'Not paid')

    context = {
        'gstn': '27AACCI6531P1Z5',
        'customer_name': 'Test, Mr Onsite Smt',
        'customer_address': 'Jhjhjhjhj, Kmm Kjkk, India, 78787',
        'customer_gstn': '',
        'delegate_type': 'EB INDIAN SPOUSE',
        'gst_amount': '7200',
        'qty': '1',
        'amount': '35400.00',
        'total_owing': '47,200.00'
    }

    # html_string = render_to_string('proforma_email.html', context)
    # html = HTML(string=html_string)
    # pdf_file = html.write_pdf()

    send_zeptomail_email(to_address, to_name, subject, html_body, attachments=None)


# Call the function to send the email
# send_registration_confirmation_email()

class PaymentTransferAPIView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PaymentTransferSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = PaymentTransferSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            data = serializer.validated_data
            instance = serializer.create(data)
            send_registration_confirmation_email(user, instance)

            return APIResponse(data=None, status_code=200, message="Email sent successfully")
        else:
            return APIResponse(data=None, status_code=400, message=serializer.errors)


