from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models

from ipgaevent.storage_backends import PublicMediaStorage


# Create your models here.


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
    password = models.CharField(max_length=255)
    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["mobile_number"]

    def __str__(self):
        return self.email if self.email else "Undefined User"




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