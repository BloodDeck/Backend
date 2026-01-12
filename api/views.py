from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

class SuperAdminDashboard(APIView):
    # Only users with is_staff=True (Super Admins) can access this
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response({"message": f"Welcome Super Admin {request.user.username}"})