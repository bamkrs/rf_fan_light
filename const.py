"""Constants for the RF Fan Light integration."""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "rf_fan_light"

# Keep integration-specific config keys local. Some Home Assistant
# versions do not expose CONF_BAUDRATE from homeassistant.const.
CONF_PORT: Final = "port"
CONF_BAUDRATE: Final = "baudrate"
DEFAULT_BAUDRATE: Final = 115200
DEFAULT_WRITE_TIMEOUT: Final = 2.0
DEFAULT_CONNECT_TIMEOUT: Final = 5.0

CONF_WRITE_TIMEOUT: Final = "write_timeout"

MANUFACTURER: Final = "Cecotec"
MODEL: Final = "A30"

FAN_SPEED_COUNT: Final = 6
