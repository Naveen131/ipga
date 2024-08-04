import base64
import tempfile

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from django.template.loader import render_to_string
from weasyprint import HTML

from ipgaevent.storage_backends import PublicMediaStorage


# Create your models here.


def send_apology_email(user):
    from accounts.views import send_zeptomail_email
    html_body= """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Payment Reminder Apology</title>
    <style>
        body {
            font-family: Arial, sans-serif;
        }
        .container {
            width: 100%;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 20px;
        }
        .content {
            font-size: 16px;
            line-height: 1.6;
        }
        .footer {
            margin-top: 20px;
            text-align: center;
            font-size: 14px;
            color: #555;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>Bharat Dalhan Seminar 2024</h2>
        </div>
        <div class="content">
            <p>Dear Sir/Ma’am,</p>
            <p>Greetings from the Bharat Dalhan Seminar 2024!</p>
            <p>We apologize for the wrong and misleading payment reminder email which you have received earlier due to a technical glitch.</p>
            <p>We request you to ignore the same as your registration is complete and confirmed.</p>
            <p>We are looking forward to seeing you at the seminar.</p>
        </div>
        <div class="footer">
            <p>Kind Regards,<br>
            Registration Desk | Bharat Dalhan Seminar 2024</p>
        </div>
    </div>
</body>
</html>
"""

    to_address = user.email
    to_name = user.first_name + ' ' + user.last_name
    subject = "Apology for incorrect email | Bharat Dalhan Seminar 2024"
    attachments = []
    send_zeptomail_email(to_address, to_name, subject, html_body, attachments=attachments)


def send_payment_reminder_email(user):
    try:
        from accounts.views import send_zeptomail_email

        profile = UserProfile.objects.get(user=user)
        address = Address.objects.filter(user=user)

        currency = 'INR'

        if address.exists():
            address = address.first()
            if address.country.name == 'India' and profile.membership_code:
                tax = 360
                amount = 2000
            elif address.country.name == 'India' and profile.membership_code == None:
                tax = 540
                amount = 3000
            else:
                tax = 18
                amount = 100
                currency = 'USD'

        html_body = """<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>BDS 2024 Payment Reminder</title>
    </head>
    <body>
        <p>Email Subject – <strong>BDS 2024 | Payment Reminder</strong></p>
    
        <p>Thank you for showing your interest in participating in the Bharat Dalhan Seminar 2024, at Vigyan Bhawan, New Delhi.</p>
    
        <p>Please note that your registration is not confirmed until you complete the process and remit the payment. We request you to kindly login to the registration portal, using your existing login credentials and make the online/offline payment at the earliest to confirm your registration.</p>
    
        <p>If you have already processed your payment, please update us with the payment details so we can confirm and validate your registration.</p>
    
        <p>Kindly let us know if you need any further assistance to process the payment.</p>
    
        <p>Best regards,</p>
    
        <p>Registration Support Desk | Bharat Dalhan Seminar 2024<br>
        Email ID: <a href="mailto:bds2024@ipga.co.in">bds2024@ipga.co.in</a><br>
        Phone: 022 - 24909133 / 022 - 35619327</p>
    </body>
    </html>
    """

        context = {

            'customer_name': user.first_name + ' ' + user.last_name,
            'customer_address': address.address + ' ' + address.city + ', ' + address.state + ', ' + address.country.name,

            'delegate_type': 'Delegate',
            'gst_amount': currency + ' ' + str(tax),
            'qty': '1',
            'amount': currency + ' ' + str(amount),
            'total_owing': currency + ' ' + str(amount + tax)
        }
        to_address = user.email
        to_name = user.first_name + ' ' + user.last_name
        subject = "BDS 2024 | Payment Reminder"
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

        send_zeptomail_email(to_address, to_name, subject, html_body, attachments=attachments)
    except Exception as e:
        pass



class CustomUserManager(BaseUserManager):
    def create_user(self, email, mobile_number, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        if not mobile_number:
            raise ValueError("The Mobile Number field must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, mobile_number=mobile_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, mobile_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, mobile_number, password, **extra_fields)

class Nationality(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class User(AbstractUser, PermissionsMixin):
    username = None
    ROLE_TYPE = (
        ('Admin', 'Admin'),
        ('OFFSITE', 'OFFSITE'),
    )
    USER_TYPE = (
        ('Internal', 'Internal'),
        ('Client', 'Client'),
        ('Delegate', 'Delegate'),
        ('VIP', 'VIP'),
        ('Speaker', 'Speaker'),
        ('Sponsor', 'Sponsor'),
        ('Exhibitor', 'Exhibitor'),
        ('Media', 'Media'),
        ('Crew', 'Crew'),
        ('Diplomat', 'Diplomat'),
        ('Vendor', 'Vendor'),
        ('Team', 'Team'),
        ('Executive Committee Member', 'Executive Committee Member'),
        ('Director', 'Director'),
        ('Chairman', 'Chairman'),
        ('Honorary Secretary', 'Honorary Secretary'),
        ('Vice Chairman', 'Vice Chairman'),

    )

    GENDER = (
        ('Male', 'Male'),
        ('Female', 'Female')
    )

    TITLE = (
        ('Mr', 'Mr'),
        ('Mrs', 'Mrs'),
        ('Ms', 'Ms'),
        ('Dr', 'Dr'),
        ('Prof', 'Prof'),
        ('Rev', 'Rev'),
        ('Other', 'Other')
    )
    title = models.CharField(max_length=255, null=True, blank=True, choices=TITLE)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    mobile_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    unique_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    designation = models.CharField(max_length=255, null=True, blank=True)
    region = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=255, null=True, blank=True, choices=GENDER)
    user_type = models.CharField(max_length=255, choices=USER_TYPE, default='Internal')
    organization_name = models.CharField(max_length=255, null=True, blank=True)
    nationality = models.ForeignKey(Nationality, on_delete=models.CASCADE, null=True, blank=True)
    reg_id = models.CharField(max_length=255, null=True, blank=True)
    role = models.CharField(max_length=255, choices=ROLE_TYPE, null=True, blank=True)
    # password = models.CharField(max_length=255)
    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["mobile_number"]

    def __str__(self):
        return self.email if self.email else "Undefined User"

    # def save(self, *args, **kwargs):
    #
    #     if self.password:
    #         self.set_password(self.password)
    #     super(User, self).save(*args, **kwargs)


    def send_proforma_invoice(self):
        from accounts.views import send_registration_confirmation_email

        print("Proforma Invoice sent successfully")
        payment = Payment.objects.filter(user=self).first()
        send_registration_confirmation_email(self, payment)

    def send_payment_reminder(self):
        print("Payment Reminder sent successfully")
        send_payment_reminder_email(self)

    def send_apology(self):
        send_apology_email(self)




class UserProfile(models.Model):

    MARITAL_STATUS = (
        ('Single', 'Single'),
        ('Married', 'Married'),
        ('Divorced', 'Divorced'),

    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gst_number = models.CharField(max_length=255, null=True, blank=True)
    gst_file = models.FileField(storage=PublicMediaStorage(), upload_to='gst_files/', null=True, blank=True)
    passport_number = models.CharField(max_length=255, null=True, blank=True)
    passport_file = models.FileField(storage=PublicMediaStorage(),upload_to='passport_files/', null=True, blank=True)
    aadhar_number = models.CharField(max_length=255, null=True, blank=True)
    aadhar_file = models.FileField(storage=PublicMediaStorage(),upload_to='aadhar_files/', null=True, blank=True)
    business_number = models.CharField(max_length=20, null=True, blank=True)
    direct_number = models.CharField(max_length=20, null=True, blank=True)
    membership_code = models.CharField(max_length=255, null=True, blank=True)


class City(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class State(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Country(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Pincode(models.Model):
    pincode = models.CharField(max_length=6)

    def __str__(self):
        return self.pincode


class Address(models.Model):
    ADDRESS_TYPE = (
        ('Billing', 'Billing'),
        ('Shipping', 'Shipping'),
        ('Other', 'Other')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.TextField()
    city = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True, blank=True)
    address_type = models.CharField(max_length=255, choices=ADDRESS_TYPE, default='Other')
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email if self.user.email else "Undefined Address"


class Membership(models.Model):
    code = models.CharField(max_length=255)

    def __str__(self):
        return self.code


class Payment(models.Model):
    PAYMENT_MODE = (
        ('Cash', 'Cash'),
        ('Card', 'Card'),
        ('Net Banking', 'Net Banking'),
        ('UPI', 'UPI'),
    )

    STATUS = (
        ('Pending', 'Pending'),
        ('Success', 'Success'),
        ('Failed', 'Failed'),
        ('Paid', 'Paid'),
        ('Partial', 'Partial'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    tax = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    payment_mode = models.CharField(max_length=255, choices=PAYMENT_MODE, default='Net Banking')
    payment_date = models.DateTimeField(null=True, blank=True)
    reference_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, choices=STATUS)

    def __str__(self):
        return self.user.email if self.user.email else "Undefined Payment"