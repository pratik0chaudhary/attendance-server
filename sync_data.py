#!/usr/bin/env python
import os
import django
from base_logging import logger
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()


def main():
    from attendance.util import pull_attendance_data, push_attendance_data
    logger.info('Start Pull')
    pull_attendance_data()
    logger.info('End Pull & Start Push')
    push_attendance_data()
    logger.info('End Push')


if __name__ == '__main__':
    main()
