from django.contrib import admin

from main.models import Patient, Payment


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    pass


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    pass
