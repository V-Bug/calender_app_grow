"""Constants for the Grow Calendar integration."""

from __future__ import annotations

DOMAIN = "grow_calendar"

PLATFORMS = ["calendar", "date", "sensor"]

CONF_GROW_NAME = "grow_name"
DEFAULT_GROW_NAME = "Grow"

ATTR_ENTRY_ID = "entry_id"
ATTR_GROW_NAME = "grow_name"
ATTR_PHASE = "phase"
SERVICE_CLEAR_PHASE_DATE = "clear_phase_date"

STORE_VERSION = 1
STORE_KEY = f"{DOMAIN}.storage"

PHASE_SEED = "seed"
PHASE_VEGETATION = "vegetation"
PHASE_BLOOM = "bloom"
PHASE_HARVEST = "harvest"

PHASES = [
    (PHASE_SEED, "Saat"),
    (PHASE_VEGETATION, "Vegetation"),
    (PHASE_BLOOM, "Blüte"),
    (PHASE_HARVEST, "Ernte"),
]

PHASE_ICON = {
    PHASE_SEED: "mdi:seed",
    PHASE_VEGETATION: "mdi:sprout",
    PHASE_BLOOM: "mdi:flower",
    PHASE_HARVEST: "mdi:basket",
}
