import os

MHz = 10 ** 6
GHz = 10 ** 9
MB = 10 ** 6
GB = 10 ** 9

HEALTH_API_PORT = 8085
HEALTH_WATCHDOG_FREQUENZY_HZ = 0.5

DISK_IMAGE_STATS_FILE = "/data/stats/disk_image/build.json"

DEBUG = os.environ.get('DEBUG', '0').lower() in ['1', 'yes', 'true']