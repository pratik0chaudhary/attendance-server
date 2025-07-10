from django.db import models

from .constants import ATTENDANCE_CACHE_REASONS, SYNC_PENDING
from .source import AttendanceSource


class AttendanceEntryCache(models.Model):
    created = models.DateTimeField(
        auto_now_add=True
    )
    source = models.ForeignKey(
        AttendanceSource,
        on_delete=models.SET_NULL,
        related_name='entry_cache', null=True
    )
    bio_id = models.CharField(
        max_length=11
    )
    timestamp = models.DateTimeField()
    entry_category = models.CharField(
        max_length=11,
        help_text='Entry Category from Device'
    )
    status = models.PositiveSmallIntegerField(
        choices=ATTENDANCE_CACHE_REASONS,
        default=SYNC_PENDING,
    )
    sync_tries = models.IntegerField(
        default=0
    )
    sync_description = models.TextField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.source} -> {self.bio_id}"

    class Meta:
        ordering = ('timestamp',)
        unique_together = (('source', 'bio_id', 'timestamp'),)
        verbose_name_plural = 'Synced Attendance Data'
