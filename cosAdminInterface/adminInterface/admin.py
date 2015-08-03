from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from adminInterface.models import AdminUser

from .models import AdminUser

class AdminUserInline(admin.StackedInline):
	model = AdminUser
	can_delete = False

class UserAdmin(UserAdmin):
    list_filter = ('is_staff', 'groups__name')
    search_fields = ('username', 'email')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions',)

    inlines = (AdminUserInline, )

# Register your models here.
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

