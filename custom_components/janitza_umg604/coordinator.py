"""Data coordinator for the Janitza UMG 604-PRO."""

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_ADDRESS_OFFSET,
    CONF_SCAN_INTERVAL,
    CONF_UNIT_ID,
    DEFAULT_ADDRESS_OFFSET,
    DEFAULT_SCAN_INTERVAL,
)
from .modbus import JanitzaConnectionError, JanitzaModbusClient

_LOGGER = logging.getLogger(__name__)


class JanitzaCoordinator(DataUpdateCoordinator[dict[str, float | int | str | None]]):
    """Coordinate polling of one meter."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        self.client = JanitzaModbusClient(
            entry.data[CONF_HOST],
            entry.data[CONF_PORT],
            entry.data[CONF_UNIT_ID],
            entry.data.get(CONF_ADDRESS_OFFSET, DEFAULT_ADDRESS_OFFSET),
        )
        super().__init__(
            hass,
            _LOGGER,
            name=f"Janitza UMG 604-PRO {entry.data[CONF_HOST]}",
            update_interval=timedelta(
                seconds=entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
            ),
        )

    async def _async_update_data(self) -> dict[str, float | int | str | None]:
        try:
            return await self.client.async_read_data()
        except JanitzaConnectionError as err:
            raise UpdateFailed(str(err)) from err

    async def async_close(self) -> None:
        await self.client.async_close()
