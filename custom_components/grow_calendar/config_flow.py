"""Config flow for Grow Calendar."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries

from .const import CONF_GROW_NAME, DEFAULT_GROW_NAME, DOMAIN


class GrowCalendarConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Grow Calendar."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Create a grow calendar entry."""
        errors = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_GROW_NAME].lower())
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=user_input[CONF_GROW_NAME],
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_GROW_NAME, default=DEFAULT_GROW_NAME): str,
                }
            ),
            errors=errors,
        )
