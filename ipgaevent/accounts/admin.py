from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from accounts.models import User, UserProfile, City, State, Country, Pincode, Address


class UserAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ['email', 'mobile_number', 'is_active', 'is_staff', 'is_superuser']
    search_fields = ['email', 'mobile_number']
    list_filter = ['is_active', 'is_staff', 'is_superuser']


class UserProfileAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ['user', 'gst_number', 'passport_number', 'aadhar_number']
    search_fields = ['user__email', 'gst_number', 'passport_number', 'aadhar_number']
    list_filter = ['user__is_active']


class CityAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    list_filter = ['name']


class StateAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    list_filter = ['name']


class CountryAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    list_filter = ['name']


class PincodeAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ['pincode']
    search_fields = ['pincode']
    list_filter = ['pincode']


class MembershipAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ['code']
    search_fields = ['code']


# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Pincode, PincodeAdmin)
admin.site.register(Address)
