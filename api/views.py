from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from .matching import *
from rest_framework.decorators import api_view, permission_classes
from .matching import knn_randmax_hybrid_matching

# Internal imports
from .models import User, Application, Inventory, Donation
from .serializers import *


class DashboardRedirectView(APIView):
    """
    Professional Redirector: Directs users to their specific dashboard 
    based on their assigned Role after a session-based login.
    """
    permission_classes = [IsAuthenticated]
    @extend_schema(exclude=True)
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

@extend_schema(tags=['Authentication'], summary="Register a new user")
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

@extend_schema(tags=['Authentication'], summary="Get or update logged in user's profile")
class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    # For a profile view, we override get_object to return the current user
    def get_object(self):
        return self.request.user

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
@extend_schema(tags=['Applications'], summary="Retrieve, Update or Delete a specific application")


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
        stats = {
            "total_users": User.objects.count(),
            "total_donors": User.objects.filter(role='donor').count(),
            "total_hospitals": User.objects.filter(role='hospital').count(),
            "total_blood_banks": User.objects.filter(role='bloodbank').count(),
            "pending_applications": Application.objects.filter(status='pending').count(),
        }
        return Response(stats, status=status.HTTP_200_OK)

@extend_schema(tags=['Hospital'], summary="Hospital Dashboard Overview")
class HospitalDashboardView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        if request.user.role != 'hospital':
            return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)
        
        inventory_count = Inventory.objects.filter(owner=request.user).count()
        return Response({
            "message": f"Welcome Hospital Admin {request.user.get_full_name()}",
            "stats": {
                "inventory_items": inventory_count, 
                "pending_requests": 0
            }
        }, status=status.HTTP_200_OK)

# --- USER MANAGEMENT ---

@extend_schema(tags=['Admin'], summary="List all registered users (Admin Only)")
class UserListView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = UserSerializer
    queryset = User.objects.all().order_by('-date_joined')

@extend_schema(tags=['Admin'], summary="Retrieve or update a specific user's status/details (Admin Only)")
class AdminUserDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = UserSerializer
    queryset = User.objects.all()

# --- APPLICATIONS ---

@extend_schema_view(
    get=extend_schema(tags=['Applications'], summary="List applications for the current user or all if admin"),
    post=extend_schema(tags=['Applications'], summary="Create a new application")
)
class ApplicationListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ApplicationSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == 'admin':
            queryset = Application.objects.all().order_by('-created_at')
            category = self.request.query_params.get('category')
            if category:
                queryset = queryset.filter(category=category)
            return queryset
        return Application.objects.filter(user=user).order_by('-created_at')

@extend_schema(tags=['Applications'], summary="Retrieve, Update or Delete a specific application")
class ApplicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ApplicationSerializer
    queryset = Application.objects.all()

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.role == 'admin':
            return Application.objects.all()
        return Application.objects.filter(user=user)

# --- INVENTORY & STOCK ---

@extend_schema(tags=['Inventory'], summary="Global inventory list (Admin Only)")
class InventoryListView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = InventorySerializer
    queryset = Inventory.objects.all().order_by('owner__first_name', 'blood_group')

@extend_schema(tags=['Hospital'], summary="View and manage current hospital inventory levels")
class HospitalInventoryView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = InventorySerializer

    def get_queryset(self):
        if self.request.user.role == 'hospital':
            return Inventory.objects.filter(owner=self.request.user)
        return Inventory.objects.none()

    def perform_create(self, serializer):
        if self.request.user.role == 'hospital':
            serializer.save(owner=self.request.user)
        else:
            raise PermissionDenied("Only hospitals can create inventory.")

@extend_schema(tags=['Blood Bank'], summary="View and manage Central Blood Bank stock")
class BloodBankStockView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = InventorySerializer

    def get_queryset(self):
        if self.request.user.role == 'bloodbank':
            return Inventory.objects.filter(owner=self.request.user)
        return Inventory.objects.none()
    
    def perform_create(self, serializer):
        if self.request.user.role == 'bloodbank':
            serializer.save(owner=self.request.user)
        else:
            raise PermissionDenied("Only blood banks can create inventory.")

class DonorHistoryView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DonationSerializer

    def get_queryset(self):
        if self.request.user.role == 'donor':
            return Donation.objects.filter(donor=self.request.user).order_by('-donation_date')
        return Donation.objects.none()

    # Add this to automatically assign the logged-in donor to the donation record
    def perform_create(self, serializer):
        serializer.save(donor=self.request.user)


@extend_schema(tags=['Common'], summary="List verified facilities for donors to select")
class FacilityListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        # Only return users who are hospitals or blood banks, and are active
        return User.objects.filter(role__in=['hospital', 'bloodbank'], is_active=True)
    
@extend_schema(tags=['Inventory'], summary="Retrieve or update a specific inventory record (Admin Only)")
class InventoryDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = InventorySerializer
    queryset = Inventory.objects.all()

    # Automatically create a ledger log when an admin updates the units
    def perform_update(self, serializer):
        old_units = self.get_object().units
        new_units = serializer.validated_data.get('units', old_units)
        diff = new_units - old_units
        
        inventory = serializer.save()
        
        if diff != 0:
            action_type = 'Addition' if diff > 0 else 'Deduction'
            InventoryLog.objects.create(
                inventory=inventory,
                action_type=action_type,
                amount=abs(diff),
                source='Manual Admin Override',
                user=self.request.user
            )

@extend_schema(tags=['Inventory'], summary="Get ledger logs for a specific inventory")
class InventoryLogListView(generics.ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = InventoryLogSerializer

    def get_queryset(self):
        inventory_id = self.kwargs['inventory_id']
        return InventoryLog.objects.filter(inventory_id=inventory_id).order_by('-date')
    

@extend_schema(tags=['Applications'], summary="Run AI Matching Algorithm for a Request")
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def match_donors_for_request(request, pk):
    try:
        application = Application.objects.get(pk=pk)
    except Application.DoesNotExist:
        return Response({"error": "Application not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Trigger the new Peak Algorithm
    matches = knn_randmax_hybrid_matching(application, gamma=0.3, k_donors=4)
    
    return Response({
        "application_id": application.id,
        "applicant": application.applicant_name,
        "matches": matches
    }, status=status.HTTP_200_OK)