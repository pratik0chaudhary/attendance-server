import logging

from django.conf import settings
from zk import ZK
from zk.exception import ZKError, ZKErrorResponse, ZKNetworkError

from django.utils import timezone
from django.core.exceptions import ImproperlyConfigured

from attendance.models import AttendanceEntryCache

logger = logging.getLogger(__name__)


class DirSyncHandler:
    def __init__(self, device):
        self._device = device
        self.zk = ZK(device.ip, device.port)

    def _get_pointer(self):
        try:
            last_entry = AttendanceEntryCache.objects.filter(
                source=self.get_device(),
                timestamp__lte=timezone.now()
            ).order_by('-timestamp')[0]
        except IndexError:
            return None
        else:
            return last_entry

    def sync(self, pull=True, **kwargs):
        pass

    def get_device(self):
        return self._device

    def pull_attendance(self, clear=None):
        clear = clear or self.get_device().clear_device

        tz = timezone.get_current_timezone()
        total_pulled = 0

        try:
            self.zk.connect()
            logger.info('Successfully connected synced for {}.'.format(self.get_device()))
        except (ImproperlyConfigured, ZKError, ZKErrorResponse, ZKNetworkError):
            logger.error('Cannot connect to {}'.format(self.get_device()))
        else:
            if self.get_device().disable_device:
                self.zk.disable_device()
                logger.info('Disabling device {} for sync'.format(self.get_device()))
            _attendances = self.zk.get_attendance()
            _attendances.reverse()
            logger.info('Got attendance device  {}.'.format(self.get_device()))
            logger.debug(
                'Pulling from device {}-{}'.format(
                    self.get_device(),
                    self.get_device().ip
                )
            )

            sync_caches = []

            now = timezone.now()
            for attendance in _attendances:
                timestamp = tz.localize(attendance.timestamp)

                ignore_timestamp_older_than = getattr(
                    settings,
                    'IGNORE_TIMESTAMPS_BEFORE',
                    None
                )
                if ignore_timestamp_older_than and timestamp.date() < ignore_timestamp_older_than:
                    break
                if self._get_pointer() and (
                        timestamp <= self._get_pointer().timestamp or timestamp > now
                ):
                    break

                total_pulled += 1
                _sync_cache = AttendanceEntryCache(
                    source=self.get_device(), bio_id=attendance.user_id,
                    timestamp=timestamp, entry_category=attendance.status)
                sync_caches.append(_sync_cache)

            if sync_caches:
                logger.info('found sync cache for {}.'.format(self.get_device()))
                AttendanceEntryCache.objects.bulk_create(sync_caches, ignore_conflicts=True)

                if clear:
                    logger.info('clearing attendance data from {}.'.format(self.get_device()))
                    self.zk.clear_attendance()
            else:
                logger.warning('No new attendance data found on {}.'.format(self.get_device()))

            logger.info('Successfully synced for {}.'.format(self.get_device()))
            # if self.get_device().disable_device:
            #     self.zk.enable_device()

        finally:
            if self.zk.is_connect:
                self.zk.disconnect()

            self.get_device().last_activity = timezone.now()
            self.get_device().save()

        logger.debug('Finished pulling for {}-{}'.format(self.get_device(), self.get_device().ip))
        return total_pulled
