from rest_framework import serializers
from .models import User
from rest_framework.validators import ValidationError, UniqueValidator
from django.contrib.auth import authenticate

# class UserSerializer(serializers.ModelSerializer):
#     email = serializers.EmailField(required=True
#         # validators=[UniqueValidator(queryset=User.objects.all())]
#     )
#     password = serializers.CharField(write_only=True, required=True)
    

#     class Meta:
#         model = User
#         fields = ['email', 'password', 'first_name', 'last_name', 'role']

#     # Check for existing email
#     def validate(self, attrs):
#         if User.objects.filter('email').exist():
#             raise ValueError({'email': 'Email already exist'})
#         return attrs

#     def create(self, attrs, validated_data):
#         user = User(
#             email = validated_data['email'],
#             first_name = validated_data['first_name'],
#             last_name = validated_data['last_name'],
#             role = validated_data['role']
#         )
#         user.set_password(validated_data['password'])
#         user.save()
#         return user

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'first_name', 'last_name', 'role']

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            role=validated_data.get('role')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only = True)

    def validate(self, attrs): 
        """ The authenticate method check the email password and return true, using the EmailBackend field
        Hence not needing a model
        """
        user = authenticate(
            email = attrs['email'],
            password = attrs['password']
        )
        if not user:
            raise ValidationError('Invalid email or password')
        attrs['user'] = user
        return attrs

        




