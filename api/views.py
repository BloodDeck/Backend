from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView

# Internal imports
from .models import User  # Ensure this is imported
from .serializers import MyTokenObtainPairSerializer 
# from .serializers import UserSerializer, ApplicationSerializer, InventorySerializer

# --- AUTHENTICATION ---

class MyTokenObtainPairView(TokenObtainPairView):
    """
    Custom Login view returning JWT tokens and user role metadata.
    """
    serializer_class = MyTokenObtainPairSerializer

# --- DASHBOARDS & STATS ---

class DashboardStatsView(generics.RetrieveAPIView):
    """
    Returns general system statistics based on the requesting user's role.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        stats = {
            "user": request.user.email,
            "role": request.user.role,
            "status": "General stats active"
        }
        return Response(stats, status=status.HTTP_200_OK)

class SuperAdminDashboardView(generics.RetrieveAPIView):
    """
    Admin-only dashboard for high-level system overview.
    """
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        return Response({
            "message": f"Welcome Super Admin {request.user.email}",
            "system_health": "Optimal",
            "pending_approvals": 5
        }, status=status.HTTP_200_OK)

class HospitalDashboardView(generics.RetrieveAPIView):
    """
    Dashboard for Hospital users to track their specific requests.
    """
    permission_classes = [IsAuthenticated] # Future: add IsHospital permission

    def get(self, request, *args, **kwargs):
        return Response({"message": "Hospital specific metrics and alerts"}, status=status.HTTP_200_OK)

# --- USER MANAGEMENT ---

class UserListView(generics.ListAPIView):
    """
    Administrative view to list all registered users.
    """
    permission_classes = [IsAdminUser]
    # serializer_class = UserSerializer
    # queryset = User.objects.all()

    def list(self, request, *args, **kwargs):
        # Placeholder until Serializers are implemented
        return Response({"users": []}, status=status.HTTP_200_OK)

# --- APPLICATIONS (Blood Bank & Hospital) ---

class ApplicationListView(generics.ListCreateAPIView):
    """
    Handles listing and creating applications for Blood Banks and Hospitals.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Professional practice: Users see only what belongs to them
        user = self.request.user
        if user.is_staff:
            return [] # Application.objects.all()
        return [] # Application.objects.filter(user=user)

    def list(self, request, *args, **kwargs):
        return Response({"applications": []}, status=status.HTTP_200_OK)

class ApplicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Full CRUD for a single application.
    """
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        return Response({"id": pk, "details": "Full application data"}, status=status.HTTP_200_OK)

# --- INVENTORY & STOCK ---

class InventoryListView(generics.ListAPIView):
    """
    View to monitor global or hospital-specific blood inventory.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response({"inventory": [], "last_updated": "2026-01-21"}, status=status.HTTP_200_OK)

class HospitalInventoryView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response({"hospital_stock": "Supply levels for your facility"}, status=status.HTTP_200_OK)

class BloodBankStockView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response({"stock": "Current central blood bank levels"}, status=status.HTTP_200_OK)

# --- DONOR SPECIFIC ---

class DonorHistoryView(generics.ListAPIView):
    """
    Lists donation history for the logged-in donor.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response({
            "donor": request.user.email,
            "history": []
        }, status=status.HTTP_200_OK)