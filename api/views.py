from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema, OpenApiExample, extend_schema_view
from django.shortcuts import redirect
from rest_framework.views import APIView

# Internal imports
from .models import User, Application
from .serializers import MyTokenObtainPairSerializer, ApplicationSerializer, InventorySerializer

# --- REDIRECTOR (Internal Utility) ---

class DashboardRedirectView(APIView):
    """
    Professional Redirector: Directs users to their specific dashboard 
    based on their assigned Role after a session-based login.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(exclude=True)  # Hide from Swagger docs as it's an internal helper
    def get(self, request):
        role = request.user.role
        if role == 'admin':
            return redirect('/api/admin/dashboard/')
        elif role == 'hospital':
            return redirect('/api/hospital/dashboard/')
        elif role == 'donor':
            return redirect('/api/donor/dashboard/')
        elif role == 'bloodbank':
            return redirect('/api/bloodbank/dashboard/')
        return redirect('/api/donor/dashboard/')

# --- AUTHENTICATION ---

@extend_schema(tags=['Authentication'], summary="Login to obtain JWT Token")
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

# --- DASHBOARDS & STATS ---

@extend_schema(tags=['Common'], summary="Get general stats for logged in user")
class DashboardStatsView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        stats = {
            "user": request.user.email,
            "role": request.user.role,
            "status": "General stats active"
        }
        return Response(stats, status=status.HTTP_200_OK)

@extend_schema(tags=['Admin'], summary="Super Admin Dashboard Overview")
class SuperAdminDashboardView(generics.RetrieveAPIView):
    permission_classes = [IsAdminUser]
    def get(self, request, *args, **kwargs):
        return Response({
            "message": f"Welcome Super Admin {request.user.email}",
            "system_health": "Optimal",
            "pending_approvals": 5
        }, status=status.HTTP_200_OK)

@extend_schema(tags=['Hospital'], summary="Hospital Dashboard Overview")
class HospitalDashboardView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        return Response({
            "message": "Hospital specific metrics and alerts",
            "stats": {"pending_requests": 2, "stock_alerts": 0}
        }, status=status.HTTP_200_OK)

# --- USER MANAGEMENT ---

@extend_schema(tags=['Admin'], summary="List all registered users (Admin Only)")
class UserListView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = ApplicationSerializer
    queryset = User.objects.all()
    def list(self, request, *args, **kwargs):
        return Response({"users": []}, status=status.HTTP_200_OK)

# --- APPLICATIONS ---

@extend_schema_view(
    get=extend_schema(tags=['Applications'], summary="List applications for the current user"),
    post=extend_schema(tags=['Applications'], summary="Create a new application")
)
class ApplicationListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ApplicationSerializer
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Application.objects.all().order_at('-created_at')
        return Application.objects.filter(user=user).order_by('-created_at')
    def list(self, request, *args, **kwargs):
        return Response({"applications": []}, status=status.HTTP_200_OK)

@extend_schema(tags=['Applications'], summary="Retrieve, Update or Delete a specific application")
class ApplicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    def retrieve(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        return Response({"id": pk, "details": "Full application data"}, status=status.HTTP_200_OK)

# --- INVENTORY & STOCK ---

@extend_schema(tags=['Inventory'], summary="Global inventory list")
class InventoryListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = InventorySerializer
    def get(self, request, *args, **kwargs):
        return Response({"inventory": [], "last_updated": "2026-01-21"}, status=status.HTTP_200_OK)

@extend_schema(tags=['Hospital'], summary="View current hospital inventory levels")
class HospitalInventoryView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        return Response({"hospital_stock": "Supply levels for your facility"}, status=status.HTTP_200_OK)

@extend_schema(tags=['Blood Bank'], summary="Central Blood Bank stock status")
class BloodBankStockView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        return Response({"stock": "Current central blood bank levels"}, status=status.HTTP_200_OK)

# --- DONOR SPECIFIC ---

@extend_schema(tags=['Donor'], summary="Donor donation history")
class DonorHistoryView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        return Response({
            "donor": request.user.email,
            "history": []
        }, status=status.HTTP_200_OK)