# Register your models here.
from django.contrib.auth.models import User, Group
from django.db.models import Count, F, Case, When, Q
from django.utils import timezone

from attendance.models import AttendanceSource, AttendanceEntryCache

from datetime import date

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from attendance.models.constants import SYNC_FAILED, SYNC_PENDING, SYNC_SUCCESS, ATTENDANCE_CACHE_REASONS
from attendance.util import push_attendance_data, pull_attendance_data


def yesterday():
    timezone.now() - timezone.timedelta(days=1)


def today():
    return timezone.now().date()


class AttendanceEntryDateFilter(admin.SimpleListFilter):
    title = _('synced time')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'synced'

    def lookups(self, request, model_admin):
        return (
            ('Today', _('Data Synced Today')),
            ('Yesterday', _('Data Synced Yesterday')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Today':
            return queryset.filter(created__date=today())
        if self.value() == 'Yesterday':
            return queryset.filter(created__date=yesterday())


class DeviceFilter(admin.SimpleListFilter):
    title = _('Attendance Device')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'device'

    def lookups(self, request, model_admin):
        attendance_sources = AttendanceSource.objects.filter(
            is_active=True
        ).annotate(
            attendance_count=Count(
                'entry_cache'
            )
        )
        return [
            (
                source.id,
                _(
                    str(source.name) + ' (' + str(source.attendance_count) + ')'
                )
            ) for source in attendance_sources
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(source=self.value())
        return queryset


class StatusFilter(admin.SimpleListFilter):
    title = _('Sync Status')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        attendance_sources = AttendanceEntryCache.objects.order_by().values(
            'status'
        ).annotate(
            attendance_count=Count('id')
        ).values_list(
            'status', 'attendance_count'
        )
        return [
            (
                status,
                _(
                    dict(ATTENDANCE_CACHE_REASONS).get(status) + ' (' + str(count) + ')'
                )
            ) for status, count in attendance_sources
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


def disable_selected_attendance_devices(model_admin, request, queryset):
    pull_attendance_data(queryset)


def enable_selected_attendance_devices(model_admin, request, queryset):
    queryset.update(is_active=True)


def sync_selected_devices(model_admin, request, queryset):
    queryset.update(is_active=True)


def sync_selected_attendance_data(model_admin, request, queryset):
    push_attendance_data(queryset)


disable_selected_attendance_devices.short_description = "Mark selected devices inactive"
enable_selected_attendance_devices.short_description = "Mark selected devices active"
sync_selected_devices.short_description = "Sync Attendance Data from selected devices"
sync_selected_attendance_data.short_description = "Sync Attendance Data to the server."


class AttendanceSourceAdmin(admin.ModelAdmin):
    _fields = (
        'serial_number',
        'name',
        'last_activity',
        'ip',
        'port',
        'disable_device',
        'clear_device',
        'timezone',
        'extra_data'
    )
    list_filter = ('last_activity',)
    list_display = (
        'name', 'serial_number', 'last_activity', 'ip', 'port', 'is_active',
        'attendance_count'
    )
    actions = (
        enable_selected_attendance_devices,
        disable_selected_attendance_devices,
        sync_selected_devices
    )
    readonly_fields = ('last_activity',)
    ordering = ('last_activity',)
    search_fields = ('name',)
    fieldsets = (
        (
            'Summary Info', {
                'classes': ('wide',),
                'fields': ('last_activity',)
            },
        ), (
            'Device Information', {
                'classes': ('wide',),
                'fields': (
                    'name', 'serial_number', 'ip', 'port', 'timezone'
                )
            }
        ), (
            'Actions', {
                'classes': ('wide',),
                'fields': (
                    'disable_device', 'clear_device',
                )
            }
        )
    )

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _att_count=Count(
                'entry_cache'
            )
        )

    def attendance_count(self, obj):
        return obj._att_count


class AttendanceEntryCacheAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            'Summary Info', {
                'classes': ('wide',),
                'fields': (
                    'created',
                    'source',
                    'bio_id',
                    'timestamp',
                    'entry_category',
                    'status',
                )
            },
        ), (
            'Additional Information', {
                'classes': ('wide', 'collapse'),
                'fields': (
                    'sync_tries', 'sync_description',
                )
            }
        )
    )
    list_filter = (
        AttendanceEntryDateFilter,
        DeviceFilter,
        StatusFilter
    )
    readonly_fields = ('created', 'source')
    list_display = (
        'source', 'created', 'bio_id', 'timestamp', 'status',
    )
    change_form_template = 'main/change_form.html'
    list_per_page = 20
    ordering = ('-created', '-timestamp',)
    date_hierarchy = 'created'
    actions = (
        sync_selected_attendance_data,
    )

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


def try_again(model_admin, request, queryset):
    queryset.update(
        next_run=timezone.now()+timezone.timedelta(seconds=5),
    )


# class ScheduleAdmin(admin.ModelAdmin):
#     list_display = (
#         'name',
#         'func',
#         'hook',
#         'args',
#         'kwargs',
#         'schedule_type',
#         'minutes',
#         'repeats',
#         'next_run',
#         'task',
#     )
#     actions = [
#         try_again
#     ]


admin.site.register(
    AttendanceSource, AttendanceSourceAdmin
)
admin.site.register(
    AttendanceEntryCache, AttendanceEntryCacheAdmin
)

admin.site.unregister(User)
admin.site.unregister(Group)
# admin.site.unregister(Schedule)
# admin.site.unregister(Success)
# admin.site.unregister(Failure)

# admin.site.register(
#     Schedule, ScheduleAdmin
# )

admin.site.site_header = "Attendance Server Administration"
admin.site.site_title = "Attendance Server Administration"
admin.site.index_title = "Welcome to Attendance Server Administration"
