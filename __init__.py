"""RF Fan Light integration."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .client import RFFanLightClient, close_safely
from .const import (
    CONF_BAUDRATE,
    CONF_PORT,
    CONF_WRITE_TIMEOUT,
    DEFAULT_CONNECT_TIMEOUT,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.BUTTON]


@dataclass(slots=True)
class RFFanLightRuntimeData:
    """Runtime data stored on the config entry."""

    client: RFFanLightClient


RFFanLightConfigEntry = ConfigEntry[RFFanLightRuntimeData]


async def async_setup_entry(hass: HomeAssistant, entry: RFFanLightConfigEntry) -> bool:
    """Set up RF Fan Light from a config entry."""

    client = RFFanLightClient(
        entry.data[CONF_PORT],
        int(entry.data[CONF_BAUDRATE]),
        write_timeout=float(entry.data.get(CONF_WRITE_TIMEOUT, 2.0)),
    )

    try:
        async with asyncio.timeout(DEFAULT_CONNECT_TIMEOUT):
            await client.async_connect()
    except (OSError, TimeoutError) as err:
        raise ConfigEntryNotReady(
            f"Could not open serial port {entry.data[CONF_PORT]}"
        ) from err

    entry.runtime_data = RFFanLightRuntimeData(client=client)

    try:
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    except Exception:
        await close_safely(client.async_close())
        raise

    return True


async def async_unload_entry(hass: HomeAssistant, entry: RFFanLightConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        await close_safely(entry.runtime_data.client.async_close())
    return unload_ok
