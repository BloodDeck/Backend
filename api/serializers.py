from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims (these are encoded in the token)
        token['username'] = user.username
        token['role'] = user.role  # hospital, donor, admin, or bloodbank
        
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # Add the role to the plain-text response for easy frontend access
        data['role'] = self.user.role
        data['username'] = self.user.username
        return data