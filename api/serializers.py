from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import *

# --- AUTH SERIALIZERS ---
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Custom claims
        token['name'] = user.get_full_name()
        token['role'] = user.role
        token['email'] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Plain-text response for frontend
        data['name'] = self.user.get_full_name()
        data['role'] = self.user.role
        data['email'] = self.user.email
        return data

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'role')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=validated_data.get('role', 'donor')
        )
        return user

# --- RESOURCE SERIALIZERS ---

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined']

class ApplicationSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Application
        fields = ['id', 'user', 'user_email', 'applicant_name', 'category', 'status', 'details', 'created_at']
        read_only_fields = ['id', 'created_at', 'user', 'user_email']

    def create(self, validated_data):
        # Automatically assign the logged-in user to the application
        request = self.context.get('request')
        validated_data['user'] = request.user
        return super().create(validated_data)

class InventorySerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)

    class Meta:
        model = Inventory
        fields = ['id', 'owner', 'owner_name', 'blood_group', 'units', 'last_updated']
        # Fix 1: Added 'owner' to read_only_fields
        read_only_fields = ['id', 'last_updated', 'owner_name', 'owner']

class DonationSerializer(serializers.ModelSerializer):
    donor_name = serializers.CharField(source='donor.get_full_name', read_only=True)
    location_name = serializers.CharField(source='location.get_full_name', read_only=True, allow_null=True)

    class Meta:
        model = Donation
        fields = ['id', 'donor', 'donor_name', 'location', 'location_name', 'blood_group', 'units', 'donation_date', 'status']
        read_only_fields = ['id', 'donation_date', 'donor']

class InventoryLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = InventoryLog
        fields = ['id', 'action_type', 'amount', 'source', 'date', 'user_name']