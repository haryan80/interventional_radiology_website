from django.contrib import admin
from .models import Speaker, Session, ScheduleItem, Registration

class ScheduleItemInline(admin.TabularInline):
    model = ScheduleItem
    extra = 1
    autocomplete_fields = ['speakers']

@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'institution', 'order', 'is_visible')
    search_fields = ('name', 'institution')
    list_filter = ('institution', 'is_visible')
    ordering = ('order', 'name')
    list_editable = ('is_visible', 'order')

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'start_time', 'end_time')
    list_filter = ('date',)
    search_fields = ('name',)
    inlines = [ScheduleItemInline]

@admin.register(ScheduleItem)
class ScheduleItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'session', 'start_time', 'end_time', 'is_break')
    list_filter = ('session', 'is_break')
    search_fields = ('title',)
    autocomplete_fields = ['speakers']
    
@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'institution', 'attendee_type', 'created_at')
    list_filter = ('attendee_type', 'created_at')
    search_fields = ('full_name', 'email', 'institution')
    readonly_fields = ('created_at',)
