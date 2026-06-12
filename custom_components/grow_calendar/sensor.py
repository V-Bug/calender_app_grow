"""Sensors for Grow Calendar."""

from __future__ import annotations

from datetime import date

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, PHASES


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up grow sensors."""
    data = hass.data[DOMAIN][entry.entry_id]
    entities = [
        GrowCurrentPhaseSensor(data),
        GrowCurrentPhaseDaySensor(data),
    ]

    for index in range(len(PHASES) - 1):
        entities.append(GrowPhaseDurationSensor(data, index))

    async_add_entities(entities)


class GrowBaseSensor(SensorEntity):
    """Base class for grow sensors."""

    _attr_has_entity_name = True

    def __init__(self, data) -> None:
        """Initialize common sensor data."""
        self._data = data
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


class GrowCurrentPhaseSensor(GrowBaseSensor):
    """Current grow phase sensor."""

    _attr_icon = "mdi:calendar-clock"

    def __init__(self, data) -> None:
        """Initialize the current phase sensor."""
        super().__init__(data)
        self._attr_name = "Aktuelle Phase"
        self._attr_unique_id = f"{data.entry.entry_id}_current_phase"

    @property
    def native_value(self) -> str | None:
        """Return the current phase."""
        current = _current_phase(self._data.phase_dates)
        return current[1] if current else None


class GrowCurrentPhaseDaySensor(GrowBaseSensor):
    """Current phase day count sensor."""

    _attr_icon = "mdi:counter"
    _attr_native_unit_of_measurement = UnitOfTime.DAYS

    def __init__(self, data) -> None:
        """Initialize the current phase day sensor."""
        super().__init__(data)
        self._attr_name = "Tag der Phase"
        self._attr_unique_id = f"{data.entry.entry_id}_current_phase_day"

    @property
    def native_value(self) -> int | None:
        """Return the one-based day of the current phase."""
        current = _current_phase(self._data.phase_dates)
        if current is None:
            return None

        start = self._data.phase_dates[current[0]]
        if start is None:
            return None

        return (date.today() - start).days + 1


class GrowPhaseDurationSensor(GrowBaseSensor):
    """Duration between two phase starts."""

    _attr_device_class = SensorDeviceClass.DURATION
    _attr_icon = "mdi:timer-sand"
    _attr_native_unit_of_measurement = UnitOfTime.DAYS

    def __init__(self, data, phase_index: int) -> None:
        """Initialize a duration sensor."""
        super().__init__(data)
        self._start_phase, self._start_name = PHASES[phase_index]
        self._end_phase, self._end_name = PHASES[phase_index + 1]
        self._attr_name = f"{self._start_name} bis {self._end_name}"
        self._attr_unique_id = (
            f"{data.entry.entry_id}_{self._start_phase}_to_{self._end_phase}"
        )

    @property
    def native_value(self) -> int | None:
        """Return days between two configured phase starts."""
        start = self._data.phase_dates.get(self._start_phase)
        end = self._data.phase_dates.get(self._end_phase)
        if start is None or end is None:
            return None

        duration = (end - start).days
        return duration if duration >= 0 else None


def _current_phase(phase_dates: dict[str, date | None]) -> tuple[str, str] | None:
    """Return the newest configured phase that has already started."""
    today = date.today()
    started_phases = [
        (phase, name, phase_dates.get(phase))
        for phase, name in PHASES
        if phase_dates.get(phase) is not None and phase_dates[phase] <= today
    ]

    if not started_phases:
        return None

    phase, name, _phase_date = max(started_phases, key=lambda item: item[2])
    return phase, name
