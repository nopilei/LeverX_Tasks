from rest_framework import permissions


class IsLecturerOrStudent(permissions.BasePermission):
    message = 'You must be either student or lecturer'

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            is_student, is_lecturer = request.user.is_student, request.user.is_lecturer
            return is_student or is_lecturer


class CommentsAccess(IsLecturerOrStudent):
    message = 'Only author of the comment can modify it.'

    def has_object_permission(self, request, view, obj):
        if request.user == obj.user:
            return True
        return request.method in permissions.SAFE_METHODS


class IsLecturerOrStudentSafe(permissions.BasePermission):
    message = 'You must be lecturer or perform read only operation as a student'

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            is_student, is_lecturer = request.user.is_student, request.user.is_lecturer
            is_safe = is_student and request.method in permissions.SAFE_METHODS
            return is_lecturer or is_safe


class FinishedTasksAccess(permissions.BasePermission):
    message = 'Only students can finish hometasks and only lecturers can set results'

    LECTURER_AVAILABLE_METHODS = permissions.SAFE_METHODS + ('PATCH',)
    STUDENT_AVAILABLE_METHODS = permissions.SAFE_METHODS + ('POST', 'DELETE')

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            is_lecturer, is_student = request.user.is_lecturer, request.user.is_student
            first_condition = is_lecturer and request.method in self.LECTURER_AVAILABLE_METHODS
            second_condition = is_student and request.method in self.STUDENT_AVAILABLE_METHODS
            return first_condition or second_condition
