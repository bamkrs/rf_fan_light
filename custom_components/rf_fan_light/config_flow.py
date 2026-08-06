"""Config flow for RF Fan Light."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .client import RFFanLightClient, close_safely
from .const import (
    CONF_BAUDRATE,
    CONF_PORT,
    CONF_WRITE_TIMEOUT,
    DEFAULT_BAUDRATE,
    DEFAULT_CONNECT_TIMEOUT,
    DEFAULT_WRITE_TIMEOUT,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PORT): str,
        vol.Optional(CONF_BAUDRATE, default=DEFAULT_BAUDRATE): int,
        vol.Optional(CONF_WRITE_TIMEOUT, default=DEFAULT_WRITE_TIMEOUT): vol.Coerce(float),
    }
)


async def _async_validate_input(hass: HomeAssistant, data: dict[str, Any]) -> None:
    """Validate that the serial port can be opened."""
    client = RFFanLightClient(
        data[CONF_PORT],
        int(data[CONF_BAUDRATE]),
        write_timeout=float(data[CONF_WRITE_TIMEOUT]),
    )

    try:
        async with asyncio.timeout(DEFAULT_CONNECT_TIMEOUT):
            await client.async_health_check()
    finally:
        await close_safely(client.async_close())


class RFFanLightConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle an RF Fan Light config flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            user_input = dict(user_input)
            user_input[CONF_BAUDRATE] = int(user_input[CONF_BAUDRATE])
            user_input[CONF_WRITE_TIMEOUT] = float(user_input[CONF_WRITE_TIMEOUT])

            await self.async_set_unique_id(user_input[CONF_PORT])
            self._abort_if_unique_id_configured()

            try:
                await _async_validate_input(self.hass, user_input)
            except FileNotFoundError:
                errors["base"] = "port_not_found"
            except (OSError, TimeoutError):
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error validating RF Fan Light setup")
                errors["base"] = "unknown"
            else:
                title = f"RF Fan Light ({user_input[CONF_PORT]})"
                return self.async_create_entry(title=title, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=USER_SCHEMA,
            errors=errors,
        )
