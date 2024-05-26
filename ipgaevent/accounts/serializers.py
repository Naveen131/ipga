from rest_framework import serializers

from accounts.models import User, UserProfile, City, State, Country, Pincode, Address
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

    gst_number = serializers.CharField(required=False)
    gst_file = CustomBase64FileField(required=False)
    aadhar_number = serializers.CharField(required=False)

    aadhar_file = CustomBase64FileField(required=False)
    passport_number = serializers.CharField(required=False)
    passport_file = CustomBase64FileField(required=False)
    city = serializers.CharField(required=False)
    state = serializers.CharField(required=False)
    country = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all(),required=True, error_messages={'required': 'Country is required'})
    pincode = serializers.CharField(required=False)
    business_number = serializers.CharField(required=False)
    direct_number = serializers.CharField(required=False)


    class Meta:
        model = UserProfile
        fields = ('title', 'first_name', 'last_name', 'mobile_number', 'gender', 'organization', 'designation',
                  'gst_number', 'gst_file', 'aadhar_number', 'aadhar_file', 'passport_number', 'passport_file',
                  'city', 'state', 'country', 'pincode', 'business_number', 'direct_number')

    def create(self, validated_data):
        # import pdb;pdb.set_trace()
        user = self.context['request'].user
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

        address_data = dict(
            user=user,
            city=validated_data.pop('city'),
            state=validated_data.pop('state'),
            country=validated_data.pop('country'),
            pincode=validated_data.pop('pincode'),
        )

        # create address
        address = Address.objects.create(**address_data)

        # update user data
        for key, value in validated_data.items():
            setattr(user, key, value)

        user.save()
        return user


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



