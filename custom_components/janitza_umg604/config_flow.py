"""Configuration flow for the Janitza UMG 604-PRO."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers import selector

from .const import (
    CONF_ADDRESS_OFFSET,
    CONF_SCAN_INTERVAL,
    CONF_UNIT_ID,
    DEFAULT_ADDRESS_OFFSET,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_UNIT_ID,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
)


class JanitzaConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the Janitza setup flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        errors: dict[str, str] = {}
        if user_input is not None:
            user_input[CONF_HOST] = user_input[CONF_HOST].strip()
            user_input[CONF_PORT] = int(user_input[CONF_PORT])
            user_input[CONF_UNIT_ID] = int(user_input[CONF_UNIT_ID])
            user_input[CONF_SCAN_INTERVAL] = int(user_input[CONF_SCAN_INTERVAL])
            user_input[CONF_ADDRESS_OFFSET] = int(user_input[CONF_ADDRESS_OFFSET])
            client = None
            try:
                from .modbus import JanitzaConnectionError, JanitzaModbusClient

                client = JanitzaModbusClient(
                    user_input[CONF_HOST],
                    user_input[CONF_PORT],
                    user_input[CONF_UNIT_ID],
                    user_input[CONF_ADDRESS_OFFSET],
                )
                await client.async_probe()
            except JanitzaConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:  # Home Assistant requires unknown setup errors to be caught.
                errors["base"] = "unknown"
            finally:
                if client is not None:
                    await client.async_close()

            if not errors:
                unique_id = (
                    f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}:"
                    f"{user_input[CONF_UNIT_ID]}"
                )
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"UMG 604-PRO ({user_input[CONF_HOST]})", data=user_input
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
                ),
                vol.Required(CONF_PORT, default=DEFAULT_PORT): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=1, max=65535, mode=selector.NumberSelectorMode.BOX)
                ),
                vol.Required(CONF_UNIT_ID, default=DEFAULT_UNIT_ID): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=0, max=255, mode=selector.NumberSelectorMode.BOX)
                ),
                vol.Required(
                    CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=MIN_SCAN_INTERVAL,
                        max=MAX_SCAN_INTERVAL,
                        unit_of_measurement="s",
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Required(
                    CONF_ADDRESS_OFFSET, default=DEFAULT_ADDRESS_OFFSET
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(min=-1, max=0, mode=selector.NumberSelectorMode.BOX)
                ),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
