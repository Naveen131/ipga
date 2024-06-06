import base64
import tempfile

from django.db import transaction
from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User, State, City, Country, Membership, Address, Payment
from accounts.serializers import SignUpSerializer, LoginSerializer, UserProfileSerializer, StateSerializer, \
    CitySerializer, CountrySerializer, PaymentTransferSerializer, GetProfileSerializer, DetailsUpdateSerializer
from ipgaevent import settings
from ipgaevent.settings import ZOHO_API_KEY
from utils.utils import APIResponse
from utils.views import ListAPIViewWithPagination, CustomRetrieveUpdateAPIView


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
            print(e, "====================================")
            return APIResponse(data=None, status_code=400, message="Error in updating user details")



class UpdateUserDetails(CustomRetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = DetailsUpdateSerializer

    def get_object(self):
        return self.request.user

    def get_view_serializer(self, instance):
        return GetProfileSerializer(instance)

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
               profile = UserProfile.objects.filter(user=user).first()
               profile.membership_code = code
               profile.save()
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
    print(attachments)
    payload = {
        "from": {"address": "contact@anrevents.in"},
        "to": [{"email_address": {"address": to_address, "name": to_name}}],
        "subject": subject,
        "htmlbody": html_body,
        "bcc": [{"email_address": {"address": "accounts@ipga.co.in", "name": "Rishabh Sharma"}}]
    }

    if attachments:
        payload["attachments"] = attachments
        # for attachment in attachments:
        #     with open(attachment, "rb") as file:
        #         content = base64.b64encode(file.read()).decode("utf-8")
        #     payload["attachments"].append({
        #         "content": content,
        #         "filename": attachment.split("/")[-1]  # Extracting filename from path
        #     })

    headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'authorization': ZOHO_API_KEY,
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
    html_body = html_body.replace('{{ Title }}', user.title if user.title else 'Mr.')
    html_body = html_body.replace('{{ Firstname }}', user.first_name)
    html_body = html_body.replace('{{ Lastname }}', user.last_name if user.last_name else '')
    html_body = html_body.replace('{{ RegCategory }}', 'Delegate')
    html_body = html_body.replace('{{Currency}}', currency)
    html_body = html_body.replace('{{ Amountrequired }}', str(amount))
    html_body = html_body.replace('{{ Payment Status }}', 'Not paid')
    address = Address.objects.filter(user=user).first()
    # payment = Payment.objects.filter(user=user).first()
    # import pdb;pdb.set_trace()

    context = {

        'customer_name': user.first_name + ' ' + user.last_name,
        'customer_address': address.address + ' ' + address.city + ', ' + address.state + ', ' + address.country.name,

        'delegate_type': 'Delegate',
        'gst_amount': currency + ' ' + str(payment.tax),
        'qty': '1',
        'amount': currency + ' ' + str(amount),
        'total_owing': currency + ' ' + str(payment.amount+payment.tax)
    }

    html_string = render_to_string('proforma_email.html', context)
    html = HTML(string=html_string)
    pdf_file = html.write_pdf()

    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf_file:
        temp_pdf_file.write(pdf_file)
        temp_pdf_file_path = temp_pdf_file.name

        # Attach PDF to the email
    with open(temp_pdf_file_path, "rb") as file:
        pdf_content_base64 = base64.b64encode(file.read()).decode("utf-8")

    # Prepare attachment payload
    attachments = [{
        "content": pdf_content_base64,
        "mime_type": "application/pdf",
        "name": "proforma_invoice.pdf"
    }]
    # Attach PDF to the email
    # attachments = ('proforma_invoice.pdf', pdf_file, 'application/pdf')

    send_zeptomail_email(to_address, to_name, subject, html_body, attachments=attachments)


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




import openpyxl
from django.http import HttpResponse
from .models import User, UserProfile, Address

def generate_xls_report():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "User Report"
    headers = [
        'Title', 'Date Joined', 'First Name', 'Last Name', 'Email', 'Mobile Number',
        'Designation', 'Gender', 'Organization Name',
        'Reg ID', 'GST Number', 'Passport Number', 'Aadhar Number',
        'Business Number', 'Direct Number', 'Address', 'City', 'State', 'Pincode', 'Country',
        'Membership Code', 'Aadhar File', 'Gst File', 'PassPort File', 'Registration Category',
        'Payment Status', 'Payment Reference', 'Payment Date', 'Payment Amount', 'Payment Tax', 'Payment Total',

    ]
    ws.append(headers)

    users = User.objects.all().order_by('id')
    for user in users:
        date_joined = user.date_joined.date()
        user_profile = UserProfile.objects.filter(user=user).first()
        payment = Payment.objects.filter(user=user)
        payment_status = "Not Paid"
        payment_ref = ""
        payment_date = ""
        payment_amount = 0
        payment_tax = 0
        payment_total = 0

        if payment.exists():
            payment = payment.first()
            payment_status = payment.status
            payment_ref = payment.reference_id
            payment_tax = payment.tax
            payment_date = payment.payment_date.date() if payment.payment_date else ""
            payment_amount = payment.amount
            payment_total = payment.amount + payment.tax
        aadhar_file = None
        gst_file = None
        passport_file = None
        if user_profile:
            aadhar_file = user_profile.aadhar_file.url if user_profile.aadhar_file else ''
            gst_file = user_profile.gst_file.url if user_profile.gst_file else ''
            passport_file = user_profile.passport_file.url if user_profile.passport_file else ''
        addresses = Address.objects.filter(user=user)
        address = None
        if addresses.exists():
            address = addresses.first()


        row = [
            user.title, date_joined, user.first_name, user.last_name, user.email, user.mobile_number,
            user.designation, user.gender,
            user.organization_name,
            user.reg_id,
            user_profile.gst_number if user_profile else '',
            user_profile.passport_number if user_profile else '', user_profile.aadhar_number if user_profile else '',
            user_profile.business_number if user_profile else '', user_profile.direct_number if user_profile else '',
            address.address if address else '', address.city if address else '', address.state if address else '',
            address.pincode if address else '', address.country.name if address else '',
            user_profile.membership_code if user_profile else '',
            aadhar_file, gst_file, passport_file,
            "Delegate",
            payment_status, payment_ref,
            payment_date, payment_amount, payment_tax, payment_total




        ]
        ws.append(row)

    from io import BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output

def download_user_report(request):
    output = generate_xls_report()
    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="user_report.xlsx"'
    return response
