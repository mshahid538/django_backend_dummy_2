from rest_framework import permissions


class MyUserRetrievePermissions(permissions.BasePermission):
    """
    Handles permissions for users.  The basic rules are

     - owner/admin may GET, PUT, POST, DELETE
     - nobody else can access
     """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def check_object_permission(self, user, obj):
        return user.is_staff or obj == user

    def has_object_permission(self, request, view, obj):
        return self.check_object_permission(request.user, obj)


class MyUserListPermissions(permissions.BasePermission):
    """
    Handles permissions for users.  The basic rules are

     - admin may get all user list
     - nobody else can access
     """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff
