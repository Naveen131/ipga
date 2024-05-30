import base64
import hashlib
from binascii import hexlify, unhexlify
from hashlib import md5
# import md5
import requests
from Crypto.Cipher import AES
from django.conf import settings
from rest_framework.permissions import IsAuthenticated

from ipgaevent.settings import MERCHANT_ID, WORKING_KEY, ACCESS_CODE
from .models import UserProfile, Address

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

class CCAvenueResponseView(views.APIView):
    def post(self, request, *args, **kwargs):
        enc_response = request.data.get('encResp')
        if not enc_response:
            return Response({'error': 'Invalid response'}, status=400)

        response_data = validate_ccavenue_response(enc_response)

        # Handle the response accordingly
        # You can parse response_data and update your order status

        return Response({'message': 'Payment successful', 'data': response_data})