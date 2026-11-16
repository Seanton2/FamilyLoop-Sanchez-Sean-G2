from django.contrib import admin

from .models import FamilyCircle, FamilyMember


@admin.register(FamilyCircle)
class FamilyCircleAdmin(admin.ModelAdmin):
    list_display = ['circle_name', 'created_by', 'invite_code', 'is_active', 'created_at']


@admin.register(FamilyMember)
class FamilyMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'family_circle', 'role', 'membership_status', 'joined_at']
    list_filter = ['role', 'membership_status']