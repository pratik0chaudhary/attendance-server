# Single File Implementation

Single File Implementation is obtained by running `sync_data.py` through any
scheduler system (cron/window-scheduler/etc.)

---

## Installation

Because the system is developed and maintained through `Django Framework`,
The following requirements needs to be installed (Recommended Wrapper):
 * `Django` (Data Structure and Database Query)
 * `psycopg2` (Database communication Driver)
 * `pyzk` (ZK communication Driver)
 * `requests` (Communication library to connect with RealHRSoft)

The following System Variables needs to be configured:

1. DATABASES
    * The database configuration for the system.
2. PROTOCOL
    * `https`
3. SERVER DOMAIN
    * `test1.aayulogic.io`
4. ATTENDANCE_API_KEY
    * Communication Pass-Phrase between Agent and RealHRSoft.
5. IGNORE_TIMESTAMPS_BEFORE
    * `date(year, month, day)` format
    * `date(2020, 8, 1)` can be set to ignore the legacy attendance data from
     being synced into the Agent/ RealHRSoft.
---

## Maintenance

Because the majority of work is done by the `sync_data.py` util, maintaining
Agent is not required. However, it is recommended to use admin site for most
operations like (adding new Device, view synced attendance timestamps, etc.)

1. To Create a user to log into the system:
    * ```python manage.py createsuperuser```
2. To run the server (as development)
    * ```python manage.py runserver```
