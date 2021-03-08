import logging

from health_api.constants import DEBUG

logging.basicConfig()
logger = logging.getLogger('HealthAPI:API')
logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)
