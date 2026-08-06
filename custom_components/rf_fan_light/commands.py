"""RF command definitions.

Replace these byte strings with the exact serial commands your RF hardware expects.
The current defaults are deliberately plain text and newline-framed by client.py.

This button-only model treats every RF operation as a stateless press. It exposes
no Home Assistant fan or light entities and therefore does not imply any physical
state tracking.

Examples you might replace these with:
- hexadecimal frames: bytes.fromhex("a1 02 03 04")
- ASCII protocol lines: b"TX FAN POWER"
- vendor-specific JSON: b'{"device":"fan","command":"power"}'
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RFButtonCommand:
    """Description of one stateless RF command button."""

    key: str
    name: str
    icon: str
    command: bytes


# Add, remove, or rename buttons here. Each entry becomes one Home Assistant
# ButtonEntity. The key must remain stable after users add the integration,
# because it is used as part of the entity's unique ID.
BUTTON_COMMANDS: tuple[RFButtonCommand, ...] = (
    RFButtonCommand(
        key="fan_power_toggle",
        name="Fan Power Toggle",
        icon="mdi:fan",
        command=b"cc power",
    ),
    RFButtonCommand(
        key="fan_speed_1",
        name="Fan Speed 1",
        icon="mdi:fan-speed-1",
        command=b"cc speed 1",
    ),
    RFButtonCommand(
        key="fan_speed_2",
        name="Fan Speed 2",
        icon="mdi:fan-speed-2",
        command=b"cc speed 2",
    ),
    RFButtonCommand(
        key="fan_speed_3",
        name="Fan Speed 3",
        icon="mdi:fan-speed-3",
        command=b"cc speed 3",
    ),
    RFButtonCommand(
        key="fan_speed_4",
        name="Fan Speed 4",
        icon="mdi:fan-speed-4",
        command=b"cc speed 1",
    ),
    RFButtonCommand(
        key="fan_speed_5",
        name="Fan Speed 5",
        icon="mdi:fan-speed-5",
        command=b"cc speed 5",
    ),
    RFButtonCommand(
        key="fan_speed_6",
        name="Fan Speed 6",
        icon="mdi:fan-speed-6",
        command=b"cc speed 6",
    ),
    RFButtonCommand(
        key="light_toggle",
        name="Light Toggle",
        icon="mdi:lightbulb",
        command=b"cc light",
    ),
    RFButtonCommand(
        key="beep_toggle",
        name="Beep Toggle",
        icon="mdi:lightbulb",
        command=b"cc light",
    ),
)


def validate_commands() -> None:
    """Validate static command mappings at startup."""
    seen_keys: set[str] = set()
    for button in BUTTON_COMMANDS:
        if not button.key:
            raise ValueError("Button command keys must not be empty")
        if button.key in seen_keys:
            raise ValueError(f"Duplicate button command key: {button.key}")
        seen_keys.add(button.key)

        if not button.name:
            raise ValueError(f"Button {button.key} must have a name")
        if not isinstance(button.command, bytes) or not button.command:
            raise ValueError(f"Button {button.key} must define a non-empty bytes command")
