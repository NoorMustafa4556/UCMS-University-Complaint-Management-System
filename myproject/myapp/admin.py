from django.contrib import admin
from .models import Complaint

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['name', 'roll_number', 'department', 'subject', 'status']
    list_filter = ['status', 'department']