from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
# --- Common / Stats ---
class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({"status": "General stats active"})

class SuperAdminDashboard(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        return Response({"message": f"Welcome Super Admin {request.user.username}"})

# --- Admin & User Management ---
class UserListView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        return Response({"users": []})

# --- Applications (Blood Bank & Hospital) ---
class ApplicationListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({"applications": []})

class ApplicationDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        return Response({"id": pk, "details": "Application information"})

# --- Inventory & Stock ---
class InventoryListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({"inventory": []})

class BloodBankStockView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({"stock": "Current blood bank levels"})

# --- Role Specific Views ---
class HospitalDashboardView(APIView):  # <--- Added this to fix your error
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({"message": "Hospital Dashboard Data"})

class HospitalInventoryView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({"inventory": "Hospital supply levels"})

class DonorHistoryView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({"history": "Donation records"})