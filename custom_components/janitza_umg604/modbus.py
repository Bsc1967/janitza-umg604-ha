"""Read-only Modbus TCP client for the Janitza UMG 604-PRO."""

from __future__ import annotations

import struct
import math
from typing import Any

from pymodbus.client import AsyncModbusTcpClient


class JanitzaConnectionError(Exception):
    """Raised when the meter cannot be read."""


class JanitzaModbusClient:
    """Small read-only wrapper around pymodbus."""

    def __init__(
        self, host: str, port: int, unit_id: int, address_offset: int = 0
    ) -> None:
        self._unit_id = unit_id
        self._address_offset = address_offset
        self._client = AsyncModbusTcpClient(host, port=port, timeout=5)

    async def _read(self, address: int, count: int) -> list[int]:
        if not self._client.connected and not await self._client.connect():
            raise JanitzaConnectionError("Kan geen Modbus TCP-verbinding maken")

        try:
            result = await self._client.read_holding_registers(
                address + self._address_offset,
                count=count,
                device_id=self._unit_id,
            )
        except (OSError, TimeoutError) as err:
            self._client.close()
            raise JanitzaConnectionError(str(err)) from err

        if result.isError():
            raise JanitzaConnectionError(f"Modbus-fout bij register {address}: {result}")
        return result.registers

    @staticmethod
    def _float(registers: list[int], index: int) -> float:
        """Decode a big-endian IEEE-754 float from two 16-bit registers."""
        return struct.unpack(">f", struct.pack(">HH", registers[index], registers[index + 1]))[0]

    @classmethod
    def _optional_float(cls, registers: list[int], index: int = 0) -> float | None:
        value = cls._float(registers, index)
        return value if math.isfinite(value) else None

    @staticmethod
    def _uint(registers: list[int], index: int = 0) -> int:
        return struct.unpack(">I", struct.pack(">HH", registers[index], registers[index + 1]))[0]

    @staticmethod
    def _string(registers: list[int]) -> str:
        raw = struct.pack(f">{len(registers)}H", *registers)
        return raw.split(b"\0", 1)[0].decode("latin-1", errors="replace").strip()

    async def async_read_data(self) -> dict[str, float | int | str | None]:
        """Read the main live values and energy counters."""
        # One contiguous request for live values: register 1317 through 1440.
        live = await self._read(1317, 124)

        def value(address: int) -> float:
            return self._float(live, address - 1317)

        data = {
            "voltage_l1": value(1317),
            "voltage_l2": value(1319),
            "voltage_l3": value(1321),
            "current_l1": value(1325),
            "current_l2": value(1327),
            "current_l3": value(1329),
            "active_power_l1": value(1333),
            "active_power_l2": value(1335),
            "active_power_l3": value(1337),
            "voltage_l1_l2": value(1357),
            "voltage_l2_l3": value(1359),
            "voltage_l3_l1": value(1361),
            "apparent_power_total": value(1367),
            "active_power_total": value(1369),
            "reactive_power_total": value(1371),
            "power_factor_total": value(1373),
            "frequency": value(1439),
        }

        # Consumption and supply counters for L1+L2+L3 (Wh).
        consumed = await self._read(9851, 14)
        data["energy_consumed"] = self._float(consumed, 0) / 1000
        data["energy_returned"] = self._float(consumed, 12) / 1000

        # Device diagnostics and additional power-quality values.
        sequence = await self._read(1443, 20)
        data["voltage_unbalance"] = self._optional_float(sequence, 4)
        data["phase_sequence"] = self._optional_float(sequence, 6)
        temperature = self._optional_float(sequence, 18)
        data["temperature"] = None if temperature is None or temperature <= -100 else temperature

        inputs_and_counts = await self._read(9975, 8)
        data["digital_input_1"] = inputs_and_counts[0]
        data["digital_input_2"] = inputs_and_counts[1]
        data["event_count"] = self._uint(inputs_and_counts, 2)
        data["flag_count"] = self._uint(inputs_and_counts, 4)
        data["transient_count"] = self._uint(inputs_and_counts, 6)

        serial_number = self._uint(await self._read(10176, 2))
        data["serial_number"] = f"{serial_number // 10000:04d}.{serial_number % 10000:04d}"
        data["production_number"] = str(self._uint(await self._read(10178, 2)))
        data["device_name"] = self._string(await self._read(10072, 32))
        data["device_description"] = self._string(await self._read(10104, 64))
        data["firmware"] = self._string(await self._read(13437, 8))

        transformers = await self._read(10032, 32)
        for phase in range(3):
            data[f"ct_primary_l{phase + 1}"] = self._optional_float(transformers, phase * 2)
            data[f"ct_secondary_l{phase + 1}"] = self._optional_float(transformers, 8 + phase * 2)
            data[f"vt_primary_l{phase + 1}"] = self._optional_float(transformers, 16 + phase * 2)
            data[f"vt_secondary_l{phase + 1}"] = self._optional_float(transformers, 24 + phase * 2)

        # L1 aliases retained for compatibility with the local web dashboard naming.
        data["ct_primary"] = data["ct_primary_l1"]
        data["ct_secondary"] = data["ct_secondary_l1"]
        data["vt_primary"] = data["vt_primary_l1"]
        data["vt_secondary"] = data["vt_secondary_l1"]

        cos_phi = await self._read(19044, 6)
        data["cos_phi_l1"] = self._optional_float(cos_phi, 0)
        data["cos_phi_l2"] = self._optional_float(cos_phi, 2)
        data["cos_phi_l3"] = self._optional_float(cos_phi, 4)

        thd = await self._read(19110, 12)
        data["thd_voltage_l1"] = self._optional_float(thd, 0)
        data["thd_voltage_l2"] = self._optional_float(thd, 2)
        data["thd_voltage_l3"] = self._optional_float(thd, 4)
        data["thd_current_l1"] = self._optional_float(thd, 6)
        data["thd_current_l2"] = self._optional_float(thd, 8)
        data["thd_current_l3"] = self._optional_float(thd, 10)

        power_factors = await self._read(15237, 8)
        data["power_factor_l1"] = self._optional_float(power_factors, 0)
        data["power_factor_l2"] = self._optional_float(power_factors, 2)
        data["power_factor_l3"] = self._optional_float(power_factors, 4)

        extended_quality = await self._read(19636, 12)
        data["power_factor_average"] = self._optional_float(extended_quality, 0)
        data["tdd_current_l1"] = self._optional_float(extended_quality, 2)
        data["tdd_current_l2"] = self._optional_float(extended_quality, 4)
        data["tdd_current_l3"] = self._optional_float(extended_quality, 6)
        data["current_unbalance"] = self._optional_float(extended_quality, 10)

        extra_energy = await self._read(19078, 32)
        apparent_energy = self._optional_float(extra_energy, 6)
        reactive_energy = self._optional_float(extra_energy, 14)
        reactive_energy_inductive = self._optional_float(extra_energy, 22)
        reactive_energy_capacitive = self._optional_float(extra_energy, 30)
        data["apparent_energy"] = None if apparent_energy is None else apparent_energy / 1000
        data["reactive_energy"] = None if reactive_energy is None else reactive_energy / 1000
        data["reactive_energy_inductive"] = (
            None if reactive_energy_inductive is None else reactive_energy_inductive / 1000
        )
        data["reactive_energy_capacitive"] = (
            None if reactive_energy_capacitive is None else reactive_energy_capacitive / 1000
        )
        return data

    async def async_probe(self) -> None:
        """Verify that the configured endpoint returns a plausible frequency."""
        registers = await self._read(1439, 2)
        frequency = self._float(registers, 0)
        if not 0 <= frequency <= 100:
            raise JanitzaConnectionError(
                "Verbinding gelukt, maar de registergegevens zijn niet herkenbaar"
            )

    async def async_close(self) -> None:
        """Close the TCP connection."""
        self._client.close()
