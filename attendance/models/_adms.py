from datetime import timedelta
from django.db import models

from django.utils.translation import ugettext_lazy as _

from attendance.models.constants import ATTSTATES, VERIFYS, VERIFYS_MAP, VERIFYS_STATES



class DeviceEmployee(models.Model):
    id = models.AutoField(db_column="userid", primary_key=True)
    # original name: PIN
    # user's ID in device aka biouser id
    id_on_device = models.CharField(db_column="badgenumber", max_length=20)

    class Meta:
        managed = False
        db_table = 'userinfo'


class DeviceTimesheet(models.Model):
    # original name: UserID
    employee = models.ForeignKey('DeviceEmployee', db_column='userid',on_delete=models.CASCADE)

    # original name: TTime
    check_time = models.DateTimeField(db_column='checktime')

    # original name: State
    # e.g. check in, check out, break out, break in etc.
    check_type = models.CharField(
        max_length=11, db_column='checktype', choices=ATTSTATES)

    # original name: Verify
    # attendance method i.e. card, finger etc
    check_method = models.IntegerField(db_column='verifycode', choices=VERIFYS)

    # device serial number original name: SN
    device_sn = models.CharField(db_column='SN', max_length=20)

    @property
    def bio_id(self):
        return int(self.employee.id_on_device)

    @property
    def checktype(self):
        return VERIFYS_STATES.get(self.check_type,'N/A')

    @property
    def checktime(self):
        # Convert the time to UTC and apply formula according to device TimeZone
        # currently assuming for Asia/Kathmandu
        # TODO: Shrawan
        utc_offset = timedelta(seconds=20700)
        return self.check_time - utc_offset

    @property
    def checkmethod(self):
        return VERIFYS_MAP[self.check_method]

    def __str__(self):
        return "{0} -> {1}: <{2}>, <{3}>".format(
            self.employee.id_on_device,
            self.check_time,
            self.get_check_type_display(),
            self.get_check_method_display()
        )

    class Meta:
        managed = False
        db_table = 'checkinout'
        ordering = ('id',)
