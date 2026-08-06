"""Button platform for RF Fan Light."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import RFFanLightConfigEntry
from .commands import BUTTON_COMMANDS, RFButtonCommand
from .const import DOMAIN
from .entity import RFFanLightEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: RFFanLightConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the RF command button entities."""
    entry_unique_id = entry.unique_id or entry.entry_id
    client = entry.runtime_data.client

    async_add_entities(
        [
            RFFanLightButton(entry_unique_id, client, button_command)
            for button_command in BUTTON_COMMANDS
        ]
    )


class RFFanLightButton(RFFanLightEntity, ButtonEntity):
    """Stateless RF command button."""

    def __init__(
        self,
        entry_unique_id: str,
        client,  # noqa: ANN001
        button_command: RFButtonCommand,
    ) -> None:
        """Initialize the button."""
        super().__init__(entry_unique_id, client)
        self._button_command = button_command
        self._attr_unique_id = f"{DOMAIN}_{entry_unique_id}_{button_command.key}"
        self._attr_name = button_command.name
        self._attr_icon = button_command.icon

    async def async_press(self) -> None:
        """Send the RF command associated with this button."""
        await self._client.async_send_command(self._button_command.command)
