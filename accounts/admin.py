from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _

from .models import UserAccounts,ProfilePhoto, Posts, Friends, FacesPermission, Chat

admin.site.register(ProfilePhoto)
admin.site.register(Posts)
admin.site.register(Friends)
admin.site.register(Chat)


@admin.register(UserAccounts)
class UserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no email field."""

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name','phone','gender','dob')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser','is_uploaded',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    ordering = ('email',)
