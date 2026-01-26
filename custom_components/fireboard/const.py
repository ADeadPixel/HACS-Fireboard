"""Constants for the Fireboard integration."""
from datetime import timedelta

DOMAIN = "fireboard"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_POLLING_INTERVAL = "polling_interval"

DEFAULT_POLLING_INTERVAL = 60  # seconds
MIN_POLLING_INTERVAL = 60 
# Safety floor to prevent API bans
# The Fireboard API has a rate limit of 200 requests/hr

API_URL = "https://fireboard.io/api/v1"
AUTH_URL = "https://fireboard.io/api/rest-auth/login/"