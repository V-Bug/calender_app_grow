"""Date entities for Grow Calendar phase starts."""

from __future__ import annotations

from datetime import date

from homeassistant.components.date import DateEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, PHASE_ICON, PHASES


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up phase date entities."""
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        GrowPhaseDateEntity(data, phase, phase_name) for phase, phase_name in PHASES
    )


class GrowPhaseDateEntity(DateEntity):
    """A date input for one phase start."""

    _attr_has_entity_name = True

    def __init__(self, data, phase: str, phase_name: str) -> None:
        """Initialize the phase date entity."""
        self._data = data
        self._phase = phase
        self._phase_name = phase_name
        self._attr_name = phase_name
        self._attr_icon = PHASE_ICON[phase]
        self._attr_unique_id = f"{data.entry.entry_id}_{phase}_date"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, data.entry.entry_id)},
            name=data.name,
            manufacturer="Custom",
            model="Grow Calendar",
        )

    async def async_added_to_hass(self) -> None:
        """Subscribe to shared data updates."""
        self.async_on_remove(self._data.async_add_listener(self._handle_data_update))

    @callback
    def _handle_data_update(self) -> None:
        """Write entity state when shared data changes."""
        self.async_write_ha_state()

    @property
    def native_value(self) -> date | None:
        """Return the selected start date."""
        return self._data.phase_dates.get(self._phase)

    async def async_set_value(self, value: date) -> None:
        """Set the phase start date."""
        await self._data.async_set_phase_date(self._phase, value)
