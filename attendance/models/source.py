import pytz
from django.db import models
from django.utils.functional import cached_property
from django.utils.module_loading import import_string


class AttendanceSource(models.Model):
    serial_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(
        max_length=50, help_text='Set name to identify the device uniquely.'
    )
    last_activity = models.DateTimeField(null=True, blank=True)
    ip = models.GenericIPAddressField(
        protocol='ipv4',
        null=True,
        blank=True
    )
    port = models.IntegerField(null=True, blank=True)
    disable_device = models.BooleanField(
        "disable device to pull attendance data",
        default=True,
        help_text="This disables the device before pulling new data and enables "
                  "the device after completion. "
                  "WARNING: Turning this off may cause data-loss if 'Clear Device' "
                  "option has been enabled. "
                  "Only applicable for direct sync devices."
    )
    is_active = models.BooleanField(default=True)
    clear_device = models.BooleanField(
        "clear device after pulling data",
        default=False,
        help_text="WARNING: This can cause data-loss if 'Disable to Pull' "
                  "option has been turned off. "
                  "Only applicable for direct sync devices."
    )
    # extra_data = JSONField(
    #     null=True,
    #     blank=True
    # )
    timezone = models.CharField(
        max_length=100,
        choices=(
            (i, i) for i in pytz.common_timezones
        ),
        blank=True,
        help_text='In which timezone, is the device located. '
                  'The device sends an unaware timestamp. '
                  'So, this timezone will be used to aware the timestamp.'
    )

    class Meta:
        verbose_name_plural = 'Attendance Devices'

    @cached_property
    def handler(self):
        return import_string(
            'attendance.handlers.DirSyncHandler'
        )(device=self)

    def __str__(self):
        return self.name


class AttendanceServer(models.Model):
    server_name = models.CharField(
        max_length=255
    )
    last_synced = models.DateTimeField()
