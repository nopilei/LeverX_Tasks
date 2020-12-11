from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    pass


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass


@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    pass


@admin.register(Hometask)
class HometaskAdmin(admin.ModelAdmin):
    pass


@admin.register(FinishedTask)
class FinishedTaskAdmin(admin.ModelAdmin):
    pass


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    pass


admin.site.register(User, UserAdmin)
