# from rest_framework.permissions import BasePermission

# class IsSuperAdmin(BasePermission):
#     def has_permission(self, request, view):
#         user = request.user
#         if user.is_authenticated and user.role == "SUPER_ADMIN":
#             return True
#         return False