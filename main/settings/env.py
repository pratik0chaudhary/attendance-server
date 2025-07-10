from datetime import date

from .settings import *

SECRET_KEY = 'eh$xnuw_&o=vjlada_=(d!t86%y4vahb2q1b@mntz^c2)vhgw%'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3'
    }
}

TIME_ZONE = 'Asia/Kathmandu'

SERVER_DOMAIN = 'sparkgroup.realhrsoft.com'
PROTOCOL = 'https'
ATTENDANCE_API_KEY = '2bq2sxLX*3m&'
IGNORE_TIMESTAMPS_BEFORE = date(2022, 8, 17)
