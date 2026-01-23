from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, Application

# --- AUTH SERIALIZER ---
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Custom claims
        token['role'] = user.role
        token['email'] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Plain-text response for frontend
        data['role'] = self.user.role
        data['email'] = self.user.email
        return data

# --- RESOURCE SERIALIZERS (Fixes the AssertionError) ---

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'role', 'is_active', 'date_joined']

class ApplicationSerializer(serializers.Serializer):
    """
    Base Serializer for Blood Bank and Hospital applications.
    """
    id = serializers.IntegerField(read_only=True)
    applicant_name = serializers.CharField(max_length=255)
    category = serializers.ChoiceField(choices=['bloodbank', 'hospital'])
    status = serializers.CharField(default='pending')
    created_at = serializers.DateTimeField(read_only=True)

class InventorySerializer(serializers.Serializer):
    """
    Base Serializer for Blood Inventory tracking.
    """
    blood_type = serializers.CharField(max_length=3)
    units = serializers.IntegerField()
    last_updated = serializers.DateTimeField(read_only=True)

class ApplicationSerializer(serializers.ModelSerializer):
    # This automatically maps to your model fields
    class Meta:
        model = Application
        fields = ['id', 'applicant_name', 'category', 'status', 'details', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        # Automatically assign the logged-in user to the application
        request = self.context.get('request')
        validated_data['user'] = request.user
        return super().create(validated_data)