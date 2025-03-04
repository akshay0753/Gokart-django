from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account



# Register your models here.
class AccountAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'last_login', 'date_joined', 'is_active')
    # list_filter = ('is_admin', 'is_active', 'is_superadmin')
    # search_fields = ('email', 'username', 'first_name', 'last_name')
    # ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'username', 'first_name', 'last_name', 'phone_number', 'password')}),
        ('Permissions', {'fields': ('is_admin', 'is_staff', 'is_active', 'is_superadmin')}),
    )
    list_display_links = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    readonly_fields = ('date_joined','last_login')
    filter_horizontal = ()
    list_filter = ()
    fieldsheets = ()


admin.site.register(Account, AccountAdmin)
# admin.site.register(Account,)

