"""Fan platform for RF Fan Light."""

from __future__ import annotations

import math

from homeassistant.components.fan import ATTR_PERCENTAGE, FanEntity, FanEntityFeature
from homeassistant.const import STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from . import RFFanLightConfigEntry
from .const import DOMAIN, FAN_SPEED_COUNT
from .entity import RFFanLightEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: RFFanLightConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the fan speed entity."""
    async_add_entities(
        [RFFanSpeedEntity(entry.unique_id or entry.entry_id, entry.runtime_data.client)]
    )


class RFFanSpeedEntity(RFFanLightEntity, RestoreEntity, FanEntity):
    """Representation of the RF-controlled fan speed.

    This entity intentionally does not implement turn_on, turn_off, or toggle.
    The fan's only power command is a raw RF toggle, which is exposed separately
    as a ButtonEntity.
    """

    _attr_name = "Fan"
    _attr_supported_features = FanEntityFeature.SET_SPEED
    _attr_speed_count = FAN_SPEED_COUNT
    _attr_assumed_state = True
    _enable_turn_on_off_backwards_compatibility = False

    def __init__(self, entry_unique_id: str, client) -> None:  # noqa: ANN001
        """Initialize the fan speed entity."""
        super().__init__(entry_unique_id, client)
        self._attr_unique_id = f"{DOMAIN}_{entry_unique_id}_fan"
        self._speed: int | None = None

    async def async_added_to_hass(self) -> None:
        """Restore the last commanded fan speed after Home Assistant restarts."""
        await super().async_added_to_hass()

        last_state = await self.async_get_last_state()
        if last_state is None or last_state.state != STATE_ON:
            return

        percentage = last_state.attributes.get(ATTR_PERCENTAGE)
        if isinstance(percentage, (int, float)) and percentage > 0:
            self._speed = _percentage_to_speed(int(percentage))

    @property
    def is_on(self) -> bool | None:
        """Return the assumed fan state based on the last speed command."""
        if self._speed is None:
            return None
        return self._speed > 0

    @property
    def percentage(self) -> int | None:
        """Return the last commanded fan speed percentage."""
        if self._speed is None:
            return None
        return round(self._speed * 100 / FAN_SPEED_COUNT)

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Return attributes describing the RF control model."""
        return {
            "power_control": "separate_toggle_button",
            "state_source": "last_speed_command",
        }

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the fan speed percentage.

        The RF hardware has no dedicated off command. Home Assistant may call
        set_percentage with 0 to mean off, but this integration deliberately
        rejects that request instead of sending an unsafe power toggle.
        """
        if percentage <= 0:
            raise HomeAssistantError(
                "This RF fan has no dedicated off command. Use the fan power "
                "toggle button entity instead."
            )

        speed = _percentage_to_speed(percentage)
        await self._client.async_send_fan_speed(speed)
        self._speed = speed
        self.async_write_ha_state()


def _percentage_to_speed(percentage: int) -> int:
    """Map Home Assistant percentage to a six-speed RF command."""
    percentage = max(1, min(100, percentage))
    return max(1, min(FAN_SPEED_COUNT, math.ceil(percentage * FAN_SPEED_COUNT / 100)))
