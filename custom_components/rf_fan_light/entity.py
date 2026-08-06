"""Base entity mixin for RF Fan Light."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo

from .client import RFFanLightClient
from .const import DOMAIN, MANUFACTURER, MODEL


class RFFanLightEntity:
    """Common attributes for RF Fan Light entities."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, entry_unique_id: str, client: RFFanLightClient) -> None:
        """Initialize the entity mixin."""
        self._entry_unique_id = entry_unique_id
        self._client = client
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_unique_id)},
            manufacturer=MANUFACTURER,
            model=MODEL,
            name="RF Fan Light",
        )
