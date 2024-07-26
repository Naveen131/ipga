from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from accounts.models import User, UserProfile, City, State, Country, Pincode, Address, Membership, Payment


class UserAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ['email', 'mobile_number', 'is_active', 'is_staff', 'is_superuser']
    search_fields = ['email', 'mobile_number']
    list_filter = ['is_active', 'is_staff', 'is_superuser']

    actions = ['send_proforma_invoice', 'send_payment_reminder']

    def send_proforma_invoice(self, request, queryset):
        for user in queryset:
            user.send_proforma_invoice()
        self.message_user(request, "Proforma Invoice sent successfully")

    def send_payment_reminder(self, request, queryset):
        for user in queryset:
            payment = Payment.objects.filter(user=user, status="Success")
            if not payment.exists():
                user.send_payment_reminder()
        self.message_user(request, "Payment Reminder sent successfully")

    def send_apology(self, request, queryset):
        for user in queryset:
            user.send_apology()
        self.message_user(request, "Apology sent successfully")


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


class AddressAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ['user', 'address', 'city', 'state', 'country', 'pincode']
    search_fields = ['user__email', 'address', 'city__name', 'state__name', 'country__name', 'pincode__pincode']


class PaymentAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ['user', 'amount', 'payment_date',]
    search_fields = ['user__email', 'amount']


# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(Pincode, PincodeAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Membership, MembershipAdmin)
admin.site.register(Payment, PaymentAdmin)
