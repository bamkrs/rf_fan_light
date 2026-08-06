"""Async serial client for the RF Fan Light integration."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable
from typing import Any

import serialx

from .commands import validate_commands
from .const import DEFAULT_WRITE_TIMEOUT

_LOGGER = logging.getLogger(__name__)


class RFFanLightClient:
    """Minimal serial client for a command-only RF bridge.

    This client assumes your serial hardware accepts one command frame at a time.
    By default, it appends a newline to each command. Adjust _frame_command if your
    bridge expects raw bytes, checksums, prefixes, or another delimiter.
    """

    def __init__(
        self,
        port: str,
        baudrate: int,
        *,
        write_timeout: float = DEFAULT_WRITE_TIMEOUT,
    ) -> None:
        """Initialize the client."""
        self._port = port
        self._baudrate = baudrate
        self._write_timeout = write_timeout
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._lock = asyncio.Lock()

        validate_commands()

    @property
    def port(self) -> str:
        """Return the configured serial port."""
        return self._port

    @property
    def connected(self) -> bool:
        """Return whether the serial connection is open."""
        return self._writer is not None and not self._writer.is_closing()

    async def async_connect(self) -> None:
        """Open the serial connection."""
        if self.connected:
            return

        _LOGGER.debug("Opening serial port %s at %s baud", self._port, self._baudrate)
        self._reader, self._writer = await serialx.open_serial_connection(
            self._port,
            baudrate=self._baudrate,
        )

    async def async_close(self) -> None:
        """Close the serial connection."""
        writer = self._writer
        self._reader = None
        self._writer = None

        if writer is not None:
            writer.close()
            await writer.wait_closed()

    async def async_send_command(self, command: bytes) -> None:
        """Send one logical RF command."""
        await self._async_send_command(command)

    async def _async_send_command(self, command: bytes) -> None:
        """Send one command frame and optionally wait for an ACK line."""
        async with self._lock:
            if not self.connected:
                await self.async_connect()

            writer = self._require_writer()
            reader = self._reader
            frame = self._frame_command(command)

            _LOGGER.debug("Writing RF serial frame: %r", frame)
            writer.write(frame)
            await asyncio.wait_for(writer.drain(), timeout=self._write_timeout)

    def _require_writer(self) -> asyncio.StreamWriter:
        """Return an open serial writer or raise."""
        if self._writer is None or self._writer.is_closing():
            raise RuntimeError("Serial writer is not connected")
        return self._writer

    def _frame_command(self, command: bytes) -> bytes:
        """Convert a logical command into a serial frame.

        Current behavior: append a newline. If your RF bridge wants raw binary
        frames, replace this method with `return command` or your encoder.
        """
        return command + b"\n"

    async def async_health_check(self) -> None:
        """Open and close the port to validate basic connectivity."""
        await self.async_connect()


async def close_safely(close_call: Awaitable[Any]) -> None:
    """Await a close operation while suppressing close-time I/O errors."""
    try:
        await close_call
    except OSError:
        _LOGGER.debug("Ignoring serial close error", exc_info=True)
