from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from api import views
from api.views import MyTokenObtainPairView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- Authentication ---
    path('api/auth/login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/register/', views.RegisterView.as_view(), name='auth_register'),
    path('api/auth/user/', views.UserProfileView.as_view(), name='auth_user'),
    path('api/admin/users/<int:pk>/', views.AdminUserDetailView.as_view(), name='admin_user_detail'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api-auth/', include('rest_framework.urls')), 
    path('api/facilities/', views.FacilityListView.as_view(), name='facility_list'),    

    # --- Admin Dashboard Routes ---
    path('api/admin/dashboard/', views.SuperAdminDashboardView.as_view(), name='dashboard_stats'),
    path('api/admin/users/', views.UserListView.as_view(), name='user_list'),
    path('api/admin/inventory/', views.InventoryListView.as_view(), name='inventory_list'),
    path('api/admin/inventory/<int:pk>/', views.InventoryDetailView.as_view(), name='inventory_detail'),
    path('api/admin/inventory/<int:inventory_id>/logs/', views.InventoryLogListView.as_view(), name='inventory_logs'), # <-- ADD THIS
    # --- Applications (Blood Banks & Hospitals) ---
    path('api/applications/', views.ApplicationListView.as_view(), name='app_list'),
    path('api/applications/<int:pk>/', views.ApplicationDetailView.as_view(), name='app_detail'),
    path('api/applications/<int:pk>/match/', views.match_donors_for_request, name='app_match'),
    
    # --- Inventory ---
    path('api/admin/inventory/', views.InventoryListView.as_view(), name='inventory_list'),

    # --- Hospital Routes ---
    path('api/hospital/dashboard/', views.HospitalDashboardView.as_view()),
    path('api/hospital/inventory/', views.HospitalInventoryView.as_view()),
    path('api/hospital/requests/', views.ApplicationListView.as_view()),

    # --- Donor Routes ---
    path('api/donor/dashboard/', views.DashboardStatsView.as_view()),
    path('api/donor/history/', views.DonorHistoryView.as_view()),

    path('api/dashboard-redirect/', views.DashboardRedirectView.as_view(), name='dashboard-redirect'),
    
    # --- Blood Bank Routes ---
    path('api/bloodbank/dashboard/', views.DashboardStatsView.as_view()),
    path('api/bloodbank/stock/', views.BloodBankStockView.as_view()),

    # --- Swagger Documentation ---
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]