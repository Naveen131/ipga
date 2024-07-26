import base64
import uuid

import requests
from django.core.files.base import ContentFile
from django.utils.text import slugify
from rest_framework import serializers

from accounts.models import User, UserProfile, City, State, Country, Pincode, Address, Payment
from utils.utils import CustomBase64FileField


class SignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],

        )
        user.set_password(validated_data['password'])
        user.reg_id = f"BDS2024{user.id}"
        user.save()
        return user


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True,error_messages={'required': 'Email is required'})
    password = serializers.CharField(required=True,error_messages={'required': 'Password is required'})

    class Meta:
        model = User
        fields = ('email', 'password')


    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        if email and password:
            user = User.objects.filter(email=email).first()
            if user:
                if not user.check_password(password):
                    raise serializers.ValidationError("Invalid Password")
            else:
                raise serializers.ValidationError("User does not exist")
        else:
            raise serializers.ValidationError("Email and Password is required")
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True, error_messages={'required': 'Title is required'})
    first_name = serializers.CharField(required=True,
                                       error_messages={'required': 'First Name is required'})
    last_name = serializers.CharField(required=True,
                                      error_messages={'required': 'Last Name is required'})
    mobile_number = serializers.CharField(required=True,
                                          error_messages={'required': 'Mobile Number is required'})
    gender = serializers.CharField(required=True,
                                   error_messages={'required':'Gender is required'})
    organization = serializers.CharField(required=True,
                                         error_messages={'required': 'Organization Name is required'})
    designation = serializers.CharField(required=True,
                                        error_messages={'required': 'Designation is required'})

    gst_number = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    gst_file = CustomBase64FileField(required=False)
    aadhar_number = serializers.CharField(required=False)

    aadhar_file = CustomBase64FileField(required=False)
    passport_number = serializers.CharField(required=False)
    passport_file = CustomBase64FileField(required=False)
    city = serializers.CharField(required=False)
    state = serializers.CharField(required=False)
    country = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all(),required=True, error_messages={'required': 'Country is required'})
    pincode = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    business_number = serializers.CharField(required=False)
    direct_number = serializers.CharField(required=False)

    primary_address = serializers.CharField(required=False)
    primary_state = serializers.CharField(required=False)
    primary_city = serializers.CharField(required=False)
    primary_pincode = serializers.CharField(required=False)
    primary_address = serializers.CharField(required=False)
    is_default_address = serializers.BooleanField(required=False)

    class Meta:
        model = UserProfile
        fields = ('title', 'first_name', 'last_name', 'mobile_number', 'gender', 'organization', 'designation',
                  'gst_number', 'gst_file', 'aadhar_number', 'aadhar_file', 'passport_number', 'passport_file',
                  'city', 'state', 'country', 'pincode', 'business_number', 'direct_number', 'primary_address',
                  'primary_state', 'primary_city', 'primary_pincode', 'is_default_address','address')

    def create(self, validated_data):
        # import pdb;pdb.set_trace()
        validated_data['organization_name'] = validated_data.pop('organization')
        user = self.context['request'].user
        is_default_address = validated_data.pop('is_default_address', False)
        # profile data
        profile_data = dict(

        user=user,
        gst_number=validated_data.pop('gst_number', None),
        gst_file=validated_data.pop('gst_file', None),
        aadhar_number=validated_data.pop('aadhar_number', None),
        aadhar_file=validated_data.pop('aadhar_file', None),
        passport_number=validated_data.pop('passport_number', None),
        passport_file=validated_data.pop('passport_file', None),
        business_number=validated_data.pop('business_number', None),
        direct_number=validated_data.pop('direct_number', None),
        )

        # create user profile
        user_profile = UserProfile.objects.create(**profile_data)

        # address object
        # pincode = Pincode.objects.get_or_create(pincode=pincode)
        # if pincode:
        #     pincode = pincode[0]
        country = validated_data.pop('country', None)

        address_data = dict(
            user=user,
            city=validated_data.pop('city'),
            state=validated_data.pop('state'),
            country=country,
            pincode=validated_data.pop('pincode'),
            address_type='Billing',
            address = validated_data.pop('address'),
            is_default=is_default_address,

        )

        # create address
        address = Address.objects.create(**address_data)

        # primary address object
        if not is_default_address:
            primary_address_data = dict(
                user=user,
                city=validated_data.pop('primary_city', None),
                state=validated_data.pop('primary_state', None),
                country=country,
                pincode=validated_data.pop('primary_pincode', None),
                address=validated_data.pop('primary_address', None),
                address_type='Shipping'
            )

            # create primary address
            primary_address = Address.objects.create(**primary_address_data)



        # update user data
        for key, value in validated_data.items():
            setattr(user, key, value)

        user.save()
        return user


class Base64OrURLFileField(serializers.FileField):

    def to_internal_value(self, data):
        # If data is a URL
        if isinstance(data, str) and data.startswith('http'):
            response = requests.get(data)
            if response.status_code == 200:
                file_name = uuid.uuid4().hex
                return ContentFile(response.content, name=file_name)
            else:
                raise serializers.ValidationError('Invalid file URL.')

        # If data is a base64 string
        elif isinstance(data, str) and 'data:' in data and ';base64,' in data:
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            file_name = f"{uuid.uuid4().hex}.{ext}"
            return ContentFile(base64.b64decode(imgstr), name=file_name)

        raise serializers.ValidationError('Invalid file data.')

class DetailsUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=False)
    title = serializers.CharField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    mobile_number = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    organization = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    designation = serializers.CharField(required=False)
    gst_number = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    gst_file = Base64OrURLFileField(required=False)
    aadhar_number = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    aadhar_file = Base64OrURLFileField(required=False)
    passport_number = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    passport_file = Base64OrURLFileField(required=False)
    city = serializers.CharField(required=False)
    state = serializers.CharField(required=False)
    country = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all(), required=False)
    pincode = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    business_number = serializers.CharField(required=False)
    direct_number = serializers.CharField(required=False)
    gender = serializers.CharField(required=False)


    class Meta:
        model = UserProfile
        fields = ('title', 'first_name', 'last_name', 'mobile_number', 'email', 'organization', 'designation',
                  'gst_number', 'gst_file', 'aadhar_number', 'aadhar_file', 'passport_number', 'passport_file',
                  'city', 'state', 'country', 'pincode', 'business_number', 'direct_number', 'address', 'gender')

    def update(self, instance, validated_data):
        # import pdb;pdb.set_trace()
        # profile data


        profile = UserProfile.objects.filter(user=instance).first()
        profile_data = dict(
            gst_number=validated_data.pop('gst_number', None),
            gst_file=validated_data.pop('gst_file', None),
            aadhar_number=validated_data.pop('aadhar_number', None),
            aadhar_file=validated_data.pop('aadhar_file', None),
            passport_number=validated_data.pop('passport_number', None),
            passport_file=validated_data.pop('passport_file', None),
            business_number=validated_data.pop('business_number', None),
            direct_number=validated_data.pop('direct_number', None),
        )

        # update user profile
        for key, value in profile_data.items():
            if value is not None:
                setattr(profile, key, value)

        # address object
        country = validated_data.pop('country', None)
        address_data = dict(
            city=validated_data.pop('city'),
            state=validated_data.pop('state'),
            country=country,
            pincode=validated_data.pop('pincode'),
            address = validated_data.pop('address'),
        )

        # update address
        address = Address.objects.filter(user=instance).first()
        for key, value in address_data.items():
            setattr(address, key, value)
        address.save()

        # update user data
        for key, value in validated_data.items():
            setattr(instance, key, value)

        profile.save()
        instance.save()
        return instance


class GetProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('title', 'first_name', 'last_name', 'mobile_number', 'email',
                  'organization_name', 'designation', 'gender')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        profile = UserProfile.objects.filter(user=instance).first()
        address = Address.objects.filter(user=instance).first()
        data['organization'] = data.pop('organization_name')
        data['gst_number'] = profile.gst_number
        data['aadhar_number'] = profile.aadhar_number
        data['passport_number'] = profile.passport_number
        data['business_number'] = profile.business_number
        data['direct_number'] = profile.direct_number
        data['gst_file'] = profile.gst_file.url if profile.gst_file else None
        data['aadhar_file'] = profile.aadhar_file.url if profile.aadhar_file else None
        data['passport_file'] = profile.passport_file.url if profile.passport_file else None
        data['city'] = address.city
        data['state'] = address.state
        data['country'] = address.country.name
        data['pincode'] = address.pincode
        data['address'] = address.address
        return data


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = '__all__'


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


class PaymentTransferSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    tax = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)

    class Meta:
        model = Payment
        fields = ('amount',)

    def create(self, validated_data):
        user = self.context['request'].user
        amount = validated_data.get('amount')
        tax = validated_data.get('tax')
        amount = amount - tax
        instance = Payment.objects.create(amount=amount, tax=tax, user=user)
        return instance


class CCAvenueRequestSerializer(serializers.Serializer):
    # order_id = serializers.CharField(max_length=50)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(max_length=3)
    redirect_url = serializers.URLField()
    cancel_url = serializers.URLField()


