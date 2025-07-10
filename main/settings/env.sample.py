from datetime import date

from .settings import *

SECRET_KEY = 'eh$xnuw_&o=vjlada_=(d!t86%y4vahb2q1b@mntz^c2)vhgw%'

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql',
    #     'NAME': 'attendance_server',
    #     'USER': 'raw-v',
    #     'PASSWORD': 'postgres',
    #     'HOST': '127.0.0.1',
    #     'PORT': '5432',
    # }
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'attendance',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': '192.168.99.61',
        'PORT': '5433',
    }
}

TIME_ZONE = 'Asia/Kathmandu'

SERVER_DOMAIN = 'localhost:1234'
PROTOCOL = 'http'
ATTENDANCE_API_KEY = 'test1Password'
IGNORE_TIMESTAMPS_BEFORE = date(2020, 8, 1)
