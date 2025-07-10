import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import When, Case, IntegerField
from zk import ZK, const

from attendance.handlers import DirSyncHandler
from attendance.models import AttendanceSource, AttendanceEntryCache

from attendance.models.constants import SYNC_PENDING, SYNC_SUCCESS, VERIFYS_STATES, SYNC_FAILED
from django.db.models import Q

CustomUser = get_user_model()
SERVER_DOMAIN = settings.SERVER_DOMAIN
PROTOCOL = settings.PROTOCOL
ATTENDANCE_API_KEY = settings.ATTENDANCE_API_KEY
ATTENDANCE_URL = 'api/v1/attendance/accept/'


def get_valid_devices():
    return AttendanceSource.objects.filter(
        is_active=True
    )


def pull_attendance_data(devices=None):
    if not devices:
        devices = get_valid_devices()
    for device in devices:
        DirSyncHandler(device).pull_attendance()


def generate_payload(entry):
    """
    format from RealHRSoft
    {
        "serial_number": "",
        "bio_id": "",
        "timestamp": null,
        "entry_method": null,
        "entry_type": null,
        "category": null,
        "remark_category": null,
        "remarks": "",
        "latitude": null,
        "longitude": null
    }
    """
    return {
            "ATTENDANCE_API_KEY": settings.ATTENDANCE_API_KEY,
            "serial_number": str(entry.source.serial_number),
            "bio_id": str(entry.bio_id),
            "timestamp": str(entry.timestamp),
            "entry_method": '',
            "entry_type": VERIFYS_STATES.get(entry.entry_category),
            "category": '',
            "remark_category": 'Others',
            "remarks": '',
            "latitude": None,
            "longitude": None
        }


def push_attendance_data(fresh_data=None):
    if not fresh_data:
        fresh_data = AttendanceEntryCache.objects.annotate(
            priority=Case(
                When(status=SYNC_PENDING, then=1),
                default=0,
                output_field=IntegerField()
            ),
        ).order_by(
            '-priority',
            'timestamp'
        ).select_related(
            'source'
        )
    print(fresh_data.count(), 'fresh data before filter')
    fresh_data=fresh_data.filter(~Q(status=SYNC_SUCCESS))[:1200]
    print(fresh_data.count(), 'fresh data after filtering sync success')
    for user_data in fresh_data:
        payload = generate_payload(user_data)
        response = requests.post(
            url="{}://{}/{}".format(
                PROTOCOL,
                SERVER_DOMAIN,
                ATTENDANCE_URL
            ),
            data=payload,
        )
        user_data.status = SYNC_SUCCESS if response.status_code == 201 else SYNC_FAILED
        user_data.sync_tries = user_data.sync_tries + 1
        user_data.sync_description = response.json()
        user_data.save(update_fields=['status', 'sync_tries', 'sync_description'])
        if not response.status_code == 201:
            print(payload,response.json() )
        

# 103.1.93.39:2001
# conn = None
# zk = ZK('192.168.102.246', port=4370, timeout=5)
# zk = ZK('103.1.93.39', port=2001, timeout=5)
# try:
#     print('Connecting to device ...')
#     conn = zk.connect()
#     print('Disabling device ...')
#     conn.disable_device()
#     print('Firmware Version: : {}'.format(conn.get_firmware_version()))
#     print('--- Get User ---')
#     users = conn.get_users()
#     for user in users:
#         privilege = 'User'
#         if user.privilege == const.USER_ADMIN:
#             privilege = 'Admin'
#
#         print('- UID #{}'.format(user.uid))
#         print('  Name       : {}'.format(user.name))
#         print('  Privilege  : {}'.format(privilege))
#         print('  Password   : {}'.format(user.password))
#         print('  Group ID   : {}'.format(user.group_id))
#         print('  User  ID   : {}'.format(user.user_id))
#
#     print("Voice Test ...")
#     conn.test_voice()
#     print('Enabling device ...')
#     conn.enable_device()
# except Exception as e:
#     print("Process terminate : {}".format(e))
# finally:
#     if conn:
#         conn.disconnect()

# attendance.util.pull_attendance_data
# attendance.util.push_attendance_data


def create_root_user():
    root_username = getattr(settings, 'ROOT_USERNAME', 'root')
    root_email = getattr(settings, 'ROOT_EMAIL', 'root@admin.com')
    root_password = getattr(settings, 'ROOT_PASSWORD', 'root')

    if CustomUser.objects.filter(email=root_email).exists():
        return
    # We're considering this One TimeThing
    CustomUser.objects.create_superuser(
        root_username, root_email, root_password
    )
    # Schedule.objects.update_or_create(
    #     func='attendance.util.pull_attendance_data',
    #     defaults={
    #         'name': 'Pull Attendance Data',
    #         'schedule_type': Schedule.MINUTES,
    #         'minutes': 10,
    #     }
    # )
    # Schedule.objects.update_or_create(
    #     func='attendance.util.push_attendance_data',
    #     defaults={
    #         'name': 'Push Attendance Data',
    #         'schedule_type': Schedule.MINUTES,
    #         'minutes': 10,
    #     }
    # )

# attendance.util.pull_attendance_data
# attendance.util.push_attendance_data
