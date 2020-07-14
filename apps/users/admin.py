from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from apps.users.models import UserProfile


class UserProfileAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('扩展信息', {'fields': ('nickname', 'mobile', 'image', 'homepage')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('扩展信息', {'fields': ('nickname', 'mobile', 'image', 'homepage')}),
    )


admin.site.register(UserProfile, UserProfileAdmin)
