"""Sensor entities for the Janitza UMG 604-PRO."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, PERCENTAGE, UnitOfApparentPower, UnitOfElectricCurrent, UnitOfElectricPotential, UnitOfEnergy, UnitOfFrequency, UnitOfPower, UnitOfReactivePower, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import JanitzaCoordinator


@dataclass(frozen=True, kw_only=True)
class JanitzaSensorDescription(SensorEntityDescription):
    suggested_display_precision: int | None = 2


SENSORS = (
    *(
        JanitzaSensorDescription(key=f"voltage_l{phase}", translation_key=f"voltage_l{phase}", device_class=SensorDeviceClass.VOLTAGE, native_unit_of_measurement=UnitOfElectricPotential.VOLT, state_class=SensorStateClass.MEASUREMENT)
        for phase in range(1, 4)
    ),
    *(
        JanitzaSensorDescription(key=f"current_l{phase}", translation_key=f"current_l{phase}", device_class=SensorDeviceClass.CURRENT, native_unit_of_measurement=UnitOfElectricCurrent.AMPERE, state_class=SensorStateClass.MEASUREMENT)
        for phase in range(1, 4)
    ),
    *(
        JanitzaSensorDescription(key=f"active_power_l{phase}", translation_key=f"active_power_l{phase}", device_class=SensorDeviceClass.POWER, native_unit_of_measurement=UnitOfPower.WATT, state_class=SensorStateClass.MEASUREMENT)
        for phase in range(1, 4)
    ),
    JanitzaSensorDescription(key="voltage_l1_l2", translation_key="voltage_l1_l2", device_class=SensorDeviceClass.VOLTAGE, native_unit_of_measurement=UnitOfElectricPotential.VOLT, state_class=SensorStateClass.MEASUREMENT),
    JanitzaSensorDescription(key="voltage_l2_l3", translation_key="voltage_l2_l3", device_class=SensorDeviceClass.VOLTAGE, native_unit_of_measurement=UnitOfElectricPotential.VOLT, state_class=SensorStateClass.MEASUREMENT),
    JanitzaSensorDescription(key="voltage_l3_l1", translation_key="voltage_l3_l1", device_class=SensorDeviceClass.VOLTAGE, native_unit_of_measurement=UnitOfElectricPotential.VOLT, state_class=SensorStateClass.MEASUREMENT),
    JanitzaSensorDescription(key="active_power_total", translation_key="active_power_total", device_class=SensorDeviceClass.POWER, native_unit_of_measurement=UnitOfPower.WATT, state_class=SensorStateClass.MEASUREMENT),
    JanitzaSensorDescription(key="reactive_power_total", translation_key="reactive_power_total", device_class=SensorDeviceClass.REACTIVE_POWER, native_unit_of_measurement=UnitOfReactivePower.VOLT_AMPERE_REACTIVE, state_class=SensorStateClass.MEASUREMENT),
    JanitzaSensorDescription(key="apparent_power_total", translation_key="apparent_power_total", device_class=SensorDeviceClass.APPARENT_POWER, native_unit_of_measurement=UnitOfApparentPower.VOLT_AMPERE, state_class=SensorStateClass.MEASUREMENT),
    JanitzaSensorDescription(key="power_factor_total", translation_key="power_factor_total", device_class=SensorDeviceClass.POWER_FACTOR, state_class=SensorStateClass.MEASUREMENT, suggested_display_precision=3),
    JanitzaSensorDescription(key="frequency", translation_key="frequency", device_class=SensorDeviceClass.FREQUENCY, native_unit_of_measurement=UnitOfFrequency.HERTZ, state_class=SensorStateClass.MEASUREMENT),
    JanitzaSensorDescription(key="energy_consumed", translation_key="energy_consumed", device_class=SensorDeviceClass.ENERGY, native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, state_class=SensorStateClass.TOTAL_INCREASING, suggested_display_precision=3),
    JanitzaSensorDescription(key="energy_returned", translation_key="energy_returned", device_class=SensorDeviceClass.ENERGY, native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR, state_class=SensorStateClass.TOTAL_INCREASING, suggested_display_precision=3),
    JanitzaSensorDescription(key="apparent_energy", translation_key="apparent_energy", native_unit_of_measurement="kVAh", state_class=SensorStateClass.TOTAL_INCREASING, suggested_display_precision=3),
    JanitzaSensorDescription(key="reactive_energy", translation_key="reactive_energy", native_unit_of_measurement="kvarh", state_class=SensorStateClass.TOTAL_INCREASING, suggested_display_precision=3),
    JanitzaSensorDescription(key="reactive_energy_inductive", translation_key="reactive_energy_inductive", native_unit_of_measurement="kvarh", state_class=SensorStateClass.TOTAL_INCREASING, suggested_display_precision=3),
    JanitzaSensorDescription(key="reactive_energy_capacitive", translation_key="reactive_energy_capacitive", native_unit_of_measurement="kvarh", state_class=SensorStateClass.TOTAL_INCREASING, suggested_display_precision=3),
    JanitzaSensorDescription(key="temperature", translation_key="temperature", device_class=SensorDeviceClass.TEMPERATURE, native_unit_of_measurement=UnitOfTemperature.CELSIUS, state_class=SensorStateClass.MEASUREMENT, suggested_display_precision=1),
    JanitzaSensorDescription(key="voltage_unbalance", translation_key="voltage_unbalance", native_unit_of_measurement=PERCENTAGE, state_class=SensorStateClass.MEASUREMENT, suggested_display_precision=2),
    JanitzaSensorDescription(key="current_unbalance", translation_key="current_unbalance", native_unit_of_measurement=PERCENTAGE, state_class=SensorStateClass.MEASUREMENT, suggested_display_precision=2),
    JanitzaSensorDescription(key="phase_sequence", translation_key="phase_sequence", entity_category=EntityCategory.DIAGNOSTIC, icon="mdi:rotate-3d-variant", suggested_display_precision=None),
    *(JanitzaSensorDescription(key=f"cos_phi_l{phase}", translation_key=f"cos_phi_l{phase}", state_class=SensorStateClass.MEASUREMENT, suggested_display_precision=3) for phase in range(1, 4)),
    *(JanitzaSensorDescription(key=f"power_factor_l{phase}", translation_key=f"power_factor_l{phase}", device_class=SensorDeviceClass.POWER_FACTOR, state_class=SensorStateClass.MEASUREMENT, suggested_display_precision=3) for phase in range(1, 4)),
    JanitzaSensorDescription(key="power_factor_average", translation_key="power_factor_average", device_class=SensorDeviceClass.POWER_FACTOR, state_class=SensorStateClass.MEASUREMENT, suggested_display_precision=3),
    *(JanitzaSensorDescription(key=f"thd_voltage_l{phase}", translation_key=f"thd_voltage_l{phase}", native_unit_of_measurement=PERCENTAGE, state_class=SensorStateClass.MEASUREMENT, suggested_display_precision=2) for phase in range(1, 4)),
    *(JanitzaSensorDescription(key=f"thd_current_l{phase}", translation_key=f"thd_current_l{phase}", native_unit_of_measurement=PERCENTAGE, state_class=SensorStateClass.MEASUREMENT, suggested_display_precision=2) for phase in range(1, 4)),
    *(JanitzaSensorDescription(key=f"tdd_current_l{phase}", translation_key=f"tdd_current_l{phase}", native_unit_of_measurement=PERCENTAGE, state_class=SensorStateClass.MEASUREMENT, suggested_display_precision=2) for phase in range(1, 4)),
    *(JanitzaSensorDescription(key=f"ct_primary_l{phase}", translation_key=f"ct_primary_l{phase}", entity_category=EntityCategory.DIAGNOSTIC, native_unit_of_measurement=UnitOfElectricCurrent.AMPERE, icon="mdi:current-ac", suggested_display_precision=2) for phase in range(1, 4)),
    *(JanitzaSensorDescription(key=f"ct_secondary_l{phase}", translation_key=f"ct_secondary_l{phase}", entity_category=EntityCategory.DIAGNOSTIC, native_unit_of_measurement=UnitOfElectricCurrent.AMPERE, icon="mdi:current-ac", suggested_display_precision=2) for phase in range(1, 4)),
    *(JanitzaSensorDescription(key=f"vt_primary_l{phase}", translation_key=f"vt_primary_l{phase}", entity_category=EntityCategory.DIAGNOSTIC, native_unit_of_measurement=UnitOfElectricPotential.VOLT, icon="mdi:sine-wave", suggested_display_precision=2) for phase in range(1, 4)),
    *(JanitzaSensorDescription(key=f"vt_secondary_l{phase}", translation_key=f"vt_secondary_l{phase}", entity_category=EntityCategory.DIAGNOSTIC, native_unit_of_measurement=UnitOfElectricPotential.VOLT, icon="mdi:sine-wave", suggested_display_precision=2) for phase in range(1, 4)),
    JanitzaSensorDescription(key="digital_input_1", translation_key="digital_input_1", icon="mdi:electric-switch"),
    JanitzaSensorDescription(key="digital_input_2", translation_key="digital_input_2", icon="mdi:electric-switch"),
    JanitzaSensorDescription(key="event_count", translation_key="event_count", entity_category=EntityCategory.DIAGNOSTIC, icon="mdi:alert-circle-outline", suggested_display_precision=None),
    JanitzaSensorDescription(key="flag_count", translation_key="flag_count", entity_category=EntityCategory.DIAGNOSTIC, icon="mdi:flag-outline", suggested_display_precision=None),
    JanitzaSensorDescription(key="transient_count", translation_key="transient_count", entity_category=EntityCategory.DIAGNOSTIC, icon="mdi:lightning-bolt", suggested_display_precision=None),
    JanitzaSensorDescription(key="serial_number", translation_key="serial_number", entity_category=EntityCategory.DIAGNOSTIC, icon="mdi:identifier", suggested_display_precision=None),
    JanitzaSensorDescription(key="production_number", translation_key="production_number", entity_category=EntityCategory.DIAGNOSTIC, icon="mdi:barcode", suggested_display_precision=None),
    JanitzaSensorDescription(key="device_name", translation_key="device_name", entity_category=EntityCategory.DIAGNOSTIC, icon="mdi:label-outline", suggested_display_precision=None),
    JanitzaSensorDescription(key="device_description", translation_key="device_description", entity_category=EntityCategory.DIAGNOSTIC, icon="mdi:card-text-outline", suggested_display_precision=None),
    JanitzaSensorDescription(key="firmware", translation_key="firmware", entity_category=EntityCategory.DIAGNOSTIC, icon="mdi:chip", suggested_display_precision=None),
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddConfigEntryEntitiesCallback) -> None:
    coordinator: JanitzaCoordinator = entry.runtime_data
    async_add_entities(JanitzaSensor(coordinator, description) for description in SENSORS)


class JanitzaSensor(CoordinatorEntity[JanitzaCoordinator], SensorEntity):
    entity_description: JanitzaSensorDescription
    _attr_has_entity_name = True

    def __init__(self, coordinator: JanitzaCoordinator, description: JanitzaSensorDescription) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.entry.unique_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.entry.unique_id)},
            name=coordinator.entry.title,
            manufacturer="Janitza",
            model="UMG 604-PRO",
            configuration_url=f"http://{coordinator.entry.data['host']}",
        )

    @property
    def native_value(self) -> float | int | str | None:
        return self.coordinator.data.get(self.entity_description.key)
