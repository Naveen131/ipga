import base64
import hashlib
import json
import tempfile
from binascii import hexlify, unhexlify
from datetime import timezone
from hashlib import md5
# import md5
import requests
from Crypto.Cipher import AES
from django.conf import settings
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from weasyprint import HTML

from ipgaevent.settings import MERCHANT_ID, WORKING_KEY, ACCESS_CODE
from utils.utils import APIResponse
from .models import UserProfile, Address, Payment
from .views import send_zeptomail_email

BLOCK_SIZE = 16

# def pad(data):
#     length = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
#     return data + chr(length) * length
# def pad(data):
#     padding_length = BLOCK_SIZE - len(data) % BLOCK_SIZE
#     padding = chr(padding_length) * padding_length
#     return data + padding

def unpad(data):
    return data[:-ord(data[len(data) - 1:])]

from Crypto.Cipher import AES
# import md5

def pad(data):
	length = 16 - (len(data) % 16)
	data += chr(length)*length
	return data

# def encrypt(plainText,workingKey):
#     iv = b'\x00' * 16  # Ensure the IV is in bytes
#     plainText = pad(plainText).encode('utf-8')
#     encDigest = md5(workingKey.encode('utf-8')).digest()
#     enc_cipher = AES.new(encDigest, AES.MODE_CBC, iv)
#     encryptedText = enc_cipher.encrypt(plainText)
#     encryptedText_base64 = base64.b64encode(encryptedText).decode('utf-8')
#     return encryptedText_base64

def encrypt(plainText, workingKey):
    iv = '\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'.encode("utf-8")
    plainText = pad(plainText)
    bytearrayWorkingKey = bytearray()
    bytearrayWorkingKey.extend(map(ord, workingKey))
    enc_cipher = AES.new(hashlib.md5(bytearrayWorkingKey).digest(), AES.MODE_CBC, iv)
    return hexlify(enc_cipher.encrypt(plainText.encode("utf-8"))).decode('utf-8')


def decrypt(cipherText, workingKey):
    iv = '\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
    encryptedText = unhexlify(cipherText)
    bytearrayWorkingKey = bytearray()
    bytearrayWorkingKey.extend(map(ord, workingKey))
    decCipher = AES.new(hashlib.md5(bytearrayWorkingKey).digest(), AES.MODE_CBC, iv)
    return unpad(decCipher.decrypt(encryptedText).decode('utf-8'))


def generate_ccavenue_request(data):
    # import pdb;pdb.set_trace()
    # settings = getattr(settings, 'CCAvenue_SETTINGS')
    working_key = WORKING_KEY
    access_code = ACCESS_CODE
    encrypted_data = encrypt(data, working_key[0])
    return {
        'encRequest': encrypted_data,
        'access_code': access_code
    }


def validate_ccavenue_response(response):
    # settings = getattr(settings, 'CCAvenue_SETTINGS')
    working_key = WORKING_KEY
    decrypted_data = decrypt(response, working_key)
    return decrypted_data


from rest_framework import views
from rest_framework.response import Response
from django.shortcuts import redirect
from .serializers import CCAvenueRequestSerializer
# from .utils.ccavenue import generate_ccavenue_request, validate_ccavenue_response

class CCAvenuePaymentView(views.APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        serializer = CCAvenueRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        # request_data = {
        #     'merchant_id': MERCHANT_ID,
        #     'order_id': data['order_id'],
        #     'currency': data['currency'],
        #     'amount': data['amount'],
        #     'redirect_url': data['redirect_url'],
        #     'cancel_url': data['cancel_url'],
        #     'language': 'EN',
        #     'billing_name': "Naveen Chaudhary",
        #     'billing_address':"Test Address",
        #     'billing_city': "Ghaziabad",
        #     'billing_state': "Uttar Pradesh",
        #     'billing_zip': "201001",
        #     'billing_country': "India",
        #     'billing_tel': "+919717266959",
        #     'billing_email': "naveen.c131@gmail.com"
        # }

        user = request.user
        full_name = user.first_name + ' ' + user.last_name
        profile = UserProfile.objects.get(user=user)
        address = Address.objects.get(user=user)
        currency = 'INR' if address.country.name == 'India' else 'USD'

        merchant_data = ('merchant_id=' + f"{MERCHANT_ID}" + '&' +
                         'order_id=' + user.reg_id + '&' + "currency=" + currency +
                         '&' + 'amount=' + str(data['amount']) + '&' + 'redirect_url=' + data['redirect_url'] +
                         '&' + 'cancel_url=' + data['cancel_url'] + '&' + 'language=' + 'English' + '&'
                         + 'billing_name=' + full_name + '&' + 'billing_address=' + address.address +
                         '&' + 'billing_city=' + address.city + '&' + 'billing_state=' + address.state +
                         '&' + 'billing_zip=' + address.pincode + '&' + 'billing_country=' + address.country.name +
                         '&' + 'billing_tel=' + user.mobile_number+ '&' + 'billing_email=' + user.email)

        # import pdb;pdb.set_trace()
        ccavenue_request = generate_ccavenue_request(merchant_data)
        ccavenue_url = 'https://secure.ccavenue.com/transaction/transaction.do?command=initiateTransaction'

        return Response({
            'ccavenue_url': ccavenue_url,
            'ccavenue_request': ccavenue_request
        })


def send_registration_confirmation_email(user, payment):
    to_address = user.email
    to_name = user.first_name + ' ' + user.last_name
    subject = "Registration Confirmation - BHARAT DALHAN SEMINAR 2024"
    amount = payment.amount
    amount_paid = payment.amount_paid if payment.amount_paid else 0
    amount_outstanding = amount - amount_paid
    country = Address.objects.filter(user=user).first().country.name
    if country == 'India':
        currency = 'INR'
    else:
        currency = 'USD'
    html_template = """ 
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>THE BHARAT DALHAN SEMINAR 2024 Registration Confirmation</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            color: #333;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            border: 1px solid #ddd;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h1 {
            text-align: center;
            color: #333;
        }
        .section {
            margin-bottom: 20px;
        }
        .section-title {
            background-color: #f2f2f2;
            padding: 10px;
            font-size: 18px;
            border-bottom: 1px solid #ddd;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        table, th, td {
            border: 1px solid #ddd;
        }
        th, td {
            padding: 10px;
            text-align: left;
        }
        .highlight {
            background-color: #ffeb3b;
            padding: 10px;
            margin-top: 20px;
        }
        .contact {
            margin-top: 20px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>THE BHARAT DALHAN SEMINAR 2024</h1>
        <p><strong>Registration ID:</strong> <span id="regId">{{RegID}}</span></p>
        <p>Dear <span id="title">{{Title}}</span> <span id="firstname">{{Firstname}}</span> <span id="lastname">{{LastName}}</span>,</p>
        <p>Congratulations! You’re registered for THE BHARAT DALHAN SEMINAR 2024 taking place on 9th August 2024 at Vigyan Bhawan, New Delhi.</p>
        <p>Kindly find your registration details mentioned below.</p>

        <div class="section">
            <div class="section-title">Registration Details</div>
            <table>
                <tr>
                    <th>Details</th>
                    <td><span id="details">Delegate</span></td>
                </tr>
                <tr>
                    <th>Name Badge</th>
                    <td><span id="badge">{{Title}}  {{Firstname}}  {{LastName}} </span></td>
                </tr>
                <tr>
                    <th>Amount Required (INR)</th>
                    <td><span id="amountRequired">{{amountRequired}}</span></td>
                </tr>
                <tr>
                    <th>Amount Outstanding (INR)</th>
                    <td><span id="amountOutstanding">{{amountOutstanding}}</span></td>
                </tr>
                <tr>
                    <th>Payment Status</th>
                    <td><span id="paymentStatus">{{paymentStatus}}</span></td>
                </tr>
            </table>
        </div>

        <div class="section">
            <div class="section-title">Payment Details</div>
            <table>
                <tr>
                    <th>Invoice Number</th>
                    <td><span id="invoiceNumber">{{invoiceNumber}}</span></td>
                </tr>
                <tr>
                    <th>Date of Payment</th>
                    <td><span id="dateOfPayment">{{dateOfPayment}}</span></td>
                </tr>
                <tr>
                    <th>Currency</th>
                    <td><span id="currency">{{currency}}</span></td>
                </tr>
                <tr>
                    <th>Payment Reference</th>
                    <td><span id="paymentReference">{{paymentReference}}</span></td>
                </tr>
                <tr>
                    <th>Amount</th>
                    <td><span id="totalPaidAmount">{{totalPaidAmount}}</span></td>
                </tr>
            </table>
        </div>

        <div class="highlight">
            Kindly carry this confirmation letter in soft/hard copy Onsite.
        </div>

        <p>Please find attached herewith Invoice towards your payment of registration fee.</p>
        <p>We look forward to welcoming you at The Bharat Dalhan Seminar 2024!</p>

        <div class="contact">
            <p><strong>Registration Support Desk | BHARAT DALHAN SEMINAR 2024</strong></p>
            <p>Email ID: <a href="mailto:bds2024@ipga.co.in">bds2024@ipga.co.in</a></p>
            <p>Phone: 022 - 24909133 / 022 - 35619327</p>
        </div>
    </div>
</body>
</html>

    """
    html_body = html_template.replace('{{RegID}}', user.reg_id)
    html_body = html_body.replace('{{Title}}', user.title if user.title else 'Mr.')
    html_body = html_body.replace('{{Firstname}}', user.first_name)
    html_body = html_body.replace('{{LastName}}', user.last_name)
    html_body = html_body.replace('{{amountRequired}}', str(payment.amount + payment.tax))
    html_body = html_body.replace('{{amountOutstanding}}', str(0))
    html_body = html_body.replace('{{paymentStatus}}', payment.status)
    html_body = html_body.replace('{{invoiceNumber}}', str(user.reg_id))
    html_body = html_body.replace('{{dateOfPayment}}', str(payment.payment_date.date()))
    html_body = html_body.replace('{{currency}}', currency)
    html_body = html_body.replace('{{paymentReference}}', payment.payment_mode)
    html_body = html_body.replace('{{totalPaidAmount}}', str(payment.amount + payment.tax))
    address = Address.objects.get(user=user)
    profile = UserProfile.objects.get(user=user)

    context = {

        'customer_name': user.first_name + ' ' + user.last_name,
        'customer_address': address.address + ' ' + address.city + ', ' + address.state + ', ' + address.country.name,
        'customer_gstn':profile.gst_number,
        'delegate_type': 'Delegate',
        'gst_amount': currency + ' ' + str(payment.tax),
        'qty': '1',
        'amount': currency + ' ' + str(amount),
        'total_owing': currency + ' ' + str(payment.amount + payment.tax),
        'invoice_number': str(user.reg_id),
        'company': user.organization_name,
        'invoice_date': payment.payment_date.date(),
    }

    html_string = render_to_string('invoice.html', context)
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
        "name": "invoice.pdf"
    }]
    # Attach PDF to the email
    # attachments = ('proforma_invoice.pdf', pdf_file, 'application/pdf')

    send_zeptomail_email(to_address, to_name, subject, html_body, attachments=attachments)







class CCAvenueResponseView(views.APIView):
    def post(self, request, *args, **kwargs):
        enc_response = request.data.get('encResp')
        if not enc_response:
            return Response({'error': 'Invalid response'}, status=400)

        response_data = validate_ccavenue_response(enc_response)



        # Handle the response accordingly
        # You can parse response_data and update your order status

        return Response({'message': 'Payment successful', 'data': response_data})


def payment_webhook(request):
    if request.method == 'POST':
        try:
            payload = json.loads(request.body)
            # Add verification logic here if needed (e.g., verify signature)
            print("=================================", payload)
            handle_payment_response(payload)
            return JsonResponse({'status': 'success'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid payload'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)


def handle_payment_response(payload):
    pass
    # # Example logic to handle the payment response
    # order_id = payload.get('order_id')
    # payment_status = payload.get('status')
    # amount_paid = payload.get('amount')
    #
    # # Find the order by ID and update its status
    # try:
    #     order = Order.objects.get(id=order_id)
    #     if payment_status == 'success':
    #         order.status = 'paid'
    #         order.amount_paid = amount_paid
    #     else:
    #         order.status = 'failed'
    #     order.save()
    # except Order.DoesNotExist:
    #     # Handle the case where the order does not exist
    #     pass


class PaymentSuccessResponse(CreateAPIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        from django.utils import timezone
        data = request.data
        amount = data.get('amount')
        tax = data.get('tax')
        user = request.user
        amount = amount - tax
        user_profile = UserProfile.objects.get(user=user)
        address = Address.objects.filter(user=user)

        if address.exists():
            address = address.first()
            if address.country.name == 'India' and user_profile.membership_code:
                tax = 360
                amount = 2000
            elif address.country.name == 'India' and user_profile.membership_code == None:
                tax = 540
                amount = 3000
            else:
                tax = 18
                amount = 100

        payment = Payment.objects.create(user=user, amount=amount, payment_date=timezone.now(), status='Success', tax=tax)
        # send_registration_confirmation_email(user, payment)
        return APIResponse(message='Payment successful', data={'payment_id': payment.id}, status_code=200)