from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from api import views
from api.views import MyTokenObtainPairView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- Authentication (Matches /admin/login) ---
    path('api/auth/login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api-auth/', include('rest_framework.urls')), 

    # --- Admin Dashboard Routes ---
    path('api/admin/dashboard/', views.SuperAdminDashboard.as_view(), name='dashboard_stats'),
    path('api/admin/users/', views.UserListView.as_view(), name='user_list'),
    
    # --- Applications (Blood Banks & Hospitals) ---
    path('api/admin/applications/', views.ApplicationListView.as_view(), name='app_list'),
    path('api/admin/applications/<int:pk>/', views.ApplicationDetailView.as_view(), name='app_detail'),
    
    # --- Inventory ---
    path('api/admin/inventory/', views.InventoryListView.as_view(), name='inventory_list'),

    path('api/hospital/dashboard/', views.HospitalDashboardView.as_view()),
    path('api/hospital/inventory/', views.HospitalInventoryView.as_view()),
    path('api/hospital/requests/', views.ApplicationListView.as_view()), # Using your previous view logic

    # Donor Routes (/donor/...)
    path('api/donor/dashboard/', views.DashboardStatsView.as_view()),
    path('api/donor/history/', views.DonorHistoryView.as_view()),

    # Blood Bank Routes (/bloodbank/...)
    path('api/bloodbank/dashboard/', views.DashboardStatsView.as_view()),
    path('api/bloodbank/stock/', views.BloodBankStockView.as_view()),

    # --- Swagger Documentation ---
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]