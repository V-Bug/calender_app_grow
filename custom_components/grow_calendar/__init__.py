"""Grow Calendar integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
import logging
from pathlib import Path

import voluptuous as vol

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.storage import Store

from .const import (
    ATTR_ENTRY_ID,
    ATTR_GROW_NAME,
    ATTR_PHASE,
    CONF_GROW_NAME,
    DEFAULT_GROW_NAME,
    DOMAIN,
    PHASES,
    PLATFORMS,
    SERVICE_CLEAR_PHASE_DATE,
    STORE_KEY,
    STORE_VERSION,
)

_LOGGER = logging.getLogger(__name__)

FRONTEND_PATH = Path(__file__).parent / "www"
FRONTEND_URL = f"/{DOMAIN}"
PHASE_KEYS = [phase for phase, _phase_name in PHASES]


@dataclass
class GrowCalendarData:
    """Shared phase data for one grow."""

    hass: HomeAssistant
    entry: ConfigEntry
    store: Store
    phase_dates: dict[str, date | None] = field(default_factory=dict)
    listeners: list[Callable[[], None]] = field(default_factory=list)
    remove_daily_update: Callable[[], None] | None = None

    @property
    def name(self) -> str:
        """Return the configured grow name."""
        return self.entry.data.get(CONF_GROW_NAME, DEFAULT_GROW_NAME)

    @callback
    def async_add_listener(self, listener: Callable[[], None]) -> Callable[[], None]:
        """Register an entity update listener."""
        self.listeners.append(listener)

        @callback
        def remove_listener() -> None:
            self.listeners.remove(listener)

        return remove_listener

    @callback
    def async_notify_listeners(self) -> None:
        """Notify entities that shared data changed."""
        for listener in list(self.listeners):
            listener()

    async def async_set_phase_date(self, phase: str, value: date | None) -> None:
        """Persist a phase start date."""
        self.phase_dates[phase] = value
        stored = await self.store.async_load() or {}
        stored[self.entry.entry_id] = {
            phase_key: phase_date.isoformat() if phase_date else None
            for phase_key, phase_date in self.phase_dates.items()
        }
        await self.store.async_save(
            stored
        )
        self.async_notify_listeners()


async def async_setup(hass: HomeAssistant, _config: dict) -> bool:
    """Set up Grow Calendar frontend assets."""
    await hass.http.async_register_static_paths(
        [StaticPathConfig(FRONTEND_URL, str(FRONTEND_PATH), False)]
    )

    async def async_clear_phase_date(call: ServiceCall) -> None:
        """Clear one configured phase date."""
        phase = call.data[ATTR_PHASE]
        data = _resolve_service_data(
            hass,
            entry_id=call.data.get(ATTR_ENTRY_ID),
            grow_name=call.data.get(ATTR_GROW_NAME),
        )
        await data.async_set_phase_date(phase, None)

    hass.services.async_register(
        DOMAIN,
        SERVICE_CLEAR_PHASE_DATE,
        async_clear_phase_date,
        schema=vol.Schema(
            {
                vol.Required(ATTR_PHASE): vol.In(PHASE_KEYS),
                vol.Optional(ATTR_ENTRY_ID): str,
                vol.Optional(ATTR_GROW_NAME): str,
            }
        ),
    )
    return True


def _resolve_service_data(
    hass: HomeAssistant,
    *,
    entry_id: str | None,
    grow_name: str | None,
) -> GrowCalendarData:
    """Resolve a service target to one grow calendar data object."""
    entries = hass.data.get(DOMAIN, {})

    if entry_id:
        if entry_id in entries:
            return entries[entry_id]
        raise HomeAssistantError(f"Grow Calendar entry_id not found: {entry_id}")

    if grow_name:
        matches = [
            data
            for data in entries.values()
            if data.name.lower() == grow_name.lower()
            or data.entry.title.lower() == grow_name.lower()
        ]
        if len(matches) == 1:
            return matches[0]
        if not matches:
            raise HomeAssistantError(f"Grow Calendar grow_name not found: {grow_name}")
        raise HomeAssistantError(f"Multiple Grow Calendar entries match: {grow_name}")

    if len(entries) == 1:
        return next(iter(entries.values()))

    raise HomeAssistantError(
        "Set entry_id or grow_name when multiple Grow Calendar entries exist"
    )


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Grow Calendar from a config entry."""
    store = Store(hass, STORE_VERSION, STORE_KEY)
    stored = await store.async_load() or {}
    raw_dates = stored.get(entry.entry_id, {})
    phase_dates = {}

    for phase, _phase_name in PHASES:
        raw_date = raw_dates.get(phase)
        phase_dates[phase] = date.fromisoformat(raw_date) if raw_date else None

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = GrowCalendarData(
        hass=hass,
        entry=entry,
        store=store,
        phase_dates=phase_dates,
    )
    data = hass.data[DOMAIN][entry.entry_id]
    data.remove_daily_update = async_track_time_change(
        hass,
        lambda _now: data.async_notify_listeners(),
        hour=0,
        minute=0,
        second=5,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        data = hass.data[DOMAIN].pop(entry.entry_id)
        if data.remove_daily_update:
            data.remove_daily_update()

    return unload_ok
