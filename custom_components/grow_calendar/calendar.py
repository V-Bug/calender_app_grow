"""Calendar entity for Grow Calendar."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, PHASES


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up grow calendar entity."""
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([GrowCalendarEntity(data)])


class GrowCalendarEntity(CalendarEntity):
    """Calendar showing grow phases as all-day events."""

    _attr_has_entity_name = True
    _attr_name = "Kalender"
    _attr_icon = "mdi:calendar-month"

    def __init__(self, data) -> None:
        """Initialize the calendar entity."""
        self._data = data
        self._attr_unique_id = f"{data.entry.entry_id}_calendar"
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
    def event(self) -> CalendarEvent | None:
        """Return the current or next event."""
        events = _build_events(self._data.phase_dates)
        for event in events:
            if event.end > date.today():
                return event
        return None

    async def async_get_events(
        self,
        hass: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Return events in the requested date range."""
        return [
            event
            for event in _build_events(self._data.phase_dates)
            if event.start < _as_date(end_date) and event.end > _as_date(start_date)
        ]


def _build_events(phase_dates: dict[str, date | None]) -> list[CalendarEvent]:
    """Build all-day phase events from configured start dates."""
    dated_phases = [
        (phase, name, phase_dates.get(phase))
        for phase, name in PHASES
        if phase_dates.get(phase) is not None
    ]
    events = []

    for index, (phase, name, start) in enumerate(dated_phases):
        next_start = (
            dated_phases[index + 1][2]
            if index + 1 < len(dated_phases)
            else max(date.today(), start) + timedelta(days=1)
        )

        if next_start < start:
            continue

        duration = (next_start - start).days
        summary = f"{name} ({duration} Tage)" if duration else name
        events.append(
            CalendarEvent(
                summary=summary,
                start=start,
                end=next_start,
                uid=f"{phase}-{start.isoformat()}",
            )
        )

    return events


def _as_date(value: date | datetime) -> date:
    """Convert a date or datetime to a comparable date."""
    if isinstance(value, datetime):
        return value.date()

    return value
